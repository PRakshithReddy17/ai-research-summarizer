"""
Unit tests for the core backend modules.

Run with:  pytest tests/ -v
"""

import numpy as np
import pytest

from modules.chunking import split_text
from modules.embeddings import create_embeddings
from modules.retriever import retrieve_relevant_chunks
from modules.vector_store import build_vector_store, search_vector_store


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

class TestChunking:
    def test_basic_split(self):
        text = "Hello world. " * 200  # ~2600 chars
        chunks = split_text(text, chunk_size=500, chunk_overlap=50)
        assert len(chunks) > 1
        for chunk in chunks:
            assert len(chunk) <= 600  # allow some tolerance

    def test_empty_text(self):
        chunks = split_text("")
        assert chunks == []

    def test_short_text_single_chunk(self):
        text = "Short text."
        chunks = split_text(text, chunk_size=1000)
        assert len(chunks) == 1
        assert chunks[0] == text


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------

class TestEmbeddings:
    def test_creates_vectors(self):
        texts = ["Hello world", "AI research"]
        vectors = create_embeddings(texts)
        assert len(vectors) == 2
        assert len(vectors[0]) == 384  # all-MiniLM-L6-v2 dimension

    def test_single_text(self):
        vectors = create_embeddings(["Just one sentence."])
        assert len(vectors) == 1


# ---------------------------------------------------------------------------
# Vector Store
# ---------------------------------------------------------------------------

class TestVectorStore:
    def test_build_and_search(self):
        embeddings = np.random.rand(10, 384).astype("float32")
        index = build_vector_store(embeddings)
        assert index.ntotal == 10

        query = np.random.rand(384).astype("float32")
        results = search_vector_store(index, query, k=3)
        assert len(results) == 3
        assert all(0 <= r < 10 for r in results)

    def test_search_k_exceeds_total(self):
        embeddings = np.random.rand(2, 384).astype("float32")
        index = build_vector_store(embeddings)
        results = search_vector_store(index, np.random.rand(384).astype("float32"), k=5)
        # FAISS pads with -1 when k > total vectors; valid indices should be 0 and 1
        valid = [r for r in results if r >= 0]
        assert len(valid) == 2


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------

class TestRetriever:
    def test_retrieves_relevant_chunks(self):
        chunks = [
            "LLMs are large language models.",
            "Transformers use attention mechanisms.",
            "Python is a programming language.",
        ]
        embeddings = create_embeddings(chunks)
        index = build_vector_store(embeddings)

        results = retrieve_relevant_chunks("What are language models?", chunks, index, k=2)
        assert len(results) == 2
        # The LLM chunk should be among the top results
        assert any("LLM" in r or "language model" in r.lower() for r in results)


# ---------------------------------------------------------------------------
# Storage (save/load round-trip)
# ---------------------------------------------------------------------------

class TestStorage:
    def test_metadata_round_trip(self, tmp_path):
        from modules.storage import save_paper_metadata, load_paper_metadata

        path = tmp_path / "test.json"
        save_paper_metadata(
            path,
            paper_id="abc",
            file_name="test.pdf",
            chunks=["chunk1", "chunk2"],
            text_preview="preview text",
            summary="A summary.",
        )

        loaded = load_paper_metadata(path)
        assert loaded is not None
        assert loaded["paper_id"] == "abc"
        assert loaded["chunks"] == ["chunk1", "chunk2"]
        assert loaded["summary"] == "A summary."

    def test_faiss_round_trip(self, tmp_path):
        from modules.storage import save_faiss_index, load_faiss_index

        embeddings = np.random.rand(5, 384).astype("float32")
        index = build_vector_store(embeddings)

        path = tmp_path / "test.index"
        save_faiss_index(index, path)

        loaded_index = load_faiss_index(path)
        assert loaded_index is not None
        assert loaded_index.ntotal == 5

    def test_load_missing_file(self, tmp_path):
        from modules.storage import load_paper_metadata, load_faiss_index

        assert load_paper_metadata(tmp_path / "nope.json") is None
        assert load_faiss_index(tmp_path / "nope.index") is None
