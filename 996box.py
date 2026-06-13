#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# new Env('996盒子抽奖')
# cron '45 9 * * *'
import requests
import os
import base64
import random
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 所需依赖 requests beautifulsoup4

import utils
import log

BOX996_UNION_ID = os.getenv("BOX996_UNION_ID")
BOX996_OPEN_ID = os.getenv("BOX996_OPEN_ID")

APP_ID = 'wx064d5257716e1fce'
APP_KEY = 'vXElr3nN'
BASE_URL = "https://api.greentool.net"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541a1f) XWEB/25046"

HEADERS = {"User-Agent": USER_AGENT, "Content-Type": "application/json;charset=UTF-8",
           "x-mini-corpid":BOX996_UNION_ID,"x-mini-appid":APP_ID}

session = requests.Session()
session.verify = False

def lottery():
    url = f"{BASE_URL}/lottery/user"

    authHeaders = {"priority": "u=1, i","x-mini-token": "f7a2d0c0a1cf4b3395d138995c01f011"}
    payload = {
        "corpid":BOX996_OPEN_ID,
        "app_id":APP_ID,
        "key":APP_KEY,
        "unionid":BOX996_UNION_ID
    }

    try:
        response = session.post(
            url, headers={**HEADERS, **authHeaders}, json=payload
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 0:
            data = result.get("data")
            log.success(f"抽奖成功，{data.get('title')}")
            return data.get('id')
        else:
            log.error(f"抽奖失败：{result.get('msg')}")
            return None
    except Exception as e:
        utils.push("996盒子抽奖", "获取 lottery 步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")

def accept(id):
    url = f"{BASE_URL}/lottery/external/accept"

    authHeaders = {"priority": "u=1, i","x-mini-token": "f7a2d0c0a1cf4b3395d138995c01f011"}
    payload = {
        "corpid":BOX996_OPEN_ID,
        "app_id":APP_ID,
        "key":APP_KEY,
        "unionid":BOX996_UNION_ID,
        "prize_id": id
    }

    try:
        response = session.post(
            url, headers={**HEADERS, **authHeaders}, json=payload
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 0:
            log.success(f"领取成功！")
        else:
            log.error(f"领取失败：{result.get('msg')}")
    except Exception as e:
        utils.push("996盒子抽奖", "获取 accept 步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")

if __name__ == "__main__":
    if not BOX996_UNION_ID or not BOX996_OPEN_ID:
        log.error("环境变量 BOX996_UNION_ID 或 BOX996_OPEN_ID 未配置。")
        utils.push("996盒子抽奖", "环境变量 BOX996_UNION_ID 或 BOX996_OPEN_ID 未配置。")
        exit(1)

    id = lottery()
    if id :
        accept(id)
