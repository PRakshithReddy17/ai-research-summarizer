import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()  # Load .env before anything reads os.getenv()

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.pdf_parser import extract_text_from_pdf, extract_first_pages
from modules.chunking import split_text
from modules.embeddings import create_embeddings
from modules.vector_store import build_vector_store
from modules.rag_engine import answer_question
from modules.retriever import retrieve_relevant_chunks
from modules.summarizer import summarize_text
from modules.storage import save_faiss_index, save_paper_metadata, load_all_papers
from modules.arxiv_fetcher import fetch_papers as arxiv_fetch_papers, download_pdf as arxiv_download_pdf
from modules.auth import init_auth, verify_api_key
from modules.rate_limiter import init_rate_limiter, check_rate_limit

from modules.llm_client import chat as llm_chat


app = FastAPI(title="AI Research Summarizer API")


def get_allowed_origins():
    origins = os.getenv("CORS_ORIGINS", "*")
    return [origin.strip() for origin in origins.split(",") if origin.strip()]

# allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FOLDER = BASE_DIR / "data"
DATA_FOLDER.mkdir(exist_ok=True)

papers: dict = {}


class AskRequest(BaseModel):
    paper_id: str
    question: str


class ArxivSearchRequest(BaseModel):
    query: str
    max_results: int = 5


class ArxivImportRequest(BaseModel):
    pdf_url: str
    title: str


class AskAllRequest(BaseModel):
    question: str


@app.middleware("http")
async def api_key_middleware(request, call_next):
    """Enforce API-key authentication and rate limiting on every request."""
    await verify_api_key(request)
    await check_rate_limit(request)
    return await call_next(request)


@app.on_event("startup")
async def startup_load_papers():
    """Validate environment and reload all previously uploaded papers from disk."""

    # --- Auth & rate limiting ---
    init_auth()
    init_rate_limiter()

    # --- Environment validation ---
    hf_token = os.getenv("HF_API_TOKEN")
    hf_model = os.getenv("HF_MODEL_NAME", "google/flan-t5-large")

    if not hf_token:
        print("[WARNING] HF_API_TOKEN is not set. The /ask and /summarize endpoints will not work.")
    else:
        print(f"[STARTUP] HF_API_TOKEN is configured. Model: {hf_model}")

    cors_origins = get_allowed_origins()
    print(f"[STARTUP] CORS origins: {cors_origins}")

    # --- Restore papers ---
    restored = load_all_papers(DATA_FOLDER)
    papers.update(restored)
    print(f"[STARTUP] Restored {len(restored)} paper(s) from disk.")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/papers")
async def list_papers():
    """Return lightweight metadata for every uploaded paper."""
    items = []
    for paper_id, data in papers.items():
        items.append({
            "paper_id": paper_id,
            "file_name": data.get("file_name", f"{paper_id}.pdf"),
            "has_summary": data.get("summary") is not None,
        })
    return {"papers": items}


@app.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    paper_id = str(uuid.uuid4())

    filepath = DATA_FOLDER / f"{paper_id}.pdf"

    with open(filepath, "wb") as f:
        f.write(await file.read())

    # extract text
    text = extract_text_from_pdf(str(filepath))

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the PDF.")

    # chunk
    chunks = split_text(text)

    if not chunks:
        raise HTTPException(status_code=400, detail="Unable to chunk the PDF content.")

    # embeddings
    embeddings = create_embeddings(chunks)

    # vector db
    index = build_vector_store(embeddings)

    # extract text from first pages for summarisation (lighter payload)
    first_pages_text = extract_first_pages(str(filepath), max_pages=5)
    text_preview = first_pages_text or text[:3000]

    papers[paper_id] = {
        "file_name": file.filename or f"{paper_id}.pdf",
        "chunks": chunks,
        "index": index,
        "text_preview": text_preview,
        "summary": None,
    }

    # --- Persist to disk so data survives restarts ---
    save_faiss_index(index, DATA_FOLDER / f"{paper_id}.index")
    save_paper_metadata(
        DATA_FOLDER / f"{paper_id}.json",
        paper_id=paper_id,
        file_name=file.filename or f"{paper_id}.pdf",
        chunks=chunks,
        text_preview=text_preview,
        summary=None,
    )

    return {
        "paper_id": paper_id,
        "message": "uploaded"
    }


@app.post("/ask")
async def ask_question(payload: AskRequest):
    paper_id = payload.paper_id
    question = payload.question

    paper = papers.get(paper_id)

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    chunks = paper["chunks"]
    index = paper["index"]

    answer = answer_question(question, chunks, index)

    return {"answer": answer}


