from typing import List

from modules.embeddings import create_embeddings
from modules.vector_store import search_vector_store


def retrieve_relevant_chunks(
    question: str,
    chunks: List[str],
    index,
    k: int = 5,
) -> List[str]:
    """
    Retrieve the most relevant text chunks for a given question.

    Steps:
        1. Convert the question into an embedding.
        2. Search the FAISS index for the nearest neighbours.
        3. Return the matching text chunks.

    Args:
        question: The user's question.
        chunks: All text chunks for the paper.
        index: The FAISS index built from the chunk embeddings.
        k: Number of top results to return.

    Returns:
        A list of the most relevant text chunks.
    """

    question_embedding = create_embeddings([question])[0]

    indices = search_vector_store(index, question_embedding, k=k)

    relevant = [chunks[i] for i in indices if i < len(chunks)]

    return relevant


if __name__ == "__main__":
    from modules.vector_store import build_vector_store

    sample_chunks = [
        "Large Language Models (LLMs) are AI systems designed to process and generate natural language.",
        "Transformers are neural network architectures that use attention mechanisms.",
        "Fine-tuning adapts a pre-trained model to a specific downstream task.",
        "RLHF stands for Reinforcement Learning from Human Feedback.",
    ]

    embeddings = create_embeddings(sample_chunks)
    idx = build_vector_store(embeddings)

    results = retrieve_relevant_chunks("What are large language models?", sample_chunks, idx, k=2)

    print("Retrieved chunks:")
    for i, chunk in enumerate(results, 1):
        print(f"  {i}. {chunk}")
