from sentence_transformers import SentenceTransformer


# Pretrained embedding model used by the dense retrieval baseline.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    # Load the sentence-embedding model.
    model = SentenceTransformer(MODEL_NAME)

    # Two deliberately different mathematical topics used to inspect
    # the behavior of the embedding space.
    texts = [
        "geometric knot theory",
        "quantum chromodynamics lattice gauge theory",
    ]

    # Convert both texts into normalized dense vectors.
    # Normalization gives each vector length 1, which means that their
    # dot product is equal to cosine similarity.
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    # Inspect the dimensions and a small part of the numerical embedding.
    print(f"Embedding shape: {embeddings.shape}")
    print()
    print("First five numbers of first embedding:")
    print(embeddings[0][:5])

    # Measure semantic similarity between the two normalized embeddings.
    similarity = embeddings[0] @ embeddings[1]

    print()
    print(f"Cosine similarity: {similarity:.3f}")


if __name__ == "__main__":
    main()