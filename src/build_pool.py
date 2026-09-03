import json
from pathlib import Path
import bm25s

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

CORPUS_FILE = Path(
    "data/benchmark_v2/corpus/arxiv_papers.jsonl"
)

QUERIES_FILE = Path(
    "data/benchmark_v2/eval/queries.jsonl"
)

QRELS_FILE = Path(
    "data/benchmark_v2/eval/qrels.jsonl"
)

CANDIDATES_FILE = Path(
    "data/benchmark_v2/eval/pool_candidates.jsonl"
)

POOL_DEPTH = 5

def load_jsonl(path):
    """Load a JSONL file into a list of Python dictionaries."""

    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    return records


def main():
    # Load the three pieces of the benchmark.
    papers = load_jsonl(CORPUS_FILE)
    queries = load_jsonl(QUERIES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    print(f"Papers: {len(papers)}")
    print(f"Queries: {len(queries)}")
    print(f"Existing judgments: {len(qrels)}")
    print()

    # Use title + abstract, matching the retrieval baselines.
    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

    # Build the BM25 index once for the complete corpus.
    corpus_tokens = bm25s.tokenize(
        documents,
        stopwords=None,
        stemmer=None,
    )

    retriever = bm25s.BM25(method="lucene")
    retriever.index(corpus_tokens)

    # Store judged query-document pairs so we can distinguish genuinely
    # new candidates from papers that were already assessed in the pilot.
    existing_pairs = {
        (qrel["query_id"], qrel["arxiv_id"])
        for qrel in qrels
    }

    bm25_pairs = set()

    for query in queries:
        query_id = query["query_id"]
        query_text = query["query"]

        query_tokens = bm25s.tokenize(
            query_text,
            stopwords=None,
            stemmer=None,
        )

        results, _ = retriever.retrieve(
            query_tokens,
            k=POOL_DEPTH,
        )

        query_pairs = {
            (
                query_id,
                papers[document_index]["arxiv_id"],
            )
            for document_index in results[0]
        }

        bm25_pairs.update(query_pairs)

        new_for_query = query_pairs - existing_pairs

        print(
            f"{query_id}: "
            f"{len(new_for_query)} new BM25 judgments"
        )

    new_bm25_pairs = bm25_pairs - existing_pairs

    print(f"BM25 top-{POOL_DEPTH} query-document pairs: {len(bm25_pairs)}")
    print(f"New BM25 judgments required: {len(new_bm25_pairs)}")

    # Build dense document embeddings once for the complete corpus.
    model = SentenceTransformer(MODEL_NAME)

    document_embeddings = model.encode(
        documents,
        normalize_embeddings=True,
    )

    dense_pairs = set()

    for query in queries:
        query_id = query["query_id"]
        query_text = query["query"]

        query_embedding = model.encode(
            query_text,
            normalize_embeddings=True,
        )

        scores = document_embeddings @ query_embedding

        ranked_indices = np.argsort(scores)[::-1][:POOL_DEPTH]

        query_pairs = {
            (
                query_id,
                papers[document_index]["arxiv_id"],
            )
            for document_index in ranked_indices
        }

        dense_pairs.update(query_pairs)

        new_for_query = query_pairs - existing_pairs

        print(
            f"{query_id}: "
            f"{len(new_for_query)} new dense judgments"
        )
    new_dense_pairs = dense_pairs - existing_pairs

    combined_pairs = bm25_pairs | dense_pairs
    new_combined_pairs = combined_pairs - existing_pairs

    paper_by_id = {
        paper["arxiv_id"]: paper
        for paper in papers
    }

    query_by_id = {
        query["query_id"]: query
        for query in queries
    }

    candidate_records = []

    for query_id, arxiv_id in sorted(new_combined_pairs):
        query = query_by_id[query_id]
        paper = paper_by_id[arxiv_id]

        candidate_records.append(
            {
                "query_id": query_id,
                "query": query["query"],
                "description": query["description"],
                "arxiv_id": arxiv_id,
                "title": paper["title"],
                "abstract": paper["abstract"],
                "relevance": None,
            }
        )
    with CANDIDATES_FILE.open("w", encoding="utf-8") as file:
        for candidate in candidate_records:
            file.write(
                json.dumps(candidate, ensure_ascii=False) + "\n"
            )

    print()
    print(
        f"Saved {len(candidate_records)} candidates "
        f"to {CANDIDATES_FILE}"
    )

    print()
    print(
        f"Dense top-{POOL_DEPTH} query-document pairs: "
        f"{len(dense_pairs)}"
    )
    print(
        f"New dense judgments required: "
        f"{len(new_dense_pairs)}"
    )

    print()
    print(
        f"Combined BM25+dense pool pairs: "
        f"{len(combined_pairs)}"
    )
    print(
        f"New judgments required after deduplication: "
        f"{len(new_combined_pairs)}"
    )
    print()
    

if __name__ == "__main__":
    main()

