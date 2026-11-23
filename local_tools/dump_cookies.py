# -*- coding: utf-8 -*-
"""只读诊断：用已登录的 xhs Chrome profile 启动 headless Chrome，导出 cookie 概览。
不会修改任何东西；结束用 os._exit 避免 browser.close() 杀掉 Chrome。
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

from playwright.sync_api import sync_playwright

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UD = os.path.join(ROOT, "browser_data", "cdp_xhs_user_data_dir")
PORT = 9222


def main():
    proc = subprocess.Popen(
        [
            CHROME,
            f"--remote-debugging-port={PORT}",
            f"--user-data-dir={UD}",
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--no-default-browser-check",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    ws = None
    for _ in range(30):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2) as r:
                ws = json.loads(r.read().decode("utf-8"))["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(1)
    if not ws:
        print("ERROR: chrome not ready")
        proc.kill()
        os._exit(2)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        ctx = browser.contexts[0]
        cookies = ctx.cookies()
        print(f"COOKIE_TOTAL\t{len(cookies)}")
        interesting = {"a1", "web_session", "webId", "gid", "xsecappid", "customerClientId"}
        for c in cookies:
            if c["name"] in interesting:
                print(f"COOKIE\t{c['domain']}\t{c['name']}\tlen={len(c['value'])}\tpath={c['path']}")
        domains = sorted({c["domain"] for c in cookies})
        print("DOMAINS\t" + ",".join(domains))
    sys.stdout.flush()
    proc.kill()
    os._exit(0)


if __name__ == "__main__":
    main()
