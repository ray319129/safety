"""
伺服馬達測試腳本
透過 BMduino 控制兩個 360度伺服馬達，確認警示牌升降功能
"""

import time
import sys
from bmduino_controller import BMduinoController
from config import VehicleConfig

def test_servo_control():
    """測試伺服馬達控制功能"""
    config = VehicleConfig()
    
    print("=" * 60)
    print("伺服馬達測試（360度伺服 x2）")
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
    print("測試 1: 降下警示牌（初始狀態）")
    print("=" * 60)
    print("預期：兩個伺服馬達應該轉到降下位置（角度 0）")
    input("按 Enter 開始測試...")
    
    try:
        print("發送指令: 降下警示牌")
        bm.lower_sign()
        time.sleep(2)  # 等待伺服動作完成
        print("✓ 降下測試完成")
        print("  請確認：警示牌是否已降下？")
    except Exception as e:
        print(f"✗ 降下測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試 2: 升起警示牌")
    print("=" * 60)
    print("預期：兩個伺服馬達應該轉到升起位置（角度 90）")
    input("按 Enter 開始測試...")
    
    try:
        print("發送指令: 升起警示牌")
        bm.raise_sign()
        time.sleep(2)  # 等待伺服動作完成
        print("✓ 升起測試完成")
        print("  請確認：警示牌是否已升起？")
    except Exception as e:
        print(f"✗ 升起測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試 3: 重複升降測試（3 次循環）")
    print("=" * 60)
    print("預期：警示牌應該可以重複升降")
    input("按 Enter 開始測試...")
    
    try:
        for i in range(3):
            print(f"\n循環 {i+1}/3:")
            print("  降下...")
            bm.lower_sign()
            time.sleep(2)
            print("  升起...")
            bm.raise_sign()
            time.sleep(2)
        print("\n✓ 重複升降測試完成")
        print("  請確認：警示牌是否可以正常重複升降？")
    except Exception as e:
        print(f"✗ 重複升降測試失敗: {e}")
    
    print("\n" + "=" * 60)
    print("測試 4: 最終狀態（降下）")
    print("=" * 60)
    print("預期：警示牌應該降下，回到初始狀態")
    input("按 Enter 開始測試...")
    
    try:
        print("發送指令: 降下警示牌")
        bm.lower_sign()
        time.sleep(2)
        print("✓ 最終狀態測試完成")
    except Exception as e:
        print(f"✗ 最終狀態測試失敗: {e}")
    
    # 清理
    try:
        bm.close()
        print("\n✓ BMduino 連接已關閉")
    except:
        pass
    
    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)
    print("\n檢查清單：")
    print("□ 降下功能正常（警示牌降下）")
    print("□ 升起功能正常（警示牌升起）")
    print("□ 重複升降正常（可以多次操作）")
    print("\n接線檢查（根據硬體連接指南）：")
    print("□ 伺服 1 訊號線 → BMduino D4")
    print("□ 伺服 2 訊號線 → BMduino D7")
    print("□ 伺服電源 → LM2596 降壓模組 5V 輸出")
    print("□ 伺服 GND → BMduino GND（共地）")
    print("\n如果以上項目都正常，表示伺服馬達連接正確！")
    print("\n注意：")
    print("- 如果伺服不轉動，檢查電源（5V，足夠電流）")
    print("- 如果轉動方向相反，可以交換伺服訊號線或修改韌體角度")
    print("- 360度伺服通常使用 PWM 控制轉速和方向")
    
    return True

if __name__ == '__main__':
    try:
        test_servo_control()
    except KeyboardInterrupt:
        print("\n\n測試被使用者中斷")
        sys.exit(0)
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

