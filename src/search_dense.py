import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


DATA_FILE = Path("data/raw/arxiv_papers.jsonl")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 5


def main():
    if len(sys.argv) != 2:
        print('Usage: python src/search_dense.py "your query here"')
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

    model = SentenceTransformer(MODEL_NAME)

    document_embeddings = model.encode(
        documents,
        normalize_embeddings=True,
    )

    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    scores = document_embeddings @ query_embedding

    ranked_indices = np.argsort(scores)[::-1][:TOP_K]

    for rank, document_index in enumerate(ranked_indices, start=1):
        paper = papers[document_index]

        print(f"{rank}. {paper['title']}")
        print(f"   arXiv: {paper['arxiv_id']}")
        print(f"   Similarity: {scores[document_index]:.3f}")
        print()


if __name__ == "__main__":
    main()
