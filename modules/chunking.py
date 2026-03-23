from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_text(text: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Split large text into smaller overlapping chunks.

    Args:
        text (str): Full research paper text
        chunk_size (int): Size of each chunk
        chunk_overlap (int): Overlap between chunks

    Returns:
        list: List of text chunks
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_text(text)

    return chunks


if __name__ == "__main__":

    sample_text = """
    Large language models (LLMs) are a class of artificial intelligence models
    designed to understand and generate human language.
    """

    chunks = split_text(sample_text)

    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1}")
        print(chunk)