@app.get("/summarize/{paper_id}")
async def get_summary(paper_id: str):
    paper = papers.get(paper_id)

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found.")

    # Return cached summary if already generated
    if paper["summary"]:
        return {"paper_id": paper_id, "summary": paper["summary"]}

    text_preview = paper.get("text_preview", "")

    if not text_preview.strip():
        raise HTTPException(status_code=400, detail="No text available for summarisation.")

    summary = summarize_text(text_preview)

    # Only cache & persist if the summary is a real result (not an error message)
    if not summary.startswith("Error generating summary"):
        paper["summary"] = summary

        # Persist updated summary to disk
        save_paper_metadata(
            DATA_FOLDER / f"{paper_id}.json",
            paper_id=paper_id,
            file_name=paper.get("file_name", f"{paper_id}.pdf"),
            chunks=paper["chunks"],
            text_preview=paper.get("text_preview", ""),
            summary=summary,
        )

    return {"paper_id": paper_id, "summary": summary}


@app.post("/search-arxiv")
async def search_arxiv(payload: ArxivSearchRequest):
    """Search arXiv for papers matching the query."""
    results = arxiv_fetch_papers(payload.query, max_results=payload.max_results)

    if not results:
        raise HTTPException(status_code=404, detail="No papers found for this query.")

    return {"results": results}


@app.post("/import-arxiv")
async def import_arxiv_paper(payload: ArxivImportRequest):
    """Download a paper from arXiv, index it, and make it available for Q&A."""
    paper_id = str(uuid.uuid4())
    file_name = f"{payload.title[:60]}.pdf"

    # Download the PDF
    filepath_str = arxiv_download_pdf(
        payload.pdf_url, payload.title, save_dir=str(DATA_FOLDER)
    )

    if not filepath_str:
        raise HTTPException(status_code=500, detail="Failed to download the PDF from arXiv.")

    # Rename to paper_id-based name for consistency
    downloaded = Path(filepath_str)
    target = DATA_FOLDER / f"{paper_id}.pdf"
    downloaded.rename(target)

    # Full pipeline: extract → chunk → embed → index
    text = extract_text_from_pdf(str(target))

    if not text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the downloaded PDF.")

    chunks = split_text(text)
    if not chunks:
        raise HTTPException(status_code=400, detail="Unable to chunk the PDF content.")

    embeddings = create_embeddings(chunks)
    index = build_vector_store(embeddings)

    first_pages_text = extract_first_pages(str(target), max_pages=5)
    text_preview = first_pages_text or text[:3000]

    papers[paper_id] = {
        "file_name": file_name,
        "chunks": chunks,
        "index": index,
        "text_preview": text_preview,
        "summary": None,
    }

    # Persist to disk
    save_faiss_index(index, DATA_FOLDER / f"{paper_id}.index")
    save_paper_metadata(
        DATA_FOLDER / f"{paper_id}.json",
        paper_id=paper_id,
        file_name=file_name,
        chunks=chunks,
        text_preview=text_preview,
        summary=None,
    )

    return {
        "paper_id": paper_id,
        "file_name": file_name,
        "message": "imported",
    }


@app.post("/ask-all")
async def ask_all_papers(payload: AskAllRequest):
    """Search across ALL uploaded papers and return a combined answer."""
    if not papers:
        raise HTTPException(status_code=404, detail="No papers have been uploaded yet.")

    question = payload.question

    # Collect top chunks from every paper
    all_chunks: list[tuple[str, str]] = []  # (paper_name, chunk_text)
    for pid, data in papers.items():
        try:
            relevant = retrieve_relevant_chunks(question, data["chunks"], data["index"], k=3)
            paper_name = data.get("file_name", pid)
            for chunk in relevant:
                all_chunks.append((paper_name, chunk))
        except Exception:
            continue

    if not all_chunks:
        raise HTTPException(status_code=400, detail="Could not retrieve relevant context from any paper.")

    # Build combined context
    context_parts = [f"[{name}]\n{text}" for name, text in all_chunks]
    context = "\n\n---\n\n".join(context_parts)

    prompt = (
        "You are an AI research assistant.\n\n"
        "Use the following excerpts from multiple research papers to answer the question.\n"
        "Cite the paper name when referencing specific findings.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer clearly and concisely:"
    )

    try:
        answer = llm_chat(prompt, max_tokens=400, temperature=0.2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {e}")

    sources = list({name for name, _ in all_chunks})

    return {"answer": answer, "sources": sources}