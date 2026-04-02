"""POLLY RAG Integration — Hierarchical retrieval from polly_rag_hierarchical.chunks with product/doc_type filtering."""
import os
from typing import Optional

from integrations.base import IntegrationBackend


class RagIntegration(IntegrationBackend):
    """
    Retrieval-augmented generation over compliance documents.

    Uses the existing polly_rag_hierarchical.chunks table with the new columns added in
    sql/004_hierarchical_rag_schema.sql:
      - product_id  → filter to one product's documents
      - doc_type    → filter to specific document types (e.g. only priips + term_sheet)
      - approved    → only return compliance-approved content

    retrieve() returns parent_section text (full section) not the small child chunk,
    so the LLM gets enough context. Deduplicates by section so the same section
    is never returned twice even if multiple child chunks matched.
    """

    name = "rag"
    # Same model used by create_rag.py and create_hierarchical_rag.py
    EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

    def __init__(self):
        self._embedder = None   # lazy-loaded (fastembed model takes a few seconds)
        self._pool = None

    def is_configured(self) -> bool:
        return bool(os.getenv("DB_URL"))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        product_id: Optional[int] = None,
        doc_types: Optional[list[str]] = None,
        top_k: int = 6,
        approved_only: bool = True,
        _fallback: bool = True,
    ) -> list[dict]:
        """
        Semantic search over polly_rag_hierarchical.chunks.

        Args:
            query:        Natural language query or tool name (e.g. "teaser content")
            product_id:   Restrict to one product. None = search all products.
            doc_types:    List of doc types to include, e.g. ['priips','term_sheet'].
                          None = all doc types.
            top_k:        Number of unique sections to return.
            approved_only: If True (default), only return approved=true chunks.

        Returns:
            List of dicts with keys:
              content      — parent_section text (full section, sent to LLM)
              section_name — heading of the section
              doc_type     — document type
              filename     — source filename
              similarity   — cosine similarity score (0-1)
        """
        embedding = self._embed(query)
        results = self._search(embedding, product_id, doc_types, top_k, approved_only)

        # If doc_type filter returned nothing (e.g. doc_types not yet set in DB),
        # retry without doc_type filter so the LLM always gets some context.
        if not results and _fallback and doc_types:
            results = self._search(embedding, product_id, None, top_k, approved_only)

        return results

    def retrieve_as_prompt_block(
        self,
        query: str,
        product_id: Optional[int] = None,
        doc_types: Optional[list[str]] = None,
        top_k: int = 6,
        approved_only: bool = True,
    ) -> str:
        """
        Same as retrieve() but returns a formatted string ready for LLM prompt injection.
        Drops in as a direct replacement for ComplianceDocSet.to_prompt_block().
        """
        chunks = self.retrieve(query, product_id, doc_types, top_k, approved_only)
        if not chunks:
            return ""

        lines = ["Compliance Document Context (retrieved):"]
        for c in chunks:
            label = f"{c['doc_type'] or 'document'} — {c['section_name'] or 'section'}"
            lines.append(f"\n[{label} | source: {c['filename']} | relevance: {c['similarity']:.2f}]")
            lines.append(c["content"])
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _embed(self, text: str) -> list[float]:
        if self._embedder is None:
            from fastembed import TextEmbedding
            self._embedder = TextEmbedding(model_name=self.EMBEDDING_MODEL)
        embeddings = list(self._embedder.embed([text]))
        return embeddings[0].tolist()

    def _search(
        self,
        embedding: list[float],
        product_id: Optional[int],
        doc_types: Optional[list[str]],
        top_k: int,
        approved_only: bool,
    ) -> list[dict]:
        from sqlalchemy import text
        pool = self._get_pool()

        emb_str = "[" + ",".join(str(v) for v in embedding) + "]"

        # Build WHERE clauses dynamically — only add filters that are set
        filters = []
        params: dict = {"emb": emb_str, "k": top_k * 4}  # fetch extra, deduplicate below

        if approved_only:
            filters.append("c.approved = true")

        if product_id is not None:
            filters.append("c.product_id = :product_id")
            params["product_id"] = product_id

        if doc_types:
            # Use ANY with a Postgres array literal — avoids per-item bind params
            placeholders = ", ".join(f":dt{i}" for i in range(len(doc_types)))
            filters.append(f"c.doc_type IN ({placeholders})")
            for i, dt in enumerate(doc_types):
                params[f"dt{i}"] = dt

        where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

        # CTE deduplicates by (document_id, section_name): keep only the
        # most-similar child chunk per section, then return parent_section text.
        sql = f"""
            WITH ranked AS (
                SELECT
                    c.id,
                    COALESCE(c.parent_section, c.content) AS content,
                    c.section_name,
                    c.doc_type,
                    d.filename,
                    d.title,
                    c.document_id,
                    1 - (c.embedding <=> cast(:emb AS vector)) AS similarity,
                    ROW_NUMBER() OVER (
                        PARTITION BY c.document_id, c.section_name
                        ORDER BY c.embedding <=> cast(:emb AS vector)
                    ) AS rn
                FROM polly_rag_hierarchical.chunks c
                JOIN polly_rag_hierarchical.documents d ON d.id = c.document_id
                {where_clause}
            )
            SELECT content, section_name, doc_type, filename, title, similarity
            FROM ranked
            WHERE rn = 1
            ORDER BY similarity DESC
            LIMIT :k
        """

        with pool.get_session() as session:
            rows = session.execute(text(sql), params).fetchall()

        return [
            {
                "content":      row.content,
                "section_name": row.section_name,
                "doc_type":     row.doc_type,
                "filename":     row.filename,
                "similarity":   round(float(row.similarity), 4),
            }
            for row in rows
        ]

    def _get_pool(self):
        if self._pool is None:
            from utils.db_pool import DatabasePool
            self._pool = DatabasePool.get()
        return self._pool
