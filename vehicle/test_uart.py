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