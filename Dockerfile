# ---- Python backend ----
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system deps for faiss-cpu
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY modules/ modules/
COPY server.py .
COPY app.py .

# Create data folder (will be mounted as volume in production)
RUN mkdir -p data

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
