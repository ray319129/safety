# 疑難排解指南

## 依賴安裝問題

### 問題 1: 樹莓派 externally-managed-environment 錯誤

**錯誤訊息：**
```
error: externally-managed-environment
This environment is externally managed
```

**原因：** 較新版本的 Raspberry Pi OS 使用 PEP 668 規範，不允許直接在系統 Python 環境中安裝套件，必須使用虛擬環境。

**解決方法：**

1. **方法一：使用修正後的安裝腳本（推薦）**
   ```bash
   cd ~/Desktop/safety/vehicle
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```
   腳本會自動建立虛擬環境並在虛擬環境中安裝套件。

2. **方法二：手動建立虛擬環境**
   ```bash
   # 確保已安裝 python3-venv
   sudo apt install -y python3-venv python3-full
   
   # 在專案根目錄建立虛擬環境
   cd ~/Desktop/safety
   python3 -m venv venv
   
   # 啟動虛擬環境
   source venv/bin/activate
   
   # 安裝依賴
   cd vehicle
   pip install --upgrade pip setuptools wheel
   pip install -r ../requirements.txt
   ```

3. **方法三：使用 --break-system-packages（不推薦）**
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```
   ⚠️ 警告：這可能會破壞系統 Python 環境，不建議使用。

**使用虛擬環境執行程式：**
```bash
# 啟動虛擬環境
cd ~/Desktop/safety
source venv/bin/activate

# 執行主程式
cd vehicle
python3 main.py 60
```

### 問題 2: Windows 編碼錯誤

**錯誤訊息：**
```
UnicodeDecodeError: 'cp950' codec can't decode byte 0x8c in position 4: illegal multibyte sequence
```

**原因：** Windows 使用 cp950 編碼，但 requirements.txt 檔案可能包含 UTF-8 字元。

**解決方法：**

1. **方法一：使用安裝腳本（推薦）**
   ```bash
   cd backend
   install_dependencies.bat
   ```

2. **方法二：手動安裝**
   ```bash
   cd backend
   python -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. **方法三：設定環境變數**
   ```bash
   # 設定 Python 使用 UTF-8 編碼
   set PYTHONIOENCODING=utf-8
   pip install -r requirements.txt
   ```

### 問題 3: 樹莓派 setuptools 錯誤

**錯誤訊息：**
```
BackendUnavailable: Cannot import 'setuptools.build_meta'
```

**原因：** 缺少或版本過舊的 setuptools。

**解決方法：**

1. **方法一：使用安裝腳本（推薦）**
   ```bash
   cd vehicle
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

2. **方法二：手動安裝**
   ```bash
   cd vehicle
   python3 -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

3. **方法三：在虛擬環境中安裝**
   ```bash
   source venv/bin/activate
   python3 -m pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

## GPS 連接問題

### 問題：GPS 無法連接或讀取資料

**可能原因：**
1. UART 未啟用
2. 序列埠路徑錯誤
3. GPS 模組電源或天線問題
4. 權限問題

**解決方法：**

1. **檢查 UART 是否啟用**
   ```bash
   sudo raspi-config
   # 選擇 Interface Options → Serial Port → 啟用
   ```

2. **檢查序列埠**
   ```bash
   ls -l /dev/tty*
   # 應該看到 /dev/ttyAMA0 或 /dev/ttyS0
   ```

3. **測試 GPS 連接**
   ```bash
   sudo minicom -D /dev/ttyAMA0 -b 9600
   # 應該看到 NMEA 資料流
   ```

4. **檢查權限**
   ```bash
   sudo usermod -a -G dialout $USER
   # 登出並重新登入
   ```

5. **更新 .env 檔案中的序列埠路徑**
   ```env
   GPS_SERIAL_PORT=/dev/ttyAMA0  # 或 /dev/ttyS0
   ```

## 攝影機問題

### 問題：攝影機無法開啟

**可能原因：**
1. 攝影機未連接
2. 攝影機索引錯誤
3. 權限問題
4. 其他程式佔用攝影機

**解決方法：**

1. **檢查攝影機連接**
   ```bash
   lsusb
   # 應該看到 Logitech 或 USB 攝影機
   ```

2. **列出可用攝影機**
   ```bash
   v4l2-ctl --list-devices
   ```

3. **測試攝影機**
   ```bash
   python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.isOpened() else 'Failed')"
   ```

4. **更新 .env 檔案中的攝影機索引**
   ```env
   CAMERA_INDEX=0  # 嘗試 0, 1, 2...
   ```

## MongoDB 連接問題

### 問題：無法連接 MongoDB

**可能原因：**
1. MongoDB 服務未啟動
2. 連接字串錯誤
3. 防火牆阻擋

**解決方法：**

1. **檢查 MongoDB 服務狀態**
   ```bash
   # Linux
   sudo systemctl status mongodb
   
   # Windows
   # 檢查服務管理員中的 MongoDB 服務
   ```

2. **啟動 MongoDB**
   ```bash
   # Linux
   sudo systemctl start mongodb
   
   # Windows
   # 在服務管理員中啟動 MongoDB
   ```

3. **檢查連接字串**
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   ```

