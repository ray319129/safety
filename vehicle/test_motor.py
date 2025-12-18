"""
L298N 馬達驅動測試腳本
透過 BMduino 控制雙馬達，確認接線是否正確
"""

import time
import sys
from bmduino_controller import BMduinoController
from config import VehicleConfig

def test_motor_control():
    """測試馬達控制功能"""
    config = VehicleConfig()
    
    print("=" * 60)
    print("L298N 馬達驅動測試")
    print("=" * 60)
    print(f"BMduino 埠: {config.BMDUINO_PORT}")
    print(f"波特率: {config.BMDUINO_BAUDRATE}")
    print()
    
    # 初始化 BMduino
    try:
        bm = BMduinoController(config.BMDUINO_PORT, config.BMDUINO_BAUDRATE)
        print("✓ BMduino 連接成功")
    except Exception as e:
        print(f"✗ BMduino 連接失敗: {e}")
        print("\n請檢查：")
        print("1. BMduino 是否已燒錄韌體")
        print("2. UART 連接是否正確（交叉連接）")
        print("3. 序列埠權限是否正確")
        return False
    
    print("\n" + "=" * 60)
    print("測試 1: 雙馬達同步前進（基本功能測試）")
    print("=" * 60)
    print("預期：兩個馬達同時正轉，履帶應該向前移動")
    print("注意：請觀察履帶移動方向，確認接線正確")
    input("按 Enter 開始測試（3 秒）...")
    
    try:
        print("發送指令: 雙馬達前進（速度 50）")
        bm.set_motor('F', 50)  # 'F' = Forward
        time.sleep(3)
        bm.stop_motor()
        print("✓ 前進測試完成")
        print("  請確認：履帶是否向前移動？")
    except Exception as e:
        print(f"✗ 前進測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試 2: 雙馬達同步後退")
    print("=" * 60)
    print("預期：兩個馬達同時反轉，履帶應該向後移動")
    print("注意：請觀察履帶移動方向，確認接線正確")
    input("按 Enter 開始測試（3 秒）...")
    
    try:
        print("發送指令: 雙馬達後退（速度 50）")
        bm.set_motor('B', 50)  # 'B' = Backward
        time.sleep(3)
        bm.stop_motor()
        print("✓ 後退測試完成")
        print("  請確認：履帶是否向後移動？")
    except Exception as e:
        print(f"✗ 後退測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試 3: 速度控制（PWM 測試）")
    print("=" * 60)
    print("預期：馬達速度應該逐漸增加")
    input("按 Enter 開始測試...")
    
    try:
        speeds = [20, 40, 60, 80, 100]
        for speed in speeds:
            print(f"速度: {speed}%")
            bm.set_motor('F', speed)
            time.sleep(2)
        bm.stop_motor()
        print("✓ 速度控制測試完成")
        print("  請確認：速度是否有明顯變化？")
    except Exception as e:
        print(f"✗ 速度控制測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試 4: 停止功能")
    print("=" * 60)
    print("預期：馬達應該立即停止")
    input("按 Enter 開始測試（先運轉 2 秒，然後停止）...")
    
    try:
        print("馬達運轉中...")
        bm.set_motor('F', 50)
        time.sleep(2)
        print("停止馬達...")
        bm.stop_motor()
        time.sleep(1)
        print("✓ 停止功能測試完成")
        print("  請確認：馬達是否立即停止？")
    except Exception as e:
        print(f"✗ 停止功能測試失敗: {e}")
    
    # 清理
    try:
        bm.stop_motor()
        bm.close()
        print("\n✓ BMduino 連接已關閉")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)
    print("\n檢查清單：")
    print("□ 雙馬達可以同步前進（履帶向前移動）")
    print("□ 雙馬達可以同步後退（履帶向後移動）")
    print("□ 速度控制正常（PWM 有效，速度有明顯變化）")
    print("□ 停止功能正常（馬達可以立即停止）")
    print("\n接線檢查（根據硬體連接指南）：")
    print("□ L298N IN1 → BMduino D5")
    print("□ L298N IN2 → BMduino D6")
    print("□ L298N ENA → BMduino D9")
    print("□ L298N IN3 → BMduino D10")
    print("□ L298N IN4 → BMduino D11")
    print("□ L298N ENB → BMduino D3")
    print("□ L298N OUT1/OUT2 → 左馬達（兩條線）")
    print("□ L298N OUT3/OUT4 → 右馬達（兩條線）")
    print("□ L298N VCC → 外部電源（12V，從 LM2596 降壓模組）")
    print("□ L298N GND → BMduino GND（共地）")
    print("\n如果以上項目都正常，表示 L298N 和馬達連接正確！")
    print("\n注意：如果履帶移動方向與預期相反，可以：")
    print("  1. 交換馬達的兩條線（OUT1↔OUT2 或 OUT3↔OUT4）")
    print("  2. 或修改韌體中的馬達方向邏輯")
    
    return True

if __name__ == '__main__':
    try:
        test_motor_control()
    except KeyboardInterrupt:
        print("\n\n測試被使用者中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

