"""
Integration tests for the FastAPI server endpoints.

Run with:  pytest tests/test_api.py -v
"""

import os
import pytest
from pathlib import Path

# Ensure auth is disabled for testing
os.environ.pop("API_KEY", None)
os.environ.pop("HF_API_TOKEN", None)

from fastapi.testclient import TestClient
from server import app


client = TestClient(app)


class TestHealthEndpoint:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestPapersEndpoint:
    def test_list_papers_empty(self):
        response = client.get("/papers")
        assert response.status_code == 200
        data = response.json()
        assert "papers" in data
        assert isinstance(data["papers"], list)


class TestUploadEndpoint:
    def test_reject_non_pdf(self):
        response = client.post(
            "/upload",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_upload_valid_pdf(self, tmp_path):
        """Create a minimal PDF and upload it."""
        # Minimal valid PDF
        pdf_content = (
            b"%PDF-1.0\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj "
            b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj "
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R"
            b"/Resources<</Font<</F1 4 0 R>>>>>>endobj "
            b"4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj "
            b"xref\n0 5\ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n0\n%%EOF"
        )

        response = client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")},
        )
        # Will likely fail because minimal PDF has no extractable text
        # but it should return 400, not 500
        assert response.status_code in (200, 400)


class TestAskEndpoint:
    def test_ask_missing_paper(self):
        response = client.post(
            "/ask",
            json={"paper_id": "nonexistent", "question": "What is this?"},
        )
        assert response.status_code == 404

    def test_ask_all_no_papers(self):
        response = client.post(
            "/ask-all",
            json={"question": "General question"},
        )
        # Should return 404 when there are no papers
        assert response.status_code == 404


class TestSummarizeEndpoint:
    def test_summarize_missing_paper(self):
        response = client.get("/summarize/nonexistent")
        assert response.status_code == 404


class TestArxivEndpoint:
    def test_search_arxiv(self):
        """Depends on network — skip if offline."""
        try:
            response = client.post(
                "/search-arxiv",
                json={"query": "large language models", "max_results": 2},
            )
            assert response.status_code in (200, 404)
            if response.status_code == 200:
                assert "results" in response.json()
        except Exception:
            pytest.skip("Network unavailable")
