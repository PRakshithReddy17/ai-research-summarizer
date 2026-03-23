"""
Shared Hugging Face LLM client using the official huggingface_hub library.

This provides a single, reliable way to call HF models from anywhere
in the codebase — no more raw HTTP calls or URL migration issues.
"""

import os
from huggingface_hub import InferenceClient


# Default model — can be overridden via HF_MODEL_NAME env var
DEFAULT_MODEL = "Qwen/Qwen2.5-Coder-32B-Instruct"

# Singleton client (created lazily on first call)
_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    """Return (or create) the shared InferenceClient singleton."""
    global _client
    if _client is None:
        token = os.getenv("HF_API_TOKEN")
        if not token:
            raise RuntimeError("HF_API_TOKEN is not configured.")
        _client = InferenceClient(token=token)
    return _client


def chat(prompt: str, model: str | None = None, max_tokens: int = 300, temperature: float = 0.3) -> str:
    """
    Send a prompt to the HF model and return the generated text.

    Uses the chat_completion endpoint (OpenAI-compatible) which works
    reliably with the current HF Inference API.
    """
    model = model or os.getenv("HF_MODEL_NAME", DEFAULT_MODEL)
    client = _get_client()

    response = client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    return response.choices[0].message.content.strip()
