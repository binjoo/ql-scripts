import hashlib
from datetime import datetime


def md5(text: str) -> str:
    m = hashlib.md5()
    m.update(text.encode("utf-8"))
    return m.hexdigest()


def log(message, level="INFO"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    levelEmoji = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔍",
    }
    emoji = levelEmoji.get(level, "ℹ️")
    print(f"[{now}] {emoji} {message}")
