# 部署說明文件

## 目錄
1. [樹莓派端部署](#樹莓派端部署)
2. [後端伺服器部署](#後端伺服器部署)
3. [前端部署](#前端部署)
4. [Ngrok 設定](#ngrok-設定)
5. [系統測試](#系統測試)

## 樹莓派端部署

### 前置需求
- Raspberry Pi 4 (4GB RAM)
- Raspberry Pi OS (64-bit)
- 已連接所有硬體模組

### 步驟 1: 系統更新

```bash
sudo apt update && sudo apt upgrade -y
```

### 步驟 2: 安裝系統依賴

```bash
# 安裝 Python 和基本工具
sudo apt install -y python3-pip python3-venv git

# 安裝 OpenCV 依賴
sudo apt install -y libopencv-dev python3-opencv

# 安裝 GPIO 庫
sudo apt install -y python3-rpi.gpio

# 安裝序列埠工具
sudo apt install -y minicom
```

### 步驟 3: 啟用 UART（GPS 通訊）

```bash
# 編輯啟動配置
sudo raspi-config
```

選擇：
- `Interface Options` → `Serial Port`
- 啟用 Serial Port
- 禁用 Serial Login
- 重啟系統

### 步驟 4: 複製專案

```bash
cd ~
git clone https://github.com/ray319129/safety.git
cd safety
```

### 步驟 5: 建立虛擬環境

```bash
python3 -m venv venv
source venv/bin/activate
```

### 步驟 6: 安裝 Python 依賴

```bash
# 先升級 pip、setuptools 和 wheel（解決 setuptools 錯誤）
python3 -m pip install --upgrade pip setuptools wheel

# 安裝依賴
pip install -r requirements.txt

# 或使用提供的安裝腳本
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 步驟 7: 設定環境變數

建立 `.env` 檔案：

```bash
cd vehicle
nano .env
```

填入以下內容（根據實際硬體連接調整）：

```env
GPS_SERIAL_PORT=/dev/ttyAMA0
GPS_BAUDRATE=9600

MOTOR_LEFT_PWM_PIN=18
MOTOR_LEFT_IN1_PIN=17
MOTOR_LEFT_IN2_PIN=27
MOTOR_RIGHT_PWM_PIN=19
MOTOR_RIGHT_IN3_PIN=22
MOTOR_RIGHT_IN4_PIN=23

SERVO_1_PIN=12
SERVO_2_PIN=13
SERVO_RAISE_ANGLE=90
SERVO_LOWER_ANGLE=0

ALARM_PIN=24

BACKEND_URL=http://your-backend-url:5000
API_TOKEN=your_api_token_here

CAMERA_INDEX=0
VISION_CONFIDENCE_THRESHOLD=0.5
OBSTACLE_MIN_AREA=500

HIGHWAY_DISTANCE=100
EXPRESSWAY_DISTANCE=80
CITY_ROAD_DISTANCE=50
LOCAL_ROAD_DISTANCE=30
```

### 步驟 8: 測試硬體連接

```bash
# 測試 GPS（需要連接 GPS 模組）
python3 -c "from gps_module import GPSModule; g = GPSModule(); g.connect(); print(g.read_gps_data())"

# 測試攝影機
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed')"
```

### 步驟 9: 啟動主程式

```bash
cd ~/safety/vehicle
source ../../venv/bin/activate
python3 main.py [速限]
```

例如：
```bash
python3 main.py 60  # 速限 60 km/h
```

### 步驟 10: 啟動影像串流服務（可選，獨立終端）

```bash
cd ~/safety/vehicle
source ../../venv/bin/activate
python3 web_api.py
```

## 後端伺服器部署

### 前置需求
- Python 3.8+
- MongoDB
- Ngrok（用於公網訪問）

### 步驟 1: 安裝 MongoDB

**Windows:**
1. 下載 MongoDB Community Server
2. 安裝並啟動服務

**Linux:**
```bash
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

### 步驟 2: 複製專案

```bash
git clone https://github.com/ray319129/safety.git
cd safety/backend
```

### 步驟 3: 建立虛擬環境

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 步驟 4: 安裝依賴

**Windows:**
```bash
# 先升級 pip、setuptools 和 wheel（解決編碼和 setuptools 錯誤）
python -m pip install --upgrade pip setuptools wheel

# 安裝依賴
pip install -r requirements.txt

# 或使用提供的安裝腳本
install_dependencies.bat
```

**Linux/Mac:**
```bash
# 先升級 pip、setuptools 和 wheel
python3 -m pip install --upgrade pip setuptools wheel

# 安裝依賴
pip install -r requirements.txt

# 或使用提供的安裝腳本
chmod +x install_dependencies.sh
./install_dependencies.sh
```

### 步驟 5: 設定環境變數

建立 `.env` 檔案：

```bash
# Windows
notepad .env

# Linux/Mac
nano .env
```

填入配置（參考 `backend/.env` 範例）

### 步驟 6: 啟動 Flask 伺服器

```bash
python app.py
```

伺服器將在 `http://localhost:5000` 啟動

## 前端部署

### 方法 1: 直接開啟（開發用）

直接在瀏覽器開啟 `frontend/index.html`

**注意：** 需要修改 `app.js` 中的 `API_URL` 為實際後端地址

### 方法 2: 使用簡單 HTTP 伺服器

```bash
cd frontend

# Python 3
python3 -m http.server 8000

# 或使用 Node.js
npx http-server -p 8000
```

然後在瀏覽器開啟 `http://localhost:8000`

### 方法 3: 整合到後端（生產環境）

將前端檔案放到後端的 `static` 目錄，Flask 會自動提供靜態檔案服務

## Ngrok 設定

### 步驟 1: 安裝 Ngrok

**Windows:**
1. 下載 ngrok.exe
2. 解壓到任意目錄

**Linux:**
```bash
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

### 步驟 2: 設定認證 Token

```bash
ngrok config add-authtoken 2rlQ64vNUG752qK5ZKEGOFxvsGx_5GvZG5k3NCduFBnA1nVV1
```

### 步驟 3: 啟動隧道

```bash
ngrok http 5000
```

### 步驟 4: 取得公網 URL

Ngrok 會顯示類似：
```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:5000
```

將此 URL 更新到：
- 車載端的 `BACKEND_URL`
- 前端的 `API_URL`

## 系統測試

### 測試 1: 後端 API

```bash
# 健康檢查
curl http://localhost:5000/api/health

# 取得事故列表
curl http://localhost:5000/api/get_accidents
```

### 測試 2: 管理員登入

```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 測試 3: 車載端連接

在樹莓派上執行主程式，確認可以成功上報事故資料

### 測試 4: 前端功能

1. 開啟前端網頁
2. 確認地圖顯示正常
3. 測試管理員登入
4. 確認即時影像串流
5. 測試偵測框開關

## 常見問題

### 依賴安裝錯誤

#### 問題 1: `UnicodeDecodeError: 'cp950' codec can't decode` (Windows)

**原因：** Windows 使用 cp950 編碼，但 requirements.txt 可能包含 UTF-8 字元。

**解決方法：**
1. 先升級 pip、setuptools 和 wheel：
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```
2. 使用提供的安裝腳本：
   ```bash
   install_dependencies.bat
   ```

#### 問題 2: `BackendUnavailable: Cannot import 'setuptools.build_meta'` (樹莓派)

**原因：** 缺少或版本過舊的 setuptools。

**解決方法：**
1. 先升級 pip、setuptools 和 wheel：
   ```bash
   python3 -m pip install --upgrade pip setuptools wheel
   ```
2. 再安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```
3. 或使用提供的安裝腳本：
   ```bash
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

### GPS 無法連接
- 檢查序列埠是否正確：`ls -l /dev/tty*`
- 確認 UART 已啟用
- 檢查 GPS 模組電源和天線

### 攝影機無法開啟
- 檢查攝影機連接：`lsusb`
- 確認攝影機索引：`v4l2-ctl --list-devices`
- 調整 `.env` 中的 `CAMERA_INDEX`

### MongoDB 連接失敗
- 確認 MongoDB 服務運行：`sudo systemctl status mongodb`
- 檢查連接字串格式
- 確認防火牆設定

### 影像串流無法顯示
- 確認車載端 `web_api.py` 正在運行
- 檢查後端 `app.py` 中的車輛 URL 設定
- 確認網路連接

## 生產環境建議

1. **安全性**
   - 更改所有預設密碼和 Token
   - 使用 HTTPS（透過 Ngrok 或反向代理）
   - 實作更嚴格的 CORS 政策

2. **效能**
   - 使用 Gunicorn 或 uWSGI 運行 Flask
   - 設定 MongoDB 索引
   - 優化影像串流品質

3. **監控**
   - 設定日誌記錄
   - 實作健康檢查端點
   - 監控系統資源使用

