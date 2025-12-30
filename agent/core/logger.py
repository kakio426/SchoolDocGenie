from loguru import logger
import sys

# Agent 전용 로거 설정
logger.remove()

# 콘솔이 있는 경우에만 표준 에러로 출력 (PyInstaller Windowed 모드에서는 sys.stderr가 None임)
if sys.stderr:
    logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")

# 디버깅을 위해 로컬 파일에도 기록 (exe 실행 시 로그 확인용)
logger.add("agent_debug.log", rotation="1 MB", level="DEBUG", encoding="utf-8")

def get_logger():
    return logger
