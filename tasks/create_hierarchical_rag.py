#!/usr/bin/env python3
"""
POLLY Hierarchical RAG Indexer -- upgrades simple flat chunks to section-aware chunks.

Writes into the same polly_rag.documents and polly_rag.chunks tables using the
new columns added in sql/004_hierarchical_rag_schema.sql.
Existing rows from the simple pipeline are untouched.

Usage:
    python tasks/create_hierarchical_rag.py --doc-dir doc-data/ --product-id 1 --doc-type prospectus
    python tasks/create_hierarchical_rag.py --doc-dir doc-data/  # no product linkage (dev/test)
"""
import json
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

# Reuse extraction + embedding from the existing pipeline -- no duplication
from tasks.create_rag import DocumentProcessor, EmbeddingService


# ---------------------------------------------------------------------------
# Hierarchical chunker -- section-aware, produces parent + child pairs
# ---------------------------------------------------------------------------

class HierarchicalChunker:
    """
    Split markdown text into sections using heading markers, then create
    small child chunks within each section for precise vector matching.

    Each chunk carries:
      content        -- small text for embedding (150-400 chars)
      section_name   -- heading of the section it belongs to
      parent_section -- full section text returned to the LLM for context
    """

    # Headings we treat as section boundaries
    HEADING_RE = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
    CHILD_CHUNK_SIZE = 400
    CHILD_OVERLAP    = 80

    def chunk(self, text: str, metadata: dict = None) -> list[dict]:
        sections = self._split_sections(text)
        chunks = []
        for section in sections:
            child_texts = self._split_child_chunks(section["content"])
            for i, child_text in enumerate(child_texts):
                chunks.append({
                    "content":        child_text,
                    "section_name":   section["heading"],
                    "parent_section": section["content"],
                    "token_count":    len(child_text.split()),
                    "metadata":       metadata or {},
                })
        return chunks

    def _split_sections(self, text: str) -> list[dict]:
        """Split text at markdown headings. Returns list of {heading, content}."""
        matches = list(self.HEADING_RE.finditer(text))

        if not matches:
            # No headings found -- treat whole text as one section
            return [{"heading": "Document", "content": text.strip()}]

        sections = []
        for i, match in enumerate(matches):
            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            if content:
                sections.append({"heading": heading, "content": content})

        # Capture any text before the first heading
        preamble = text[:matches[0].start()].strip()
        if preamble:
            sections.insert(0, {"heading": "Preamble", "content": preamble})

        return sections

    def _split_child_chunks(self, text: str) -> list[str]:
        """Split a section into overlapping child chunks."""
        if len(text) <= self.CHILD_CHUNK_SIZE:
            return [text]

        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHILD_CHUNK_SIZE,
            chunk_overlap=self.CHILD_OVERLAP,
            separators=["\n\n", "\n", ". ", " "],
            length_function=len,
        )
        docs = splitter.create_documents([text])
        return [d.page_content for d in docs if d.page_content.strip()]


# ---------------------------------------------------------------------------
# Hierarchical RAG Indexer
# ---------------------------------------------------------------------------

