from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
PROJECTS_DIR = STORAGE_DIR / "projects"
MODELS_DIR = BASE_DIR / "models"

MAX_UPLOAD_SIZE = 100 * 1024 * 1024
MAX_EXTRACTED_SIZE = 300 * 1024 * 1024
MAX_FILES = 5000

ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "null"
]

for directory in (STORAGE_DIR, PROJECTS_DIR, MODELS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
