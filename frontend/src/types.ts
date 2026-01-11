export interface PDFUploadResult {
  pdf_id: string;
  filename: string;
  message: string;
}

export interface UploadError {
  filename: string;
  error: string;
}

export interface UploadResponse {
  uploaded: PDFUploadResult[];
  errors: UploadError[];
}

export interface SearchResult {
  pdf_id: string;
  filename: string;
  confidence_score: number;
  snippet: string;
}

export interface SearchResponse {
  results: SearchResult[];
  query: string;
}

export interface PDFMetadata {
  id: string;
  filename: string;
  upload_time: string;
  file_size: number;
  text_preview: string;
}
