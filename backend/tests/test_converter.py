import pytest
from backend.services.converter_service import ConverterService
import os

def test_hwp_to_markdown_basic():
    # 이 테스트는 실제 HWP 파일이 없으면 실패하거나 Mocking이 필요함
    # 여기서는 인터페이스 검증 우선
    service = ConverterService()
    
    # HWP 파일이 없는 경우 에러 처리 검증
    with pytest.raises(FileNotFoundError):
        service.convert_hwp("non_existent.hwp")

def test_excel_to_markdown_basic():
    service = ConverterService()
    
    # 임시 파일 생성 후 테스트할 수 있지만, 일단 인터페이스 실패 확인
    with pytest.raises(FileNotFoundError):
        service.convert_excel("non_existent.xlsx")
