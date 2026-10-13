"""
Central configuration for EduPath AI.
Module 1 settings (paths, chunking, embeddings) + Module 2 settings (LLM).
"""
import os
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file if present

# ---- Paths ----
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, "data", "processed")
CHROMA_DB_DIR = os.path.join(BASE_DIR, "chroma_db")

CATEGORIES = ["career", "scholarship", "course", "scheme"]

# ---- Chunking ----
CHUNK_SIZE = 500
CHUNK_OVERLAP = 80

# ---- Embeddings (Module 1) ----
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# ---- ChromaDB ----
COLLECTION_NAME = "career_advisor_docs"

# ---- LLM (Module 2) ----
# Get a free key at https://aistudio.google.com/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-flash-lite-latest"

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:latest"

# How many chunks to retrieve per category when building recommendations
RETRIEVAL_TOP_K = 4