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

    def get_history(self) -> list:
        """전체 기록 반환"""
        if not self.history_path.exists():
            return []
        try:
            with open(self.history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
