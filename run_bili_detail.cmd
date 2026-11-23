@echo off
chcp 65001 >nul
cd /d "%~dp0"
setlocal

echo === Bilibili single video detail (headless) ===
set "ID="
set /p ID=BV id or BV link (av link is NOT supported): 
if "%ID%"=="" (
    echo Nothing entered, abort.
    goto :end
)
set "C="
set /p C=Fetch comments too? y/N: 
if /i "%C%"=="y" (set "COMMENTS=true") else (set "COMMENTS=false")

echo.
echo Fetching detail for " %ID% " , comments=%COMMENTS% ...
uv run main.py --platform bili --type detail --specified_id "%ID%" --get_comment %COMMENTS% --headless true

echo.
echo Done. Output dir: data\bili\jsonl\

:end
pause
