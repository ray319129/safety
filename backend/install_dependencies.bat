@echo off
REM Backend dependency installation script (Windows)
REM Fix encoding issues and install dependencies

echo Installing backend dependencies...

REM Upgrade pip, setuptools, and wheel first
python -m pip install --upgrade pip setuptools wheel

REM Install dependencies
pip install -r requirements.txt

echo.
echo Installation complete!
pause

