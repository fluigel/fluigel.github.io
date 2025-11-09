@echo off
chcp 65001 >nul
title Fluegel Local Server

echo.
echo ---------------------------------------------
echo     🚀 Fluegel Tower Local Server Starting...
echo ---------------------------------------------
echo.
echo     ▶ 주소: http://127.0.0.1:5500
echo     ▶ 종료: Ctrl + C
echo.

REM 💡 브라우저 자동 실행
start "" http://127.0.0.1:5500

REM 💡 Python 내장 웹서버 실행 (Live Server와 동일)
python -m http.server 5500

pause
