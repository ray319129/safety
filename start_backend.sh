#!/bin/bash
# 後端啟動腳本（本機端操作）

cd "$(dirname "$0")/backend"
source venv/bin/activate

python app.py

