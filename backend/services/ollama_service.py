import requests
import json
from core.logger import logger

class OllamaService:
    def __init__(self, base_url="http://localhost:11434", model="llama3"):
        self.base_url = base_url
        # 강력한 오타 교정: 사용자가 'exaone3.5.2.4b'라고 입력해도 'exaone3.5:2.4b'로 자동 변환
        if "exaone" in model.lower() and ":" not in model and model.count(".") >= 2:
            self.model = model.replace("3.5.", "3.5:")
            logger.info(f"OllamaService auto-corrected model name: {model} -> {self.model}")
        else:
            self.model = model

    def ask_question(self, context: str, question: str) -> str:
        prompt = f"""
        당신은 학교 행정 전문가입니다. 
        사용자의 직책이나 상황을 고려하여 문서의 내용을 바탕으로 친절하게 답변해 주세요.
        
        [참조 문서 내용]
        {context[:8000]}
        
        [사용자 질문]
        {question}
        
        [답변 가이드]
        - 문서에 근거하여 답변하되, 질문자가 할 일을 구체적으로 짚어주세요.
        - 답변에 **, ##, * 과 같은 마크다운 강조 기호를 절대 사용하지 마세요. 
        - 깔끔하게 숫자(1, 2, 3)나 문장으로만 답변하세요.
        - 문서에 없는 내용은 "문서에서 관련 정보를 찾을 수 없습니다"라고 답하세요.
        - 답변은 한국어로 정중하게 작성하세요.
        """
        response = self._generate(prompt)
        # 마크다운 강조 기호(**)만 정교하게 제거 (단일 별표 마스킹은 유지)
        import re
        clean_response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
        # 기타 불필요한 기호 제거
        return clean_response.replace("__", "").replace("# ", "").strip()

    def analyze_document_comprehensive(self, content: str) -> dict:
        system_prompt = """
        당신은 학교 행정 전문가입니다. 아래 문서를 분석하여 반드시 지정된 JSON 형식으로만 응답하세요.
        
        주의사항:
        1. 반드시 { 로 시작해서 } 로 끝나는 유효한 JSON 데이터만 출력하세요.
        2. 다른 설명이나 인사말은 절대 하지 마세요.
        3. 날짜는 YYYY.MM.DD 형식을 지향하되, 없으면 '미기재'로 적으세요.
        4. action_items는 교사가 직접 수행해야 할 구체적인 업무와 기한을 포함하세요.

        출력 형식:
        {
            "metadata": { "title": "문서 제목", "date": "발행일", "doc_number": "문서번호" },
            "summary": "3줄 핵심 요약",
            "keywords": ["핵심어1", "핵심어2"],
            "action_items": ["수행과제1 (기한)", "수행과제2"]
        }
        """
        # 앞부분 6000자면 대부분의 핵심 정보가 포함됩니다.
        doc_content = content[:6000].strip()
        full_prompt = f"{system_prompt}\n\n[분석 대상 문서]\n{doc_content}"
        
        try:
            response_text = self._generate(full_prompt)
            # JSON 추출 로직 (더 정교하게)
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    # 따옴표 문제 등 간단한 수정 시도
                    fixed_json = json_match.group().replace("'", '"')
                    return json.loads(fixed_json)
            
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Ollama Analysis Critical Failed: {e}")
            return {
                "metadata": {"title": "문서 분석 실패", "date": "", "doc_number": ""},
                "summary": "상세 분석 중 오류가 발생했습니다. 로컬 AI 모델의 응답 형식이 올바르지 않습니다.",
                "keywords": ["오류"],
                "action_items": ["파일 내용을 조금 줄여서 다시 시도해 보시거나, Gemini API를 사용해 보세요."]
            }

    def compare_documents(self, text_a: str, text_b: str) -> str:
        prompt = f"""
        두 학교 문서를 비교 분석해 주세요. 
        예산, 날짜, 기한, 주요 정책 변경 사항을 중점적으로 살펴봐 주세요.
        
        문서 A (기존):
        {text_a[:7000]}
        
        문서 B (신규):
        {text_b[:7000]}
        
        비교 분석 결과 (한국어, 평문으로):
        """
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            # 대용량 문서 처리를 위해 500초까지 대기
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=500)
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except requests.exceptions.Timeout:
            logger.error("Ollama generation timed out (500s).")
            return "Ollama 분석 시간 초과: 문서가 너무 길거나 로컬 성능이 부족합니다."
        except Exception as e:
            logger.error(f"Ollama Request Failed at line 102: {e}")
            return f"Ollama 연결 오류: {str(e)}"
