from datetime import datetime


def info(message, emoji="ℹ️"):
    printf(message, emoji)


def success(message, emoji="✅"):
    printf(message, emoji)


def warn(message, emoji="⚠️"):
    printf(message, emoji)


def error(message, emoji="❌"):
    printf(message, emoji)


def debug(message, emoji="🔍"):
    printf(message, emoji)


def printf(message, emoji):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {emoji} {message}")
