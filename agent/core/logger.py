from loguru import logger
import sys

# Agent 전용 로거 설정 (파일 대신 표준 출력 중심)
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

def get_logger():
    return logger
