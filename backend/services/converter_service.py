import os
import pandas as pd
from backend.core.logger import logger

try:
    from pyhwpx import Hwp
    HWP_AVAILABLE = True
except ImportError:
    HWP_AVAILABLE = False
    logger.warning("pyhwpx is not available. HWP conversion will be limited.")

class ConverterService:
    def convert_hwp(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not HWP_AVAILABLE:
            return "HWP 변환 라이브러리가 설치되지 않았습니다."
        
        try:
            hwp = Hwp()
            try:
                hwp.open(file_path)
                # 텍스트 추출 및 간단한 마크다운 변환 로직 (실제 구현 시 고도화 필요)
                text = hwp.get_text()
                return text
            finally:
                hwp.quit()
        except Exception as e:
            logger.error(f"Error converting HWP: {str(e)}")
            return f"HWP 변환 중 오류 발생: {str(e)}"

    def convert_excel(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # 모든 시트를 읽어서 마크다운으로 변환
            with pd.ExcelFile(file_path) as xls:
                markdown_parts = []
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                    markdown_parts.append(f"### Sheet: {sheet_name}\n")
                    markdown_parts.append(df.to_markdown(index=False))
                    markdown_parts.append("\n")
            
            return "\n".join(markdown_parts)

        except Exception as e:
            logger.error(f"Error converting Excel: {str(e)}")
            return f"Excel 변환 중 오류 발생: {str(e)}"
