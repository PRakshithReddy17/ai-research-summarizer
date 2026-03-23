import faiss
import numpy as np


def build_vector_store(embeddings):
    """
    Create a FAISS index from embeddings.
    """

    embeddings = np.array(embeddings).astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index


def search_vector_store(index, query_embedding, k=5):
    """
    Search for most similar vectors.
    """

    query_embedding = np.array([query_embedding]).astype("float32")

    distances, indices = index.search(query_embedding, k)

    return indices[0]


if __name__ == "__main__":

    sample_vectors = np.random.rand(10, 384).astype("float32")

    index = build_vector_store(sample_vectors)

    query = np.random.rand(384).astype("float32")

    results = search_vector_store(index, query)

    print("Nearest indices:", results)