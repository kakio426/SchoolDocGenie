import pandas as pd
import io
from fastapi.testclient import TestClient

def test_analyze_endpoint():
    from main import app
    
    with TestClient(app) as client:
        # Excel 파일 생성
        df = pd.DataFrame({"제목": ["2026 교육과정"], "내용": ["교육과정 운영 계획"]})
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        files = {"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = client.post("/analyze", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # 변환 결과
        assert "content" in data
        
        # AI 분석 결과
        assert "analysis" in data
        assert "title" in data["analysis"]
        assert "summary" in data["analysis"]
        assert "keywords" in data["analysis"]
