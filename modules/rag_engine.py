import os

from modules.retriever import retrieve_relevant_chunks
from modules.llm_client import chat


def answer_question(question, chunks, index, model=None):
    """
    Answer a question using RAG (Retrieval Augmented Generation).

    Steps:
    1. Retrieve the most relevant text chunks (via retriever module)
    2. Build a prompt with the retrieved context
    3. Send the context + question to a Hugging Face model via InferenceClient
    """

    try:
        # Step 1 — Retrieve relevant chunks
        relevant_chunks = retrieve_relevant_chunks(question, chunks, index)

        context = "\n\n".join(relevant_chunks)

        # Step 2 — Create prompt
        prompt = (
            "You are an AI research assistant.\n\n"
            "Use the research paper context below to answer the user's question.\n\n"
            f"Context:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Instructions:\n"
            "- Answer clearly and concisely\n"
            "- Base your answer only on the provided context"
        )

        # Step 3 — Call the LLM
        return chat(prompt, model=model, max_tokens=300, temperature=0.2)

    except Exception as e:
        return f"Error generating answer: {e}"


# Optional test block
if __name__ == "__main__":

    print("RAG engine test")

    dummy_chunks = [
        "Large Language Models (LLMs) are AI systems designed to process and generate natural language.",
        "Transformers are neural network architectures that use attention mechanisms."
    ]

    # simple test index
    from modules.embeddings import create_embeddings
    from modules.vector_store import build_vector_store

    embeddings = create_embeddings(dummy_chunks)
    index = build_vector_store(embeddings)

    question = "What are large language models?"

    answer = answer_question(question, dummy_chunks, index)

    print("\nAnswer:\n")
    print(answer)
