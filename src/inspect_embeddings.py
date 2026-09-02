from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main():
    model = SentenceTransformer(MODEL_NAME)

    texts = [
        "geometric knot theory",
        "quantum chromodynamics lattice gauge theory",
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    print(f"Embedding shape: {embeddings.shape}")
    print()
    print("First five numbers of first embedding:")
    print(embeddings[0][:5])

    similarity = embeddings[0] @ embeddings[1]

    print()
    print(f"Cosine similarity: {similarity:.3f}")


if __name__ == "__main__":
    main()
