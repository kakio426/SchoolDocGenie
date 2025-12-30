import pytest
from unittest.mock import MagicMock, patch
import os

# Set fake env vars before anything else
os.environ['SUPABASE_URL'] = 'https://fake.co'
os.environ['SUPABASE_ANON_KEY'] = 'fake'
os.environ['GEMINI_API_KEY'] = 'fake'

from backend.services.supabase_service import SupabaseService

@pytest.fixture
def mocks():
    with patch('backend.services.gemini_service.genai'), \
         patch('backend.services.supabase_service.create_client') as mock_supabase:
        
        mock_client = MagicMock()
        mock_supabase.return_value = mock_client
        yield mock_client

def test_store_document(mocks):
    service = SupabaseService()
    # Mock embedding response
    with patch.object(service.ai, 'generate_embedding', return_value=[0.1, 0.2]):
        service.store_document("test content", {"file": "a.hwp"}, "summary text")
        
        mocks.table.assert_called_with("documents")
        mocks.table().insert.assert_called_once()
        args = mocks.table().insert.call_args[0][0]
        assert args["content"] == "test content"
        assert args["embedding"] == [0.1, 0.2]

def test_search_documents(mocks):
    mock_response = MagicMock()
    mock_response.data = [{"content": "found", "similarity": 0.9}]
    mocks.rpc.return_value.execute.return_value = mock_response
    
    service = SupabaseService()
    with patch.object(service.ai, 'generate_embedding', return_value=[0.1, 0.2]):
        results = service.search_documents("query")
        
        assert len(results) == 1
        assert results[0]["content"] == "found"
        mocks.rpc.assert_called_once()
