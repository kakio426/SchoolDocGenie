import sys
import os
import time
import requests
import json
from services.converter_service import LocalConverterService
from masking import MaskingService
from core.logger import logger
from gui import AgentGUI

# Configuration
SERVER_URL = "http://127.0.0.1:8001/analyze/text"

def process_file(file_path, gui):
    """파일 변환, 마스킹, 프리뷰, 전송 전체 프로세스 처리"""
    try:
        filename = os.path.basename(file_path)
        logger.info(f"Processing File: {filename}")
        
        # 1. 파일 변환 (Local)
        # HWP 변환을 시도하고 실패 시 메시지 출력
        converter = LocalConverterService()
        raw_text = converter.convert_to_markdown(file_path)
        
        if not raw_text or raw_text.startswith("❌"):
            gui.show_message("오류", f"파일 변환에 실패했습니다: {filename}\n세부 내용: {raw_text}", is_error=True)
            return

        # 2. PII 마스킹 (Local)
        masker = MaskingService()
        masked_text = masker.mask_pii(raw_text)
        
        # 3. GUI 프리뷰 & 편집 (Human-in-the-loop)
        final_text = gui.show_preview(filename, masked_text)
        
        if not final_text:
            logger.info("User cancelled upload.")
            return # 사용자가 취소함

        # 4. 서버 전송
        payload = {
            "text": final_text,
            "filename": filename,
            "save": True
        }
        
        try:
            response = requests.post(SERVER_URL, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            doc_id = result.get("document_id")
            
            gui.show_message("성공", f"분석 및 전송이 완료되었습니다!\n\n문서 ID: {doc_id}\n제목: {result.get('analysis', {}).get('title')}\n\n웹 대시보드에서 실시간으로 확인됩니다.")
            logger.info(f"Upload Success. ID: {doc_id}")
            
        except requests.exceptions.ConnectionError:
            gui.show_message("전송 실패", "서버(Backend)에 연결할 수 없습니다.\n서버가 켜져 있는지 확인해주세요.", is_error=True)
        except Exception as e:
            gui.show_message("전송 오류", f"전송 중 오류가 발생했습니다: {str(e)}", is_error=True)

    except Exception as e:
        logger.error(f"Critical Error: {e}")
        gui.show_message("치명적 오류", f"작업 중 알 수 없는 오류가 발생했습니다.\n{str(e)}", is_error=True)

if __name__ == "__main__":
    # GUI 초기화
    app = AgentGUI()
    
    # 1. 법적 고지 (필수)
    if not app.show_disclaimer():
        sys.exit(0)

    # 2. 파일 처리
    target_file = None
    
    # Drag & Drop으로 실행된 경우 (인자가 있음)
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        process_file(target_file, app)
    else:
        # 그냥 실행된 경우 -> 파일 선택창 띄우기
        target_file = app.select_file()
        if target_file:
            process_file(target_file, app)
    
    # 별도 메인루프 없이 작업 종료 시 프로세스 종료
    sys.exit(0)
