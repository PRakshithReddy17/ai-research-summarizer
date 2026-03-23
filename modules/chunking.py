"""
Text chunking — splits large documents into overlapping chunks for embedding.

Pure-Python implementation (no langchain dependency) that replicates the
behaviour of RecursiveCharacterTextSplitter.
"""

from __future__ import annotations


_SEPARATORS = ["\n\n", "\n", " ", ""]


def _split_by_separator(text: str, separator: str) -> list[str]:
    """Split *text* on *separator*, keeping non-empty pieces."""
    if separator == "":
        return list(text)
    return [part for part in text.split(separator) if part]


def _recursive_split(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """Recursively split *text* using the hierarchy of separators."""
    if len(text) <= chunk_size:
        return [text]

    sep = separators[0] if separators else ""
    remaining_seps = separators[1:] if len(separators) > 1 else []

    pieces = _split_by_separator(text, sep)

    chunks: list[str] = []
    current = ""

    for piece in pieces:
        # Re-attach the separator when joining (except for char-level split)
        candidate = (current + sep + piece) if current else piece

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            # Flush the accumulated text
            if current:
                chunks.append(current)
            # If this single piece is still too large, recurse with finer seps
            if len(piece) > chunk_size and remaining_seps:
                chunks.extend(_recursive_split(piece, chunk_size, remaining_seps))
            else:
                current = piece
                continue
            current = ""

    if current:
        chunks.append(current)

    return chunks


def split_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """
    Split large text into smaller overlapping chunks.

    Args:
        text:           Full research paper text.
        chunk_size:     Maximum characters per chunk.
        chunk_overlap:  Number of overlapping characters between consecutive chunks.

    Returns:
        List of text chunks.
    """
    if not text or not text.strip():
        return []

    raw_chunks = _recursive_split(text.strip(), chunk_size, _SEPARATORS)

    if chunk_overlap <= 0 or len(raw_chunks) <= 1:
        return raw_chunks

    # Merge with overlap
    merged: list[str] = []
    for i, chunk in enumerate(raw_chunks):
        if i == 0:
            merged.append(chunk)
        else:
            # Grab the tail of the previous chunk as overlap prefix
            prev = raw_chunks[i - 1]
            overlap = prev[-chunk_overlap:] if len(prev) > chunk_overlap else prev
            merged.append(overlap + chunk)

    return merged


if __name__ == "__main__":

    sample_text = """
    Large language models (LLMs) are a class of artificial intelligence models
    designed to understand and generate human language.
    """

    chunks = split_text(sample_text)

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}")
        print(chunk)
