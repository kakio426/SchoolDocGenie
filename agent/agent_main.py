import sys
import os
import requests
import threading
from tkinter import messagebox
from services.converter_service import LocalConverterService
from services.monitor_service import FolderMonitorService
from masking import MaskingService
from core.logger import logger
from core.config_manager import ConfigManager
from core.history_manager import HistoryManager
from gui import AgentGUI

# Configuration
BASE_BACKEND_URL = "http://127.0.0.1:8001"
PROXY_URL = f"{BASE_BACKEND_URL}/analyze/proxy"

def get_headers(config):
    provider = config.get_config("ai_provider", "Gemini 3.0 Flash").lower()
    
    # 모델명 오타 교정 안전장치
    model_name = config.get_config("ollama_model", "")
    if "ollama" in provider and "exaone" in model_name.lower() and ":" not in model_name and model_name.count(".") >= 2:
        model_name = model_name.replace("3.5.", "3.5:")
        logger.info(f"Header auto-correction: {config.get_config('ollama_model')} -> {model_name}")

    headers = {
        "x-ai-provider": "ollama" if "ollama" in provider else "gemini",
        "x-user-gemini-key": config.get_api_key(),
        "x-ollama-url": config.get_config("ollama_url"),
        "x-ollama-model": model_name
    }
    return headers

def process_file(file_path, gui, config, history, auto_mode=False):
    """파일 변환, 마스킹, 프리뷰, 전송 전체 프로세스 처리"""
    try:
        filename = os.path.basename(file_path)
        logger.info(f"Processing File: {filename}")
        
        # 1. 파일 변환 (Local)
        converter = LocalConverterService()
        raw_text = converter.convert_to_markdown(file_path)
        
        if not raw_text or raw_text.startswith("❌"):
            if not auto_mode:
                gui.show_message("오류", f"파일 변환에 실패했습니다: {filename}\n세부 내용: {raw_text}", is_error=True)
            return False

        # 중복 체크
        existing_records = history.get_history()
        for record in existing_records:
            if record.get("full_content") == raw_text:
                if not auto_mode:
                    from threading import Event
                    overlap_event = Event()
                    user_ok = {"val": False}
                    
                    def check_overlap():
                        user_ok["val"] = messagebox.askyesno("중복 알림", f"'{filename}'은 이미 분석된 기록이 있습니다. 다시 보시겠습니까?")
                        overlap_event.set()
                        
                    gui.root.after(0, check_overlap)
                    overlap_event.wait()
                    
                    if user_ok["val"]:
                        gui.root.after(0, lambda: gui._show_record_detail(record))
                    return True
                else: 
                    return True

        # 2. PII 마스킹 (Local)
        masker = MaskingService()
        masked_text = masker.mask_pii(raw_text)
        
        # 3. GUI 프리뷰 (Auto 모드면 건너뜀)
        final_text = masked_text
        if not auto_mode:
            # 프리뷰는 사용자 입력을 기다려야 하므로, 메인 스레드에서 실행하고 완료를 기다려야 함
            # 여기서는 편의상 간단한 큐나 이벤트를 쓰지 않고 직접 호출 시 Thread-safe하게 처리
            # (사실 CTkTopLevel은 메인 스레드에서 생성되어야 함)
            from threading import Event
            preview_event = Event()
            res = {"text": masked_text}
            
            def open_preview():
                res["text"] = gui.show_preview(filename, masked_text)
                preview_event.set()
                
            gui.root.after(0, open_preview)
            preview_event.wait() # 프리뷰가 닫힐 때까지 스레드 대기
            final_text = res["text"]
            
            if not final_text:
                return False

        # 4. 서버 전송 및 진행 상태 알림
        current_provider = config.get_config("ai_provider", "Gemini API")
        gui.root.after(0, lambda: gui.set_analysis_progress(filename, len(final_text), True, current_provider))
        
        payload = {"text": final_text, "filename": filename, "save": False}
        headers = get_headers(config)
        
        try:
            response = requests.post(PROXY_URL, json=payload, headers=headers, timeout=300)
            response.raise_for_status()
            result = response.json()
            
            analysis_data = result.get("analysis", {})
            
            # 분석 실패 감지 (제목이 없거나 오류 키워드 포함 시)
            if not analysis_data or "실패" in analysis_data.get("title", "") or not analysis_data.get("title"):
                 error_msg = analysis_data.get("summary", "서버로부터 유효한 분석 결과를 받지 못했습니다.")
                 if not auto_mode:
                     gui.show_message("분석 실패", f"AI 분석이 실패했습니다.\n\n사유: {error_msg}\n\nOllama 모델명이나 서버 상태를 확인해주세요.", is_error=True)
                 return False

            # 5. 로컬 히스토리 저장
            history.add_record(filename, final_text, analysis_data)
            
            gui.root.after(0, lambda: gui.set_analysis_progress(filename, is_start=False))
            
            if not auto_mode:
                gui.show_message("성공", f"분석 완료: {analysis_data.get('title')}")
            else:
                logger.info(f"Auto Processing Success: {filename}")
            return True
            
        except Exception as e:
            if not auto_mode:
                gui.root.after(0, lambda: gui.show_message("분석 오류", f"분석 중 오류가 발생했습니다: {str(e)}", is_error=True))
            return False

    except Exception as e:
        logger.error(f"Critical Error: {e}")
        return False

if __name__ == "__main__":
    config = ConfigManager()
    history = HistoryManager()
    gui = AgentGUI(config_manager=config)
    
    # 1. 법적 고지 (최초 1회 필수)
    if not config.get_config("disclaimer_agreed"):
        if gui.show_disclaimer():
            config.set_config("disclaimer_agreed", True)
        else:
            sys.exit(0)

    # 2. 핸들러 등록
    def chat_handler(content, query):
        try:
            res = requests.post(f"{BASE_BACKEND_URL}/analyze/chat", 
                                json={"text": content, "query": query}, headers=get_headers(config))
            return res.json().get("answer", "응답 실패")
        except Exception as e: return str(e)

    def compare_handler(text_a, text_b):
        try:
            res = requests.post(f"{BASE_BACKEND_URL}/analyze/compare",
                                json={"text_a": text_a, "text_b": text_b}, headers=get_headers(config))
            return res.json().get("comparison", "비교 분석 실패")
        except Exception as e: return str(e)

    def batch_handler(file_paths):
        def run():
            success = 0
            for fp in file_paths:
                if process_file(fp, gui, config, history, auto_mode=True):
                    success += 1
            gui.root.after(0, lambda: messagebox.showinfo("일괄 처리 완료", f"{len(file_paths)}개 중 {success}개 분석 성공!"))
        threading.Thread(target=run, daemon=True).start()

    monitor_service = FolderMonitorService(lambda fp: process_file(fp, gui, config, history, auto_mode=True))

    gui.chat_handler = chat_handler
    gui.compare_handler = compare_handler
    gui.batch_handler = batch_handler
    gui.chat_save_handler = history.add_chat_message # 채팅 저장 핸들러 추가
    gui.history_fetcher = history.get_history
    gui.delete_handler = history.delete_record
    gui.monitor_start_handler = monitor_service.start
    gui.monitor_stop_handler = monitor_service.stop

    import threading
    
    # Drag & Drop Support (argv)
    if len(sys.argv) > 1:
        process_file(sys.argv[1], gui, config, history)

    # 메인 루프 시작
    gui.root.mainloop()
    monitor_service.stop()
    sys.exit(0)
