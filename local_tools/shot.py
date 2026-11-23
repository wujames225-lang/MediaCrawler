# -*- coding: utf-8 -*-
"""
通用 CDP 截图脚本：连上正在运行的调试 Chrome，截当前页面，并用 OpenCV 自动抠出二维码。

用法：
    uv run local_tools/shot.py [端口] [输出前缀]
默认 端口=9222，输出前缀=local_tools/shot
产出：
    <prefix>_full.png   整页截图（viewport）
    <prefix>_qr_0.png   检测到的第 1 个二维码（带白边），无二维码时不生成
注意：connect_over_cdp 下绝不能调用 browser.close()，否则会真把关掉的 Chrome 杀掉；
      脚本结尾用 os._exit(0) 强制退出。
"""
import os
import sys
import time

import cv2
import numpy as np
from playwright.sync_api import sync_playwright


def find_qr_boxes(png_bytes: bytes):
    """在截图中找二维码，返回 (box, 裁剪图) 列表，box=(x,y,w,h)。"""
    arr = np.frombuffer(png_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return []
    detector = cv2.QRCodeDetector()
    try:
        ok, decoded, points, _ = detector.detectMulti(img)
    except Exception:
        decoded, points = [], None
    results = []
    if points is not None and len(points):
        for i in range(len(points)):
            pts = points[i]
            if pts is None or len(pts) == 0:
                continue
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            x0, x1 = int(max(0, min(xs))), int(min(img.shape[1], max(xs)))
            y0, y1 = int(max(0, min(ys))), int(min(img.shape[0], max(ys)))
            margin = int(max(x1 - x0, y1 - y0) * 0.12)
            x0, y0 = max(0, x0 - margin), max(0, y0 - margin)
            x1, y1 = min(img.shape[1], x1 + margin), min(img.shape[0], y1 + margin)
            if x1 - x0 < 80 or y1 - y0 < 80:
                continue
            crop = img[y0:y1, x0:x1]
            results.append(((x0, y0, x1 - x0, y1 - y0), crop))
    return results


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9222
    prefix = sys.argv[2] if len(sys.argv) > 2 else "local_tools/shot"
    url = f"http://127.0.0.1:{port}/json/version"

    ws = None
    for _ in range(60):
        try:
            import urllib.request

            with urllib.request.urlopen(url, timeout=2) as resp:
                import json

                ws = json.loads(resp.read().decode("utf-8"))["webSocketDebuggerUrl"]
            break
        except Exception:
            time.sleep(1)
    if not ws:
        print(f"ERROR: cannot get webSocketDebuggerUrl from {url}")
        return 2

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws)
        contexts = browser.contexts
        if not contexts:
            print("ERROR: no browser context")
            return 3
        pages = contexts[0].pages
        if not pages:
            print("ERROR: no page")
            return 4
        print("PAGES\t" + " | ".join(f"{i}:{pg.url}" for i, pg in enumerate(pages)))
        page = pages[-1]
        for pg in pages:
            u = (pg.url or "").lower()
            if not u.startswith(("chrome://", "devtools://", "about:", "https://www.google.com")):
                if not u.startswith("https://www.bing.com"):
                    page = pg
                    break
        png = page.screenshot(type="png", full_page=False)
        full_path = f"{prefix}_full.png"
        with open(full_path, "wb") as f:
            f.write(png)
        print(f"SAVED\t{full_path}\t{len(png)} bytes\turl={page.url}")
        qrs = find_qr_boxes(png)
        print(f"QR_COUNT\t{len(qrs)}")
        for i, (box, crop) in enumerate(qrs):
            out = f"{prefix}_qr_{i}.png"
            cv2.imwrite(out, crop)
            print(f"QR_SAVED\t{out}\tbox={box}")
        print("DONE")

    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    sys.exit(main())
