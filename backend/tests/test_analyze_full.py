
import pytest
from fastapi.testclient import TestClient
from main import app
import pandas as pd
import io
import os
from unittest.mock import patch, MagicMock

client = TestClient(app)

def test_analyze_endpoint_full():
    # Mocking Gemini Service to avoid real API calls during test
    with patch("services.gemini_service.GeminiService") as MockGeminiService:
        mock_service = MockGeminiService.return_value
        
        # Mocking analyze_document response
        mock_service.analyze_document.return_value = {
            "summary": "This is a test summary.",
            "keywords": ["test", "education"],
            "action_items": ["Review", "Approve"]
        }
        
        # Mocking extract_metadata response
        mock_service.extract_metadata.return_value = {
            "title": "2026 Education Plan",
            "date": "2025.11.11",
            "doc_number": "123-456"
        }

        # Create a dummy Excel file
        df = pd.DataFrame({"Title": ["Test Title"], "Content": ["Test Content"]})
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        # Send request
        response = client.post(
            "/analyze", 
            files={"file": ("test_full.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        
        # Check structure
        assert "filename" in data
        assert data["filename"] == "test_full.xlsx"
        assert "content" in data
        assert "analysis" in data
        
        analysis = data["analysis"]
        assert analysis["title"] == "2026 Education Plan"
        assert analysis["date"] == "2025.11.11"
        assert analysis["doc_number"] == "123-456"
        assert analysis["summary"] == "This is a test summary."
        assert analysis["keywords"] == ["test", "education"]
        assert analysis["action_items"] == ["Review", "Approve"]

def test_analyze_endpoint_invalid_file():
    # Test with unsupported file type
    response = client.post(
        "/analyze",
        files={"file": ("test.txt", io.BytesIO(b"content"), "text/plain")}
    )
    assert response.status_code == 400
