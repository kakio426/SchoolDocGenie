
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_analyze_text_endpoint():
    """텍스트 기반 분석 엔드포인트 테스트 (Hybrid Mode)"""
    test_data = {
        "text": "# 테스트 공문\n\n이 문서는 2026학년도 학교 운영 계획에 대한 내용을 담고 있습니다.",
        "filename": "test_memo.md",
        "save": False  # 테스트 시 DB 저장은 끔
    }
    
    response = client.post("/analyze/text", json=test_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["filename"] == "test_memo.md"
    assert "analysis" in data
    assert "summary" in data["analysis"]
    assert "title" in data["analysis"]
    print(f"\nAI 분석 제목: {data['analysis']['title']}")

def test_analyze_text_missing_fields():
    """필수 필드 누락 시 에러 처리 테스트"""
    incomplete_data = {
        "filename": "fail.md"
    }
    
    response = client.post("/analyze/text", json=incomplete_data)
    # Pydantic validation error (422)
    assert response.status_code == 422