class HierarchicalRAGIndexer:
    """
    Process documents into hierarchical chunks and store in the existing
    polly_rag.documents + polly_rag.chunks tables using the new columns.
    """

    def __init__(self, doc_dir: Path, product_id: int = None,
                 doc_type: str = None, jurisdiction: str = "UK",
                 approved: bool = False):
        from utils.db_pool import DatabasePool
        self.doc_dir     = doc_dir
        self.product_id  = product_id
        self.doc_type    = doc_type
        self.jurisdiction = jurisdiction
        self.approved    = approved
        self.pool        = DatabasePool.get()
        self.processor   = DocumentProcessor()
        self.chunker     = HierarchicalChunker()
        self.embedder    = EmbeddingService()

    def process_all(self) -> dict:
        files = sorted(
            f for f in self.doc_dir.iterdir()
            if f.suffix.lower() in (".pdf", ".pptx", ".docx")
        )
        print(f"\nFound {len(files)} documents in {self.doc_dir}")
        print(f"product_id={self.product_id}  doc_type={self.doc_type}  "
              f"approved={self.approved}  jurisdiction={self.jurisdiction}\n")

        stats = {"documents": [], "total_chunks": 0, "total_files": len(files)}
        for filepath in files:
            try:
                doc_stats = self.process_document(filepath)
                stats["documents"].append(doc_stats)
                stats["total_chunks"] += doc_stats.get("chunk_count", 0)
            except Exception as e:
                print(f"  ERROR processing {filepath.name}: {e}")
                stats["documents"].append({"filename": filepath.name, "error": str(e)})

        print(f"\n=== Done: {len(files)} documents, {stats['total_chunks']} chunks ===")
        return stats

    def process_document(self, filepath: Path) -> dict:
        from sqlalchemy import text
        t0 = time.monotonic()
        filename  = filepath.name
        file_type = filepath.suffix.lower().lstrip(".")
        file_size = filepath.stat().st_size

        print(f"  Processing: {filename} ({file_size // 1024}K)")

        # 1. Extract text
        markdown_text = self.processor.extract(filepath)
        print(f"    Extracted: {len(markdown_text)} chars")

        # 2. Hierarchical chunk
        metadata = {"filename": filename, "file_type": file_type,
                    "product_id": self.product_id, "doc_type": self.doc_type}
        chunks = self.chunker.chunk(markdown_text, metadata)
        print(f"    Chunks: {len(chunks)}")

        if not chunks:
            return {"filename": filename, "chunk_count": 0, "warning": "no text extracted"}

        # 3. Embed child content (small text, precise matching)
        embeddings = self.embedder.embed([c["content"] for c in chunks])
        print(f"    Embedded: {len(embeddings)} vectors")

        # 4. Store -- upsert into existing tables using new columns
        with self.pool.get_session() as session:
            # Upsert document row -- uses existing UNIQUE(filename) constraint
            result = session.execute(
                text("""
                    INSERT INTO polly_rag_hierarchical.documents
                        (filename, file_type, title, file_size_bytes, markdown_text,
                         chunk_count, product_id, doc_type, approved, jurisdiction)
                    VALUES
                        (:filename, :file_type, :title, :file_size, :markdown,
                         :chunk_count, :product_id, :doc_type, :approved, :jurisdiction)
                    ON CONFLICT (filename) DO UPDATE SET
                        markdown_text = EXCLUDED.markdown_text,
                        chunk_count   = EXCLUDED.chunk_count,
                        product_id    = EXCLUDED.product_id,
                        doc_type      = EXCLUDED.doc_type,
                        approved      = EXCLUDED.approved,
                        jurisdiction  = EXCLUDED.jurisdiction,
                        processed_at  = NOW()
                    RETURNING id
                """),
                {
                    "filename":    filename,
                    "file_type":   file_type,
                    "title":       filepath.stem,
                    "file_size":   file_size,
                    "markdown":    markdown_text,
                    "chunk_count": len(chunks),
                    "product_id":  self.product_id,
                    "doc_type":    self.doc_type,
                    "approved":    self.approved,
                    "jurisdiction": self.jurisdiction,
                },
            )
            doc_id = result.fetchone()[0]

            # Remove existing chunks for this document before re-inserting
            session.execute(
                text("DELETE FROM polly_rag_hierarchical.chunks WHERE document_id = :doc_id"),
                {"doc_id": doc_id},
            )

            # Insert hierarchical chunks with new columns
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                emb_str = "[" + ",".join(str(v) for v in embedding) + "]"
                session.execute(
                    text("""
                        INSERT INTO polly_rag_hierarchical.chunks
                            (document_id, chunk_index, content, token_count, metadata,
                             embedding, section_name, parent_section,
                             product_id, doc_type, approved, jurisdiction)
                        VALUES
                            (:doc_id, :idx, :content, :tokens, :meta,
                             cast(:emb AS vector), :section_name, :parent_section,
                             :product_id, :doc_type, :approved, :jurisdiction)
                    """),
                    {
                        "doc_id":         doc_id,
                        "idx":            i,
                        "content":        chunk["content"],
                        "tokens":         chunk["token_count"],
                        "meta":           json.dumps(chunk["metadata"]),
                        "emb":            emb_str,
                        "section_name":   chunk["section_name"],
                        "parent_section": chunk["parent_section"],
                        "product_id":     self.product_id,
                        "doc_type":       self.doc_type,
                        "approved":       self.approved,
                        "jurisdiction":   self.jurisdiction,
                    },
                )

        elapsed = time.monotonic() - t0
        print(f"    Stored: doc_id={doc_id}, {len(chunks)} chunks ({elapsed:.1f}s)")
        return {
            "filename":    filename,
            "doc_id":      doc_id,
            "chunk_count": len(chunks),
            "elapsed_seconds": round(elapsed, 1),
        }


