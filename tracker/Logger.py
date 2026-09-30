import logging
import os

LOG_FOLDER = "logs"
LOG_FILE = "expense_tracker.log"


# 1. Create the application logger that writes to logs/expense_tracker.log
def getLogger(folder: str = LOG_FOLDER) -> logging.Logger:
    logger = logging.getLogger("expense_tracker")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    os.makedirs(folder, exist_ok=True)
    handler = logging.FileHandler(os.path.join(folder, LOG_FILE), encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
