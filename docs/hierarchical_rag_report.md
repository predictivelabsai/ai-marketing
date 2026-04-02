# POLLY Hierarchical RAG — Architecture, Results & Roadmap

---

## 1. What Changed From Naive RAG

The original RAG pipeline (built in `tasks/create_rag.py`) was a standard flat chunker: every document was split into equal 800-character chunks with 150-character overlap, embedded with `BAAI/bge-small-en-v1.5`, and stored in `polly_rag.chunks`. Retrieval was a single vector similarity scan across all 934 chunks from all documents with no filtering.

The hierarchical pipeline replaces this with a structure that mirrors how financial documents are actually written — in named sections — and adds product-level and compliance-level metadata so that retrieval can be scoped before the vector search runs.

### Side-by-Side Architecture

```
NAIVE RAG                               HIERARCHICAL RAG
─────────────────────────────────────── ──────────────────────────────────────────────────
Document (any)                          Document (linked to polly.products)
    ↓                                       ↓
RecursiveCharacterTextSplitter              HierarchicalChunker
  chunk_size=800, overlap=150                 1. Split at markdown headings (##, ###)
  → equal flat cuts regardless                2. Per section: create child chunks (400 chars)
    of document structure                     3. Store child text + full parent section
    ↓                                       ↓
polly_rag.chunks                        polly_rag_hierarchical.chunks
  content     (800 chars)                 content        (small — embedded, matched)
  metadata    {filename, file_type}       parent_section (full section — sent to LLM)
  embedding   vector(384)                 section_name   (heading text)
  ── no product link                      product_id     FK → polly.products
  ── no doc_type                          doc_type       'prospectus','term_sheet','priips'…
  ── no approved flag                     approved       boolean (compliance gate)
  ── no section structure                 jurisdiction   'UK','EU','US','APAC'
    ↓                                       ↓
SELECT … ORDER BY cosine_dist LIMIT 5   WHERE approved=true
  (scans all chunks, all products)        AND product_id = :product_id       ← pre-filter
                                          AND doc_type IN (…)                ← pre-filter
                                          ORDER BY cosine_dist LIMIT k*4
                                          → deduplicate by (document, section)
                                          → return top_k unique parent sections
```

---

## 2. Database Schema

Two new tables in the `polly_rag_hierarchical` schema. Zero changes to the existing `polly_rag.*` tables which remain in production.

### `polly_rag_hierarchical.documents`

| Column | Type | Purpose |
|--------|------|---------|
| `id` | SERIAL PK | — |
| `filename` | VARCHAR | Source file name (UNIQUE) |
| `file_type` | VARCHAR | pdf / pptx / docx |
| `markdown_text` | TEXT | Full extracted text |
| `chunk_count` | INTEGER | Number of child chunks |
| `product_id` | INTEGER FK → `polly.products` | Links doc to a financial product |
| `doc_type` | VARCHAR | Document role: prospectus, term_sheet, priips, mifid_disclosures, product_description, terms_conditions, market_research, faq, teaser, pitch_deck |
| `compliance_document_id` | INTEGER FK → `polly.compliance_documents` | Links to approval record |
| `approved` | BOOLEAN | Set by Management persona approval |
| `approved_by` | INTEGER FK → `polly.users` | Who approved |
| `jurisdiction` | VARCHAR | Regulatory jurisdiction |

### `polly_rag_hierarchical.chunks`

| Column | Type | Purpose |
|--------|------|---------|
| `content` | TEXT | Small child chunk — gets embedded and matched |
| `parent_section` | TEXT | Full section text — sent to the LLM as context |
| `section_name` | TEXT | Heading of the section (e.g. "Section 8: Risk Factors") |
| `product_id` | INTEGER | Denormalised from document for fast filtering |
| `doc_type` | VARCHAR | Denormalised from document for fast filtering |
| `approved` | BOOLEAN | Denormalised — retrieval only returns `approved=true` |
| `embedding` | vector(384) | BAAI/bge-small-en-v1.5 embedding of `content` |

### Indexes

```sql
-- Vector search (HNSW — approximate nearest neighbour, fast at scale)
CREATE INDEX idx_h_chunks_embedding ON polly_rag_hierarchical.chunks
    USING hnsw (embedding vector_cosine_ops);

-- Pre-filter index — applied BEFORE vector search to narrow candidate set
CREATE INDEX idx_h_chunks_filter ON polly_rag_hierarchical.chunks
    (product_id, doc_type, approved);
```

---

## 3. How product_id Works — One Product vs Many

### Why product_id exists

Every content generation tool in POLLY (teaser, FAQ, pitch deck, compliance review) must draw only from the documents for the product being marketed. Without `product_id`, a query about "FTSE Autocallable barrier levels" could retrieve chunks from the XTCC Solar prospectus — factually wrong and a compliance failure.

### Current state — one product

```
polly.products
  id=1  XTCC Solar 4Y Principal Protected Note

polly_rag_hierarchical.chunks
  1838 chunks, all with product_id=1
```

