import os
import pandas as pd
from core.logger import logger
import tempfile
import re
import zipfile
from xml.etree import ElementTree as ET

# HTML을 마크다운으로 바꿔주는 라이브러리
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
    logger.warning("pyhwpx is not available. Please install HWP on Windows.")


class LocalConverterService:
    def convert_to_markdown(self, file_path: str) -> str:
        """agent_main.py에서 기대하는 통합 변환 메서드"""
        return self.convert_document(file_path)

    def convert_hwp(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not HWP_AVAILABLE:
            return "❌ [오류] Windows 환경 및 한글(HWP) 설치가 필요합니다."
        
        if not MARKDOWNIFY_AVAILABLE:
            return "❌ [오류] markdownify 라이브러리가 필요합니다."

        hwp = None
        temp_html_path = None
        
        try:
            hwp = Hwp(visible=False)
            hwp.open(file_path)
            
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                temp_html_path = tmp.name
            
            hwp.SaveAs(temp_html_path, "HTML")
            
            html_content = None
            for enc in ['utf-8', 'cp949', 'euc-kr']:
                try:
                    with open(temp_html_path, 'r', encoding=enc) as f:
                        html_content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if html_content is None:
                raise ValueError("Could not decode HTML file.")
            
            markdown_content = md(html_content, strip=['a', 'img'], heading_style="ATX")
            markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
            
            return f"# HWP 변환 결과\n\n{markdown_content}"

        except Exception as e:
            logger.error(f"HWP Conversion Failed: {e}")
            return f"변환 실패: {str(e)}"
            
        finally:
            if hwp: hwp.quit()
            if temp_html_path and os.path.exists(temp_html_path):
                try: os.remove(temp_html_path)
                except: pass

    def convert_excel(self, file_path: str) -> str:
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with pd.ExcelFile(file_path) as xls:
                markdown_parts = []
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    df = df.fillna("")
                    markdown_parts.append(f"### Sheet: {sheet_name}\n")
                    markdown_parts.append(df.to_markdown(index=False))
                    markdown_parts.append("\n---\n")
            return "\n".join(markdown_parts)
        except Exception as e:
            logger.error(f"Excel Error: {str(e)}")
            return f"Excel Error: {str(e)}"

    def convert_hwpx(self, file_path: str) -> str:
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                text_parts = []
                for file_name in sorted(zip_ref.namelist()):
                    if file_name.startswith('Contents/section') and file_name.endswith('.xml'):
                        xml_content = zip_ref.read(file_name)
                        root = ET.fromstring(xml_content)
                        for elem in root.iter():
                            if elem.text and elem.text.strip():
                                text_parts.append(elem.text.strip())
                return f"# HWPX 변환 결과\n\n" + "\n".join(text_parts) if text_parts else "텍스트 추출 불가"
        except Exception as e:
            return f"HWPX Error: {str(e)}"

    def convert_odt(self, file_path: str) -> str:
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                if 'content.xml' not in zip_ref.namelist(): return "content.xml not found"
                xml_content = zip_ref.read('content.xml')
                root = ET.fromstring(xml_content)
                text_parts = []
                ns = {'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
                for para in root.findall('.//text:p', ns):
                    para_text = ''.join(para.itertext())
                    if para_text.strip(): text_parts.append(para_text.strip())
                return f"# ODT 변환 결과\n\n" + "\n\n".join(text_parts) if text_parts else "텍스트 추출 불가"
        except Exception as e:
            return f"ODT Error: {str(e)}"

    def convert_document(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.hwp': return self.convert_hwp(file_path)
        elif ext == '.hwpx': return self.convert_hwpx(file_path)
        elif ext == '.odt': return self.convert_odt(file_path)
        elif ext in ['.xlsx', '.xls']: return self.convert_excel(file_path)
        return f"Unsupported: {ext}"
