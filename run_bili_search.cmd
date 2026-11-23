@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

echo === Bilibili keyword search (headless) ===
set "KW="
set /p KW=Keywords, comma separated [e.g. AI视频,教程]: 
if "%KW%"=="" (
    echo Nothing entered, abort.
    goto :end
)
set "N="
set /p N=Max videos, default 10: 
if "%N%"=="" set "N=10"

echo.
echo Searching " %KW% " , max %N% videos ...
uv run main.py --platform bili --type search --keywords "%KW%" --crawler_max_notes_count %N% --headless true

echo.
echo Done. Output dir: data\bili\jsonl\  (same-day runs append to the same file)

:end
pause