All retrieval queries are scoped to `product_id=1`. The filter eliminates zero rows right now (only one product), but the architecture is in place.

### When a second product is added

```
polly.products
  id=1  XTCC Solar Note
  id=2  FTSE 100 Autocallable Note      ← new
  id=3  S&P 500 Kick-Out Note           ← new

polly_rag_hierarchical.chunks
  chunks with product_id=1  (1838 rows — XTCC docs)
  chunks with product_id=2  (new rows — FTSE docs)
  chunks with product_id=3  (new rows — S&P docs)
```

The retrieval call scopes to the active product:

```python
# Campaign manager is working on FTSE product
rag.retrieve(
    query      = "barrier protection capital at risk",
    product_id = 2,           # only FTSE docs returned
    doc_types  = ["term_sheet", "priips"],
    approved_only = True,
)
# → never returns XTCC or S&P chunks
```

### Indexing a second product

```bash
# Put FTSE docs in a staging folder, then:
python tasks/create_hierarchical_rag.py \
  --doc-dir doc-data/ftse-autocallable/ \
  --product-id 2 \
  --doc-type term_sheet \
  --approved
```

Run once per document type. The `UNIQUE(filename)` constraint on the documents table prevents double-indexing the same file.

---

## 4. Evaluation Results

### Test setup

- 8 questions covering: product overview, terms, currency, protection, issuer, risks, ISIN, underlying asset
- Same question set used for both pipelines
- Scoring: keyword match fraction (pass threshold ≥ 0.5)
- Model: `grok-3-fast` (XAI)
- Embedding: `BAAI/bge-small-en-v1.5` (384d, local)

### Naive RAG vs Hierarchical RAG

| # | Category | Question | Naive | Hierarchical |
|---|----------|----------|-------|--------------|
| 1 | product_overview | What is the XTCC Solar structured product? | PASS 1.0 | PASS 1.0 |
| 2 | product_terms | What is the maturity or term? | PASS 1.0 | PASS 1.0 |
| 3 | currency | What currency denominations? | PASS 1.0 | PASS 1.0 |
| 4 | protection | What level of principal protection? | PASS 1.0 | PASS 1.0 |
| 5 | issuer | Who is the issuer? | PASS 1.0 | PASS 1.0 |
| 6 | risks | What are the key risks? | **FAIL 0.667** | **PASS 1.0** |
| 7 | identifiers | What is the ISIN? | PASS 1.0 | PASS 1.0 |
| 8 | underlying_asset | What are carbon credits? | PASS 1.0 | PASS 1.0 |

### Aggregate Comparison

| Metric | Naive RAG | Hierarchical RAG | Delta |
|--------|-----------|------------------|-------|
| **Passed** | 7/8 | **8/8** | +1 |
| **Accuracy** | 95.8% | **100.0%** | +4.2% |
| **Mean similarity** | 0.818 | **0.825** | +0.007 |
| **Total chunks** | 934 | 1838 | +904 |
| **Context per retrieval** | 800 chars/chunk | Full section (1000–3000 chars) | ~3x |
| **Product filtering** | None | product_id scoped | ✅ |
| **Doc type filtering** | None | per-agent doc_type list | ✅ |
| **Compliance gate** | None | approved=true enforced | ✅ |
| **Section attribution** | None | section_name in every chunk | ✅ |

### Why Q6 (risks) improved

The naive RAG retrieved FAQ and overview chunks as the top matches for the risk question because they had higher cosine similarity. The actual risk factors in the Listing Particulars (Section 8, ~3000 chars) were split across multiple 800-char chunks — no single chunk scored high enough to surface.

The hierarchical pipeline stores the full Section 8 text as `parent_section`. Even when a child chunk matches at medium similarity, the LLM receives the full risk section as context and can answer correctly.

---

## 5. How Retrieval Works Per Agent

Each POLLY agent calls the RAG with query terms and a filtered doc_type list relevant to its task:

| Agent : Tool | Query passed to RAG | doc_types filtered |
|---|---|---|
| `compliance:review` | content being reviewed | `term_sheet`, `priips`, `mifid_disclosures` |
| `compliance:risk-warnings` | product type + jurisdiction | `priips`, `term_sheet` |
| `content:teaser` | product name + audience | `product_description`, `term_sheet`, `teaser` |
| `content:faq` | product FAQ topics | `faq`, `term_sheet`, `product_description` |
| `content:pitch-deck` | product pitch content | `pitch_deck`, `product_description`, `term_sheet` |
| `campaign:create` | campaign parameters | `mifid_disclosures`, `product_description` |
| `strategy:market-research` | market and competitor context | `market_research`, `product_description` |

The retrieval is a drop-in via `rag.retrieve_as_prompt_block(...)` which returns a formatted string injected directly into the LLM system prompt, replacing the current `ComplianceDocSet.to_prompt_block()` 500-char truncation.

---

## 6. Enhancements Still To Build

### 6.1 doc_type Assignment (High Priority)

All 7 XTCC docs are currently indexed with `doc_type=NULL`. The filter `doc_types=["priips","term_sheet"]` will return zero results until this is populated. Two options:

