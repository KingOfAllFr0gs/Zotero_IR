import json
from pathlib import Path

import bm25s


CORPUS_FILE = Path("data/raw/arxiv_papers.jsonl")
QUERIES_FILE = Path("data/eval/queries.jsonl")
QRELS_FILE = Path("data/eval/qrels.jsonl")

QUERY_ID = "q001"
K = 5


def load_jsonl(path):
    records = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            records.append(json.loads(line))

    return records


def main():
    papers = load_jsonl(CORPUS_FILE)
    queries = load_jsonl(QUERIES_FILE)
    qrels = load_jsonl(QRELS_FILE)

    query_record = next(
        query for query in queries
        if query["query_id"] == QUERY_ID
    )

    query_text = query_record["query"]

    relevant_ids = {
        qrel["arxiv_id"]
        for qrel in qrels
        if qrel["query_id"] == QUERY_ID
        and qrel["relevance"] == 1
    }

    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

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

    results, scores = retriever.retrieve(
        query_tokens,
        k=K,
    )

    retrieved_ids = [
        papers[document_index]["arxiv_id"]
        for document_index in results[0]
    ]

    relevant_retrieved = sum(
        arxiv_id in relevant_ids
        for arxiv_id in retrieved_ids
    )

    precision_at_k = relevant_retrieved / K

    print(f"Query: {query_text}")
    print(f"Relevant retrieved: {relevant_retrieved}/{K}")
    print(f"Precision@{K}: {precision_at_k:.3f}")


if __name__ == "__main__":
    main()

