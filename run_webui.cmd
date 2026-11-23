@echo off
chcp 65001 >nul
title MediaCrawler WebUI
cd /d "%~dp0"
echo ============================================
echo  MediaCrawler WebUI backend
echo  URL: http://127.0.0.1:8080
echo  Press Ctrl+C to stop.
echo ============================================
".venv\Scripts\python.exe" -m uvicorn api.main:app --host 127.0.0.1 --port 8080
pause
