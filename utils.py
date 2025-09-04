import hashlib
import requests
import json
import os


import log


def md5(text: str) -> str:
    m = hashlib.md5()
    m.update(text.encode("utf-8"))
    return m.hexdigest()


def push(title: str, content: str):
    """
    向指定的 API 端点发送一个 POST 请求来推送通知。
    :param title: 通知的标题。
    :param content: 通知的内容。
    """

    API_URL = os.getenv("UTILS_PUSH_URL")
    if not API_URL:
        log.warn("通知发送失败，UTILS_PUSH_URL 未配置。")
        return None
    headers = {"Content-Type": "application/json"}
    payload = {"title": title, "content": content}
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        log.success(f"通知发送完成，响应状态码 {response.status_code}")
    except Exception as e:
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


def ai(system: str, content: str) -> str:
    AI_TOKEN = os.getenv("UTILS_AI_TOKEN")
    AI_MODEL = os.getenv("UTILS_AI_MODEL")
    if not AI_TOKEN or not AI_MODEL:
        log.warn("AI 请求失败，UTILS_AI_TOKEN 或 UTILS_AI_MODEL 未配置。")
        return None

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AI_TOKEN}",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
        "stream": False,
    }

    try:
        response = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=32,
        )
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"]
    except Exception as e:
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")
        return None