DOC_TYPE_CHOICES = [
    "product_description", "prospectus", "term_sheet", "priips",
    "mifid_disclosures", "faq", "teaser", "pitch_deck",
    "terms_conditions", "market_research",
]

JURISDICTION_CHOICES = ["UK", "EU", "US", "APAC"]


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="POLLY Hierarchical RAG Indexer -- process documents into "
                    "section-aware vector chunks for product-scoped retrieval.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  # Index all docs in doc-data/ (no product link, not approved)
  python tasks/create_hierarchical_rag.py

  # Index for a specific product and doc type
  python tasks/create_hierarchical_rag.py --product-id 1 --doc-type term_sheet

  # Index and mark as approved (skip web approval step)
  python tasks/create_hierarchical_rag.py --product-id 1 --doc-type prospectus --approved

  # Index from custom directory with EU jurisdiction
  python tasks/create_hierarchical_rag.py --doc-dir /data/docs --jurisdiction EU

  # List valid doc types
  python tasks/create_hierarchical_rag.py --list-types

doc types:
  product_description   Product overview / marketing summary
  prospectus            Offering document / listing particulars
  term_sheet            Final terms / term sheet
  priips                PRIIPs KID / key information document
  mifid_disclosures     MiFID II disclosure documents
  faq                   Frequently asked questions
  teaser                Short marketing teaser
  pitch_deck            Investor pitch deck (PPTX/PDF)
  terms_conditions      Terms & conditions
  market_research       Market research / analysis

workflow:
  1. Upload docs via CLI (this script) or web UI (/documents)
  2. Documents start as approved=false (pending)
  3. Management user approves via web UI (/documents -> Approve)
  4. RAG starts serving approved docs to content agents
  5. Use --approved flag to skip step 2-3 (e.g. for initial bulk load)
""",
    )

    parser.add_argument(
        "--doc-dir", default=str(ROOT / "doc-data"),
        help="Directory containing PDF/DOCX/PPTX files (default: doc-data/)",
    )
    parser.add_argument(
        "--product-id", type=int, default=None,
        help="Link documents to a product (polly.products.id). "
             "Required for RAG filtering by product in agents.",
    )
    parser.add_argument(
        "--doc-type", default=None, choices=DOC_TYPE_CHOICES,
        help="Document type -- controls which agents retrieve this doc. "
             "Use --list-types to see all options.",
    )
    parser.add_argument(
        "--jurisdiction", default="UK", choices=JURISDICTION_CHOICES,
        help="Regulatory jurisdiction (default: UK)",
    )
    parser.add_argument(
        "--approved", action="store_true",
        help="Mark documents as approved immediately. Without this flag, "
             "docs start as pending and must be approved via web UI by a "
             "management user before RAG serves them.",
    )
    parser.add_argument(
        "--list-types", action="store_true",
        help="Print valid doc types and exit",
    )
    args = parser.parse_args()

    if args.list_types:
        print("Valid document types:")
        for dt in DOC_TYPE_CHOICES:
            print(f"  {dt}")
        print(f"\nValid jurisdictions: {', '.join(JURISDICTION_CHOICES)}")
        sys.exit(0)

    doc_dir = Path(args.doc_dir)
    if not doc_dir.exists():
        print(f"ERROR: Directory not found: {doc_dir}")
        sys.exit(1)

    indexer = HierarchicalRAGIndexer(
        doc_dir=doc_dir,
        product_id=args.product_id,
        doc_type=args.doc_type,
        jurisdiction=args.jurisdiction,
        approved=args.approved,
    )
    stats = indexer.process_all()

    out = ROOT / "test-results" / "hierarchical_rag_indexing.json"
    out.parent.mkdir(exist_ok=True)
    stats["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(out, "w") as f:
        json.dump(stats, f, indent=2)
    print(f"\nStats written to {out}")


if __name__ == "__main__":
    main()