4. **測試連接**
   ```bash
   python3 -c "from pymongo import MongoClient; c = MongoClient('mongodb://localhost:27017/'); print(c.server_info())"
   ```

## 影像串流問題

### 問題：前端無法顯示即時影像

**可能原因：**
1. 車載端 web_api.py 未運行
2. 後端無法連接到車載端
3. 網路連接問題
4. CORS 設定問題

**解決方法：**

1. **確認車載端影像串流服務運行**
   ```bash
   cd vehicle
   python3 web_api.py
   # 應該在 http://localhost:8080/video_stream 提供串流
   ```

2. **檢查後端配置**
   ```python
   # backend/app.py 中的車輛 URL 應該正確
   vehicle_url = f'http://vehicle_ip:8080/video_stream?overlay={overlay}'
   ```

3. **測試影像串流**
   ```bash
   # 在瀏覽器中開啟
   http://localhost:5000/api/video/vehicle_001?overlay=false
   ```

4. **檢查 CORS 設定**
   ```python
   # backend/app.py
   CORS_ORIGINS = '*'  # 開發環境
   ```

## GPIO 權限問題

### 問題：無法控制 GPIO 腳位

**錯誤訊息：**
```
Permission denied
```

**解決方法：**

1. **將使用者加入 gpio 群組**
   ```bash
   sudo usermod -a -G gpio $USER
   # 登出並重新登入
   ```

2. **使用 sudo 執行（不推薦）**
   ```bash
   sudo python3 main.py
   ```

## 其他常見問題

### 問題：模組導入錯誤

**錯誤訊息：**
```
ModuleNotFoundError: No module named 'xxx'
```

**解決方法：**

1. **確認在虛擬環境中**
   ```bash
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

2. **重新安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

### 問題：版本不相容

**錯誤訊息：**
```
AttributeError: module 'pkgutil' has no attribute 'ImpImporter'
ERROR: Failed to build 'numpy'
```

**原因：** Python 3.13 是較新版本，舊版本的 numpy (如 1.24.3) 不相容。

**解決方法：**

1. **檢查 Python 版本**
   ```bash
   python3 --version
   # Python 3.13 需要 numpy >= 1.26.0
   ```

2. **更新 requirements.txt**
   - 已更新為使用相容版本：`numpy>=1.26.0`
   - 重新執行安裝腳本

3. **手動安裝相容版本**
   ```bash
   source venv/bin/activate
   pip install --upgrade pip setuptools wheel
   pip install numpy>=1.26.0
   pip install -r requirements.txt
   ```

4. **如果仍有問題，使用預編譯的 wheel**
   ```bash
   # 樹莓派可以使用 piwheels 預編譯套件
   pip install --only-binary :all: numpy opencv-python
   ```

## 取得協助

如果以上方法都無法解決問題，請：

1. 檢查日誌檔案
2. 確認所有硬體連接正確
3. 檢查環境變數設定
4. 查看 GitHub Issues
5. 提供完整的錯誤訊息和系統資訊

