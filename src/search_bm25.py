import json
import sys
from pathlib import Path

import bm25s


DATA_FILE = Path("data/raw/arxiv_papers.jsonl")
TOP_K = 5


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/search_bm25.py \"your query here\"")
        return

    query = sys.argv[1]
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
    query,
    stopwords=None,
    stemmer=None,
        )

    query_terms = bm25s.tokenize(
    query,
    stopwords=None,
    stemmer=None,
    return_ids=False,
    )[0]
    print("Query term document frequencies:")

    for term in query_terms:
        document_frequency = 0

        for document in documents:
            terms = bm25s.tokenize(
                document,
                stopwords=None,
                stemmer=None,
                return_ids=False,
            )[0]

            if term in set(terms):
                document_frequency += 1

        print(f"   {term}: {document_frequency}/{len(documents)}")
        print()
    results, scores = retriever.retrieve(
        query_tokens,
        k=TOP_K,
    )

    for rank, document_index in enumerate(results[0], start=1):
        paper = papers[document_index]
        score = scores[0, rank - 1]
        document_terms = bm25s.tokenize(
            documents[document_index],
            stopwords=None,
            stemmer=None,
            return_ids=False,
        )[0]
        document_term_set = set(document_terms)
        matched_terms = [
            term for term in query_terms
            if term in document_term_set
        ]    
        print(f"{rank}. {paper['title']}")
        print(f"   arXiv: {paper['arxiv_id']}")
        print(f"   BM25 score: {score:.3f}")
        print(f"   Matched query terms: {', '.join(matched_terms)}")
        print()

if __name__ == "__main__":
    main()
