from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PDFUploadResponse(BaseModel):
    pdf_id: str
    filename: str
    message: str


class UploadResponse(BaseModel):
    uploaded: List[PDFUploadResponse]
    errors: List[dict]


class SearchQuery(BaseModel):
    query: str


class SearchResult(BaseModel):
    pdf_id: str
    filename: str
    confidence_score: float
    snippet: str


class SearchResponse(BaseModel):
    results: List[SearchResult]
    query: str


class PDFMetadata(BaseModel):
    id: str
    filename: str
    upload_time: str
    file_size: int
    text_preview: str


class ErrorResponse(BaseModel):
    detail: str
