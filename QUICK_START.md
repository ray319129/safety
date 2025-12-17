# 快速開始指南

## 完整系統啟動流程

### 第一步：樹莓派端配置與啟動

#### 1.1 設定環境變數

```bash
cd ~/Desktop/safety/vehicle
nano .env
```

填入以下配置（根據實際硬體連接調整）：

```env
# GPS 配置
GPS_SERIAL_PORT=/dev/ttyAMA0
GPS_BAUDRATE=9600

# 馬達控制 GPIO 腳位
MOTOR_LEFT_PWM_PIN=18
MOTOR_LEFT_IN1_PIN=17
MOTOR_LEFT_IN2_PIN=27
MOTOR_RIGHT_PWM_PIN=19
MOTOR_RIGHT_IN3_PIN=22
MOTOR_RIGHT_IN4_PIN=23

# 伺服控制 GPIO 腳位
SERVO_1_PIN=12
SERVO_2_PIN=13
SERVO_RAISE_ANGLE=90
SERVO_LOWER_ANGLE=0

# 警示音 GPIO 腳位
ALARM_PIN=24

# 後端 API 配置（需要填入實際的後端 URL）
BACKEND_URL=http://your-backend-ip:5000
API_TOKEN=your_api_token_here

# 視覺辨識配置
CAMERA_INDEX=0
VISION_CONFIDENCE_THRESHOLD=0.5
OBSTACLE_MIN_AREA=500

# 道路類型與距離配置（單位：公尺）
HIGHWAY_DISTANCE=100
EXPRESSWAY_DISTANCE=80
CITY_ROAD_DISTANCE=50
LOCAL_ROAD_DISTANCE=30
```

**重要：** 
- `BACKEND_URL` 需要填入後端伺服器的實際 IP 地址或 Ngrok URL
- 如果後端在本機，需要先取得本機 IP：`ip addr show` 或 `ifconfig`

#### 1.2 測試硬體連接（可選）

```bash
# 測試 GPS（需要連接 GPS 模組）
sudo minicom -D /dev/ttyAMA0 -b 9600
# 按 Ctrl+A 然後 X 退出

# 測試攝影機
source ../venv/bin/activate
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Failed'); cap.release()"
```

#### 1.3 啟動車載端主程式

**方法一：使用啟動腳本（推薦）**
```bash
cd ~/Desktop/safety
source venv/bin/activate
chmod +x start_vehicle.sh
./start_vehicle.sh 60  # 60 是道路速限（km/h）
```

**方法二：手動啟動**
```bash
cd ~/Desktop/safety
source venv/bin/activate
cd vehicle
python3 main.py 60  # 60 是道路速限（km/h）
```

**速限對應的移動距離：**
- 高速公路（速限 >= 100）：100 公尺
- 快速道路（速限 > 60）：80 公尺
- 城市道路（速限 50-60）：50 公尺
- 地方道路（速限 < 50）：30 公尺

#### 1.4 啟動影像串流服務（可選，獨立終端）

```bash
cd ~/Desktop/safety
source venv/bin/activate
cd vehicle
python3 web_api.py
```

這會在 `http://localhost:8080/video_stream` 提供影像串流。

---

### 第二步：本機端後端配置與啟動

#### 2.1 安裝 MongoDB

**Windows:**
1. 下載 MongoDB Community Server
2. 安裝並啟動 MongoDB 服務

**Linux/Mac:**
```bash
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### 2.2 設定後端環境變數

```bash
cd backend
# Windows: notepad .env
# Linux/Mac: nano .env
```

確認以下配置：

```env
# Flask 配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
SECRET_KEY=safety-system-secret-key-change-in-production

# MongoDB 配置
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=safety_db

# 管理員配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# CORS 配置
CORS_ORIGINS=*
```

#### 2.3 啟動後端伺服器

**Windows:**
```bash
cd backend
venv\Scripts\activate
python app.py
```

**Linux/Mac:**
```bash
cd backend
source venv/bin/activate
python app.py
```

伺服器將在 `http://localhost:5000` 啟動。

#### 2.4 設定 Ngrok 公網隧道（讓樹莓派可以訪問）

**新開一個終端視窗：**

```bash
# 設定認證 Token（只需執行一次）
ngrok config add-authtoken 2rlQ64vNUG752qK5ZKEGOFxvsGx_5GvZG5k3NCduFBnA1nVV1

# 啟動隧道
ngrok http 5000
```

**記下產生的 URL，例如：**
```
Forwarding  https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:5000
```

**更新樹莓派的 .env 檔案：**
```env
BACKEND_URL=https://xxxx-xxxx-xxxx.ngrok-free.app
```

---

### 第三步：前端配置與啟動

#### 3.1 修改前端配置

編輯 `frontend/app.js`，找到以下行並修改：

```javascript
const CONFIG = {
    API_URL: 'http://localhost:5000/api',  // 改為實際後端地址
    VIDEO_STREAM_URL: 'http://localhost:5000/api/video/vehicle_001',
    // ...
};
```

