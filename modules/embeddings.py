from sentence_transformers import SentenceTransformer


# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """
    Convert text chunks into vector embeddings.
    """

    embeddings = model.encode(chunks)

    return embeddings


if __name__ == "__main__":

    sample_chunks = [
        "Large Language Models are powerful AI systems.",
        "Transformers changed natural language processing."
    ]

    vectors = create_embeddings(sample_chunks)

    print("Number of vectors:", len(vectors))
    print("Vector dimension:", len(vectors[0]))