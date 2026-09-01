import json
from pathlib import Path

import bm25s


DATA_FILE = Path("data/raw/arxiv_papers.jsonl")
QUERY = "geometric knot theory"
TOP_K = 5


def main():
    papers = []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            papers.append(json.loads(line))

    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

    corpus_tokens = bm25s.tokenize(
        documents,
        stopwords=None,
        stemmer=None,
    )

    retriever = bm25s.BM25()
    retriever.index(corpus_tokens)

    query_tokens = bm25s.tokenize(
        QUERY,
        stopwords=None,
        stemmer=None,
    )

    results, scores = retriever.retrieve(
        query_tokens,
        k=TOP_K,
    )

    for rank, document_index in enumerate(results[0], start=1):
        paper = papers[document_index]
        score = scores[0, rank - 1]

        print(f"{rank}. {paper['title']}")
        print(f"   arXiv: {paper['arxiv_id']}")
        print(f"   BM25 score: {score:.3f}")
        print()


if __name__ == "__main__":
    main()
