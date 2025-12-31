from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import shutil
import os

# .env 파일 명시적 로드 (절대 경로 사용)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

from pydantic import BaseModel
from typing import Optional

class TextAnalysisRequest(BaseModel):
    text: str
    filename: Optional[str] = "unnamed.md"
    save: Optional[bool] = True

import uuid
from services.converter_service import ConverterService

app = FastAPI(title="School-Doc Genie API")

def get_ai_service(provider: str, gemini_key: str = None, ollama_url: str = None, ollama_model: str = None):
    if provider == "ollama":
        from services.ollama_service import OllamaService
        return OllamaService(
            base_url=ollama_url or "http://localhost:11434",
            model=ollama_model or "llama3"
        )
    else:
        from services.gemini_service import GeminiService
        return GeminiService(api_key=gemini_key)


from core.logger import logger



origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    logger.info("Health check endpoint called")
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application started")
    os.makedirs("temp", exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    logger.info(f"Uploading file: {file.filename}")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".hwp", ".hwpx", ".odt", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Only HWP, HWPX, ODT, and Excel files are supported")
    
    temp_path = f"temp/{uuid.uuid4()}{file_ext}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 통합 변환 메서드 사용 (지연 로드)
        converter = ConverterService()
        content = converter.convert_document(temp_path)
            
        return {"filename": file.filename, "content": content}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {"error": str(e)}
    finally:
            os.remove(temp_path)
            logger.info(f"Removed temp file: {temp_path}")


async def perform_analysis(content: str, filename: str, save: bool):
    """공통 분석 로직 (텍스트 수신 -> AI 통합 분석 (제목/날짜/키워드) -> 저장)"""
    from services.gemini_service import GeminiService
    gemini = GeminiService()
    
    # 통합 분석 실행 (메타데이터 + 키워드)
    logger.info("Step 2: Performing AI metadata/keyword extraction...")
    full_result = gemini.analyze_document_comprehensive(content)
    
    metadata = full_result.get("metadata", {})
    keywords = full_result.get("keywords", [])
    
    document_id = None
    if save:
        try:
            logger.info("Step 3: Archiving to Supabase...")
            from services.supabase_service import SupabaseService
            supabase = SupabaseService()
            
            doc_metadata = {
                "filename": filename,
                "title": metadata.get("title", ""),
                "date": metadata.get("date", ""),
                "doc_number": metadata.get("doc_number", ""),
                "keywords": keywords
            }
            
            # 요약은 빈칸으로 저장
            document_id = supabase.store_document(
                content=content,
                metadata=doc_metadata,
                summary=""
            )
            logger.info(f"Archived successfully. ID: {document_id}")
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            
    return {
        "filename": filename,
        "content": content,
        "document_id": document_id,
        "analysis": {
            "title": metadata.get("title", "제목 없음"),
            "date": metadata.get("date", ""),
            "doc_number": metadata.get("doc_number", ""),
            "summary": "", 
            "keywords": keywords,
            "action_items": []
        }
    }


@app.post("/analyze/text")
async def analyze_text(request: TextAnalysisRequest):
    """Hybrid Mode: 로컬 에이전트로부터 텍스트를 직접 받아서 분석"""
    logger.info(f"Received text analysis request for: {request.filename}")
    try:
        result = await perform_analysis(request.text, request.filename, request.save)
        return result
    except ValueError as ve:
        if "AI 사용량" in str(ve):
            logger.warning(f"Quota Exceeded: {ve}")
            raise HTTPException(status_code=429, detail=str(ve))
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze/proxy")
async def analyze_proxy(
    request: TextAnalysisRequest,
    x_ai_provider: Optional[str] = Header("gemini"),
    x_user_gemini_key: Optional[str] = Header(None),
    x_ollama_url: Optional[str] = Header(None),
    x_ollama_model: Optional[str] = Header(None)
):
    """Stateless Mode: 사용자 선택 API/Local 모델을 사용하여 분석만 수행하고 저장하지 않음"""
    if x_ai_provider == "gemini" and not x_user_gemini_key:
        raise HTTPException(status_code=401, detail="Gemini API Key가 필요합니다.")
    
    logger.info(f"Stateless Proxy: Analyzing {request.filename} via {x_ai_provider}")
    
    try:
        ai_service = get_ai_service(x_ai_provider, x_user_gemini_key, x_ollama_url, x_ollama_model)
        
        # 통합 분석 실행
        full_result = ai_service.analyze_document_comprehensive(request.text)
        
        metadata = full_result.get("metadata", {})
        keywords = full_result.get("keywords", [])
        
        return {
            "filename": request.filename,
            "content": request.text,
            "document_id": "stateless-no-id",
            "analysis": {
                "title": metadata.get("title", "제목 없음"),
                "date": metadata.get("date", ""),
                "doc_number": metadata.get("doc_number", ""),
                "summary": full_result.get("summary", ""), 
                "keywords": keywords,
                "action_items": full_result.get("action_items", [])
            }
        }
    except ValueError as ve:
        if "사용량" in str(ve):
            raise HTTPException(status_code=429, detail=str(ve))
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        logger.error(f"Proxy Analysis Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),
    save: bool = Form(True) # 기본값 True, Form 데이터로 받음
):
    logger.info(f"Analyzing file: {file.filename}, save={save}")
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in [".hwp", ".hwpx", ".odt", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Only HWP, HWPX, ODT, and Excel files are supported")
    
    temp_path = f"temp/{uuid.uuid4()}{file_ext}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. 파일 변환 (지연 로드)
        converter = ConverterService()
        content = converter.convert_document(temp_path)
        
        # 2. 공통 분석 로직 실행
        return await perform_analysis(content, file.filename, save)
    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Removed temp file: {temp_path}")


@app.get("/search")
async def search_documents(q: str):
    logger.info(f"Searching documents: {q}")
    
    try:
        from services.supabase_service import SupabaseService
        supabase = SupabaseService()
        
        results = supabase.search_documents(q)
        return {"results": results}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/chat")
async def analyze_chat(
    request: dict, # { "text": "...", "query": "..." }
    x_ai_provider: Optional[str] = Header("gemini"),
    x_user_gemini_key: Optional[str] = Header(None),
    x_ollama_url: Optional[str] = Header(None),
    x_ollama_model: Optional[str] = Header(None)
):
    """문서 기반 질의응답 (Stateless)"""
    ai_service = get_ai_service(x_ai_provider, x_user_gemini_key, x_ollama_url, x_ollama_model)
    answer = ai_service.ask_question(request.get("text", ""), request.get("query", ""))
    return {"answer": answer}

@app.post("/analyze/compare")
async def analyze_compare(
    request: dict, # { "text_a": "...", "text_b": "..." }
    x_ai_provider: Optional[str] = Header("gemini"),
    x_user_gemini_key: Optional[str] = Header(None),
    x_ollama_url: Optional[str] = Header(None),
    x_ollama_model: Optional[str] = Header(None)
):
    """두 문서 비교 분석 (Stateless)"""
    ai_service = get_ai_service(x_ai_provider, x_user_gemini_key, x_ollama_url, x_ollama_model)
    comparison = ai_service.compare_documents(request.get("text_a", ""), request.get("text_b", ""))
    return {"comparison": comparison}

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print(">>> School-Doc Genie Backend v1.2 (Timeout 500s) 시작")
    print("="*50 + "\n")
    uvicorn.run(app, host="127.0.0.1", port=8001)
