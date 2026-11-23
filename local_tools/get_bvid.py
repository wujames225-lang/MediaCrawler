# -*- coding: utf-8 -*-
"""
本机辅助脚本：把搜索结果里的 aid 解析成真实 bvid。

背景：MediaCrawler 的 B 站 detail 模式只接受 BV 号（av 链接解析会报
"Unable to parse video ID from URL"），而搜索结果 jsonl 里保存的是 av 链接。
本脚本复用 MediaCrawler 自己的 CDP 浏览器（已保存登录态）和 BilibiliClient，
调用 /x/web-interface/view/detail?aid=... 拿回 View.bvid。

用法：
    uv run local_tools/get_bvid.py 117396186598118 116493347192456
不带参数时使用下面的 AID_LIST。
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402

from playwright.async_api import async_playwright  # noqa: E402

from media_platform.bilibili.client import BilibiliClient  # noqa: E402
from tools import utils  # noqa: E402
from tools.cdp_browser import CDPBrowserManager  # noqa: E402
from tools.crawler_util import convert_browser_context_cookies  # noqa: E402

AID_LIST = ["117396186598118"]


async def main() -> int:
    aids = sys.argv[1:] or AID_LIST
    launcher = CDPBrowserManager()
    async with async_playwright() as playwright:
        browser_context = await launcher.launch_and_connect(playwright, headless=True)
        pages = browser_context.pages
        page = pages[0] if pages else await browser_context.new_page()
        await page.goto("https://www.bilibili.com", wait_until="domcontentloaded")
        user_agent = await page.evaluate("navigator.userAgent")
        cookie_str, cookie_dict = await convert_browser_context_cookies(
            browser_context, urls=["https://www.bilibili.com"]
        )
        utils.logger.info("[get_bvid] cookie keys: %s", len(cookie_dict))

        client = BilibiliClient(
            headers={
                "User-Agent": user_agent,
                "Cookie": cookie_str,
                "Origin": "https://www.bilibili.com",
                "Referer": "https://www.bilibili.com",
                "Content-Type": "application/json;charset=UTF-8",
            },
            playwright_page=page,
            cookie_dict=cookie_dict,
        )

        failed = 0
        for aid in aids:
            try:
                data = await client.get_video_info(aid=int(aid))
                view = data.get("View") or {}
                print(f"RESULT\taid={aid}\tbvid={view.get('bvid')}\ttitle={view.get('title')}")
            except Exception as exc:  # noqa: BLE001
                failed += 1
                print(f"ERROR\taid={aid}\t{exc}")

        await launcher.cleanup()
        print("DONE")
        return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
