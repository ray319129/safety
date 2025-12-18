# BMduino 韌體使用手冊

## 概述

本韌體適用於 **BMduino-UNO (BM53A367A)**，用於控制安全警示車的馬達、伺服、警報、LED 和光感測模組。

## 硬體連接

### UART 序列埠連接（Raspberry Pi ↔ BMduino）

**重要：使用硬體 UART 進行雙向通信**

| Raspberry Pi 4 | BMduino-UNO | 說明 |
|----------------|-------------|------|
| GPIO 14 (Pin 8, TXD) | D0 (RX) | Pi 發送 → BMduino 接收 |
| GPIO 15 (Pin 10, RXD) | D1 (TX) | BMduino 發送 → Pi 接收 |
| GND (Pin 6/9/14/20/25/30/34/39) | GND | 共地 |

**連接方式（交叉連接）：**
- BMduino TX (D1) → Pi RX (GPIO 15, Pin 10)
- BMduino RX (D0) → Pi TX (GPIO 14, Pin 8)
- 共地 GND → GND

**波特率：9600**

### 腳位定義

根據 BM53A367A 手冊（Arduino UNO 相容腳位）：

| 功能 | BMduino 腳位 | 說明 |
|------|-------------|------|
| 左馬達 IN1 | D5 (PWM) | L298N 左馬達方向控制 1 |
| 左馬達 IN2 | D6 (PWM) | L298N 左馬達方向控制 2 |
| 左馬達 ENA | D9 (PWM) | L298N 左馬達速度控制 |
| 右馬達 IN3 | D10 (PWM) | L298N 右馬達方向控制 1 |
| 右馬達 IN4 | D11 (PWM) | L298N 右馬達方向控制 2 |
| 右馬達 ENB | D3 (PWM) | L298N 右馬達速度控制 |
| 伺服 1 | D4 (PWM) | 360度伺服馬達 1 |
| 伺服 2 | D7 (PWM) | 360度伺服馬達 2 |
| 警報 (ISD1820) | D8 | ISD1820 PLAY 腳位 |
| LED 燈條 | D12 (PWM) | 透過 MOSFET 控制 |
| 光感測 | A0 | 類比輸入（0-1023） |

### 連接方式

1. **L298N 馬達驅動模組**
   - L298N IN1 → BMduino D5
   - L298N IN2 → BMduino D6
   - L298N ENA → BMduino D9
   - L298N IN3 → BMduino D10
   - L298N IN4 → BMduino D11
   - L298N ENB → BMduino D3
   - L298N GND → BMduino GND
   - L298N VCC → 外部 5V/12V（依馬達規格）

2. **伺服馬達（360度）**
   - 伺服 1 訊號線 → BMduino D4
   - 伺服 2 訊號線 → BMduino D7
   - 伺服電源 → 外部 5V（注意電流，必要時獨立供電）
   - 伺服 GND → BMduino GND

3. **ISD1820 警報模組**
   - ISD1820 PLAY → BMduino D8
   - ISD1820 GND → BMduino GND
   - ISD1820 VCC → 5V

4. **LED 燈條**
   - LED 控制線（MOSFET Gate）→ BMduino D12
   - LED 電源 → 外部 12V/5V（依燈條規格）
   - LED GND → BMduino GND

5. **光感測模組**
   - 光感測輸出 → BMduino A0
   - 光感測 VCC → 3.3V 或 5V
   - 光感測 GND → BMduino GND

6. **UART 序列埠連接（與 Raspberry Pi）**
   - BMduino D0 (RX) → Raspberry Pi GPIO 14 (TXD, Pin 8)
   - BMduino D1 (TX) → Raspberry Pi GPIO 15 (RXD, Pin 10)
   - BMduino GND → Raspberry Pi GND

## Raspberry Pi UART 設定

### 啟用 UART（Raspberry Pi OS）

1. **編輯 boot 設定檔**
   ```bash
   sudo nano /boot/config.txt
   ```

2. **確認以下設定（通常已預設啟用）**
   ```
   enable_uart=1
   ```

3. **禁用藍牙使用 UART（如果需要）**
   在 `/boot/config.txt` 中添加：
   ```
   dtoverlay=disable-bt
   ```
   注意：這會禁用藍牙，但確保 UART 可用

4. **重新啟動**
   ```bash
   sudo reboot
   ```

5. **確認 UART 裝置**
   ```bash
   ls -l /dev/serial0
   # 應該顯示指向 /dev/ttyAMA0 或 /dev/ttyS0
   ```

6. **設定權限（如果需要）**
   ```bash
   sudo usermod -a -G dialout $USER
   # 登出並重新登入以生效
   ```

## 燒錄步驟

### 方法 1：使用 Arduino IDE

