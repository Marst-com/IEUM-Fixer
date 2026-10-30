
# IEUM Fixer

AI-Powered Project Recovery System

## Version
0.2.0

## Architecture
- Frontend: HTML, CSS, Vanilla JavaScript
- Backend: Python, FastAPI
- AI: PyTorch
- Archive: ZIP
- Validation: Python AST, Node.js

## Features
- ZIP upload
- Folder upload
- Project explorer
- Python syntax analysis
- JavaScript typo detection
- HTML tag analysis
- CSS structure analysis
- JSON validation
- Safe automatic repair
- Project validation
- ZIP export
- PyTorch classifier architecture

## Requirements
- Python 3.10+
- PyTorch CPU or CUDA
- Modern browser
- Node.js (optional, for JS validation)

## Backend

cd backend

python -m pip install -r requirements.txt

python main.py

## Frontend

cd frontend

python -m http.server 5500 --bind 127.0.0.1

Open:
http://127.0.0.1:5500

## API
http://127.0.0.1:8000/docs
