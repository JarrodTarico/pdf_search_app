# PDF Search Backend

FastAPI backend for the PDF Search application.

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
pytest tests/ -v
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
