# 📄 AI Research Summarizer

A full-stack **RAG (Retrieval-Augmented Generation)** application for uploading research papers, asking grounded questions, and generating AI-powered summaries — built with **FastAPI**, **Next.js 14**, **FAISS**, and **Hugging Face**.

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Vercel-black?style=for-the-badge)](https://ai-research-summarizer-self.vercel.app)
[![Backend API](https://img.shields.io/badge/⚡_Backend_API-Render-46E3B7?style=for-the-badge)](https://ai-research-summarizer-9nmx.onrender.com/health)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📤 **PDF Upload & Indexing** | Upload research papers — text is extracted, chunked, embedded, and indexed in FAISS |
| 💬 **RAG-powered Q&A** | Ask questions about any uploaded paper and get grounded answers from the actual content |
| 📝 **AI Summarization** | One-click summaries of research papers using Hugging Face LLMs |
| 🔍 **arXiv Search & Import** | Search arXiv directly from the app and import papers with one click |
| 📚 **Cross-paper Search** | Ask a question across all uploaded papers simultaneously |
| 💾 **Persistent Storage** | Papers, indexes, and summaries survive server restarts |
| 🗂️ **Chat History** | Conversation history persisted in localStorage per paper |
| 🔑 **API Key Auth & Rate Limiting** | Optional API key authentication and configurable rate limiting |
| 📖 **Markdown Rendering** | AI responses rendered with full Markdown support |
| 🐳 **Docker Support** | Docker and docker-compose for one-command local deployment |

---

## 🏗️ Architecture

```
┌─────────────────────┐        ┌──────────────────────────────┐
│   Next.js Frontend  │  HTTP  │      FastAPI Backend          │
│   (Vercel)          │◄──────►│      (Render)                │
│                     │        │                              │
│  • Upload PDFs      │        │  • PDF parsing (pypdf)       │
│  • Chat interface   │        │  • Text chunking             │
│  • arXiv search     │        │  • Embeddings (HF API)       │
│  • Summary cards    │        │  • FAISS vector store        │
│  • Markdown render  │        │  • RAG question answering    │
└─────────────────────┘        │  • AI summarization          │
                               │  • arXiv integration         │
                               │  • Persistent disk storage   │
                               └──────────┬───────────────────┘
                                          │
                                          ▼
                               ┌──────────────────────┐
                               │  Hugging Face API     │
                               │  • Embeddings         │
                               │  • Chat Completion    │
                               │  • Text Generation    │
                               └──────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- [Hugging Face API Token](https://huggingface.co/settings/tokens) (free)

### 1. Clone the repo

```bash
git clone https://github.com/PRakshithReddy17/ai-research-summarizer.git
cd ai-research-summarizer
```

### 2. Set up the backend

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\Activate.ps1    # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your HF_API_TOKEN
```

### 3. Set up the frontend

```bash
npm install
```

### 4. Run locally

```bash
# Terminal 1 — Backend
uvicorn server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Frontend
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** and start uploading papers!

---

## 🐳 Docker (Alternative)

```bash
# Set your Hugging Face token
export HF_API_TOKEN=hf_your_token_here

# Build and run both services
docker-compose up --build -d
```

- Backend: [http://localhost:8000](http://localhost:8000)
- Frontend: [http://localhost:3000](http://localhost:3000)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `GET` | `/papers` | List all uploaded papers |
| `POST` | `/upload` | Upload a PDF file |
| `POST` | `/ask` | Ask a question about a specific paper |
| `GET` | `/summarize/{paper_id}` | Generate/retrieve paper summary |
| `POST` | `/ask-all` | Ask a question across all papers |
| `POST` | `/search-arxiv` | Search arXiv for papers |
| `POST` | `/import-arxiv` | Import a paper from arXiv |

---

## 🧩 Project Structure

```
ai-research-summarizer/
├── server.py                   # FastAPI application & API routes
├── modules/
│   ├── pdf_parser.py           # PDF text extraction (pypdf)
│   ├── chunking.py             # Recursive text splitter (pure Python)
│   ├── embeddings.py           # HF Inference API embeddings
│   ├── vector_store.py         # FAISS index management
│   ├── retriever.py            # Similarity search & chunk retrieval
│   ├── rag_engine.py           # RAG question answering
│   ├── summarizer.py           # AI paper summarization
│   ├── llm_client.py           # Hugging Face InferenceClient wrapper
│   ├── arxiv_fetcher.py        # arXiv API integration
│   ├── storage.py              # Persistent FAISS & metadata storage
│   ├── auth.py                 # API key authentication middleware
│   └── rate_limiter.py         # In-memory rate limiter
├── app/
│   ├── page.tsx                # Landing page
│   ├── layout.tsx              # Root layout
│   └── dashboard/
│       └── page.tsx            # Main dashboard (chat + sidebar)
├── components/
│   ├── ChatWindow.tsx          # Chat interface
│   ├── MessageBubble.tsx       # Message display with Markdown
│   ├── Sidebar.tsx             # Paper list & navigation
│   ├── UploadPDF.tsx           # PDF upload with progress
│   ├── ArxivSearch.tsx         # arXiv search panel
│   ├── PaperSummaryCard.tsx    # AI summary display
│   ├── QuestionInput.tsx       # Question input bar
│   └── Navbar.tsx              # Top navigation
├── lib/
│   ├── api.ts                  # Backend API client
│   ├── local-storage.ts        # Chat history persistence
│   ├── types.ts                # TypeScript types
│   └── utils.ts                # Utility functions
├── tests/
│   ├── test_modules.py         # Unit tests for backend modules
│   └── test_api.py             # API endpoint tests
├── Dockerfile                  # Backend container
├── Dockerfile.frontend         # Frontend container
├── docker-compose.yml          # Full-stack orchestration
├── render.yaml                 # Render.com deploy config
├── requirements.txt            # Python dependencies
└── package.json                # Node.js dependencies
```

---

## ⚙️ Environment Variables

| Variable | Service | Required | Default | Description |
|----------|---------|----------|---------|-------------|
| `HF_API_TOKEN` | Backend | ✅ | — | Hugging Face API token |
| `HF_MODEL_NAME` | Backend | ❌ | `Qwen/Qwen2.5-Coder-32B-Instruct` | LLM model for Q&A and summaries |
| `CORS_ORIGINS` | Backend | ❌ | `*` | Allowed frontend origins (comma-separated) |
| `API_KEY` | Backend | ❌ | — | Optional API key for authentication |
| `RATE_LIMIT_RPM` | Backend | ❌ | `30` | Max requests per minute per IP |
| `NEXT_PUBLIC_API_URL` | Frontend | ✅ | `http://localhost:8000` | Backend API URL |
| `NEXT_PUBLIC_API_KEY` | Frontend | ❌ | — | Must match backend `API_KEY` |

---

## 🌐 Deployment

The app is deployed on:

- **Frontend:** [Vercel](https://vercel.com) → [ai-research-summarizer-self.vercel.app](https://ai-research-summarizer-self.vercel.app)
- **Backend:** [Render](https://render.com) → [ai-research-summarizer-9nmx.onrender.com](https://ai-research-summarizer-9nmx.onrender.com/health)

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment instructions.

> **Note:** Render free tier spins down after 15 min of inactivity. The first request after idle takes ~30 seconds to cold-start.

---

## 🧪 Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/ -v
```

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — High-performance Python API framework
- [FAISS](https://github.com/facebookresearch/faiss) — Facebook AI Similarity Search
- [Hugging Face Hub](https://huggingface.co/docs/huggingface_hub) — LLM inference & embeddings API
- [pypdf](https://pypdf.readthedocs.io/) — PDF text extraction
- [NumPy](https://numpy.org/) — Vector operations

**Frontend**
- [Next.js 14](https://nextjs.org/) — React framework with App Router
- [Tailwind CSS](https://tailwindcss.com/) — Utility-first CSS
- [Radix UI](https://www.radix-ui.com/) — Accessible UI primitives
- [Lucide Icons](https://lucide.dev/) — Beautiful icon set
- [react-markdown](https://github.com/remarkjs/react-markdown) — Markdown rendering

**Infrastructure**
- [Docker](https://www.docker.com/) — Containerization
- [Render](https://render.com/) — Backend hosting
- [Vercel](https://vercel.com/) — Frontend hosting

---

## 📄 License

This project is open source under the [MIT License](LICENSE).

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

<p align="center">
  Built with ❤️ by <a href="https://github.com/PRakshithReddy17">Rakshith Reddy</a>
</p>
