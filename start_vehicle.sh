#!/bin/bash
# 車載端啟動腳本（樹莓派端操作）

cd "$(dirname "$0")/vehicle"
source ../venv/bin/activate

# 檢查是否提供速限參數
if [ -z "$1" ]; then
    echo "使用方式: ./start_vehicle.sh [速限]"
    echo "範例: ./start_vehicle.sh 60"
    exit 1
fi

python3 main.py "$1"

