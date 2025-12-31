import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.logger import logger

class FolderMonitorHandler(FileSystemEventHandler):
    def __init__(self, callback, extensions=None):
        self.callback = callback
        self.extensions = extensions or ['.hwp', '.hwpx', '.odt', '.xlsx', '.xls']

    def on_created(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in self.extensions:
            logger.info(f"New file detected: {event.src_path}")
            # 파일이 완전히 저장될 때까지 잠시 대기
            time.sleep(1)
            self.callback(event.src_path)

class FolderMonitorService:
    def __init__(self, callback):
        self.callback = callback
        self.observer = None
        self.watch_path = None

    def start(self, path):
        if self.observer:
            self.stop()
        
        if not os.path.exists(path):
            logger.error(f"Watch path does not exist: {path}")
            return False

        self.watch_path = path
        event_handler = FolderMonitorHandler(self.callback)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_path, recursive=False)
        self.observer.start()
        logger.info(f"Folder monitor started on: {path}")
        return True

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Folder monitor stopped.")
