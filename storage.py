import json
import os
from typing import List
from logger import get_logger

logger = get_logger(__name__)

class EmailStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._emails = self._load()

    def _load(self) -> List[str]:
        if not os.path.exists(self.file_path):
            self._save([])
            return []
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"The {self.file_path} file is corrupted. Resetting the list.")
            self._save([])
            return []

    def _save(self, emails: List[str]) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(emails, f, indent=4)

    def add(self, email: str) -> bool:
        if email not in self._emails:
            self._emails.append(email)
            self._save(self._emails)
            return True
        return False

    def remove(self, email: str) -> bool:
        if email in self._emails:
            self._emails.remove(email)
            self._save(self._emails)
            return True
        return False

    def get_all(self) -> List[str]:
        return self._emails.copy()

class ProcessedStorage:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._processed_ids = set(self._load())

    def _load(self) -> List[str]:
        if not os.path.exists(self.file_path):
            self._save(set())
            return []
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            logger.error(f"The {self.file_path} file is corrupted. Resetting.")
            self._save(set())
            return []

    def _save(self, ids: set) -> None:
        with open(self.file_path, 'w') as f:
            json.dump(list(ids), f, indent=4)

    def is_processed(self, msg_id: str) -> bool:
        return msg_id in self._processed_ids

    def mark_processed(self, msg_id: str) -> None:
        self._processed_ids.add(msg_id)
        self._save(self._processed_ids)
