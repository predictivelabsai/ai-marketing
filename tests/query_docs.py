#!/usr/bin/env python3
"""
POLLY RAG Query & Evaluation — Query the vector DB and evaluate answer accuracy.

Usage:
    python tests/query_docs.py                    # Run all test queries
    python tests/query_docs.py --question "What is XTCC?"  # Single query
"""
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

RESULTS_DIR = ROOT / "test-results"
RESULTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# RAG Query Engine
# ---------------------------------------------------------------------------

class RAGQueryEngine:
    """Query the vector DB and generate answers with XAI/Grok."""

    def __init__(self):
        from utils.db_pool import DatabasePool
        from fastembed import TextEmbedding

        self.pool = DatabasePool.get()
        self._embedder = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

        # XAI for answer generation
        from integrations.xai_int import XaiIntegration
        self.xai = XaiIntegration(model=os.getenv("XAI_MODEL", "grok-3-fast"))

    def embed_query(self, question: str) -> list[float]:
        embeddings = list(self._embedder.embed([question]))
        return embeddings[0].tolist()

    def search(self, question: str, top_k: int = 5) -> list[dict]:
        """Vector similarity search against polly_rag.chunks."""
        from sqlalchemy import text

        embedding = self.embed_query(question)
        emb_str = "[" + ",".join(str(v) for v in embedding) + "]"

        with self.pool.get_session() as session:
            result = session.execute(
                text("""
                    SELECT c.id, c.content, c.metadata, c.chunk_index,
                           d.id AS document_id, d.filename, d.title,
                           1 - (c.embedding <=> cast(:emb AS vector)) AS similarity
                    FROM polly_rag.chunks c
                    JOIN polly_rag.documents d ON d.id = c.document_id
                    ORDER BY c.embedding <=> cast(:emb AS vector)
                    LIMIT :k
                """),
                {"emb": emb_str, "k": top_k},
            )
            rows = result.fetchall()
            keys = result.keys()
            return [dict(zip(keys, row)) for row in rows]

    async def answer(self, question: str, top_k: int = 5) -> dict:
        """Full RAG: search → build context → generate answer."""
        t0 = time.monotonic()

        chunks = self.search(question, top_k)

        # Build context from retrieved chunks
        context_parts = []
        for c in chunks:
            source = c["filename"]
            context_parts.append(f"[Source: {source}, chunk {c['chunk_index']}]\n{c['content']}")
        context_text = "\n\n---\n\n".join(context_parts)

        # Generate answer
        system = (
            "You are a financial product specialist answering questions about XTCC Solar "
            "structured products and Sustainable Capital. Use ONLY the provided context to answer. "
            "If the context doesn't contain the answer, say 'Information not found in documents.' "
            "Be specific and cite document sources when possible."
        )
        user_prompt = f"Context from financial product documents:\n\n{context_text}\n\n---\n\nQuestion: {question}"

        answer_text = await self.xai.generate(system, user_prompt, temperature=0.3, max_tokens=1000)
        elapsed_ms = int((time.monotonic() - t0) * 1000)

        # Log query
        self._log_query(question, answer_text, chunks, elapsed_ms)

        return {
            "question": question,
            "answer": answer_text,
            "sources": [
                {
                    "filename": c["filename"],
                    "chunk_index": c["chunk_index"],
                    "similarity": round(float(c["similarity"]), 4),
                    "snippet": c["content"][:150],
                }
                for c in chunks
            ],
            "latency_ms": elapsed_ms,
        }

    def _log_query(self, question, answer, chunks, latency_ms):
        from sqlalchemy import text
        source_data = [
            {"chunk_id": c["id"], "document_id": c["document_id"],
             "similarity": round(float(c["similarity"]), 4)}
            for c in chunks
        ]
        try:
            with self.pool.get_session() as session:
                session.execute(
                    text("""
                        INSERT INTO polly_rag.query_log (question, answer, source_chunks, model_used, latency_ms)
                        VALUES (:q, :a, :s, :m, :l)
                    """),
                    {
                        "q": question, "a": answer,
                        "s": json.dumps(source_data),
                        "m": self.xai.model, "l": latency_ms,
                    },
                )
        except Exception:
            pass  # Don't fail the query if logging fails


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "question": "What is the XTCC Solar structured product?",
        "expected_keywords": ["solar", "carbon", "structured", "capital"],
        "category": "product_overview",
    },
    {
        "question": "What is the maturity or term of the XTCC Solar product?",
        "expected_keywords": ["4", "year"],
        "category": "product_terms",
    },
    {
        "question": "What currency denominations are the XTCC Solar notes available in?",
        "expected_keywords": ["usd", "gbp"],
        "category": "currency",
    },
    {
        "question": "What level of principal protection does the XTCC product offer?",
        "expected_keywords": ["principal", "protect", "100"],
        "category": "protection",
    },
    {
        "question": "Who is the issuer of the XTCC notes?",
        "expected_keywords": ["sustainable", "capital"],
        "category": "issuer",
    },
    {
        "question": "What are the key risks of investing in the XTCC Solar product?",
        "expected_keywords": ["risk", "credit", "market"],
        "category": "risks",
    },
    {
        "question": "What is the ISIN for the XTCC Solar notes?",
        "expected_keywords": ["ch1213603926"],
        "category": "identifiers",
    },
    {
        "question": "What are carbon credits and how do they relate to XTCC?",
        "expected_keywords": ["carbon", "credit"],
        "category": "underlying_asset",
    },
]


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(result: dict, test_case: dict) -> dict:
    """Score a single query result against expected keywords."""
    answer_lower = result["answer"].lower()
    expected = test_case["expected_keywords"]

    found = [kw for kw in expected if kw.lower() in answer_lower]
    missing = [kw for kw in expected if kw.lower() not in answer_lower]
    score = len(found) / len(expected) if expected else 0

    top_sim = max((s["similarity"] for s in result["sources"]), default=0)

    return {
        "question": test_case["question"],
        "category": test_case["category"],
        "answer": result["answer"],
        "keyword_score": round(score, 3),
        "keywords_found": found,
        "keywords_missing": missing,
        "top_similarity": round(top_sim, 4),
        "top_sources": result["sources"][:3],
        "latency_ms": result["latency_ms"],
        "status": "passed" if score >= 0.5 else "failed",
    }


