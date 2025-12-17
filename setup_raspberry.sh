#!/bin/bash
# 樹莓派端自動安裝腳本

echo "=========================================="
echo "自動安全警示車 - 樹莓派端安裝腳本"
echo "=========================================="

# 更新系統
echo "[1/8] 更新系統套件..."
sudo apt update && sudo apt upgrade -y

# 安裝系統依賴
echo "[2/8] 安裝系統依賴..."
sudo apt install -y python3-pip python3-venv git
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y python3-rpi.gpio
sudo apt install -y minicom

# 啟用 UART
echo "[3/8] 設定 UART..."
echo "請手動執行: sudo raspi-config"
echo "選擇 Interface Options → Serial Port → 啟用"

# 複製專案
echo "[4/8] 複製專案..."
if [ ! -d "safety" ]; then
    git clone https://github.com/ray319129/safety.git
fi
cd safety

# 檢查並安裝 python3-venv
echo "[5/9] 檢查 Python 虛擬環境支援..."
if ! python3 -m venv --help > /dev/null 2>&1; then
    echo "安裝 python3-venv..."
    sudo apt install -y python3-venv python3-full
fi

# 建立虛擬環境
echo "[6/9] 建立虛擬環境..."
python3 -m venv venv

# 檢查虛擬環境是否建立成功
if [ ! -d "venv" ]; then
    echo "錯誤: 無法建立虛擬環境"
    echo "請手動執行: sudo apt install python3-venv python3-full"
    exit 1
fi

# 啟動虛擬環境
source venv/bin/activate

# 安裝 Python 依賴
echo "[7/9] 安裝 Python 依賴..."
python3 -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 設定環境變數
echo "[8/9] 設定環境變數..."
if [ ! -f "vehicle/.env" ]; then
    echo "請編輯 vehicle/.env 檔案設定配置"
    cp .env vehicle/.env 2>/dev/null || echo "請手動建立 vehicle/.env"
fi

echo "[9/9] 安裝完成！"
echo ""
echo "下一步："
echo "1. 編輯 vehicle/.env 設定配置"
echo "2. 執行: cd vehicle && python3 main.py [速限]"

