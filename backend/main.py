from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from backend.services.converter_service import ConverterService

app = FastAPI(title="School-Doc Genie API")
converter = ConverterService()


from backend.core.logger import logger


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
    if file_ext not in [".hwp", ".xlsx", ".xls"]:
        raise HTTPException(status_code=400, detail="Only HWP and Excel files are supported")
    
    temp_path = f"temp/{uuid.uuid4()}{file_ext}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        if file_ext == ".hwp":
            content = converter.convert_hwp(temp_path)
        else:
            content = converter.convert_excel(temp_path)
            
        return {"filename": file.filename, "content": content}
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
            logger.info(f"Removed temp file: {temp_path}")


