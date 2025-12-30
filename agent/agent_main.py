import sys
import os
import time
import requests
import json
from services.converter_service import LocalConverterService
from masking import MaskingService
from core.logger import logger
from core.config_manager import ConfigManager
from core.history_manager import HistoryManager
from gui import AgentGUI

# Configuration - Stateless Proxy Endpoint
SERVER_URL = "http://127.0.0.1:8001/analyze/proxy"

def process_file(file_path, gui, config, history):
    """파일 변환, 마스킹, 프리뷰, 전송 전체 프로세스 처리"""
    try:
        filename = os.path.basename(file_path)
        logger.info(f"Processing File: {filename}")
        
        # API Key 확인
        api_key = config.get_api_key()
        if not api_key:
            api_key = gui.show_settings_popup()
            if api_key:
                config.set_api_key(api_key)
            else:
                return False

        # 1. 파일 변환 (Local)
        converter = LocalConverterService()
        raw_text = converter.convert_to_markdown(file_path)
        
        if not raw_text or raw_text.startswith("❌"):
            gui.show_message("오류", f"파일 변환에 실패했습니다: {filename}\n세부 내용: {raw_text}", is_error=True)
            return False

        # 2. PII 마스킹 (Local)
        masker = MaskingService()
        masked_text = masker.mask_pii(raw_text)
        
        # 3. GUI 프리뷰 & 편집 (Human-in-the-loop)
        final_text = gui.show_preview(filename, masked_text)
        
        if not final_text:
            logger.info("User cancelled upload.")
            return False

        # 4. 서버 전송 (Proxy Mode)
        payload = {
            "text": final_text,
            "filename": filename,
            "save": False
        }
        headers = {
            "x-user-gemini-key": api_key
        }
        
        try:
            logger.info("Sending to stateless proxy...")
            response = requests.post(SERVER_URL, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 401:
                gui.show_message("인증 실패", "API Key가 올바르지 않거나 만료되었습니다. 설정을 다시 확인해주세요.", is_error=True)
                new_key = gui.show_settings_popup(current_key=api_key)
                if new_key:
                    config.set_api_key(new_key)
                return False

            response.raise_for_status()
            result = response.json()
            
            # 5. 로컬 히스토리 저장
            history.add_record(filename, final_text, result.get("analysis", {}))
            
            gui.show_message("성공", f"분석이 완료되었습니다!\n\n제목: {result.get('analysis', {}).get('title')}\n\n데이터는 서버에 저장되지 않고 내 PC에만 기록되었습니다.")
            logger.info("Stateless Analysis Success.")
            return True
            
        except requests.exceptions.ConnectionError:
            gui.show_message("전송 실패", "서버(Backend)에 연결할 수 없습니다.\n서버가 켜져 있는지 확인해주세요.", is_error=True)
        except Exception as e:
            gui.show_message("분석 오류", f"분석 중 오류가 발생했습니다: {str(e)}", is_error=True)
            return False

    except Exception as e:
        logger.error(f"Critical Error: {e}")
        gui.show_message("치명적 오류", f"작업 중 알 수 없는 오류가 발생했습니다.\n{str(e)}", is_error=True)
        return False

if __name__ == "__main__":
    config = ConfigManager()
    history = HistoryManager()
    gui = AgentGUI()
    
    # 1. 법적 고지 (최초 1회 필수)
    if not gui.show_disclaimer():
        sys.exit(0)

    # 2. 핸들러 등록 (Chat & Compare)
    def chat_handler(content, query):
        try:
            headers = {"x-user-gemini-key": config.get_api_key()}
            res = requests.post("http://127.0.0.1:8001/analyze/chat", 
                                json={"text": content, "query": query}, headers=headers)
            res.raise_for_status()
            return res.json().get("answer", "응답을 받지 못했습니다.")
        except Exception as e:
            return f"오류 발생: {str(e)}"

    def compare_handler(text_a, text_b):
        try:
            headers = {"x-user-gemini-key": config.get_api_key()}
            res = requests.post("http://127.0.0.1:8001/analyze/compare", 
                                json={"text_a": text_a, "text_b": text_b}, headers=headers)
            res.raise_for_status()
            return res.json().get("comparison", "비교 분석을 수행하지 못했습니다.")
        except Exception as e:
            return f"분석 중 오류 발생: {str(e)}"

    gui.chat_handler = chat_handler
    gui.compare_handler = compare_handler

    # 3. 메인 루프
    if len(sys.argv) > 1:
        # 파일이 파라미터로 넘어온 경우 (Drag & Drop) 바로 처리 후 종료
        process_file(sys.argv[1], gui, config, history)
        sys.exit(0)
    else:
        # 일반 실행 시 메뉴 표시
        while True:
            choice = gui.show_main_menu()
            
            if choice == 'process':
                fpath = gui.select_file()
                if fpath:
                    process_file(fpath, gui, config, history)
            elif choice == 'history':
                gui.show_history(history.get_history())
            elif choice == 'settings':
                new_key = gui.show_settings_popup(current_key=config.get_api_key())
                if new_key:
                    config.set_api_key(new_key)
            else: # exit
                break
        
    sys.exit(0)
