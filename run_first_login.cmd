@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo  MediaCrawler  Bilibili first-time login check
echo  A Chrome window will open with a QR code.
echo  Scan it with the Bilibili mobile App to sign in.
echo  Login state is kept in browser_data\ - you only need
echo  this once (or again after the login expires).
echo ============================================================
echo.

uv run main.py --platform bili --lt qrcode --type search --keywords "AI视频" --crawler_max_notes_count 3

echo.
echo Done. Data saved under: data\bili\jsonl\
pause
