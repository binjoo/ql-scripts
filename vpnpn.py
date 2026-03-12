#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# new Env('冲上云霄签到')
# cron '45 9 * * *'
import requests
import os
import time

# 所需依赖 requests beautifulsoup4

import utils
import log

VPNPN_USERNAME = os.getenv("VPNPN_USERNAME")
VPNPN_PASSWORD = os.getenv("VPNPN_PASSWORD")

BASE_URL = "https://my.vpnpn.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541012) XWEB/16389"

HEADERS = {"User-Agent": USER_AGENT, "Content-Type": "application/json;charset=UTF-8"}

PROXIES = {
    "http": os.getenv("PROXY_HTTP"),
    "https": os.getenv("PROXY_HTTPS"),
}

session = requests.Session()

def login():
    log.info(f"正在进行登录...")
    url = f"{BASE_URL}/api/user/login"

    try:
        payload = {
            "username": VPNPN_USERNAME,
            "password": VPNPN_PASSWORD
        }
        response = session.post(
            url, headers={**HEADERS}, json=payload, proxies=PROXIES
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == 0:
            log.error(f"登录失败，{result.get('message')}")
            return None
        else:
            log.success(f"登录成功")
            return result.get("data")
    except Exception as e:
        utils.push("冲上云霄签到", "获取 Token 步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")

def captcha():
    log.info(f"正在识别验证码")
    url = f"{BASE_URL}/captcha?{time.time()}"

    try:
        response = session.get(
            url, headers={**HEADERS}, proxies=PROXIES
        )

        response.raise_for_status()
        result = response.json()

        base64 = result.get("img")
        re = utils.captcha(10110, base64)

        log.info(f"验证码识别完成，耗时 {round(re.get('data').get('time') * 1000)} ms")
        
        if re.get("code") == 10000:
          data = re.get("data").get("data")
          log.success(f"验证码识别成功，text：{data}")
          return data
        else:
          log.error(f"验证码识别失败，code：{re.get('code')}")
    except Exception as e:
        utils.push("冲上云霄签到", "解析验证码步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


def sign(token: str, text: str):
    log.info(f"正在进行签到...")
    url = f"{BASE_URL}/api/user/sign"

    params = {
        "v": text
    }
    
    authHeaders = {"Authorization": f"Bearer {token}"}

    try:
        response = session.get(
            url, headers={**HEADERS, **authHeaders}, params=params, proxies=PROXIES
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == 0:
            log.error(f"签到失败，{result.get('message')}")
            return None
        else:
            log.success(f"签到成功，获得 {convert_bytes(result.get('data'))} MB流量")
            return result.get("data")
    except Exception as e:
        utils.push("冲上云霄签到", "获取 Token 步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")

def info(token: str):
    log.info(f"正在获取订阅信息...")
    url = f"{BASE_URL}/api/user/info"
    
    authHeaders = {"Authorization": f"Bearer {token}"}

    try:
        response = session.post(
            url, headers={**HEADERS, **authHeaders}, proxies=PROXIES
        )
        response.raise_for_status()
        result = response.json()

        if result.get("status") == 0:
            log.error(f"获取失败，{result.get('message')}")
        else:
            log.success(f"======订阅信息 TOP======")
            log.success(f"总流量 {convert_bytes(result.get('data').get('traffic'))}")
            log.success(f"已用流量 {convert_bytes(result.get('data').get('trafficked'))}")
            log.success(f"剩余流量 {convert_bytes(result.get('data').get('traffic') - result.get('data').get('trafficked'))}")
            log.success(f"======订阅信息 BOTTOM======")
    except Exception as e:
        utils.push("冲上云霄签到", "获取订阅信息步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")

def convert_bytes(bytes_value, precision=2):
    if bytes_value < 0:
        raise ValueError("字节数不能为负数。")
    if bytes_value == 0:
        return "0.00 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    base = 1024
    
    current_value = float(bytes_value)
    unit_index = 0
    while current_value >= base and unit_index < len(units) - 1:
        current_value /= base
        unit_index += 1
            
    return f"{current_value:.{precision}f} {units[unit_index]}"

if __name__ == "__main__":
    if not VPNPN_USERNAME or not VPNPN_PASSWORD:
        log.error("环境变量 VPNPN_USERNAME 或 VPNPN_PASSWORD 未配置。")
        utils.push("冲上云霄签到", "环境变量 VPNPN_USERNAME 或 VPNPN_PASSWORD 未配置。")
        exit(1)

    token = login()
    text = None

    if token:
        text = captcha()
    
    if token and text:
        sign(token, text)
        info(token)