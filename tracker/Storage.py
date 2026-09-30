import json
import os
from datetime import datetime

from tracker.Logger import getLogger


# JSON file storage with atomic saves
class JsonStorage:
    def __init__(self, fileName: str):
        self.fileName = fileName
        self.logger = getLogger()
        self.data = self.load()

    def emptyData(self) -> dict:
        return {"nextId": 1, "expenses": [], "budgets": {}}

    def load(self) -> dict:
        if not os.path.exists(self.fileName):
            return self.emptyData()
        try:
            with open(self.fileName, "r", encoding="utf-8") as newFile:
                data = json.load(newFile)
            if not all(key in data for key in ("nextId", "expenses", "budgets")):
                raise ValueError("Storage file is missing required fields.")
            return data
        except (json.JSONDecodeError, ValueError) as e:
            backupName = f"{self.fileName}.corrupt-{datetime.now():%Y%m%d%H%M%S}"
            os.replace(self.fileName, backupName)
            self.logger.error(f"Storage file was unreadable ({e}). Moved to {backupName}.")
            return self.emptyData()

    def save(self) -> None:
        folder = os.path.dirname(self.fileName)
        if folder:
            os.makedirs(folder, exist_ok=True)
        tempName = f"{self.fileName}.tmp"
        with open(tempName, "w", encoding="utf-8") as newFile:
            json.dump(self.data, newFile, indent=2)
        os.replace(tempName, self.fileName)