async def run_evaluation():
    """Run all test cases and produce evaluation report."""
    engine = RAGQueryEngine()

    # Get DB stats
    from sqlalchemy import text as sql_text
    with engine.pool.get_session() as session:
        doc_count = session.execute(sql_text("SELECT COUNT(*) FROM polly_rag.documents")).scalar()
        chunk_count = session.execute(sql_text("SELECT COUNT(*) FROM polly_rag.chunks")).scalar()

    print(f"\nRAG Evaluation: {doc_count} documents, {chunk_count} chunks")
    print(f"Running {len(TEST_CASES)} test queries...\n")

    results = []
    for i, tc in enumerate(TEST_CASES):
        print(f"  [{i + 1}/{len(TEST_CASES)}] {tc['question'][:60]}...")
        result = await engine.answer(tc["question"])
        eval_result = evaluate(result, tc)
        results.append(eval_result)
        status = "PASS" if eval_result["status"] == "passed" else "FAIL"
        print(f"         {status} (score={eval_result['keyword_score']}, sim={eval_result['top_similarity']}, {eval_result['latency_ms']}ms)")

    # Aggregate
    passed = sum(1 for r in results if r["status"] == "passed")
    mean_score = sum(r["keyword_score"] for r in results) / len(results)
    mean_sim = sum(r["top_similarity"] for r in results) / len(results)

    report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "test_group": "rag_evaluation",
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "llm_model": os.getenv("XAI_MODEL", "grok-3-fast"),
        "total_documents": doc_count,
        "total_chunks": chunk_count,
        "total_questions": len(TEST_CASES),
        "passed": passed,
        "failed": len(TEST_CASES) - passed,
        "overall_accuracy": round(mean_score, 3),
        "mean_retrieval_similarity": round(mean_sim, 4),
        "tests": results,
    }

    # Write results
    output_path = RESULTS_DIR / "rag_evaluation.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n=== Results: {passed}/{len(TEST_CASES)} passed, accuracy={mean_score:.1%}, mean_sim={mean_sim:.3f} ===")
    print(f"Written to {output_path}")
    return report


async def single_query(question: str):
    """Run a single query and print the result."""
    engine = RAGQueryEngine()
    result = await engine.answer(question)
    print(f"\nQuestion: {question}")
    print(f"\nAnswer: {result['answer']}")
    print(f"\nSources ({len(result['sources'])}):")
    for s in result["sources"]:
        print(f"  - {s['filename']} (chunk {s['chunk_index']}, sim={s['similarity']})")
    print(f"\nLatency: {result['latency_ms']}ms")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query POLLY RAG and evaluate accuracy")
    parser.add_argument("--question", "-q", help="Single question to ask")
    args = parser.parse_args()

    if args.question:
        asyncio.run(single_query(args.question))
    else:
        asyncio.run(run_evaluation())


if __name__ == "__main__":
    main()
