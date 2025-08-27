#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# new Env('飞牛NAS签到')
# cron '45 11 * * *'

import requests
import json
import os
from bs4 import BeautifulSoup

# 所需依赖 requests beautifulsoup4

import utils
import log

FNNAS_COOKIE = os.getenv("FNNAS_COOKIE")
# 只需保留 pvRK_2132_saltkey、pvRK_2132_auth
BASE_URL = "https://club.fnnas.com"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36 Edg/138.0.0.0"

HEADERS = {"User-Agent": USER_AGENT, "cookie": FNNAS_COOKIE}


def token():
    indexUrl = f"{BASE_URL}/plugin.php?id=zqlj_sign"

    response = requests.get(indexUrl, headers=HEADERS)
    if response.status_code != 200:
        log.error(f"请求失败，状态码：{response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    print(response.text)
    print(soup.find("a", class_="btna", string="点击打卡"))

    span = soup.find("span", string="登录")
    if span:
        log.error("当前 COOKIE 已失效，请重新设置。")
        utils.push("飞牛NAS签到", "当前 COOKIE 已失效，请重新设置。")
        return None
    else:
        log.success("当前 COOKIE 未失效，正常进入...")
        return soup.select_one("div.signbtn a").get("href").strip()


def sign(token):
    signUrl = f"{BASE_URL}/{token}"

    response = requests.get(signUrl, headers=HEADERS)

    soup = BeautifulSoup(response.text, "html.parser")
    log.info(soup.select_one("#messagetext p:first-child").get_text().strip())


def credits():
    myUrl = f"{BASE_URL}/plugin.php?id=zqlj_sign"

    response = requests.get(myUrl, headers=HEADERS)
    if response.status_code != 200:
        log.error(f"请求失败，状态码：{response.status_code}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    stats_dict = {}

    target_div = None

    for div in soup.select("div.bm"):
        strong_tag = div.find("strong")
        if strong_tag and "我的打卡动态" in strong_tag.get_text():
            target_div = div
            break

    if target_div:
        list_items = target_div.select("ul.xl.xl1 li")
        for item in list_items:
            raw_text = item.get_text().strip()

            parts = raw_text.replace("：", ":", 1).split(":", 1)

            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                stats_dict[key] = value
    return stats_dict


if __name__ == "__main__":
    if not FNNAS_COOKIE:
        log.error("FNNAS_COOKIE 未配置。")
        utils.push("飞牛NAS 签到", "环境变量 FNNAS_COOKIE 未配置。")
        exit(1)

    signToken = token()
    if signToken:
        sign(signToken)
        stats_dict = credits()
        if stats_dict:
            for key in stats_dict:
                value = stats_dict.get(key, "N/A")
                log.info(f"{key}：{value}", "🥇")
