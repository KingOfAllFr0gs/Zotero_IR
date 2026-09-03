import json
import sys
from pathlib import Path

import bm25s
import numpy as np
from sentence_transformers import SentenceTransformer


CORPUS_FILE = Path(
    "data/benchmark_v2/corpus/arxiv_papers.jsonl"
)

QUERIES_FILE = Path(
    "data/benchmark_v2/eval/queries.jsonl"
)

QRELS_FILE = Path(
    "data/benchmark_v2/eval/qrels.jsonl"
)

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 5


def load_jsonl(path):
    """Load a JSONL file into a list of Python dictionaries."""

    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/compare_rankings.py q012")
        return

    query_id = sys.argv[1]

    papers = load_jsonl(CORPUS_FILE)
    queries = load_jsonl(QUERIES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    # Find the requested evaluation query.
    query = next(
        (
            query
            for query in queries
            if query["query_id"] == query_id
        ),
        None,
    )

    if query is None:
        print(f"Unknown query ID: {query_id}")
        return

    query_text = query["query"]

    # Build relevance lookup for this query.
    judgments = {
        qrel["arxiv_id"]: qrel["relevance"]
        for qrel in qrels
        if qrel["query_id"] == query_id
    }

    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

    # ------------------------------------------------------------
    # BM25
    # ------------------------------------------------------------

    corpus_tokens = bm25s.tokenize(
        documents,
        stopwords=None,
        stemmer=None,
    )

    retriever = bm25s.BM25(method="lucene")
    retriever.index(corpus_tokens)

    query_tokens = bm25s.tokenize(
        query_text,
        stopwords=None,
        stemmer=None,
    )

    bm25_results, bm25_scores = retriever.retrieve(
        query_tokens,
        k=TOP_K,
    )

    # ------------------------------------------------------------
    # Dense retrieval
    # ------------------------------------------------------------

    model = SentenceTransformer(MODEL_NAME)

    document_embeddings = model.encode(
        documents,
        normalize_embeddings=True,
    )

    query_embedding = model.encode(
        query_text,
        normalize_embeddings=True,
    )

    dense_scores = document_embeddings @ query_embedding

    dense_indices = np.argsort(
        dense_scores
    )[::-1][:TOP_K]

    # ------------------------------------------------------------
    # Display
    # ------------------------------------------------------------

    print()
    print(f"{query_id}: {query_text}")
    print()
    print("Information need:")
    print(query["description"])
    print()

    print("=" * 80)
    print("BM25")
    print("=" * 80)

    for rank, document_index in enumerate(
        bm25_results[0],
        start=1,
    ):
        paper = papers[document_index]
        relevance = judgments.get(
            paper["arxiv_id"],
            "unjudged",
        )

        print(
            f"{rank}. {paper['title']} "
            f"[relevance={relevance}]"
        )
        print(
            f"   arXiv: {paper['arxiv_id']}"
        )
        print(
            f"   BM25 score: "
            f"{bm25_scores[0, rank - 1]:.3f}"
        )
        print()

    print("=" * 80)
    print("DENSE")
    print("=" * 80)

    for rank, document_index in enumerate(
        dense_indices,
        start=1,
    ):
        paper = papers[document_index]
        relevance = judgments.get(
            paper["arxiv_id"],
            "unjudged",
        )

        print(
            f"{rank}. {paper['title']} "
            f"[relevance={relevance}]"
        )
        print(
            f"   arXiv: {paper['arxiv_id']}"
        )
        print(
            f"   Similarity: "
            f"{dense_scores[document_index]:.3f}"
        )
        print()


if __name__ == "__main__":
    main()
