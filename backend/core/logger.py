from loguru import logger
import sys

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("logs/app.log", rotation="10 MB", level="DEBUG")

def get_logger():
    return logger
