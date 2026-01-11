import os
import pytest
from fastapi.testclient import TestClient
from io import BytesIO

# Set test database before importing app
os.environ["TEST_MODE"] = "1"

from app.main import app
from app.database import DATABASE_PATH, init_db

# Test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Setup and teardown for each test."""
    # Use a test database
    import app.database as db_module
    db_module.DATABASE_PATH = "test_pdf_search.db"
    
    # Initialize fresh database
    init_db()
    
    yield
    
    # Cleanup test database
    if os.path.exists("test_pdf_search.db"):
        os.remove("test_pdf_search.db")


def create_simple_pdf() -> bytes:
    """Create a minimal valid PDF for testing."""
    # This is a minimal valid PDF with text "Hello World"
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT
/F1 12 Tf
100 700 Td
(Hello World) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000360 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
435
%%EOF"""
    return pdf_content


def create_pdf_with_text(text: str) -> bytes:
    """Create a PDF with specific text content."""
    pdf_content = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length {len(text) + 40} >>
stream
BT
/F1 12 Tf
100 700 Td
({text}) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
0000000360 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
435
%%EOF""".encode()
    return pdf_content


class TestHealthCheck:
    """Tests for health check endpoint."""
    
    def test_health_check(self):
        """Test that health check returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestUploadEndpoint:
    """Tests for PDF upload endpoint."""
    
    def test_upload_valid_pdf(self):
        """Test uploading a valid PDF file."""
        pdf_content = create_simple_pdf()
        files = [("files", ("test.pdf", BytesIO(pdf_content), "application/pdf"))]
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["uploaded"]) == 1
        assert len(data["errors"]) == 0
        assert data["uploaded"][0]["filename"] == "test.pdf"
        assert "pdf_id" in data["uploaded"][0]
    
    def test_upload_multiple_pdfs(self):
        """Test uploading multiple PDF files."""
        pdf_content = create_simple_pdf()
        files = [
            ("files", ("test1.pdf", BytesIO(pdf_content), "application/pdf")),
            ("files", ("test2.pdf", BytesIO(pdf_content), "application/pdf")),
        ]
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["uploaded"]) == 2
        assert len(data["errors"]) == 0
    
    def test_upload_invalid_file_type(self):
        """Test uploading a non-PDF file."""
        files = [("files", ("test.txt", BytesIO(b"Hello World"), "text/plain"))]
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["uploaded"]) == 0
        assert len(data["errors"]) == 1
        assert "must be a PDF" in data["errors"][0]["error"]
    
    def test_upload_corrupted_pdf(self):
        """Test uploading a corrupted PDF file."""
        files = [("files", ("test.pdf", BytesIO(b"not a pdf"), "application/pdf"))]
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["uploaded"]) == 0
        assert len(data["errors"]) == 1


class TestSearchEndpoint:
    """Tests for search endpoint."""
    
    def test_search_with_results(self):
        """Test searching with matching results."""
        # First upload a PDF
        pdf_content = create_pdf_with_text("Python programming language")
        files = [("files", ("python.pdf", BytesIO(pdf_content), "application/pdf"))]
        client.post("/upload", files=files)
        
        # Search for content
        response = client.post("/search", json={"query": "Python"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "Python"
        assert "results" in data
    
    def test_search_no_results(self):
        """Test searching with no matching results."""
        response = client.post("/search", json={"query": "nonexistent"})
        
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
    
    def test_search_empty_query(self):
        """Test searching with empty query."""
        response = client.post("/search", json={"query": ""})
        
        assert response.status_code == 400
        assert "empty" in response.json()["detail"].lower()
    
    def test_search_whitespace_query(self):
        """Test searching with whitespace-only query."""
        response = client.post("/search", json={"query": "   "})
        
        assert response.status_code == 400


class TestPDFMetadataEndpoint:
    """Tests for PDF metadata endpoint."""
    
    def test_get_pdf_metadata(self):
        """Test getting metadata for an uploaded PDF."""
        # First upload a PDF
        pdf_content = create_simple_pdf()
        files = [("files", ("metadata_test.pdf", BytesIO(pdf_content), "application/pdf"))]
        upload_response = client.post("/upload", files=files)
        pdf_id = upload_response.json()["uploaded"][0]["pdf_id"]
        
        # Get metadata
        response = client.get(f"/pdf/{pdf_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pdf_id
        assert data["filename"] == "metadata_test.pdf"
        assert "upload_time" in data
        assert "file_size" in data
        assert "text_preview" in data
    
    def test_get_nonexistent_pdf(self):
        """Test getting metadata for non-existent PDF."""
        response = client.get("/pdf/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
