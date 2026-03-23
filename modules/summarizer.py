import os

from modules.llm_client import chat


def summarize_text(text: str, model: str | None = None) -> str:
    """
    Generate a concise summary of research paper text using the
    Hugging Face Inference API (via InferenceClient).

    Args:
        text: The extracted paper text (or first few pages).
        model: Optional HF model override.

    Returns:
        A summary string, or an error message on failure.
    """

    # Truncate input to avoid exceeding model token limits.
    max_chars = int(os.getenv("SUMMARIZER_MAX_CHARS", "3000"))
    truncated = text[:max_chars].strip()

    if not truncated:
        return "No text available to summarize."

    prompt = (
        "You are an AI research assistant.\n\n"
        "Summarize the following research paper excerpt clearly and concisely. "
        "Include the main contribution, methodology, key results, and limitations "
        "if present.\n\n"
        f"Paper excerpt:\n{truncated}\n\n"
        "Summary:"
    )

    try:
        return chat(prompt, model=model, max_tokens=300, temperature=0.3)

    except Exception as e:
        return f"Error generating summary: {e}"


if __name__ == "__main__":
    sample = (
        "Large Language Models (LLMs) are AI systems designed to process and "
        "generate natural language. This paper proposes a novel fine-tuning "
        "strategy that improves factual accuracy by 12% on standard benchmarks "
        "while reducing hallucination rates."
    )

    print("Generating summary...\n")
    print(summarize_text(sample))