**Option A — filename-to-doctype map file** (`doc-data/manifest.json`):
```json
{
  "Listing Particulars_Sustainable Capital 2024.04.03 (2).pdf": "prospectus",
  "XTCC 2023-F6 USD 4Yr Solar Term Sheet FINAL.pdf": "term_sheet",
  "XTCC 4Y Principal Protected Detailed Overview and FAQ..docx": "faq",
  "XTCC GBP 4Yr Solar IM 100 PP .pdf": "prospectus",
  "V4_XTCC_Pitchdeck_Updated_03-07-2024.pptx": "pitch_deck",
  "XTCC OVERVIEW.pptx": "product_description",
  "XTCC_1pp_Flier_v7 (1).pdf": "teaser"
}
```
Indexer reads this at startup and sets `doc_type` per file automatically.

**Option B — UPDATE query** (instant fix for existing rows):
```sql
UPDATE polly_rag_hierarchical.documents SET doc_type='prospectus'
  WHERE filename LIKE 'Listing Particulars%';
UPDATE polly_rag_hierarchical.documents SET doc_type='term_sheet'
  WHERE filename LIKE 'XTCC 2023-F6%';
UPDATE polly_rag_hierarchical.documents SET doc_type='faq'
  WHERE filename LIKE 'XTCC 4Y Principal%';
UPDATE polly_rag_hierarchical.documents SET doc_type='prospectus'
  WHERE filename LIKE 'XTCC GBP%';
UPDATE polly_rag_hierarchical.documents SET doc_type='pitch_deck'
  WHERE filename LIKE 'V4_XTCC_Pitchdeck%';
UPDATE polly_rag_hierarchical.documents SET doc_type='product_description'
  WHERE filename LIKE 'XTCC OVERVIEW%';
UPDATE polly_rag_hierarchical.documents SET doc_type='teaser'
  WHERE filename LIKE 'XTCC_1pp_Flier%';

-- Propagate to chunks
UPDATE polly_rag_hierarchical.chunks c
SET doc_type = d.doc_type
FROM polly_rag_hierarchical.documents d
WHERE c.document_id = d.id;
```

### 6.2 Wire RagIntegration Into Agents (High Priority)

`integrations/rag_int.py` is built but not yet called by any agent. Each agent's `execute()` method needs one change:

```python
# Replace this (500-char truncation):
doc_block = context.compliance_docs.to_prompt_block()

# With this (full section retrieval):
rag = context.get_integration("rag")
doc_block = (
    rag.retrieve_as_prompt_block(query=tool_name, product_id=product_db_id, doc_types=[...])
    if rag else context.compliance_docs.to_prompt_block()  # graceful fallback
)
```

### 6.3 Persistent Sessions With product_db_id (Medium Priority)

Currently `SessionContext.product` is in-memory and holds product name as a string, not the integer `polly.products.id`. The RAG filter needs an integer `product_id`. Sessions need to be DB-backed so the `product_id` persists across requests — especially across WhatsApp/Telegram messages.

### 6.4 Document Upload UI + Email Ingestion (Medium Priority)

Currently documents are indexed by running `tasks/create_hierarchical_rag.py` from the terminal. The target flow is:
- Management emails attachments to `compliance@polly.yourfirm.com` → SMTP webhook parses → indexer runs → chunks stored with `approved=false` → Management approves via `compliance:approve` → `approved` flipped to `true` on all chunks
- Or: drag-drop upload in the `/profile` web UI

### 6.5 Re-ranking (Low Priority — After Agent Wiring)

Currently the top-k chunks are returned purely by cosine similarity. A cross-encoder re-ranker (e.g. `ms-marco-MiniLM-L-6-v2` via `sentence-transformers`) would re-score the top 20 retrieved chunks by reading the (query, chunk) pair together, improving precision on complex compliance questions. Only worth adding after the agent wiring is complete and real usage reveals retrieval gaps.

### 6.6 Hybrid Search — BM25 + Vector (Low Priority)

For exact term lookups (ISIN numbers, specific clause references, defined terms like "Autocall Observation Date"), BM25 keyword search outperforms vector similarity. A hybrid retrieval (BM25 score + cosine score combined) would handle both semantic and exact-match queries. `pgvector` combined with `pg_trgm` (already available in PostgreSQL) can implement this without additional infrastructure.

---

## 7. Files Added This Sprint

| File | Purpose |
|------|---------|
| `sql/004_hierarchical_rag_schema.sql` | Creates `polly_rag_hierarchical` schema + tables + indexes |
| `tasks/create_hierarchical_rag.py` | Hierarchical indexer — section-aware chunker, writes to new schema |
| `integrations/rag_int.py` | `RagIntegration` backend — filtered retrieval + prompt block formatter |
| `test-results/hierarchical_rag_evaluation.json` | Raw evaluation results |
| `docs/hierarchical_rag_report.md` | This report |

---

*Evaluated: 2026-04-01 | Model: grok-3-fast | Embedding: BAAI/bge-small-en-v1.5 (384d) | DB: pgvector HNSW*
