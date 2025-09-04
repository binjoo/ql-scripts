#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# new Env('三诺健康签到')
# cron '45 9 * * *'
import requests
import os
import base64
import random

# 所需依赖 requests beautifulsoup4

import utils
import log

SINO_UNION_ID = os.getenv("SINO_UNION_ID")
SINO_OPEN_ID = os.getenv("SINO_OPEN_ID")

BASE_URL = "https://ican.sinocare.com/api"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541012) XWEB/16389"

HEADERS = {"User-Agent": USER_AGENT, "Content-Type": "application/json;charset=UTF-8"}


def generateAuthString() -> str:
    credentialsStr = "miniapp-snjk:ac67459c7d3b6eb7522309uma766r00a"
    credentialsBytes = credentialsStr.encode("utf-8")
    base64_encoded_bytes = base64.b64encode(credentialsBytes)
    authString = base64_encoded_bytes.decode("utf-8")
    return f"Basic {authString}"


def token():
    tokenUrl = f"{BASE_URL}/sino-auth/oauth/token"

    try:
        authHeaders = {"Authorization": generateAuthString()}
        params = {
            "tenantId": "000000",
            "grant_type": "wechat",
            "scope": "all",
            "type": "account",
            "union_id": SINO_UNION_ID,
            "open_id": SINO_OPEN_ID,
        }
        response = requests.get(
            tokenUrl, headers={**HEADERS, **authHeaders}, params=params, json={}
        )
        response.raise_for_status()
        result = response.json()

        HEADERS["sino-auth"] = result.get("access_token")
        log.success("获取 Token 成功...")
    except Exception as e:
        utils.push("三诺健康签到", "获取 Token 步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


def sign():
    signUrl = f"{BASE_URL}/sino-member/signRecord/sign"

    try:
        response = requests.get(signUrl, headers=HEADERS)

        result = response.json()

        if result.get("code") == 200 and result.get("success"):
            log.success("签到成功！")
        else:
            log.error(f"签到失败：{result.get('msg')}")

    except Exception as e:
        utils.push("三诺健康签到", "签到步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


def question():
    questionUrl = f"{BASE_URL}/sino-social/dailyQuestion/getQuestion"
    questionId = None
    outputString = None

    try:
        response = requests.get(questionUrl, headers=HEADERS)

        log.debug("尝试获得当天题目...")
        result = response.json()

        if result.get("code") == 200 and result.get("success"):

            questionId = result.get("data").get("questionId")

            if result.get("data").get("type") == "sn-radio":
                questionType = "单选题"
            elif result.get("data").get("type") == "sn-checkbox":
                questionType = "多选题"

            questionTitle = result.get("data").get("name")

            optionLines = []
            for option in result.get("data").get("options"):
                sn = option["sn"]
                name = option["name"]
                optionLines.append(f"{sn}. {name}")
            optionsString = "\n".join(optionLines)

            outputString = (
                f"题型：{questionType}\n"
                f"题目：{questionTitle}\n"
                f"选项：\n"
                f"{optionsString}\n"
            )

        else:
            log.error(f"签到失败：{result.get('msg')}")
            utils.push("三诺健康签到", f"登录失败：{result.get('msg')}")

    except Exception as e:
        utils.push("三诺健康签到", "题目步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")

    return questionId, outputString


def ai(content: str) -> str:
    system = "我会发给你一个关于健康的题目，请仔细阅读题目，并告诉我选项。记住，只要告诉我选项即可，不需要内容。"
    return utils.ai(system, content)


def answer(id: str, aiAnswer: str):
    questionUrl = f"{BASE_URL}/sino-social/dailyQuestion/getQuestionResult"
    payload = {
        "questionId": id,
        "answerTime": random.randint(30, 120),
        "accountAnswer": aiAnswer,
    }

    try:
        response = requests.post(questionUrl, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()

        if result.get("code") == 200 and result.get("success"):
            log.success(f"答题完成：{result.get('msg')}")
        else:
            log.warn(f"答题失败：{result.get('msg')}")

    except Exception as e:
        utils.push("三诺健康签到", "题目步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


def detail():
    questionUrl = f"{BASE_URL}/sino-member/integral/detail"

    try:
        response = requests.post(questionUrl, headers=HEADERS)
        response.raise_for_status()
        result = response.json()

        log.success(f"当前积分：{result.get('data').get('nowIntegral')}")
    except Exception as e:
        utils.push("三诺健康签到", "详情步骤出现异常")
        log.error(f"异常类型: {type(e).__name__}")
        log.error(f"异常信息: {e}")


if __name__ == "__main__":
    if not SINO_UNION_ID or not SINO_OPEN_ID:
        log.error("环境变量 SINO_UNION_ID 或 SINO_OPEN_ID 未配置。")
        utils.push("三诺健康签到", "环境变量 SINO_UNION_ID 或 SINO_OPEN_ID 未配置。")
        exit(1)

    token()
    sign()
    id, output = question()
    aiAnswer = ai(output)
    if aiAnswer is not None:
        answer(id, aiAnswer)
    detail()