1. **安裝 Arduino IDE**
   - 下載並安裝 [Arduino IDE](https://www.arduino.cc/en/software)
   - 版本建議 1.8.x 或 2.x

2. **安裝 BMduino 開發板支援**
   - 開啟 Arduino IDE
   - 檔案 → 偏好設定 → 額外的開發板管理員網址
   - 添加：`https://raw.githubusercontent.com/bestmodulescorp/BMduino_Board_Manager/main/package_bestmodules_index.json`
   - 工具 → 開發板 → 開發板管理員
   - 搜尋 "BMduino" 並安裝

3. **選擇開發板**
   - 工具 → 開發板 → BMduino Boards → BMduino-UNO (HT32F52367)

4. **選擇序列埠（燒錄時使用 USB）**
   - 連接 BMduino 到電腦（USB Type-C，僅用於燒錄）
   - 工具 → 序列埠 → 選擇對應的 COM 埠（Windows）或 /dev/ttyACM0（Linux/Mac）
   - **注意：燒錄完成後，將使用 UART 與 Raspberry Pi 連接，不再需要 USB**

5. **上傳程式**
   - 開啟 `bmduino_firmware.ino`
   - 點擊「上傳」按鈕（→）
   - 等待編譯和上傳完成

### 方法 2：使用 Keil IDE（進階）

參考 BM53A367A 使用手冊中的 Keil IDE 設定步驟。

## 通訊協定

BMduino 透過 UART 硬體序列埠（**9600 baud**）接收指令，指令格式為純文字，以 `\n` 結尾。

### 指令列表

| 指令 | 格式 | 說明 | 範例 |
|------|------|------|------|
| 馬達前進 | `M F <speed>` | 速度 0-100 | `M F 60` |
| 馬達後退 | `M B <speed>` | 速度 0-100 | `M B 40` |
| 馬達停止 | `M S 0` | 停止所有馬達 | `M S 0` |
| 升起警示牌 | `S U` | 兩個伺服轉到 90 度 | `S U` |
| 降下警示牌 | `S D` | 兩個伺服轉到 0 度 | `S D` |
| 播放警報 | `A P <secs>` | 播放秒數 1-10 | `A P 3` |
| 設定 LED 亮度 | `L S <value>` | 亮度 0-255 | `L S 128` |
| 查詢光感測 | `Q L` | 回傳 `L <value>` | `Q L` |

### 回應格式

- 查詢光感測：`L 523`（523 為 ADC 數值 0-1023）
- 其他指令：無回應（執行成功）

## 測試步驟

### 1. 序列埠監視器測試

1. 開啟 Arduino IDE 序列埠監視器（工具 → 序列埠監視器）
2. 設定：**9600 baud**，換行符號選擇「Newline」
3. 輸入測試指令：
   ```
   M F 50
   ```
   應該看到馬達開始轉動

### 2. Python 測試腳本

在 Raspberry Pi 上測試（使用 UART）：

```python
import serial
import time

# 連接 BMduino（使用 UART 硬體序列埠）
ser = serial.Serial('/dev/serial0', 9600, timeout=1)
time.sleep(2)  # 等待 BMduino 重置

# 測試馬達
ser.write(b'M F 60\n')
time.sleep(2)
ser.write(b'M S 0\n')

# 測試伺服
ser.write(b'S U\n')
time.sleep(2)
ser.write(b'S D\n')

# 測試警報
ser.write(b'A P 2\n')

# 測試 LED
ser.write(b'L S 255\n')
time.sleep(1)
ser.write(b'L S 0\n')

# 查詢光感測
ser.write(b'Q L\n')
response = ser.readline().decode('utf-8').strip()
print(f'光感測值: {response}')

ser.close()
```

## 故障排除

### 問題 1：UART 序列埠無法連接

- **檢查 UART 連接**：確認 GPIO 14/15 和 GND 連接正確（交叉連接）
- **檢查 UART 是否啟用**：確認 `/boot/config.txt` 中有 `enable_uart=1`
- **檢查埠號**：執行 `ls -l /dev/serial0` 確認指向正確的 UART 裝置
- **檢查權限**：確認使用者已加入 `dialout` 群組
- **檢查連接方向**：確認是交叉連接（TX→RX, RX→TX）

### 問題 2：指令無反應

- **檢查序列埠設定**：確認 baud rate 為 **9600**（不是 115200）
- **檢查指令格式**：確認指令以 `\n` 結尾
- **檢查硬體連接**：確認 UART 連接正確（交叉連接）
- **檢查共地**：確認 Raspberry Pi 和 BMduino 的 GND 已連接
- **檢查電源**：確認 BMduino 已上電（可透過其他腳位測試）

### 問題 3：馬達不轉動

- **檢查電源**：確認 L298N 有外部電源供應
- **檢查連接**：確認 IN1/IN2/ENA 連接正確
- **檢查馬達**：直接測試馬達是否正常

### 問題 4：伺服不轉動

- **檢查電源**：確認伺服有足夠的 5V 電源（可能需要獨立供電）
- **檢查訊號線**：確認訊號線連接正確
- **注意**：本韌體使用簡化的 PWM 控制，實際應用建議使用 Servo 函式庫

## 注意事項

1. **電源供應**：
   - BMduino 本身由 USB 供電（5V）
   - 馬達和 LED 需要外部電源（依規格選擇 5V/12V）
   - 所有模組必須共地（GND 連接在一起）

2. **電流限制**：
   - BMduino GPIO 腳位最大電流約 20mA
   - 馬達、LED、伺服需要較大電流，必須使用外部驅動（L298N、MOSFET）

3. **PWM 頻率**：
   - 本韌體使用 Arduino 預設 PWM 頻率
   - 伺服馬達建議使用 50Hz PWM，如需精確控制請使用 Servo 函式庫

4. **UART 序列埠通訊**：
   - 確保 Raspberry Pi 和 BMduino 使用相同的 baud rate（**9600**）
   - 使用硬體 UART（`/dev/serial0`），不是 USB 序列埠
   - 連接方式為交叉連接（TX→RX, RX→TX）
   - 必須共地（GND 連接）
   - 指令必須以 `\n` 結尾

## 進階功能

### 自動 LED 亮度調整

韌體支援根據光感測值自動調整 LED 亮度（目前未啟用，可自行修改程式碼啟用）。

### 自訂伺服角度

可以修改 `raiseSign()` 和 `lowerSign()` 函式中的角度值，以符合實際硬體需求。

## 技術支援

如有問題，請參考：
- BM53A367A 使用手冊
- Arduino IDE 文件
- HT32F52367 技術文件

