
import pytest
from unittest.mock import MagicMock, patch
from services.supabase_service import SupabaseService

@patch("services.supabase_service.create_client")
@patch("services.supabase_service.GeminiService")
def test_store_document(MockGemini, mock_create_client):
    # Setup mocks
    mock_supabase = mock_create_client.return_value
    mock_gemini = MockGemini.return_value
    
    # Mock embedding generation
    mock_gemini.generate_embedding.return_value = [0.1, 0.2, 0.3]
    
    # Mock Supabase insert response
    mock_insert = mock_supabase.table.return_value.insert.return_value
    mock_insert.execute.return_value.data = [{"id": "doc-123"}]
    
    service = SupabaseService("http://test.com", "key")
    
    # Call store_document
    doc_id = service.store_document(
        content="Test Content",
        metadata={"title": "Test"},
        summary="Test Summary"
    )
    
    # Verify behavior
    mock_gemini.generate_embedding.assert_called_with("Test Content")
    
    mock_supabase.table.assert_called_with("documents")
    mock_supabase.table().insert.assert_called_with({
        "content": "Test Content",
        "metadata": {"title": "Test"},
        "summary": "Test Summary",
        "embedding": [0.1, 0.2, 0.3]
    })
    
    # Verify return value (This will fail initially as it returns None)
    assert doc_id == "doc-123"
