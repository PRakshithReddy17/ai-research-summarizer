# Deployment Guide

## Architecture

- **Backend (FastAPI)** → Render.com (free tier)
- **Frontend (Next.js)** → Vercel (free tier)

---

## Step 1 — Deploy Backend on Render

1. Push your code to GitHub.
2. Go to [https://render.com](https://render.com) and sign up / log in.
3. Click **New → Web Service** and connect your GitHub repo.
4. Render will detect `render.yaml` and auto-configure.
5. Set these **environment variables** in the Render dashboard:
   - `HF_API_TOKEN` → your Hugging Face token (`hf_...`)
   - `CORS_ORIGINS` → your Vercel frontend URL (e.g. `https://your-app.vercel.app`)
   - `API_KEY` → optional, set a secret key to protect your API
6. Click **Deploy**. Wait for the build to complete.
7. Note the deployed backend URL (e.g. `https://ai-research-summarizer-api.onrender.com`).

The health check is at `/health`.

## Step 2 — Deploy Frontend on Vercel

1. Go to [https://vercel.com](https://vercel.com) and sign up / log in.
2. Click **Add New → Project** and import the same GitHub repo.
3. Set **Framework Preset** to `Next.js`.
4. Set these **environment variables** in the Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` → your Render backend URL (e.g. `https://ai-research-summarizer-api.onrender.com`)
   - `NEXT_PUBLIC_API_KEY` → same value as `API_KEY` on Render (leave empty if not using auth)
5. Click **Deploy**.

## Step 3 — Update CORS

After both are deployed, go back to Render and set:
- `CORS_ORIGINS` → your actual Vercel URL (e.g. `https://ai-research-summarizer.vercel.app`)

---

## Alternative: Railway

1. Create a new project at [https://railway.app](https://railway.app).
2. Connect your GitHub repo — Railway will use the included `Procfile`.
3. Set the same environment variables: `HF_API_TOKEN`, `CORS_ORIGINS`, `HF_MODEL_NAME`.

## Alternative: Docker Compose (self-hosted)

```bash
# Set your token
export HF_API_TOKEN=hf_your_token_here

# Build and run both services
docker-compose up --build -d
```

Backend: http://localhost:8000 | Frontend: http://localhost:3000

---

## Environment Variables Reference

| Variable | Where | Required | Description |
|---|---|---|---|
| `HF_API_TOKEN` | Backend | Yes | Hugging Face API token |
| `HF_MODEL_NAME` | Backend | No | Default: `Qwen/Qwen2.5-Coder-32B-Instruct` |
| `CORS_ORIGINS` | Backend | Yes | Frontend URL (comma-separated) |
| `API_KEY` | Backend | No | API key for authentication |
| `RATE_LIMIT_RPM` | Backend | No | Max requests/min per IP (default: 30) |
| `NEXT_PUBLIC_API_URL` | Frontend | Yes | Backend URL |
| `NEXT_PUBLIC_API_KEY` | Frontend | No | Must match `API_KEY` on backend |

## Important Notes

- Render free tier spins down after 15 min of inactivity. First request after idle takes ~30 seconds.
- Uploaded PDFs are stored on Render's ephemeral disk — they will be lost on redeploy.
- Hugging Face free tier has rate limits — suitable for demos, not heavy production.
