import pytest
from unittest.mock import patch, MagicMock
from backend.services.gemini_service import GeminiService

def test_gemini_connection_missing_key():
    # Test that initialization fails without an API key
    with patch.dict('os.environ', {}, clear=True):
         with pytest.raises(ValueError):
            GeminiService()

def test_gemini_generate_content():
    # Mocking the google-genai response
    mock_response = MagicMock()
    mock_response.text = "Hello, I am Gemini."
    
    with patch('google.generativeai.GenerativeModel') as MockModel:
        instance = MockModel.return_value
        instance.generate_content.return_value = mock_response
        
        service = GeminiService(api_key="fake-key")
        response = service.generate_content("Hello")
        
        assert response == "Hello, I am Gemini."
        instance.generate_content.assert_called_with("Hello")
