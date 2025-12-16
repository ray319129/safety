@echo off
REM 後端啟動腳本（Windows 本機端操作）

cd /d "%~dp0backend"
call venv\Scripts\activate.bat

python app.py

pause

