
import requests

try:
    url = "http://127.0.0.1:8001/analyze/text"
    payload = {
        "text": "이 공문은 테스트용입니다. 중등 진로전담교사 배치 관련 내용을 포함하고 있습니다.",
        "filename": "test_script.md",
        "save": True
    }
    response = requests.post(url, json=payload, timeout=20)
    data = response.json()
    print(f"Status Code: {response.status_code}")
    print(f"Document ID: {data.get('document_id')}")
    print(f"Title: {data.get('analysis', {}).get('title')}")
except Exception as e:
    print(f"Error: {e}")
