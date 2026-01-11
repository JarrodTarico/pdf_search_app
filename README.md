# PDF Search Application

A full-stack web application for uploading PDFs and searching across their content using TF-IDF ranking.

## Features

- **Upload PDFs**: Drag-and-drop or file picker support for multiple PDFs
- **Text Extraction**: Automatic text extraction from uploaded PDFs using PyMuPDF
- **Smart Search**: TF-IDF + cosine similarity based search across all documents
- **Ranked Results**: Results sorted by confidence score with highlighted snippets
- **Modern UI**: Clean, responsive React frontend

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite
- **Backend**: Python, FastAPI
- **Search**: scikit-learn (TF-IDF + cosine similarity)
- **PDF Processing**: PyMuPDF (fitz)
- **Database**: SQLite

## Project Structure

```
pdf_search_app_p1/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── database.py       # SQLite operations
│   │   ├── pdf_extractor.py  # PDF text extraction
│   │   ├── search_engine.py  # TF-IDF search
│   │   └── schemas.py        # Pydantic models
│   ├── tests/
│   │   └── test_api.py       # API tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── api.ts           # API client
│   │   └── types.ts         # TypeScript types
│   └── package.json
└── README.md
```

## Running Locally

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm

### Terminal 1 - Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at http://localhost:8000

### Terminal 2 - Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at http://localhost:5173

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/upload` | POST | Upload one or more PDF files |
| `/search` | POST | Search across all uploaded PDFs |
| `/pdf/{pdf_id}` | GET | Get metadata for a specific PDF |
| `/health` | GET | Health check endpoint |

### Upload PDFs

```bash
curl -X POST http://localhost:8000/upload \
  -F "files=@document1.pdf" \
  -F "files=@document2.pdf"
```

### Search Documents

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your search terms"}'
```

## Running Tests

```bash
cd backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest tests/ -v
```

## Pushing to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: PDF Search app with React frontend and FastAPI backend"

# Add remote repository
git remote add origin <your-github-repo-url>

# Push to main branch
git push -u origin main
```

## Limitations

- Maximum file size: 10MB per PDF
- PDFs must contain extractable text (scanned images without OCR are not supported)
- Search works best with English text

## License

MIT
