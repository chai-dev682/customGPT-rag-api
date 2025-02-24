import argparse
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.upload import FileUploadService


def main():
    parser = argparse.ArgumentParser(description='Upload files to CustomGPT project')
    parser.add_argument('folder_path', help='Path to the folder containing files to upload')
    parser.add_argument('project_id', help='CustomGPT project ID')
    parser.add_argument('--no-recursive', action='store_true', help='Disable recursive folder scanning')
    
    args = parser.parse_args()

    uploader = FileUploadService()
    uploader.upload_folder(args.folder_path, args.project_id, recursive=not args.no_recursive)

if __name__ == "__main__":
    main()