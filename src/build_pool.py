import json
from pathlib import Path

import bm25s
import numpy as np
from sentence_transformers import SentenceTransformer


# Dense retrieval model used in benchmark v2.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Benchmark-v2 data files.
CORPUS_FILE = Path(
    "data/benchmark_v2/corpus/arxiv_papers.jsonl"
)

QUERIES_FILE = Path(
    "data/benchmark_v2/eval/queries.jsonl"
)

QRELS_FILE = Path(
    "data/benchmark_v2/eval/qrels.jsonl"
)

# System-blind annotation file containing only previously unjudged
# query-document pairs discovered by the retrieval pool.
CANDIDATES_FILE = Path(
    "data/benchmark_v2/eval/pool_candidates.jsonl"
)

# Pool to the same depth as the current evaluation cutoff.
#
# This first v2 pool guarantees judgments for BM25 and dense top-5 results.
# A deeper pool can be constructed later for stronger pooled-recall estimates.
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
    # Load the corpus, evaluation queries, and existing relevance judgments.
    papers = load_jsonl(CORPUS_FILE)
    queries = load_jsonl(QUERIES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    print(f"Papers: {len(papers)}")
    print(f"Queries: {len(queries)}")
    print(f"Existing judgments: {len(qrels)}")
    print()

    # Use exactly the same title + abstract representation as the standalone
    # BM25 and dense retrieval baselines.
    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

    # Record every query-document pair that already has a human judgment.
    #
    # Relevance is query-specific, so the same paper may legitimately need
    # separate judgments for different queries.
    existing_pairs = {
        (qrel["query_id"], qrel["arxiv_id"])
        for qrel in qrels
    }

    # ------------------------------------------------------------------
    # BM25 pool
    # ------------------------------------------------------------------

    # Build the BM25 index once for the complete corpus.
    corpus_tokens = bm25s.tokenize(
        documents,
        stopwords=None,
        stemmer=None,
    )

    retriever = bm25s.BM25(method="lucene")
    retriever.index(corpus_tokens)

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

        # Store query-document pairs rather than document IDs alone because
        # relevance depends on the information need.
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

    print()
    print(
        f"BM25 top-{POOL_DEPTH} query-document pairs: "
        f"{len(bm25_pairs)}"
    )
    print(
        f"New BM25 judgments required: "
        f"{len(new_bm25_pairs)}"
    )
    print()

    # ------------------------------------------------------------------
    # Dense retrieval pool
    # ------------------------------------------------------------------

    # Encode the corpus once rather than recomputing document embeddings
    # separately for every query.
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

        # With normalized embeddings, dot product equals cosine similarity.
        scores = document_embeddings @ query_embedding

        # Keep the document indices with the highest similarity scores.
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

    print()
    print(
        f"Dense top-{POOL_DEPTH} query-document pairs: "
        f"{len(dense_pairs)}"
    )
    print(
        f"New dense judgments required: "
        f"{len(new_dense_pairs)}"
    )

    # ------------------------------------------------------------------
    # Combined relevance pool
    # ------------------------------------------------------------------

    # Pool the union of BM25 and dense results.
    #
    # Using more than one retrieval system reduces the risk of defining
    # relevance only from documents surfaced by a single ranking method.
    combined_pairs = bm25_pairs | dense_pairs

    # Only genuinely unjudged query-document pairs require annotation.
    new_combined_pairs = combined_pairs - existing_pairs

    print()
    print(
        f"Combined BM25+dense pool pairs: "
        f"{len(combined_pairs)}"
    )
    print(
        f"New judgments required after deduplication: "
        f"{len(new_combined_pairs)}"
    )

    # Fast lookup tables for constructing annotation records.
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

        # Deliberately omit retrieval system, score, and rank.
        #
        # This makes the annotation file system-blind so that relevance
        # judgments are based on the information need and paper content
        # rather than knowledge of which system retrieved the candidate.
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

    # Do not overwrite an existing annotation file.
    #
    # The current candidate file may contain completed human judgments and
    # therefore represents research data rather than disposable output.
    if CANDIDATES_FILE.exists():
        print()
        print(
            f"Candidate file already exists: {CANDIDATES_FILE}"
        )
        print("Existing annotation data was left unchanged.")
        return

    # Write one system-blind annotation candidate per JSONL line.
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


if __name__ == "__main__":
    main()