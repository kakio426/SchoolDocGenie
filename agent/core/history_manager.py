import json
import os
from datetime import datetime
from pathlib import Path

class HistoryManager:
    """분석 기록을 로컬 JSON 파일에 저장하고 관리하는 클래스"""
    
    def __init__(self, history_path: Path = None):
        if history_path:
            self.history_path = history_path
        else:
            self.history_path = Path("analysis_history.json")
            
        if not self.history_path.exists():
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def add_record(self, filename: str, content: str, analysis: dict):
        """새로운 분석 기록 추가"""
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            history = []
            
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename": filename,
            "content_snippet": content[:500] + "...", # 프리뷰용
            "full_content": content,
            "analysis": analysis
        }
        
        # 목록 맨 앞에 추가
        history.insert(0, record)
        
        # 최대 100개까지만 유지 (성능 및 용량 관리)
        history = history[:100]
        
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)

    def add_chat_message(self, timestamp: str, filename: str, query: str, answer: str):
        """특정 기록에 채팅 내역 추가"""
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            # 파일명과 시간으로 해당 기록 찾기
            for record in history:
                if record.get("filename") == filename and record.get("timestamp") == timestamp:
                    if "chat_history" not in record:
                        record["chat_history"] = []
                    record["chat_history"].append({
                        "query": query,
                        "answer": answer,
                        "time": datetime.now().strftime("%H:%M:%S")
                    })
                    break
            
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"채팅 저장 오류: {e}")

    def delete_record(self, timestamp: str, filename: str) -> bool:
        """분석 기록 삭제"""
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                history = json.load(f)
            
            original_len = len(history)
            # 타임스탬프와 파일명이 모두 일치하는 항목 제외
            history = [r for r in history if not (r.get("timestamp") == timestamp and r.get("filename") == filename)]
            
            if len(history) < original_len:
                with open(self.history_path, "w", encoding="utf-8") as f:
                    json.dump(history, f, ensure_ascii=False, indent=4)
                return True
            return False
        except Exception as e:
            print(f"기록 삭제 오류: {e}")
            return False

    def get_history(self) -> list:
        """전체 기록 반환"""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
