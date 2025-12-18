# BMduino UART 連接設定指南

## 概述

本文件說明如何將 Raspberry Pi 4 與 BMduino-UNO (BM53A367A) 透過 UART 硬體序列埠進行雙向通信。

## 硬體連接

### 連接方式（交叉連接）

| Raspberry Pi 4 | BMduino-UNO | 說明 |
|----------------|-------------|------|
| GPIO 14 (Pin 8, TXD) | D0 (RX) | Pi 發送 → BMduino 接收 |
| GPIO 15 (Pin 10, RXD) | D1 (TX) | BMduino 發送 → Pi 接收 |
| GND (任意 GND 腳位) | GND | 共地（必須連接）|

**重要：這是交叉連接**
- BMduino TX (D1) → Pi RX (GPIO 15, Pin 10)
- BMduino RX (D0) → Pi TX (GPIO 14, Pin 8)
- 共地 GND → GND

### Raspberry Pi 4 GPIO 腳位圖

```
     3.3V  [1]  [2]  5V
   GPIO 2  [3]  [4]  5V
   GPIO 3  [5]  [6]  GND
   GPIO 4  [7]  [8]  GPIO 14 (TXD) ← 連接到 BMduino D0 (RX)
     GND  [9] [10]  GPIO 15 (RXD) ← 連接到 BMduino D1 (TX)
  GPIO 17 [11] [12] GPIO 18
  GPIO 27 [13] [14] GND
  GPIO 22 [15] [16] GPIO 23
     3.3V [17] [18] GPIO 24
  GPIO 10 [19] [20] GND
   GPIO 9 [21] [22] GPIO 25
  GPIO 11 [23] [24] GPIO 8
     GND [25] [26] GPIO 7
   GPIO 0 [27] [28] GPIO 1
   GPIO 5 [29] [30] GND
   GPIO 6 [31] [32] GPIO 12
  GPIO 13 [33] [34] GND
  GPIO 19 [35] [36] GPIO 16
  GPIO 26 [37] [38] GPIO 20
     GND [39] [40] GPIO 21
```

## Raspberry Pi 設定步驟

### 步驟 1：啟用 UART

1. **編輯 boot 設定檔**
   ```bash
   sudo nano /boot/config.txt
   ```

2. **確認或添加以下設定**
   ```
   enable_uart=1
   ```

3. **（可選）禁用藍牙使用 UART**
   如果需要確保 UART 完全可用，可以禁用藍牙：
   ```
   dtoverlay=disable-bt
   ```
   **注意：** 這會禁用藍牙功能，但確保 UART 可用

4. **重新啟動**
   ```bash
   sudo reboot
   ```

### 步驟 2：確認 UART 裝置

重新啟動後，檢查 UART 裝置：

```bash
# 檢查 /dev/serial0 是否存在
ls -l /dev/serial0

# 應該顯示類似：
# lrwxrwxrwx 1 root root 7 Dec 17 13:00 /dev/serial0 -> ttyAMA0
# 或
# lrwxrwxrwx 1 root root 5 Dec 17 13:00 /dev/serial0 -> ttyS0
```

### 步驟 3：設定權限

將使用者加入 `dialout` 群組以獲得序列埠存取權限：

```bash
sudo usermod -a -G dialout $USER
```

**重要：** 需要登出並重新登入（或重新啟動）才能生效。

### 步驟 4：測試 UART 連接

建立測試腳本 `test_uart.py`：

```python
import serial
import time

try:
    # 連接 BMduino（使用 UART）
    ser = serial.Serial('/dev/serial0', 9600, timeout=1)
    print("UART 連接成功！")
    
    # 等待 BMduino 重置
    time.sleep(2)
    
    # 發送測試指令
    print("發送測試指令: M F 50")
    ser.write(b'M F 50\n')
    time.sleep(2)
    
    # 停止馬達
    print("停止馬達")
    ser.write(b'M S 0\n')
    
    # 查詢光感測
    print("查詢光感測值")
    ser.write(b'Q L\n')
    time.sleep(0.5)
    
    # 讀取回應
    if ser.in_waiting > 0:
        response = ser.readline().decode('utf-8').strip()
        print(f"BMduino 回應: {response}")
    
    ser.close()
    print("測試完成！")
    
except serial.SerialException as e:
    print(f"UART 連接失敗: {e}")
    print("請檢查：")
    print("1. UART 是否已啟用（enable_uart=1）")
    print("2. 硬體連接是否正確（交叉連接）")
    print("3. 權限是否正確（使用者是否在 dialout 群組）")
except Exception as e:
    print(f"錯誤: {e}")
```

執行測試：

```bash
cd ~/Desktop/safety/vehicle
source ../venv/bin/activate
python3 test_uart.py
```

## BMduino 韌體設定

### 確認波特率

確認 `bmduino_firmware.ino` 中的設定：

```cpp
Serial.begin(9600);  // 必須是 9600
```

### 燒錄韌體

1. 使用 USB 連接 BMduino 到電腦
2. 使用 Arduino IDE 燒錄 `bmduino_firmware.ino`
3. 燒錄完成後，**斷開 USB 連接**
4. 使用 UART 連接 BMduino 到 Raspberry Pi

## 配置檔案設定

在 Raspberry Pi 上編輯 `vehicle/.env`：

```env
# BMduino UART 配置
BMDUINO_PORT=/dev/serial0
BMDUINO_BAUDRATE=9600
```

## 故障排除

### 問題 1：找不到 /dev/serial0

**解決方法：**
```bash
# 檢查 UART 是否啟用
cat /boot/config.txt | grep enable_uart

# 如果沒有，添加 enable_uart=1 並重新啟動
sudo nano /boot/config.txt
# 添加：enable_uart=1
sudo reboot
```

### 問題 2：權限被拒絕

**解決方法：**
```bash
# 將使用者加入 dialout 群組
sudo usermod -a -G dialout $USER

# 登出並重新登入，或重新啟動
```

### 問題 3：無法接收資料

**檢查項目：**
1. 確認連接方向正確（交叉連接）
2. 確認共地（GND）已連接
3. 確認波特率為 9600（不是 115200）
4. 確認 BMduino 已上電

### 問題 4：資料錯誤或亂碼

**可能原因：**
- 波特率不匹配（確認兩邊都是 9600）
- 連接方向錯誤（確認是交叉連接）
- 電源不穩定

## 注意事項

1. **USB vs UART**
   - 燒錄時使用 USB 連接
   - 運行時使用 UART 連接
   - 不要同時連接 USB 和 UART

2. **電源供應**
   - BMduino 需要獨立電源（不依賴 USB）
   - 確保所有模組共地（GND 連接）

3. **連接方向**
   - 必須是交叉連接（TX→RX, RX→TX）
   - 直連會導致無法通信

4. **波特率**
   - 固定為 9600，不要更改
   - Raspberry Pi 和 BMduino 必須使用相同的波特率

## 測試清單

- [ ] UART 已啟用（`enable_uart=1`）
- [ ] `/dev/serial0` 存在且可存取
- [ ] 使用者已加入 `dialout` 群組
- [ ] 硬體連接正確（交叉連接 + 共地）
- [ ] BMduino 韌體已燒錄（9600 baud）
- [ ] `.env` 設定正確（`/dev/serial0`, `9600`）
- [ ] 測試腳本可以成功通信

