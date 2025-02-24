import os
import hashlib
from typing import Set, Dict
import sqlite3
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
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database"""
        self.db_path = 'uploaded_files.db'
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS uploaded_files (
                    project_id TEXT,
                    file_hash TEXT,
                    file_path TEXT,
                    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (project_id, file_hash)
                )
            ''')

    def _load_existing_files(self, project_id: str):
        """Load existing files from local SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT file_hash FROM uploaded_files WHERE project_id = ?', 
                    (project_id,)
                )
                self.uploaded_files = {row[0] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Warning: Could not load existing files from database: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash for a file"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def upload_file(self, file_path: str, project_id: str) -> Dict:
        """Upload a single file if it doesn't exist"""
        try:
            self._load_existing_files(project_id)

            file_hash = self.get_file_hash(file_path)
            
            if file_hash in self.uploaded_files:
                print(f"Skipping {file_path} (already exists)")
                return {"status": "already_exists"}

            url = f"{self.BASE_URL}/projects/{project_id}/sources"
            
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/octet-stream')}
                response = requests.post(url, headers=self.headers, files=files)
                
                # Store file info in database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        'INSERT INTO uploaded_files (project_id, file_hash, file_path) VALUES (?, ?, ?)',
                        (project_id, file_hash, file_path)
                    )
                
                self.uploaded_files.add(file_hash)
                print(f"Successfully uploaded: {file_path}")
                return {"status": "success", "response": response.text}

        except Exception as e:
            print(f"Error uploading {file_path}: {e}")
            return {"status": "error", "message": str(e)}

    def upload_folder(self, folder_path: str, project_id: str, recursive: bool = True):
        """Upload all files from a folder"""
        if not os.path.exists(folder_path):
            print(f"Error: Folder {folder_path} does not exist")
            return

        uploaded_count = 0
        skipped_count = 0
        error_count = 0

        for root, _, files in os.walk(folder_path):
            if not recursive and root != folder_path:
                continue

            for file in files:
                file_path = os.path.join(root, file)
                try:
                    result = self.upload_file(file_path, project_id)
                    if result["status"] == "success":
                        uploaded_count += 1
                    elif result["status"] == "already_exists":
                        skipped_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
                    error_count += 1

        print("\nUpload Summary:")
        print(f"Files uploaded: {uploaded_count}")
        print(f"Files skipped: {skipped_count}")
        print(f"Errors: {error_count}")

class FileWatcher(FileSystemEventHandler):
    def __init__(self, upload_service: FileUploadService, project_id: str):
        self.upload_service = upload_service
        self.project_id = project_id
    
    def on_created(self, event):
        if not event.is_directory:
            self.upload_service.upload_file(event.src_path, self.project_id)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.upload_service.upload_file(event.src_path, self.project_id)

def start_file_watcher(project_id: str):
    """Start watching folder for file changes"""
    upload_service = FileUploadService()
    event_handler = FileWatcher(upload_service, project_id)
    observer = Observer()
    observer.schedule(event_handler, settings.WATCH_FOLDER, recursive=False)
    observer.start()
    return observer
