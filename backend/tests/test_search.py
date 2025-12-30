
import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch, MagicMock

client = TestClient(app)

@patch("services.supabase_service.SupabaseService")
def test_search_documents(MockSupabaseService):
    # Mocking Supabase Service
    mock_service = MockSupabaseService.return_value
    
    # Mocking search_documents response
    mock_service.search_documents.return_value = [
        {
            "id": "doc-1",
            "metadata": {
                "title": "2026 Curriculum Plan",
                "date": "2025.11.11"
            },
            "summary": "This is a plan.",
            "similarity": 0.85
        }
    ]

    # Test GET /search
    response = client.get("/search?q=curriculum")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "results" in data
    assert len(data["results"]) == 1
    assert data["results"][0]["metadata"]["title"] == "2026 Curriculum Plan"
    
    # Verify mock was called correctly
    mock_service.search_documents.assert_called_with("curriculum")

@patch("services.supabase_service.SupabaseService")
def test_search_documents_empty(MockSupabaseService):
    # Mocking empty response
    mock_service = MockSupabaseService.return_value
    mock_service.search_documents.return_value = []

    response = client.get("/search?q=unknown")
    
    assert response.status_code == 200
    assert len(response.json()["results"]) == 0
