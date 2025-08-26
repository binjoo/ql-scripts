# new Env('HiFiTi 签到')
# cron '45 10 * * *'

import requests
import json
import os
from bs4 import BeautifulSoup

# 所需依赖 requests beautifulsoup4

import utils
import log

USERNAME = os.getenv("HIFITI_USERNAME")
PASSWORD = os.getenv("HIFITI_PASSWORD")
BASE_URL = "https://www.hifiti.com"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0"
)


def login(username, password):
    loginUrl = f"{BASE_URL}/user-login.htm"
    session = requests.Session()

    resp = session.get(loginUrl)
    log.debug(f"登录页Cookie：{session.cookies.get_dict()}")

    # 准备登录请求头
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": BASE_URL,
        "Referer": loginUrl,
        "User-Agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/plain, */*; q=0.01",
    }

    # 表单数据
    data = {"email": USERNAME, "password": utils.md5(PASSWORD)}

    # 发送登录 POST 请求
    response = session.post(loginUrl, headers=headers, data=data)

    log.info("尝试登录....")

    try:
        result = response.json()
        if result.get("code") == "0":
            log.success("登录成功")
            return session
        else:
            log.error(f"登录失败：{result.get('message')}")
            return None
    except json.JSONDecodeError:
        log.warn("返回内容不是有效 JSON，可能登录失败或者返回了登录页面HTML")
        return None


def sign(session):
    signUrl = f"{BASE_URL}/sg_sign.htm"
    headers = {
        "X-Requested-With": "XMLHttpRequest",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/",
        "User-Agent": USER_AGENT,
        "Accept": "text/plain, */*; q=0.01",
    }

    response = session.post(signUrl, headers=headers, data={})

    try:
        result = response.json()
        if result.get("code") == "0":
            log.success(f"签到成功，{result.get('message')}")
        else:
            log.warn(f"签到失败，{result.get('message')}")
    except Exception as e:
        log.error(f"签到响应解析异常：,{e}")
        print(response.text)


def getCredits(session):
    myUrl = f"{BASE_URL}/my.htm"
    headers = {
        "User-Agent": USER_AGENT,
        "Referer": f"{BASE_URL}/sg_sign.htm",
    }

    response = session.get(myUrl, headers=headers)
    if response.status_code != 200:
        log.error(f"请求失败，状态码：{response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    span = soup.find("span", string="金币：")
    if span:
        em = span.find_next_sibling("b")
        if em:
            return em.text.strip()

    log.warn("未能找到金币数量")
    return None


if __name__ == "__main__":
    if not USERNAME or not PASSWORD:
        log.error("未错误：环境变量 HIFITI_USERNAME 或 HIFITI_PASSWORD 未配置。")
        exit(1)

    session = login(USERNAME, PASSWORD)
    if session:
        sign(session)
        gold = getCredits(session)
        if gold is not None:
            log.success(f"当前金币数量：{gold}", "🪙")
        else:
            log.warn("获取金币失败")
