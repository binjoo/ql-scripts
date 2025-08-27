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

        try:
            log.success("服务器响应：", response.json())
        except json.JSONDecodeError:
            log.warn("服务器响应：", response.text)
    except requests.exceptions.RequestException as e:
        log.error(f"通知发送失败，{e}")
