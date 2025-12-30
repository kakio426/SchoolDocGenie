import os
import google.generativeai as genai

class GeminiService:
    def __init__(self, api_key: str = None):
        from dotenv import load_dotenv
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=BASE_DIR / '.env')
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')
        self._cache = {}

    def _get_hash(self, content: str) -> str:
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def analyze_document_comprehensive(self, content: str) -> dict:
        """메타데이터 추출과 분석을 한 번의 API 호출로 통합 (Quota 절약)"""
        import json
        import re
        from core.logger import logger
        
        system_prompt = """
        You are an expert school administrative assistant. 
        Analyze the document and return a STRICT JSON object.
        
        Output format:
        {
            "metadata": {
                "title": "Document Title",
                "date": "YYYY.MM.DD",
                "doc_number": "Number or empty"
            },
            "keywords": ["key1", "key2"]
        }
        """
        
        full_prompt = f"{system_prompt}\n\nDocument Content:\n{content[:5000]}"
        
        try:
            response = self.model.generate_content(full_prompt)
            text_response = response.text.strip()
            
            # JSON만 추출
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return json.loads(text_response)
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                raise ValueError("AI 사용량이 초과되었습니다. 1분 후 다시 시도해주세요.")
            logger.error(f"Comprehensive Analysis Failed: {e}")
            return {
                "metadata": {"title": "제목 없음", "date": "", "doc_number": ""},
                "keywords": []
            }

    def generate_embedding(self, text: str) -> list:
        try:
            from core.logger import logger
            # Ensure text is not empty
            if not text or not text.strip():
                return [0.0] * 768

            logger.info(f"Requesting embedding for text (len: {len(text)})...")
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )
            
            if result is None:
                logger.error("genai.embed_content returned None. Check API Key or Quota.")
                return [0.0] * 768
                
            if 'embedding' in result:
                return result['embedding']
            
            logger.error(f"Embedding key missing in result: {result}")
            return [0.0] * 768
        except Exception as e:
            from core.logger import logger
            logger.error(f"CRITICAL: Gemini Embedding Library Error: {type(e).__name__}: {e}")
            return [0.0] * 768


    def extract_metadata(self, content: str) -> dict:
        import json
        import re
        from core.logger import logger
        
        prompt = f"""
        Extract the following metadata from the document:
        1. Title of the document
        2. Date (YYYY.MM.DD format)
        3. Document Number (if available)

        Return strictly in JSON format:
        {{
            "title": "Document Title",
            "date": "YYYY.MM.DD",
            "doc_number": "Document Number or empty string"
        }}

        Document Content (first 1000 chars):
        {content[:1000]}
        """
        
        try:
            response = self.model.generate_content(prompt)
            text_response = response.text.strip()
            
            # Clean up if model adds code blocks
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            
            # Find JSON object
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback
            try:
                return json.loads(text_response)
            except:
                return {"title": "제목 없음", "date": "", "doc_number": ""}
                
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {"title": "제목 없음", "date": "", "doc_number": ""}
