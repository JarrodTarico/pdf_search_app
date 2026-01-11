import fitz  # PyMuPDF
from typing import Tuple

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


class PDFExtractionError(Exception):
    """Custom exception for PDF extraction errors."""
    pass


class FileTooLargeError(Exception):
    """Custom exception for files exceeding size limit."""
    pass


class EmptyPDFError(Exception):
    """Custom exception for PDFs with no extractable text."""
    pass


def validate_file_size(file_size: int) -> None:
    """Validate that file size is within limits."""
    if file_size > MAX_FILE_SIZE:
        raise FileTooLargeError(
            f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds maximum allowed size (10MB)"
        )


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_bytes: The PDF file content as bytes
        
    Returns:
        Extracted text content as a string
        
    Raises:
        PDFExtractionError: If the PDF cannot be read or processed
        EmptyPDFError: If the PDF contains no extractable text
    """
    try:
        # Open PDF from bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(text)
        
        doc.close()
        
        full_text = "\n".join(text_parts)
        
        if not full_text.strip():
            raise EmptyPDFError("PDF contains no extractable text")
        
        return full_text
        
    except EmptyPDFError:
        raise
    except fitz.fitz.FileDataError as e:
        raise PDFExtractionError(f"Invalid or corrupted PDF file: {str(e)}")
    except Exception as e:
        raise PDFExtractionError(f"Could not extract text from PDF: {str(e)}")


def is_valid_pdf(filename: str) -> bool:
    """Check if the filename has a PDF extension."""
    return filename.lower().endswith('.pdf')
