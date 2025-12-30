import pytest
from unittest.mock import MagicMock, patch
import json
from backend.services.gemini_service import GeminiService

def test_caching_mechanism():
    # Test that repeated calls with same content hit the cache
    mock_response = MagicMock()
    mock_response.text = json.dumps({"summary": "Cached"})
    
    with patch('google.generativeai.GenerativeModel') as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value = mock_response
        
        service = GeminiService(api_key="fake")
        
        # First call
        service.analyze_document("Same Content")
        
        # Second call
        service.analyze_document("Same Content")
        
        # Verify API was called only ONCE
        assert instance.generate_content.call_count == 1
