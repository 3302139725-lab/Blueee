#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调用 Jev (TypeSafe System One) 做类型化判断。
不做聊天/生成，只返回结构化判断：choice / score / noul。

用法:
    python jev.py request.json     # request.json = {"state":..., "questions":{...}}
    type request.json | python jev.py   # 或从 stdin 读

API Key 来源（按顺序）:
    1. 环境变量 JEVMODEL_API_KEY
    2. 文件 %USERPROFILE%\\.config\\opencode\\jev_api_key.txt
"""
import os
import sys
import json
import urllib.request
import urllib.error

ENDPOINT = "https://jevmodel.org/v1/systemone"
DEFAULT_MODEL = "jev-latest"
KEY_FILE = os.path.join(os.path.expanduser("~"), ".config", "opencode", "jev_api_key.txt")


def get_key():
    k = os.environ.get("JEVMODEL_API_KEY")
    if k and k.strip():
        return k.strip()
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    key = get_key()
    if not key:
        print(json.dumps({
            "error": "缺少 API Key",
            "hint": "设置环境变量 JEVMODEL_API_KEY，或把 key 写进 " + KEY_FILE,
        }, ensure_ascii=False))
        sys.exit(1)

    # 读取请求
    try:
        if len(sys.argv) > 1:
            with open(sys.argv[1], "r", encoding="utf-8") as f:
                req = json.load(f)
        else:
            req = json.load(sys.stdin)
    except Exception as e:
        print(json.dumps({"error": "请求解析失败", "detail": str(e)}, ensure_ascii=False))
        sys.exit(1)

    body = {
        "model": req.get("model", DEFAULT_MODEL),
        "state": req["state"],
        "questions": req["questions"],
    }
    data = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(
        ENDPOINT,
        data=data,
        method="POST",
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
        },
    )
    # 代理（Jev 在大陆被地区限制，需走代理）：优先 JEVMODEL_PROXY，其次 HTTPS_PROXY/HTTP_PROXY
    proxy = (os.environ.get("JEVMODEL_PROXY")
             or os.environ.get("HTTPS_PROXY")
             or os.environ.get("https_proxy")
             or os.environ.get("HTTP_PROXY")
             or os.environ.get("http_proxy"))
    if proxy:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({"http": proxy, "https": proxy})
        )
    else:
        opener = urllib.request.build_opener()
    try:
        with opener.open(r, timeout=30) as resp:
            out = resp.read().decode("utf-8", "replace")
            try:
                parsed = json.loads(out)
                print(json.dumps(parsed, ensure_ascii=False, indent=2))
            except Exception:
                print(out)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        print(json.dumps({"error": "HTTP " + str(e.code), "detail": detail}, ensure_ascii=False))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({"error": "请求失败", "detail": str(e)}, ensure_ascii=False))
        sys.exit(2)


if __name__ == "__main__":
    main()
