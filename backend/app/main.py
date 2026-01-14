import uuid
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db, insert_pdf, get_pdf_by_id, get_all_pdfs
from .pdf_extractor import (
    extract_text_from_pdf,
    validate_file_size,
    is_valid_pdf,
    PDFExtractionError,
    FileTooLargeError,
    EmptyPDFError,
)
from .search_engine import search_documents
from .schemas import (
    UploadResponse,
    PDFUploadResponse,
    SearchQuery,
    SearchResponse,
    SearchResult,
    PDFMetadata,
)

# Initialize FastAPI app
app = FastAPI(
    title="PDF Search API",
    description="API for uploading PDFs and searching across their content",
    version="1.0.0",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.post("/upload", response_model=UploadResponse)
async def upload_pdfs(files: List[UploadFile] = File(...)):
    """
    Upload one or more PDF files.
    
    Extracts text from each PDF and stores it in the database.
    Returns the pdf_id for each successfully uploaded file.
    """
    uploaded = []
    errors = []
    
    for file in files:
        try:
            # Validate file extension
            if not is_valid_pdf(file.filename or ""):
                errors.append({
                    "filename": file.filename,
                    "error": "File must be a PDF"
                })
                continue
            
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            try:
                validate_file_size(file_size)
            except FileTooLargeError as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                continue
            
            # Extract text from PDF
            try:
                text_content = extract_text_from_pdf(content)
            except EmptyPDFError as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                continue
            except PDFExtractionError as e:
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })
                continue
            
            # Generate unique ID and store in database
            pdf_id = str(uuid.uuid4())
            insert_pdf(pdf_id, file.filename or "unknown.pdf", text_content, file_size)
            
            uploaded.append(PDFUploadResponse(
                pdf_id=pdf_id,
                filename=file.filename or "unknown.pdf",
                message="Successfully uploaded and processed"
            ))
            
        except Exception as e:
            errors.append({
                "filename": file.filename or "unknown",
                "error": f"Unexpected error: {str(e)}"
            })
    
    return UploadResponse(uploaded=uploaded, errors=errors)


@app.post("/search", response_model=SearchResponse)
async def search_pdfs(search_query: SearchQuery):
    """
    Search across all uploaded PDFs.
    
    Returns ranked results with confidence scores and snippets.
    """
    if not search_query.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    results = search_documents(search_query.query)
    
    search_results = [
        SearchResult(
            pdf_id=r['pdf_id'],
            filename=r['filename'],
            confidence_score=r['confidence_score'],
            sentiment_score=r['sentiment_score'],
            snippet=r['snippet']
        )
        for r in results
    ]
    
    return SearchResponse(results=search_results, query=search_query.query)


@app.get("/pdf/{pdf_id}", response_model=PDFMetadata)
async def get_pdf_metadata(pdf_id: str):
    """
    Get metadata for a specific PDF.
    
    Returns filename, upload time, file size, and a preview of the text content.
    """
    pdf = get_pdf_by_id(pdf_id)
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Create a short text preview (first 500 characters)
    text_preview = pdf['text_content'][:500]
    if len(pdf['text_content']) > 500:
        text_preview += "..."
    
    return PDFMetadata(
        id=pdf['id'],
        filename=pdf['filename'],
        upload_time=str(pdf['upload_time']),
        file_size=pdf['file_size'],
        text_preview=text_preview
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
