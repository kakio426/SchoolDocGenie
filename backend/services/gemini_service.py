import os
import google.generativeai as genai

class GeminiService:
    def __init__(self, api_key: str = None):
        import hashlib
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        
        genai.configure(api_key=self.api_key)
        # Using Gemini 3.0 Flash (December 2025 latest model)
        self.model = genai.GenerativeModel('gemini-3.0-flash')
        self._cache = {}

    def _get_hash(self, content: str) -> str:
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_document(self, content: str) -> dict:
        import json
        
        content_hash = self._get_hash(content)
        if content_hash in self._cache:
            return self._cache[content_hash]

        system_prompt = """
        You are an expert administrative assistant for Korean schools.
        Analyze the following document and provide a summary in VALID JSON format.
        Do not include markdown code blocks (```json). Just raw JSON.
        
        Output Schema:
        {
            "summary": "Concise summary of the document",
            "keywords": ["List", "of", "keywords"],
            "action_items": ["Action 1", "Action 2"]
        }
        """
        
        full_prompt = f"{system_prompt}\n\nDocument Content:\n{content}"
        
        response = self.model.generate_content(full_prompt)
        text_response = response.text.strip()
        
        # Clean up if model adds code blocks
        if text_response.startswith("```json"):
            text_response = text_response[7:]
        if text_response.endswith("```"):
            text_response = text_response[:-3]
            
        try:
            result = json.loads(text_response)
            self._cache[content_hash] = result
            return result
        except json.JSONDecodeError:
            raise ValueError(f"Failed to parse JSON response: {text_response}")

    def generate_embedding(self, text: str) -> list:
        # Using Google's dedicated embedding model
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']


