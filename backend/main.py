from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import shutil
import os

# .env 파일 명시적 로드
from pathlib import Path
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

import uuid
from services.converter_service import ConverterService

app = FastAPI(title="School-Doc Genie API")
converter = ConverterService()


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
        
        # 통합 변환 메서드 사용
        content = converter.convert_document(temp_path)
            
        return {"filename": file.filename, "content": content}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Removed temp file: {temp_path}")


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
        
        # 1. 파일 변환 (통합 메서드 사용)
        content = converter.convert_document(temp_path)
        
        # 2. AI 분석
        from services.gemini_service import GeminiService
        gemini = GeminiService()
        
        # 메타데이터 추출
        metadata = gemini.extract_metadata(content)
        
        # 문서 내용 분석
        analysis_result = gemini.analyze_document(content)
        
        document_id = None
        if save:
            try:
                from services.supabase_service import SupabaseService
                supabase = SupabaseService()
                
                # 메타데이터 업데이트
                doc_metadata = {
                    "filename": file.filename,
                    "title": metadata.get("title", ""),
                    "date": metadata.get("date", ""),
                    "doc_number": metadata.get("doc_number", ""),
                    "keywords": analysis_result.get("keywords", [])
                }
                
                document_id = supabase.store_document(
                    content=content,
                    metadata=doc_metadata,
                    summary=analysis_result.get("summary", "")
                )
            except Exception as e:
                logger.error(f"Failed to save document: {e}")
                # 저장은 실패해도 분석 결과는 반환
        
        return {
            "filename": file.filename,
            "content": content,
            "document_id": document_id,
            "analysis": {
                "title": metadata.get("title", "제목 없음"),
                "date": metadata.get("date", ""),
                "doc_number": metadata.get("doc_number", ""),
                "summary": analysis_result.get("summary", ""),
                "keywords": analysis_result.get("keywords", []),
                "action_items": analysis_result.get("action_items", [])
            }
        }
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
