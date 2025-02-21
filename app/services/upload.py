from typing import Set
from watchdog.events import FileSystemEventHandler
from app.core.config import settings

class FileUploadService:
    BASE_URL = settings.BASE_URL
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {settings.CUSTOMGPT_API_KEY}",
            "Content-Type": "application/json"
        }
        self.uploaded_files: Set[str] = set()

class FileWatcher(FileSystemEventHandler):
    def __init__(self, upload_service: FileUploadService):
        self.upload_service = upload_service
        