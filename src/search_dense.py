# import json
# import sys
# from pathlib import Path

# import numpy as np
# from sentence_transformers import SentenceTransformer


# DATA_FILE = Path("data/raw/arxiv_papers.jsonl")
# MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
# TOP_K = 5


# def main():
#     if len(sys.argv) != 2:
#         print('Usage: python src/search_dense.py "your query here"')
#         return

#     query = sys.argv[1]

#     papers = []

#     with DATA_FILE.open("r", encoding="utf-8") as file:
#         for line in file:
#             papers.append(json.loads(line))

#     documents = [
#         paper["title"] + " " + paper["abstract"]
#         for paper in papers
#     ]

#     model = SentenceTransformer(MODEL_NAME)

#     document_embeddings = model.encode(
#         documents,
#         normalize_embeddings=True,
#     )

#     query_embedding = model.encode(
#         query,
#         normalize_embeddings=True,
#     )

#     scores = document_embeddings @ query_embedding

#     ranked_indices = np.argsort(scores)[::-1][:TOP_K]

#     for rank, document_index in enumerate(ranked_indices, start=1):
#         paper = papers[document_index]

#         print(f"{rank}. {paper['title']}")
#         print(f"   arXiv: {paper['arxiv_id']}")
#         print(f"   Similarity: {scores[document_index]:.3f}")
#         print()


# if __name__ == "__main__":
#     main()

import json
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


# Location of the corpus used for retrieval.
DATA_FILE = Path("data/raw/arxiv_papers.jsonl")

# Generic pretrained sentence-embedding model used as the dense baseline.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Number of search results to return.
TOP_K = 5


def main():
    # Expect exactly one command-line argument containing the search query.
    #
    # Example:
    # python src/search_dense.py "geometric knot theory"
    if len(sys.argv) != 2:
        print('Usage: python src/search_dense.py "your query here"')
        return

    query = sys.argv[1]
    papers = []

    # Load the JSONL corpus.
    # Blank lines are ignored so accidental whitespace does not break loading.
    with DATA_FILE.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                papers.append(json.loads(line))

    # Use title + abstract as the searchable document representation.
    # BM25 uses the same representation, making the two baselines comparable.
    documents = [
        paper["title"] + " " + paper["abstract"]
        for paper in papers
    ]

    # Load the pretrained sentence-embedding model.
    model = SentenceTransformer(MODEL_NAME)

    # Encode all documents as normalized dense vectors.
    #
    # Because these vectors have unit length, their dot product is equivalent
    # to cosine similarity.
    document_embeddings = model.encode(
        documents,
        normalize_embeddings=True,
    )

    # Encode the query in the same vector space as the documents.
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    )

    # Compute the similarity between the query and every document.
    scores = document_embeddings @ query_embedding

    # Sort document indices by decreasing similarity and keep the top results.
    ranked_indices = np.argsort(scores)[::-1][:TOP_K]

    # Display the ranked papers and their cosine-similarity scores.
    for rank, document_index in enumerate(ranked_indices, start=1):
        paper = papers[document_index]

        print(f"{rank}. {paper['title']}")
        print(f"   arXiv: {paper['arxiv_id']}")
        print(f"   Similarity: {scores[document_index]:.3f}")
        print()


if __name__ == "__main__":
    main()