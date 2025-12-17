#!/bin/bash
# 車載端啟動腳本（樹莓派端操作）

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv"
VEHICLE_DIR="$SCRIPT_DIR/vehicle"

# 檢查虛擬環境是否存在
if [ ! -d "$VENV_DIR" ]; then
    echo "錯誤: 虛擬環境不存在"
    echo "請先執行: cd vehicle && ./install_dependencies.sh"
    exit 1
fi

# 進入車載端目錄
cd "$VEHICLE_DIR"

# 啟動虛擬環境
source "$VENV_DIR/bin/activate"

# 檢查是否提供速限參數
if [ -z "$1" ]; then
    echo "使用方式: ./start_vehicle.sh [速限]"
    echo "範例: ./start_vehicle.sh 60"
    exit 1
fi

# 執行主程式
python3 main.py "$1"

