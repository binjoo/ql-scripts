#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# new Env('米哈社签到')
import requests
import base64
import json
import os
from Cryptodome.Cipher import AES
from Cryptodome.Hash import SHA256

# 所需依赖 requests pycryptodomex
# 第一次使用前先抓https://bxo30.xyz/api/user/qd请求中的encryptedData和iv参数将其填到68和69行对应位置

import utils
import log

MHS_USERNAME = os.getenv("MHS_USERNAME")
MHS_PASSWORD = os.getenv("MHS_PASSWORD")
MHS_ENCRYPTED_DATA = os.getenv("MHS_ENCRYPTED_DATA")
MHS_IV = os.getenv("MHS_IV")

BASE_URL = "https://bxo30.xyz"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0"

HEADERS = {"Host": "bxo30.xyz","Accept": "application/json, text/plain, */*","User-Agent": USER_AGENT, "Content-Type": "application/json;charset=UTF-8"}

session = requests.Session()

def login():
    url = f"{BASE_URL}/api/auth/login"

    payload = {"userName": MHS_USERNAME, "password": MHS_PASSWORD}
    response = session.post(url, json=payload, headers=HEADERS)
    
    response.raise_for_status()
    json = response.json()
    if response.status_code == 200:
        log.success(f'登录结果：{json.get("msg")}')
    else:
        log.error(f"登录失败，状态码：{response.status_code}")
        return None
    
    plaintext = decrypt_aes_cbc_base64(
        json.get("data"), json.get("iv")
    )
    return plaintext.get("token")

def sign(token):
    url = f"{BASE_URL}/api/user/qd"
    addHeaders = {
        "Token": token
    }

    payload = {"encryptedData": MHS_ENCRYPTED_DATA, "iv": MHS_IV}
    response = session.post(url, json=payload, headers={**HEADERS, **addHeaders})

    response.raise_for_status()
    if response.status_code == 200:
        data = response.json()
        if data.get("code") == 1:
            log.success(f"签到成功：{data.get('msg')}")
            return True
        else:
            log.warn(f"签到失败：{data.get('msg')}")
            return True
    else:
        log.error("请求失败，状态码:", response.status_code)
        return False

def info(token):
    url = f"{BASE_URL}/api/user/info"
    addHeaders = {
        "Token": token
    }

    response = session.post(url, headers={**HEADERS, **addHeaders})

    response.raise_for_status()
    json = response.json()
    if response.status_code == 200:
        log.success(f'获取用户信息成功：{json.get("msg")}')
    else:
        log.error(f"获取用户信息失败：状态码：{response.status_code}")
    
    plaintext = decrypt_aes_cbc_base64(
        json.get("data"), json.get("iv")
    )

    log.info("======用户信息 TOP======")
    log.info(f"ID：{plaintext.get("id")}")
    log.info(f"经验：{plaintext.get("jy")}")
    log.info(f"积分：{plaintext.get("jf")}")
    log.info("======用户信息 BOTTOM======")

def decrypt_aes_cbc_base64(
    cipher_b64: str, iv_b64: str, mH: str = "mhs-1234-s981re-k071y2"
):
    try:
        key = SHA256.new(mH.encode()).digest()
        iv = base64.b64decode(iv_b64)
        ciphertext = base64.b64decode(cipher_b64)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_plaintext = cipher.decrypt(ciphertext)

        pad_len = padded_plaintext[-1]
        plaintext = padded_plaintext[:-pad_len].decode("utf-8")

        try:
            return json.loads(plaintext)
        except json.JSONDecodeError:
            return plaintext
    except Exception as e:
        print(f"😖解密失败: {e}")
        return None

if __name__ == "__main__":
    if not MHS_USERNAME or not MHS_PASSWORD:
        log.error("环境变量 MHS_USERNAME 或 MHS_PASSWORD 未配置。")
        utils.push("米哈社签到", "环境变量 MHS_USERNAME 或 MHS_PASSWORD 未配置。")
        exit(1)

    token = login()
    
    if token:
        sign(token)
        info(token)