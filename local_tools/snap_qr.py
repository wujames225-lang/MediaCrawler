# -*- coding: utf-8 -*-
"""通过 CDP(9222) 截取正在运行的 Chrome 页面，并把 B 站登录二维码单独截出来。
用法：在 MediaCrawler 目录下 `uv run python local_tools/snap_qr.py`
产物：local_tools/bili_login_full.png（整页）与 local_tools/bili_login_qr.png（二维码元素）
"""
import json
import os
import urllib.request

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    ver = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=10))
    ws = ver["webSocketDebuggerUrl"]
    print("browser:", ver.get("Browser"), "ws:", ws)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        pages = [pg for ctx in browser.contexts for pg in ctx.pages]
        for pg in pages:
            print("PAGE:", pg.url)
        if not pages:
            print("no page found")
            return
        target = next((pg for pg in pages if "bilibili.com" in pg.url), pages[0])
        print("TARGET:", target.url)
        full = os.path.join(HERE, "bili_login_full.png")
        target.screenshot(path=full)
        print("saved:", full)
        try:
            el = target.locator("xpath=//div[@class='login-scan-box']").first
            el.screenshot(path=os.path.join(HERE, "bili_login_qr.png"))
            print("saved: bili_login_qr.png")
        except Exception as e:  # 页面结构变化时只保留整页截图
            print("qr element not found:", repr(e)[:200])

        # 重要：connect_over_cdp 下调用 browser.close() 会真的把 Chrome 关掉，
        # 从而中断正在等待扫码的 MediaCrawler，所以这里直接硬退出进程，不做清理。
        os._exit(0)


if __name__ == "__main__":
    main()
