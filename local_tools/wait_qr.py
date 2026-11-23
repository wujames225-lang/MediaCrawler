# -*- coding: utf-8 -*-
"""轮询 CDP(9222)，一旦 B 站登录二维码面板出现就立刻截图保存（最多等 90 秒）。

用法：在 MediaCrawler 目录下 `uv run python local_tools/wait_qr.py`
产物：local_tools/bili_qr_live.png（二维码元素截图，含 60px 白边便于手机扫）
注意：connect_over_cdp 下调用 browser.close() 会真的关掉 Chrome，所以这里用 os._exit 硬退出。
"""
import json
import os
import time
import urllib.request

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bili_qr_live.png")
WAIT_SECONDS = 90


def _ws_url() -> str:
    return json.load(urllib.request.urlopen("http://127.0.0.1:9222/json/version", timeout=5))["webSocketDebuggerUrl"]


def main() -> None:
    deadline = time.time() + WAIT_SECONDS
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(_ws_url())
        while time.time() < deadline:
            pages = [pg for ctx in browser.contexts for pg in ctx.pages]
            for pg in pages:
                if "bilibili.com" not in pg.url:
                    continue
                try:
                    box = pg.locator("xpath=//div[@class='login-scan-box']").first
                    if box.count() > 0 and box.is_visible():
                        # 借助整页截图 + 裁剪区域，避免元素截图边缘缺白边
                        box.screenshot(path=OUT)
                        with open(os.path.join(HERE, "bili_qr_ok.txt"), "w", encoding="utf-8") as f:
                            f.write(pg.url)
                        os._exit(0)
                except Exception:
                    pass
            time.sleep(1)
        os._exit(2)


if __name__ == "__main__":
    main()
