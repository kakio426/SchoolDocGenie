import os
import google.generativeai as genai

class GeminiService:
    def __init__(self, api_key: str = None):
        from dotenv import load_dotenv
        from pathlib import Path
        BASE_DIR = Path(__file__).resolve().parent.parent
        load_dotenv(dotenv_path=BASE_DIR / '.env')
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-3-flash-preview')
        else:
            self.model = None
        
        self._cache = {}

    def _get_hash(self, content: str) -> str:
        import hashlib
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def generate_content(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text

    def ask_question(self, context: str, question: str) -> str:
        """문서 내용을 바탕으로 질문에 답변"""
        prompt = f"""
        You are a helpful school administrative assistant. 
        Answer the following question based ONLY on the provided document content.
        If the answer is not in the document, say "문서에서 관련 내용을 찾을 수 없습니다."
        
        CRITICAL: Do not use any markdown formatting like asterisks(*) or hashes(#). 
        Provide the answer in clean plain text.

        Document Content:
        {context[:10000]}
        
        Question: {question}
        
        Answer (in Korean, helpful tone, plain text only):
        """
        response_text = self.model.generate_content(prompt).text.strip()
        # 특수 문자 제거 (마스크 처리된 * 등은 제외하고 형식상 들어가는 기호 위주)
        import re
        # **볼드** 나 # 제목 등을 제거하기 위해 re.sub 사용
        clean_text = re.sub(r'[*#]', '', response_text)
        return clean_text

    def compare_documents(self, text_a: str, text_b: str) -> str:
        """두 문서의 차이점 분석 (작년 vs 올해 등)"""
        prompt = f"""
        Analyze and compare these two school documents. 
        Highlight changes in budget, dates, deadlines, and major policy requirements.
        
        Document A (Previous/Reference):
        {text_a[:7000]}
        
        Document B (Current/New):
        {text_b[:7000]}
        
        Comparison Summary (in Korean, Markdown format):
        """
        return self.model.generate_content(prompt).text.strip()

    def analyze_document_comprehensive(self, content: str) -> dict:
        """메타데이터 추출과 분석을 한 번의 API 호출로 통합 (Quota 절약)"""
        import json
        import re
        from core.logger import logger
        
        system_prompt = """
        You are an elite school administrative assistant with high logical reasoning capabilities. 
        Analyze the document and return a STRICT JSON object.
        
        Guidelines:
        1. Reasoning: Don't just copy text. If an event is on March 3rd, infer that preparations usually end by the day before.
        2. Tables: Carefully parse merged cells and grids. Identify budget limits and person-in-charge accurately.
        3. Summary: Provide a 3-5 line executive summary in Korean focusing on 'What is this?' and 'Why is it important?'.
        4. Action Items: List specific tasks with deadlines or requirements.
        
        Output format:
        {
            "metadata": {
                "title": "Document Title",
                "date": "YYYY.MM.DD",
                "doc_number": "Number or empty"
            },
            "summary": "Reasoned executive summary in Korean",
            "keywords": ["key1", "key2"],
            "action_items": ["Specific Task (Deadline)", "Requirement"]
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
                "summary": "AI 분석 중 오류가 발생했습니다.",
                "keywords": [],
                "action_items": []
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
