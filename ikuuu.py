#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# new Env('IKUUU 签到')
# cron '15 12 * * *'
import requests
import os

# 所需依赖 requests beautifulsoup4

import utils
import log

USERNAME = os.getenv("IKUUU_USERNAME")
PASSWORD = os.getenv("IKUUU_PASSWORD")
BASE_URL = "https://ikuuu.org"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"

HEADERS = {"User-Agent": USER_AGENT}


def login():
    loginUrl = f"{BASE_URL}/auth/login"
    params = {"host": "ikuuu.org", "email": USERNAME, "passwd": PASSWORD, "code": ""}

    session = requests.Session()
    session.get(loginUrl)

    # 准备登录请求头
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": BASE_URL,
        "Referer": loginUrl,
        "User-Agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/javascript, */*; q=0.01",
    }

    try:
        response = session.post(loginUrl, headers=headers, params=params)

        log.debug("尝试登录....")
        result = response.json()

        if result.get("ret") == 1:
            log.success(result.get("msg"))
            return session
        else:
            log.error(f"登录失败：{result.get("msg")}")
            utils.push("IKUUU 签到", f"登录失败：{result.get('msg')}")
            return None

    except Exception as e:
        utils.push("IKUUU 签到", "登录步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")
        return None


def sign(session):
    signUrl = f"{BASE_URL}/user/checkin"

    try:
        response = session.post(signUrl, headers=HEADERS)

        result = response.json()
        if result.get("ret") == 1:
            log.success(f"签到成功，{result.get('msg')}")
        else:
            log.warn(f"签到失败，{result.get('msg')}")

    except Exception as e:
        utils.push("IKUUU 签到", "签到步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        log.error("环境变量 IKUUU_USERNAME 或 IKUUU_PASSWORD 未配置。")
        utils.push("IKUUU 签到", "环境变量 IKUUU_USERNAME 或 IKUUU_PASSWORD 未配置。")
        exit(1)

    session = login()

    if session:
        sign(session)
