import os

from modules.pdf_parser import extract_text_from_pdf
from modules.chunking import split_text
from modules.embeddings import create_embeddings
from modules.vector_store import build_vector_store
from modules.rag_engine import answer_question


data_folder = "data"

pdf_files = [f for f in os.listdir(data_folder) if f.endswith(".pdf")]

pdf_path = os.path.join(data_folder, pdf_files[0])

print("Reading:", pdf_path)

# Step 1 — Extract text
text = extract_text_from_pdf(pdf_path)

# Step 2 — Chunk text
chunks = split_text(text)

print("Chunks:", len(chunks))

# Step 3 — Create embeddings
embeddings = create_embeddings(chunks)

# Step 4 — Build vector DB
index = build_vector_store(embeddings)

print("Vector database ready")

# Step 5 — Ask question
while True:

    question = input("\nAsk a question about the paper (or type 'exit'): ")

    if question.lower() == "exit":
        break

    answer = answer_question(question, chunks, index)

    print("\nAI Answer:\n")
    print(answer)