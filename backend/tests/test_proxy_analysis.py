import pytest
import os
import sys
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add backend to path for importing main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

def test_proxy_analysis_missing_key():
    """Test 1.1: Request without API key should fail with 401"""
    response = client.post("/analyze/proxy", json={"text": "Test content", "filename": "test.txt"})
    assert response.status_code == 401
    assert "API Key가 필요합니다" in response.json()["detail"]

@patch("services.gemini_service.GeminiService.analyze_document_comprehensive")
@patch("services.supabase_service.SupabaseService.store_document")
def test_proxy_analysis_success(mock_store, mock_analyze):
    """Test 1.2: Request with API key should succeed and NOT store in DB"""
    
    # Mock Analysis Result
    mock_analyze.return_value = {
        "metadata": {"title": "Test Title", "date": "2025.12.31", "doc_number": "123"},
        "keywords": ["test", "proxy"],
        "summary": ""
    }
    
    headers = {"x-user-gemini-key": "fake-valid-key"}
    payload = {"text": "Test content for proxy analysis", "filename": "proxy_test.txt"}
    
    response = client.post("/analyze/proxy", json=payload, headers=headers)
    
    # Verify Success
    assert response.status_code == 200
    data = response.json()
    assert data["analysis"]["title"] == "Test Title"
    
    # Verify Statelessness (Supabase should NOT be called)
    mock_store.assert_not_called()
    
    # Verify Gemini was called (Implementation detail: we'll check if key was passed later)
    mock_analyze.assert_called_once()
