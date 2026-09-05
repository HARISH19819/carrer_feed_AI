import os
import shutil
from abc import ABC, abstractmethod
from typing import Optional

class BaseFileStorageService(ABC):
    @abstractmethod
    async def save_file(self, filename: str, content: bytes) -> str:
        """Save file and return storage reference/path."""
        pass

    @abstractmethod
    async def read_file(self, file_ref: str) -> bytes:
        """Read file content given storage reference."""
        pass

    @abstractmethod
    async def delete_file(self, file_ref: str) -> bool:
        """Delete file given storage reference."""
        pass

class LocalFileStorageService(BaseFileStorageService):
    def __init__(self, base_dir: str = "uploads/resumes"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    async def save_file(self, filename: str, content: bytes) -> str:
        safe_name = os.path.basename(filename)
        file_path = os.path.join(self.base_dir, safe_name)
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path

    async def read_file(self, file_ref: str) -> bytes:
        if not os.path.exists(file_ref):
            raise FileNotFoundError(f"File not found: {file_ref}")
        with open(file_ref, "rb") as f:
            return f.read()

    async def delete_file(self, file_ref: str) -> bool:
        try:
            if os.path.exists(file_ref):
                os.remove(file_ref)
                return True
            return False
        except Exception:
            return False

file_storage_service = LocalFileStorageService()
