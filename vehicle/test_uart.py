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