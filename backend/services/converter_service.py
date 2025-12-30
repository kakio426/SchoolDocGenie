import os
import pandas as pd
from core.logger import logger
import tempfile
import re
import zipfile
from xml.etree import ElementTree as ET

# HTML을 마크다운으로 바꿔주는 라이브러리 (pip install markdownify)
try:
    from markdownify import markdownify as md
    MARKDOWNIFY_AVAILABLE = True
except ImportError:
    MARKDOWNIFY_AVAILABLE = False

# Windows 전용 라이브러리 체크
try:
    from pyhwpx import Hwp
    HWP_AVAILABLE = True
except ImportError:
    HWP_AVAILABLE = False
    logger.warning("pyhwpx is not available. This works ONLY on Windows with HWP installed.")


class ConverterService:
    # [Phase 1: Backend Diet] 
    # HWP 변환은 이제 로컬 에이전트(Client)에서만 수행됩니다.
    # 서버에는 한글 프로그램이 없으므로 이 로직은 작동하지 않습니다.

    def convert_hwp(self, file_path: str) -> str:
        return "❌ [오류] HWP 변환은 로컬 에이전트(.exe)에서만 가능합니다. 파일을 직접 서버로 올리지 마세요."

    def convert_hwpx(self, file_path: str) -> str:
        return "❌ [오류] HWPX 변환은 로컬 에이전트(.exe)에서만 가능합니다."

    def convert_odt(self, file_path: str) -> str:
        """ODT 파일 변환 (LibreOffice 포맷)"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not MARKDOWNIFY_AVAILABLE:
            return "❌ [서버 오류] markdownify 라이브러리를 설치해주세요."
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # ODT는 content.xml에 본문이 있음
                if 'content.xml' not in zip_ref.namelist():
                    return "# ODT 변환 결과\n\ncontent.xml을 찾을 수 없습니다."
                
                xml_content = zip_ref.read('content.xml')
                
                # XML을 문자열로 변환 (간단한 태그 제거)
                root = ET.fromstring(xml_content)
                text_parts = []
                
                # 네임스페이스 처리
                ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
                
                # 모든 단락 추출
                for para in root.findall('.//text:p', ns):
                    para_text = ''.join(para.itertext())
                    if para_text.strip():
                        text_parts.append(para_text.strip())
                
                if not text_parts:
                    return "# ODT 변환 결과\n\n텍스트를 추출할 수 없습니다."
                
                full_text = "\n\n".join(text_parts)
                return f"# ODT 변환 결과\n\n{full_text}"
                
        except Exception as e:
            logger.error(f"ODT Error: {str(e)}")
            return f"ODT 변환 중 오류 발생: {str(e)}"

    def convert_document(self, file_path: str) -> str:
        """파일 확장자에 따라 적절한 변환 메서드 호출"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.hwp':
            return self.convert_hwp(file_path)
        elif ext == '.hwpx':
            return self.convert_hwpx(file_path)
        elif ext == '.odt':
            return self.convert_odt(file_path)
        elif ext in ['.xlsx', '.xls']:
            return self.convert_excel(file_path)
        else:
            return f"❌ 지원하지 않는 파일 형식입니다: {ext}"
