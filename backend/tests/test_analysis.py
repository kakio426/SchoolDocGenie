import pytest
from unittest.mock import MagicMock, patch
import json
from backend.services.gemini_service import GeminiService

def test_analyze_document_structure():
    # Test that the analysis returns the expected JSON structure
    mock_response = MagicMock()
    # Mocking a valid JSON string response from LLM
    expected_json = {
        "summary": "This is a summary.",
        "keywords": ["test", "document"],
        "action_items": ["Review", "Approve"]
    }
    mock_response.text = json.dumps(expected_json)
    
    with patch('google.generativeai.GenerativeModel') as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value = mock_response
        
        service = GeminiService(api_key="fake")
        result = service.analyze_document("Markdown content here")
        
        assert isinstance(result, dict)
        assert result["summary"] == "This is a summary."
        assert "keywords" in result
        assert "action_items" in result

def test_analyze_document_json_parsing_error():
    # Test handling of invalid JSON response
    mock_response = MagicMock()
    mock_response.text = "Not a JSON string"
    
    with patch('google.generativeai.GenerativeModel') as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value = mock_response
        
        service = GeminiService(api_key="fake")
        # Should probably return a default error dict or raise wrapped error
        # Here we assume it handles it gracefully or raises exception
        with pytest.raises(ValueError, match="Failed to parse JSON"):
            service.analyze_document("Markdown content")