**如果使用 Ngrok：**
```javascript
const CONFIG = {
    API_URL: 'https://xxxx-xxxx-xxxx.ngrok-free.app/api',
    VIDEO_STREAM_URL: 'https://xxxx-xxxx-xxxx.ngrok-free.app/api/video/vehicle_001',
    // ...
};
```

#### 3.2 啟動前端

**方法一：使用 Python HTTP 伺服器**
```bash
cd frontend
python -m http.server 8000
# 或
python3 -m http.server 8000
```

**方法二：使用 Node.js**
```bash
cd frontend
npx http-server -p 8000
```

**方法三：直接在瀏覽器開啟**
- 直接開啟 `frontend/index.html`（某些功能可能受限於 CORS）

#### 3.3 開啟網頁

在瀏覽器開啟：`http://localhost:8000`

---

### 第四步：系統測試

#### 4.1 測試後端 API

```bash
# 健康檢查
curl http://localhost:5000/api/health

# 取得事故列表
curl http://localhost:5000/api/get_accidents

# 管理員登入
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

#### 4.2 測試車載端連接

在樹莓派上執行主程式後，檢查：
- GPS 是否成功定位
- 攝影機是否正常運作
- 是否成功上報事故資料到後端

#### 4.3 測試前端功能

1. **開啟前端網頁**
2. **檢查地圖顯示**：應該看到事故標記（如果有）
3. **測試管理員登入**：
   - 點擊「管理員登入」
   - 輸入：`admin` / `admin123`
4. **測試即時影像**：應該看到影像串流
5. **測試偵測框開關**：切換開關，影像應該顯示/隱藏偵測框

---

### 第五步：完整系統流程測試

#### 5.1 模擬事故流程

1. **在樹莓派上啟動主程式**
   ```bash
   cd ~/Desktop/safety
   source venv/bin/activate
   ./start_vehicle.sh 60
   ```

2. **觀察系統行為**
   - GPS 取得事故位置
   - 視覺辨識偵測障礙物
   - 車輛自動往後移動
   - 達到目標距離後：
     - 升起警示牌
     - 播放警示音
     - 上報事故資料
     - 開始影像串流

3. **在前端查看**
   - 地圖上應該出現事故標記
   - 即時影像應該顯示
   - 事故列表應該更新

---

## 系統架構圖

```
┌─────────────────┐
│   樹莓派端      │
│  ┌───────────┐  │
│  │ main.py   │──┼──> 上報事故資料
│  │ web_api   │──┼──> 提供影像串流
│  └───────────┘  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   後端伺服器    │
│  ┌───────────┐  │
│  │ Flask API  │  │
│  │ MongoDB   │  │
│  └───────────┘  │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   前端網頁      │
│  ┌───────────┐  │
│  │ Google Map│  │
│  │ Video     │  │
│  │ Admin     │  │
│  └───────────┘  │
└─────────────────┘
```

---

## 常見問題快速解決

### 問題 1：樹莓派無法連接到後端

**解決方法：**
1. 確認後端伺服器正在運行
2. 確認 Ngrok 隧道已啟動
3. 檢查樹莓派 `.env` 中的 `BACKEND_URL` 是否正確
4. 測試連線：`curl https://your-ngrok-url.ngrok-free.app/api/health`

### 問題 2：前端無法顯示影像

**解決方法：**
1. 確認車載端 `web_api.py` 正在運行
2. 確認後端可以連接到車載端
3. 檢查 `backend/app.py` 中的車輛 URL 設定
4. 測試：`http://localhost:5000/api/video/vehicle_001?overlay=false`

### 問題 3：GPS 無法定位

**解決方法：**
1. 確認 GPS 模組已連接並供電
2. 確認 UART 已啟用：`sudo raspi-config`
3. 檢查序列埠：`ls -l /dev/tty*`
4. 測試 GPS：`sudo minicom -D /dev/ttyAMA0 -b 9600`

### 問題 4：攝影機無法開啟

**解決方法：**
1. 確認攝影機已連接：`lsusb`
2. 檢查攝影機索引：`v4l2-ctl --list-devices`
3. 更新 `.env` 中的 `CAMERA_INDEX`

---

## 下一步優化建議

1. **安全性**
   - 更改所有預設密碼和 Token
   - 使用 HTTPS（透過 Ngrok 或反向代理）
   - 實作更嚴格的 CORS 政策

2. **效能**
   - 使用 Gunicorn 運行 Flask（生產環境）
   - 設定 MongoDB 索引
   - 優化影像串流品質和頻寬

3. **功能擴展**
   - 添加多車輛支援
   - 實作歷史資料查詢
   - 添加通知系統（Email/SMS）

4. **監控**
   - 設定日誌記錄
   - 實作健康檢查端點
   - 監控系統資源使用

---

## 取得協助

如果遇到問題：
1. 查看 `TROUBLESHOOTING.md` 疑難排解指南
2. 查看 `docs/deployment.md` 詳細部署說明
3. 查看 `docs/api.md` API 文件
4. 檢查系統日誌
5. 提供完整的錯誤訊息和系統資訊

---

**祝使用順利！**

