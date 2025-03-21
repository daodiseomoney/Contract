import os
from typing import BinaryIO
from werkzeug.utils import secure_filename

class LocalStorageGateway:
    def __init__(self):
        self.upload_folder = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(self.upload_folder, exist_ok=True)

    def store_file(self, file: BinaryIO) -> str:
        """Store BIM file locally and return file path"""
        filename = secure_filename(file.filename)
        file_path = os.path.join(self.upload_folder, filename)
        file.save(file_path)
        return file_path

    def retrieve_file(self, file_path: str) -> bytes:
        """Retrieve file content from local storage"""
        with open(file_path, 'rb') as f:
            return f.read()