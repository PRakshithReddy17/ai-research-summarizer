"""
Persistent storage layer for papers, chunks, metadata, and FAISS indexes.

Data layout inside DATA_FOLDER:
    <paper_id>.pdf          – the original PDF
    <paper_id>.index        – serialised FAISS index
    <paper_id>.json         – JSON with chunks, text_preview, summary, metadata
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss


# ---------------------------------------------------------------------------
# FAISS helpers
# ---------------------------------------------------------------------------

def save_faiss_index(index, path: Path) -> None:
    """Write a FAISS index to disk."""
    faiss.write_index(index, str(path))


def load_faiss_index(path: Path):
    """Read a FAISS index from disk.  Returns None if the file is missing."""
    if not path.exists():
        return None
    return faiss.read_index(str(path))


# ---------------------------------------------------------------------------
# Paper metadata / chunk helpers
# ---------------------------------------------------------------------------

def save_paper_metadata(
    path: Path,
    *,
    paper_id: str,
    file_name: str,
    chunks: List[str],
    text_preview: str,
    summary: Optional[str],
) -> None:
    """Persist paper metadata + chunks to a JSON file."""
    payload = {
        "paper_id": paper_id,
        "file_name": file_name,
        "chunks": chunks,
        "text_preview": text_preview,
        "summary": summary,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_paper_metadata(path: Path) -> Optional[Dict[str, Any]]:
    """Load paper metadata from a JSON file.  Returns None if missing."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))  # utf-8-sig strips BOM
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Bulk loader — called once at server startup
# ---------------------------------------------------------------------------

def load_all_papers(data_folder: Path) -> Dict[str, Dict[str, Any]]:
    """
    Scan the data folder and reload every paper that has both a
    .json metadata file and a .index FAISS file.

    Returns a dict keyed by paper_id, matching the in-memory
    ``papers`` structure used by the FastAPI server.
    """
    papers: Dict[str, Dict[str, Any]] = {}

    for meta_path in sorted(data_folder.glob("*.json")):
        paper_id = meta_path.stem

        index_path = data_folder / f"{paper_id}.index"
        index = load_faiss_index(index_path)
        if index is None:
            continue

        meta = load_paper_metadata(meta_path)
        if meta is None:
            continue

        papers[paper_id] = {
            "file_name": meta.get("file_name", f"{paper_id}.pdf"),
            "chunks": meta.get("chunks", []),
            "index": index,
            "text_preview": meta.get("text_preview", ""),
            "summary": meta.get("summary"),
        }

    return papers
