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


def captcha(type_code: int, image_base64: str) -> str:
    """
    发送验证码识别请求
    :param type_code: 验证码类型代码
    :param image_base64: 验证码图片Base64编码字符串
    :return: 识别结果字典或None
    """
    log.info(f"[CAPTCHA] Image Base64 (first 50 chars): {image_base64[:50]}...")
    
    CAPTCHA_TOKEN = os.getenv("CAPTCHA_TOKEN")
    CAPTCHA_API_HOST = 'http://api.jfbym.com/api/YmServer/customApi'

    if not CAPTCHA_TOKEN:
        log.warning("[CAPTCHA] CAPTCHA_TOKEN not found, skipping captcha request.")
        return None
    
    payload = {
        "token": CAPTCHA_TOKEN,
        "type": type_code,
        "image": image_base64
    }

    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # requests 库会自动将 Python 字典转换为 JSON 字符串并设置 Content-Type
        response = requests.post(CAPTCHA_API_HOST, json=payload, headers=headers)
        response.raise_for_status()  # 检查HTTP状态码，如果不是2xx则抛出异常
        result = response.json()
        if result.get("code") == 10000:
            # 假设 JavaScript 中的 response.data.data.data 对应 Python 的 result['data']['data']
            # 需要根据实际API返回结构调整
            recognition_data = result.get("data", {}).get("data")
            log.info(f"[CAPTCHA] Image Result: {recognition_data}")
            log.info('[CAPTCHA] 🎉 识别完成。')
        else:
            log.info(f"[CAPTCHA] 🥀 识别失败，{result.get('msg', '未知错误')}")
        
        return result # 返回完整的响应数据，对应 JavaScript 中的 resolve(response.data)
    except requests.exceptions.HTTPError as http_err:
        log.error(f"[CAPTCHA] 🥀 HTTP错误发生: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        log.error(f"[CAPTCHA] 🥀 连接错误发生: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        log.error(f"[CAPTCHA] 🥀 请求超时: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        log.error(f"[CAPTCHA] 🥀 请求失败: {req_err}")
    except json.JSONDecodeError as json_err:
        log.error(f"[CAPTCHA] 🥀 JSON解析失败: {json_err}. 原始响应: {response.text}")
    except Exception as e:
        log.error(f"[CAPTCHA] 🥀 发生未知错误: {e}")
    
    return None # 发生异常时返回 None