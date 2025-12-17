# 自動安全警示車（Automatic Road Safety Warning Vehicle）

## 專案概述

當發生交通事故時，使用者啟動此裝置，裝置會自動往後移動固定距離並升起警示牌，同時將事故資料與即時影像傳送到後端系統。

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                      Raspberry Pi 4                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   GPS    │  │  Camera  │  │  Motor   │  │  Servo   │   │
│  │  Module  │  │  Vision  │  │ Control  │  │ Control  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Alarm   │  │   Main   │  │   Web    │                 │
│  │  Module  │  │ Program  │  │   API    │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Flask Backend Server                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   REST   │  │ MongoDB  │  │  Ngrok   │                 │
│  │   API    │  │ Database │  │  Tunnel  │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Web Frontend                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Google  │  │  Video   │  │  Admin   │                 │
│  │   Maps   │  │  Stream  │  │  Panel   │                 │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## 功能流程圖

```
開始
  │
  ▼
GPS 初始化並取得事故位置（起點）
  │
  ▼
啟動視覺辨識模組
  │
  ▼
判斷道路類型（速限）
  │
  ├─→ 高速公路 → 目標距離：100m
  ├─→ 快速道路/速限>60 → 目標距離：80m
  ├─→ 速限50-60 → 目標距離：50m
  └─→ 速限<50 → 目標距離：30m
  │
  ▼
開始移動（循環）
  │
  ├─→ 視覺辨識偵測障礙物
  │   │
  │   ├─→ 有障礙物 → 計算避障路徑 → 執行避障 → 回歸原路徑
  │   └─→ 無障礙物 → 繼續前進
  │
  ├─→ GPS 計算累積距離
  │
  └─→ 檢查是否達到目標距離
      │
      ├─→ 未達到 → 繼續移動
      └─→ 已達到 → 停止移動
          │
          ▼
升起警示牌（兩個伺服馬達）
  │
  ▼
播放警示音（ISD1820）
  │
  ▼
上報事故資料到後端（GPS + 影像）
  │
  ▼
開始即時影像串流
  │
  ▼
結束
```

## 檔案架構

```
safety/
├── README.md                         # 專案說明文件
├── requirements.txt                  # 車載端 Python 依賴
├── .gitignore                       # Git 忽略檔案
│
├── vehicle/                          # 車載端程式（Raspberry Pi）
│   ├── __init__.py
│   ├── gps_module.py                 # GPS 定位與距離計算
│   ├── vision_module.py              # 視覺辨識與避障
│   ├── motor_controller.py           # 履帶馬達控制
│   ├── servo_controller.py           # 伺服馬達控制
│   ├── alarm.py                      # ISD1820 警示音控制
│   ├── main.py                       # 主程式
│   ├── web_api.py                    # 影像串流 API
│   └── config.py                     # 車載端配置
│
├── backend/                          # 後端伺服器
│   ├── __init__.py
│   ├── app.py                        # Flask 主應用
│   ├── models.py                     # MongoDB 資料模型
│   ├── auth.py                       # 管理員驗證
│   ├── config.py                     # 後端配置
│   └── requirements.txt              # 後端依賴
│
├── frontend/                         # 前端網頁
│   ├── index.html                    # 主頁面
│   ├── style.css                     # 樣式表
│   └── app.js                        # 前端邏輯
│
├── docs/                             # 文件
│   ├── deployment.md                 # 部署說明
│   └── api.md                        # API 文件
│
├── start_vehicle.sh                  # 車載端啟動腳本
├── start_backend.sh                  # 後端啟動腳本（Linux/Mac）
├── start_backend.bat                 # 後端啟動腳本（Windows）
└── setup_raspberry.sh                # 樹莓派自動安裝腳本
```

## 硬體連接

### Raspberry Pi GPIO 連接

| 硬體 | GPIO 腳位 | 說明 |
|------|----------|------|
| L298N IN1 | GPIO 17 | 左馬達正轉 |
| L298N IN2 | GPIO 27 | 左馬達反轉 |
| L298N IN3 | GPIO 22 | 右馬達正轉 |
| L298N IN4 | GPIO 23 | 右馬達反轉 |
| L298N ENA | GPIO 18 | 左馬達 PWM |
| L298N ENB | GPIO 19 | 右馬達 PWM |
| Servo 1 | GPIO 12 | 警示牌伺服 1 |
| Servo 2 | GPIO 13 | 警示牌伺服 2 |
| ISD1820 PLAY | GPIO 24 | 播放觸發 |
| GPS RX | GPIO 15 (UART) | GPS 接收 |
| GPS TX | GPIO 14 (UART) | GPS 發送 |

## 安裝步驟

### 樹莓派端操作

1. 更新系統：
```bash
sudo apt update && sudo apt upgrade -y
```

2. 安裝依賴套件：
```bash
sudo apt install -y python3-pip python3-venv git
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y python3-rpi.gpio
```

3. 啟用 UART（用於 GPS）：
```bash
sudo raspi-config
# 選擇 Interface Options → Serial Port → 啟用
```

4. 複製專案：
```bash
cd ~
git clone https://github.com/ray319129/safety.git
cd safety
```

5. 安裝 Python 虛擬環境支援（如果需要）：
```bash
sudo apt install -y python3-venv python3-full
```

6. 建立虛擬環境並安裝依賴：
```bash
# 方法一：使用自動安裝腳本（推薦）
cd vehicle
chmod +x install_dependencies.sh
./install_dependencies.sh

# 方法二：手動建立虛擬環境
cd ~/safety
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

6. 設定環境變數：
```bash
cp .env.example .env
# 編輯 .env 檔案填入配置
```

### 本機端操作（後端伺服器）

1. 安裝 Python 和 MongoDB：
```bash
# Windows: 下載並安裝 Python 和 MongoDB
# 或使用 Docker
```

2. 複製專案：
```bash
git clone https://github.com/ray319129/safety.git
cd safety/backend
```

3. 建立虛擬環境：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

4. 安裝依賴：
```bash
pip install -r requirements.txt
```

5. 設定環境變數：
```bash
# 編輯 .env 檔案
```

6. 啟動 MongoDB：
```bash
# Windows: 啟動 MongoDB 服務
mongod
```

7. 啟動 Flask 伺服器：
```bash
python app.py
```

8. 啟動 Ngrok（新終端）：
```bash
ngrok http 5000
# 記下產生的公網 URL
```

## 使用說明

### 啟動車載系統

在樹莓派上執行：

**方法一：使用啟動腳本（推薦）**
```bash
cd ~/safety
chmod +x start_vehicle.sh
./start_vehicle.sh 60  # 速限 60 km/h
```

**方法二：手動啟動**
```bash
cd ~/safety
source venv/bin/activate
cd vehicle
python3 main.py 60  # 速限 60 km/h
```

### 啟動後端服務

在本機或伺服器上執行：
```bash
cd safety/backend
python app.py
```

### 開啟前端網頁

在瀏覽器開啟 `frontend/index.html` 或透過 Ngrok URL 訪問。

## API 文件

詳見 `docs/api.md`

## 授權

MIT License

