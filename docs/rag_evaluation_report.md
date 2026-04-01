# POLLY RAG Evaluation Report

## Overview

| Metric | Value |
|--------|-------|
| **Documents processed** | 7 (4 PDF, 2 PPTX, 1 DOCX) |
| **Total chunks** | 934 |
| **Embedding model** | BAAI/bge-small-en-v1.5 (384d, local) |
| **LLM model** | grok-3-fast (XAI) |
| **Vector index** | pgvector HNSW (cosine similarity) |
| **Test questions** | 8/8 passed |
| **Overall accuracy** | **95.8%** |
| **Mean retrieval similarity** | 0.818 |

## Source Documents

| Document | Type | Size | Chunks |
|----------|------|------|--------|
| Listing Particulars - Sustainable Capital | PDF | 1.2 MB | 616 |
| XTCC GBP 4Yr Solar Investment Memorandum | PDF | 1.1 MB | 156 |
| XTCC USD 4Yr Solar Term Sheet | PDF | 213 KB | 76 |
| XTCC Pitchdeck (Updated 2024) | PPTX | 21 MB | 40 |
| XTCC 4Y Principal Protected Overview & FAQ | DOCX | 276 KB | 26 |
| XTCC Overview | PPTX | 4.5 MB | 12 |
| XTCC 1-Page Flier | PDF | 351 KB | 8 |

## Evaluation Results

### Q1: What is the XTCC Solar structured product?
- **Score**: 1.0 | **Similarity**: 0.810 | **Latency**: 2.2s
- **Answer**: The XTCC Solar structured product is a USD-denominated, 4-year, 100% principal-protected carbon credit investment product issued by Sustainable Capital PLC as Series 2023-F6 Notes due 2027. It provides indirect exposure to High-Integrity Carbon Credits (HICC) sourced exclusively from verified and audited solar energy projects.
- **Sources**: Term Sheet (chunk 0), XTCC Overview (chunk 3, 11)

### Q2: What is the maturity or term of the XTCC Solar product?
- **Score**: 1.0 | **Similarity**: 0.837 | **Latency**: 1.5s
- **Answer**: The maturity or term of the XTCC Solar product is 4 years.
- **Sources**: Term Sheet (chunk 0), GBP Investment Memo (chunk 0), FAQ (chunk 8)

### Q3: What currency denominations are the XTCC Solar notes available in?
- **Score**: 1.0 | **Similarity**: 0.842 | **Latency**: 2.0s
- **Answer**: The XTCC Solar notes are available in USD and GBP denominations.
- **Sources**: Term Sheet (chunk 9), GBP Investment Memo (chunk 0)

### Q4: What level of principal protection does the XTCC product offer?
- **Score**: 1.0 | **Similarity**: 0.803 | **Latency**: 1.6s
- **Answer**: The XTCC 4-Year Principal Protected Investment offers 100% principal protection at maturity. This means that at the end of the four-year term, investors are guaranteed to receive their initial investment amount back, regardless of the performance of the underlying assets.
- **Sources**: FAQ (chunk 8, 0, 22)

### Q5: Who is the issuer of the XTCC notes?
- **Score**: 1.0 | **Similarity**: 0.789 | **Latency**: 1.9s
- **Answer**: The issuer of the XTCC Notes is Sustainable Capital PLC, a company incorporated with limited liability in England and Wales with registered number 12423459.
- **Sources**: GBP Investment Memo (chunk 70, 67, 40)

### Q6: What are the key risks of investing in the XTCC Solar product?
- **Score**: 0.667 | **Similarity**: 0.784 | **Latency**: 1.7s
- **Answer**: The provided context does not specifically outline the key risks. While the documents discuss features, benefits, and structure including principal protection and exposure to high-integrity carbon credits, detailed risk factors were not found in the retrieved chunks.
- **Note**: Partial pass — "market" keyword not found. Risk factors are in the Listing Particulars but retrieval favoured FAQ/overview chunks.

### Q7: What is the ISIN for the XTCC Solar notes?
- **Score**: 1.0 | **Similarity**: 0.813 | **Latency**: 0.9s
- **Answer**: The ISIN for the XTCC Solar Notes is CH1213603926.
- **Sources**: GBP Investment Memo (chunk 0), Term Sheet (chunk 9)

### Q8: What are carbon credits and how do they relate to XTCC?
- **Score**: 1.0 | **Similarity**: 0.864 | **Latency**: 5.9s
- **Answer**: Carbon credits are units of measurement representing the removal or reduction of greenhouse gas emissions. XTCC is the world's first investment product ecosystem specifically focused on high-integrity carbon credits, creating stock market-quoted instruments that establish fair market value.
- **Sources**: FAQ (chunk 24, 25, 12)

## Scoring Methodology

- **Keyword score**: Fraction of expected keywords found in the answer (case-insensitive)
- **Pass threshold**: Score >= 0.5
- **Similarity**: Cosine similarity between question embedding and best matching chunk
- **Sources**: Top-3 chunks retrieved by vector similarity search (top-5 used for context)

## Pipeline Architecture

```
doc-data/ (PDF/PPTX/DOCX)
    → pymupdf4llm / python-pptx / python-docx (text extraction)
    → RecursiveCharacterTextSplitter (800 chars, 150 overlap)
    → fastembed BAAI/bge-small-en-v1.5 (384d embeddings)
    → polly_rag.chunks (pgvector HNSW index)

User Question
    → fastembed (embed query)
    → pgvector cosine similarity search (top-5 chunks)
    → XAI/Grok (generate answer from context)
    → Answer with source citations
```

## Commands

```bash
# Process documents
python tasks/create_rag.py

# Run evaluation
python tests/query_docs.py

# Single query
python tests/query_docs.py -q "What is the minimum investment?"
```

---
*Report generated from test-results/rag_evaluation.json*
