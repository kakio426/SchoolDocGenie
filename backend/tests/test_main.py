from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

import pandas as pd
import io

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

def test_upload_excel():
    with TestClient(app) as client:
        # Create a simple Excel file in memory
        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        files = {"file": ("test.xlsx", excel_buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        assert "content" in response.json()
        assert "Sheet1" in response.json()["content"]
        assert "A" in response.json()["content"]
        assert "1" in response.json()["content"]



