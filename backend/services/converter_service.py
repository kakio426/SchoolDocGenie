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
    def convert_hwp(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not HWP_AVAILABLE:
            return "❌ [서버 오류] Windows 환경 및 한글(HWP) 설치가 필요합니다."
        
        if not MARKDOWNIFY_AVAILABLE:
            return "❌ [서버 오류] markdownify 라이브러리를 설치해주세요."

        hwp = None
        temp_html_path = None
        
        try:
            # 1. HWP 인스턴스 실행 (백그라운드 모드)
            hwp = Hwp(visible=False) # 창 띄우지 않음
            hwp.open(file_path)
            
            # 2. 핵심 전략: 텍스트 추출이 아니라 'HTML'로 다른 이름으로 저장
            # 이렇게 하면 HWP가 알아서 표를 <table> 태그로 만들어줍니다.
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                temp_html_path = tmp.name
            
            # 포맷 "HTML"로 저장
            hwp.SaveAs(temp_html_path, "HTML")
            
            # 3. 저장된 HTML 파일 읽기 (인코딩 자동 감지 로직 추가)
            html_content = None
            # 윈도우 HWP는 보통 cp949로 저장되므로, utf-8 실패 시 cp949를 시도해야 함
            for enc in ['utf-8', 'cp949', 'euc-kr']:
                try:
                    with open(temp_html_path, 'r', encoding=enc) as f:
                        html_content = f.read()
                    break # 성공하면 루프 탈출
                except UnicodeDecodeError:
                    continue # 실패하면 다음 인코딩 시도
            
            if html_content is None:
                raise ValueError("변환된 HTML 파일의 인코딩을 인식할 수 없습니다.")
            
            # 4. HTML -> Markdown 변환 (표 구조 보존됨!)
            # strip=['a', 'img'] 링크나 이미지는 제거하고 텍스트와 표만 남김
            markdown_content = md(html_content, strip=['a', 'img'], heading_style="ATX")
            
            # 불필요한 공백 정리
            markdown_content = re.sub(r'\n\s*\n', '\n\n', markdown_content)
            
            return f"# HWP 변환 결과\n\n{markdown_content}"

        except Exception as e:
            logger.error(f"HWP Conversion Failed: {e}")
            return f"변환 실패: {str(e)}"
            
        finally:
            # 5. 정리 (파일 삭제 및 HWP 종료)
            if hwp:
                hwp.quit()
            
            if temp_html_path and os.path.exists(temp_html_path):
                try:
                    os.remove(temp_html_path)
                except:
                    pass

    def convert_excel(self, file_path: str) -> str:
        # 엑셀 변환 로직 (기존 유지하되 tabulate 의존성 확인)
        if not os.path.exists(file_path):
             raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # tabulate 라이브러리가 필요합니다 (pip install tabulate)
            with pd.ExcelFile(file_path) as xls:
                markdown_parts = []
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    # NaN 값 빈칸으로 처리
                    df = df.fillna("")
                    markdown_parts.append(f"### Sheet: {sheet_name}\n")
                    # to_markdown은 'tabulate' 라이브러리에 의존합니다.
                    markdown_parts.append(df.to_markdown(index=False))
                    markdown_parts.append("\n---\n")
            
            return "\n".join(markdown_parts)

        except ImportError:
             return "❌ [서버 오류] tabulate 라이브러리를 설치해주세요 (pip install tabulate)."
        except Exception as e:
            logger.error(f"Excel Error: {str(e)}")
            return f"Excel 변환 중 오류 발생: {str(e)}"

    def convert_hwpx(self, file_path: str) -> str:
        """HWPX 파일 변환 (ZIP 기반 XML 포맷)"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                # HWPX는 Contents/section*.xml 파일들에 본문이 있음
                text_parts = []
                
                for file_name in sorted(zip_ref.namelist()):
                    if file_name.startswith('Contents/section') and file_name.endswith('.xml'):
                        xml_content = zip_ref.read(file_name)
                        root = ET.fromstring(xml_content)
                        
                        # 모든 텍스트 노드 추출
                        for elem in root.iter():
                            if elem.text and elem.text.strip():
                                text_parts.append(elem.text.strip())
                
                if not text_parts:
                    return "# HWPX 변환 결과\n\n텍스트를 추출할 수 없습니다."
                
                full_text = "\n".join(text_parts)
                return f"# HWPX 변환 결과\n\n{full_text}"
                
        except Exception as e:
            logger.error(f"HWPX Error: {str(e)}")
            return f"HWPX 변환 중 오류 발생: {str(e)}"

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
