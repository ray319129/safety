# 硬體連接完整指南

## 系統架構總覽

```
┌─────────────────────────────────────────────────────────────┐
│                    Raspberry Pi 4 (主控)                      │
│  - GPS (NEO-M8) ──→ /dev/ttyAMA0 (UART)                      │
│  - 攝影機 (Logitech C920e) ──→ USB                           │
│  - BMduino (UART) ──→ GPIO 14/15 (/dev/serial0)             │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ UART (9600 baud)
                            │ GPIO 14 (TX) → BMduino D0 (RX)
                            │ GPIO 15 (RX) ← BMduino D1 (TX)
                            │ GND → GND
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              BMduino-UNO (BM53A367A)                        │
│  - L298N 馬達驅動 (雙馬達履帶)                                │
│  - 360度伺服馬達 x2 (警示牌)                                  │
│  - ISD1820 警報模組                                           │
│  - LED 燈條 (透過 MOSFET)                                     │
│  - 光感測模組 (自動亮度調整)                                   │
└─────────────────────────────────────────────────────────────┘
```

## 一、Raspberry Pi 4 腳位定義

### GPIO 腳位圖（40-pin Header）

```
     3.3V  [1]  [2]  5V
   GPIO 2  [3]  [4]  5V
   GPIO 3  [5]  [6]  GND
   GPIO 4  [7]  [8]  GPIO 14 (TXD) ← UART 發送（連 BMduino D0）
     GND  [9] [10]  GPIO 15 (RXD) ← UART 接收（連 BMduino D1）
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

### Raspberry Pi 使用的腳位

| 功能 | GPIO | Pin | 連接目標 | 說明 |
|------|------|-----|---------|------|
| UART TX | GPIO 14 | Pin 8 | BMduino D0 (RX) | 發送指令到 BMduino |
| UART RX | GPIO 15 | Pin 10 | BMduino D1 (TX) | 接收 BMduino 回應 |
| GPS UART | /dev/ttyAMA0 | - | GPS 模組 | GPS 資料接收 |
| USB | USB 2.0/3.0 | - | Logitech C920e | 攝影機連接 |
| GND | GND | Pin 6/9/14/20/25/30/34/39 | 所有模組 | 共地 |

---

## 二、BMduino-UNO (BM53A367A) 腳位定義

### 完整腳位連接表

| 功能 | BMduino 腳位 | 連接目標 | 說明 |
|------|-------------|---------|------|
| **UART 通信** | | | |
| UART RX | D0 | Raspberry Pi GPIO 14 (TX) | 接收 Pi 指令 |
| UART TX | D1 | Raspberry Pi GPIO 15 (RX) | 發送回應到 Pi |
| **L298N 馬達驅動（左馬達）** | | | |
| 左馬達方向 1 | D5 (PWM) | L298N IN1 | 控制左馬達方向 |
| 左馬達方向 2 | D6 (PWM) | L298N IN2 | 控制左馬達方向 |
| 左馬達速度 | D9 (PWM) | L298N ENA | PWM 速度控制 |
| **L298N 馬達驅動（右馬達）** | | | |
| 右馬達方向 1 | D10 (PWM) | L298N IN3 | 控制右馬達方向 |
| 右馬達方向 2 | D11 (PWM) | L298N IN4 | 控制右馬達方向 |
| 右馬達速度 | D3 (PWM) | L298N ENB | PWM 速度控制 |
| **伺服馬達** | | | |
| 伺服 1 | D4 (PWM) | 360度伺服 1 訊號線 | 警示牌升降控制 |
| 伺服 2 | D7 (PWM) | 360度伺服 2 訊號線 | 警示牌升降控制 |
| **警報模組** | | | |
| ISD1820 觸發 | D8 | ISD1820 PLAY 腳位 | 播放警報音 |
| **LED 控制** | | | |
| LED PWM | D12 (PWM) | MOSFET Gate | 控制 LED 亮度 |
| **光感測** | | | |
| 光感測輸入 | A0 | 光感測模組輸出 | 類比輸入（0-1023） |
| **電源與地** | | | |
| 電源 | VCC | 外部 5V | BMduino 電源 |
| 共地 | GND | 所有模組 GND | 共地連接 |

---

## 三、L298N 馬達驅動模組連接

### L298N 腳位說明

| L298N 腳位 | 連接目標 | 說明 |
|-----------|---------|------|
| IN1 | BMduino D5 | 左馬達方向控制 1 |
| IN2 | BMduino D6 | 左馬達方向控制 2 |
| ENA | BMduino D9 | 左馬達速度控制（PWM） |
| IN3 | BMduino D10 | 右馬達方向控制 1 |
| IN4 | BMduino D11 | 右馬達方向控制 2 |
| ENB | BMduino D3 | 右馬達速度控制（PWM） |
| OUT1 | 左馬達正極 | 左馬達輸出 1 |
| OUT2 | 左馬達負極 | 左馬達輸出 2 |
| OUT3 | 右馬達正極 | 右馬達輸出 1 |
| OUT4 | 右馬達負極 | 右馬達輸出 2 |
| VCC | 外部電源（5V/12V） | 馬達電源（依馬達規格） |
| GND | BMduino GND | 共地 |

### 馬達控制邏輯

| 指令 | IN1 | IN2 | ENA | 動作 |
|------|-----|-----|-----|------|
| 前進 | HIGH | LOW | PWM | 左馬達正轉 |
| 後退 | LOW | HIGH | PWM | 左馬達反轉 |
| 停止 | LOW | LOW | 0 | 左馬達停止 |

（右馬達同理，使用 IN3/IN4/ENB）

---

## 四、360度伺服馬達連接

### 伺服馬達連接

| 功能 | 連接 | 說明 |
|------|------|------|
| 伺服 1 訊號線 | BMduino D4 | PWM 訊號（50Hz） |
| 伺服 2 訊號線 | BMduino D7 | PWM 訊號（50Hz） |
| 伺服電源 | 外部 5V | 獨立供電（建議） |
| 伺服 GND | BMduino GND | 共地 |

**注意：**
- 360度伺服使用 PWM 控制轉速和方向
- 角度 0-90 度：正轉
- 角度 90-180 度：反轉
- 角度 90 度：停止

---

## 五、ISD1820 警報模組連接

| 功能 | 連接 | 說明 |
|------|------|------|
| PLAY 腳位 | BMduino D8 | 觸發播放（HIGH） |
| VCC | 5V | 電源 |
| GND | BMduino GND | 共地 |

**操作方式：**
- 將 PLAY 腳位拉高（HIGH）開始播放
- 拉低（LOW）停止播放

---

## 六、LED 燈條連接（透過 MOSFET）

### MOSFET 連接方式

| 功能 | 連接 | 說明 |
|------|------|------|
| MOSFET Gate | BMduino D12 (PWM) | PWM 控制訊號 |
| MOSFET Drain | LED 燈條負極 | LED 負極 |
| MOSFET Source | GND | 共地 |
| LED 燈條正極 | 外部電源（12V/5V） | 依燈條規格 |

**注意：**
- LED 燈條不能直接接 GPIO（電流不足）
- 必須使用 MOSFET 或專用驅動模組
- PWM 值 0-255 控制亮度

---

## 七、光感測模組連接

| 功能 | 連接 | 說明 |
|------|------|------|
| 類比輸出 | BMduino A0 | ADC 輸入（0-1023） |
| VCC | 3.3V 或 5V | 電源 |
| GND | BMduino GND | 共地 |

**功能：**
- 讀取環境光照強度
- 可用於自動調整 LED 亮度（韌體中可啟用）

---

## 八、GPS 模組 (NEO-M8) 連接

| 功能 | Raspberry Pi | GPS 模組 | 說明 |
|------|------------|---------|------|
| UART TX | GPIO 14 (TXD) | GPS RX | Pi 發送（通常不使用） |
| UART RX | GPIO 15 (RXD) | GPS TX | GPS 發送 NMEA 資料 |
| 共地 | GND | GND | 共地 |
| 電源 | 3.3V 或 5V | VCC | GPS 電源 |

**注意：** GPS 使用 `/dev/ttyAMA0`，與 BMduino 使用不同的 UART。

---

## 九、電源供應總覽

### 電源需求表

| 模組 | 電壓 | 電流 | 電源來源 | 備註 |
|------|------|------|---------|------|
| Raspberry Pi 4 | 5V | ~2.5A | USB-C 電源供應器 | 必須穩定供電 |
| BMduino-UNO | 5V | ~100mA | USB 或外部 5V | 可與 Pi 共用 |
| L298N + 雙馬達 | 5V/12V | 依馬達規格 | 外部電源（18650 電池組） | 建議獨立供電 |
| 伺服馬達 x2 | 5V | ~1A/個 | 外部 5V | 建議獨立供電 |
| ISD1820 | 5V | ~50mA | 外部 5V | 可與伺服共用 |
| LED 燈條 | 12V/5V | 依燈條規格 | 外部電源 | 依燈條規格 |
| GPS 模組 | 3.3V/5V | ~50mA | Raspberry Pi 3.3V/5V | 低功耗 |
| 光感測模組 | 3.3V/5V | ~10mA | Raspberry Pi 3.3V/5V | 低功耗 |

### 電源連接建議

1. **主電源（18650 電池組，4 顆串聯 = 14.8V）**
   - 降壓至 12V：供給 L298N 和 LED 燈條（如需要）
   - 降壓至 5V：供給伺服、ISD1820、BMduino

2. **Raspberry Pi 電源**
   - 使用專用 USB-C 電源供應器（5V, 3A）
   - 或從電池組降壓至 5V（需確保電流足夠）

3. **共地連接**
   - **所有模組的 GND 必須連接在一起**
   - 這是確保信號正確的關鍵

---

## 十、完整連接檢查清單

### ✅ UART 連接（Raspberry Pi ↔ BMduino）

- [ ] BMduino D0 (RX) → Raspberry Pi GPIO 14 (TX, Pin 8)
- [ ] BMduino D1 (TX) → Raspberry Pi GPIO 15 (RX, Pin 10)
- [ ] BMduino GND → Raspberry Pi GND（任意 GND 腳位）

### ✅ L298N 馬達驅動（雙馬達履帶）

- [ ] L298N IN1 → BMduino D5
- [ ] L298N IN2 → BMduino D6
- [ ] L298N ENA → BMduino D9
- [ ] L298N IN3 → BMduino D10
- [ ] L298N IN4 → BMduino D11
- [ ] L298N ENB → BMduino D3
- [ ] L298N GND → BMduino GND
- [ ] L298N VCC → 外部電源（5V/12V，依馬達規格）
- [ ] L298N OUT1/OUT2 → **左馬達**（兩條線）
- [ ] L298N OUT3/OUT4 → **右馬達**（兩條線）

### ✅ 伺服馬達（360度 x2）

- [ ] 伺服 1 訊號線 → BMduino D4
- [ ] 伺服 2 訊號線 → BMduino D7
- [ ] 伺服電源 → 外部 5V（注意電流需求，建議獨立供電）
- [ ] 伺服 GND → BMduino GND

### ✅ ISD1820 警報模組

- [ ] ISD1820 PLAY → BMduino D8
- [ ] ISD1820 GND → BMduino GND
- [ ] ISD1820 VCC → 5V

### ✅ LED 燈條（透過 MOSFET）

- [ ] MOSFET Gate → BMduino D12
- [ ] MOSFET Drain → LED 燈條負極
- [ ] MOSFET Source → GND
- [ ] LED 燈條正極 → 外部電源（12V/5V，依燈條規格）

### ✅ 光感測模組

- [ ] 光感測輸出 → BMduino A0
- [ ] 光感測 VCC → 3.3V 或 5V
- [ ] 光感測 GND → BMduino GND

### ✅ GPS 模組 (NEO-M8)

- [ ] GPS TX → Raspberry Pi GPIO 15 (RXD) 或 /dev/ttyAMA0
- [ ] GPS RX → Raspberry Pi GPIO 14 (TXD) 或 /dev/ttyAMA0
- [ ] GPS GND → Raspberry Pi GND
- [ ] GPS VCC → 3.3V 或 5V

### ✅ 攝影機 (Logitech C920e)

- [ ] USB 連接 → Raspberry Pi USB 埠

### ✅ 電源連接

- [ ] Raspberry Pi USB-C 電源供應器
- [ ] 18650 電池組（4 顆串聯）→ 降壓模組 → 各模組電源
- [ ] **所有模組 GND 共地連接**

---

## 十一、接線注意事項

1. **交叉連接**
   - UART 必須交叉連接（TX→RX, RX→TX）
   - 直連會導致無法通信

2. **共地連接**
   - 所有模組的 GND 必須連接在一起
   - 這是確保信號正確的關鍵

3. **電源分離**
   - 馬達和伺服建議使用獨立電源
   - 避免大電流干擾 Raspberry Pi

4. **PWM 腳位**
   - 確認使用支援 PWM 的腳位（D3, D4, D5, D6, D7, D9, D10, D11, D12）

5. **電流限制**
   - BMduino GPIO 最大電流約 20mA
   - 馬達、LED、伺服必須使用外部驅動

---

## 十二、測試步驟

### 1. 測試 UART 連接

```bash
# 在 Raspberry Pi 上
cd ~/Desktop/safety/vehicle
source ../venv/bin/activate
python3 test_uart.py
```

### 2. 測試馬達

透過 BMduino 發送指令：
```
M F 50  # 前進，速度 50
M S 0   # 停止
```

### 3. 測試伺服

```
S U  # 升起警示牌
S D  # 降下警示牌
```

### 4. 測試警報

```
A P 3  # 播放 3 秒
```

### 5. 測試 LED

```
L S 255  # 最大亮度
L S 0    # 關閉
```

### 6. 測試光感測

```
Q L  # 查詢光感測值
```

---

## 十三、故障排除

### UART 無法連接
- 檢查連接方向（交叉連接）
- 檢查共地連接
- 檢查波特率（9600）
- 檢查 UART 是否啟用（`enable_uart=1`）

### 馬達不轉動
- 檢查 L298N 電源
- 檢查馬達連接
- 檢查 PWM 訊號

### 伺服不轉動
- 檢查伺服電源（5V，足夠電流）
- 檢查訊號線連接
- 檢查 PWM 頻率（50Hz）

### 警報不響
- 檢查 ISD1820 電源
- 檢查 PLAY 腳位連接
- 確認韌體已正確燒錄

---

## 十四、安全注意事項

1. **電源極性**
   - 確認所有電源極性正確
   - 反接可能損壞元件

2. **電流保護**
   - 使用保險絲保護電路
   - 避免短路

3. **散熱**
   - L298N 可能發熱，注意散熱
   - 長時間運行需監控溫度

4. **絕緣**
   - 確保所有接線絕緣良好
   - 避免短路

---

## 十五、元件清單

### 必須元件

- [ ] Raspberry Pi 4 (4GB)
- [ ] BMduino-UNO (BM53A367A)
- [ ] Logitech C920e 攝影機
- [ ] NEO-M8 GPS 模組
- [ ] L298N 馬達驅動模組
- [ ] **DC 馬達 x2**（履帶用）
- [ ] 360度伺服馬達 x2
- [ ] ISD1820 警報模組
- [ ] LED 燈條 + MOSFET
- [ ] 光感測模組
- [ ] 18650 電池 x4 + 電池座
- [ ] 降壓模組（12V→5V）
- [ ] 杜邦線、跳線
- [ ] USB-C 電源供應器（5V, 3A）

### 可選元件

- [ ] 保險絲
- [ ] 散熱片（L298N）
- [ ] 電容（電源穩壓）
