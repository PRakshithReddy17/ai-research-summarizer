"""
Embedding module — converts text chunks into vector embeddings.

Uses the Hugging Face Inference API (remote) so we don't need to load
PyTorch or sentence-transformers locally. This keeps memory usage under
512 MB for free-tier hosting.
"""

import os
import numpy as np
from huggingface_hub import InferenceClient


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    """Return (or create) the shared InferenceClient singleton."""
    global _client
    if _client is None:
        token = os.getenv("HF_API_TOKEN")
        _client = InferenceClient(token=token) if token else InferenceClient()
    return _client


def create_embeddings(chunks: list[str]) -> np.ndarray:
    """
    Convert text chunks into vector embeddings using the HF Inference API.

    Args:
        chunks: List of text strings to embed.

    Returns:
        numpy array of shape (len(chunks), embedding_dim) with float32 dtype.
    """
    client = _get_client()

    result = client.feature_extraction(
        text=chunks,
        model=EMBEDDING_MODEL,
    )

    # The API returns nested lists — convert to numpy float32 for FAISS
    embeddings = np.array(result, dtype="float32")

    # If a single string was passed, the API may return shape (1, seq_len, dim)
    # or (seq_len, dim). We need (n_chunks, dim).
    if embeddings.ndim == 3:
        # Mean pooling over the token dimension (axis=1)
        embeddings = embeddings.mean(axis=1)

    return embeddings


if __name__ == "__main__":

    sample_chunks = [
        "Large Language Models are powerful AI systems.",
        "Transformers changed natural language processing."
    ]

    vectors = create_embeddings(sample_chunks)

    print("Number of vectors:", len(vectors))
    print("Vector dimension:", len(vectors[0]))
    print("Dtype:", vectors.dtype)
