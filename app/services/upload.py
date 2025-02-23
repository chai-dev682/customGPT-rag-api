import os
import hashlib
from typing import Set, Dict
import requests
from watchdog.observers import Observer
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
    
    def get_file_hash(self, file_path: str) -> str:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def upload_file(self, file_path: str, project_id: str) -> Dict:
        file_hash = self.get_file_hash(file_path)
        
        if file_hash in self.uploaded_files:
            return {"status": "already_exists"}
        
        url = f"{self.BASE_URL}/projects/{project_id}/sources"
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=self.headers, files=files)
            
            self.uploaded_files.add(file_hash)
            return response.text

class FileWatcher(FileSystemEventHandler):
    def __init__(self, upload_service: FileUploadService):
        self.upload_service = upload_service
    
    def on_created(self, event):
        if not event.is_directory:
            self.upload_service.upload_file(event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.upload_service.upload_file(event.src_path)

def start_file_watcher():
    upload_service = FileUploadService()
    event_handler = FileWatcher(upload_service)
    observer = Observer()
    observer.schedule(event_handler, settings.WATCH_FOLDER, recursive=False)
    observer.start()
    return observer
