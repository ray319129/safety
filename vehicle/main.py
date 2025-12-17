"""
自動安全警示車主程式
整合所有模組，實作完整系統流程
"""

import time
import sys
import signal
import requests
import base64
import cv2
import threading
from typing import Optional, Tuple

from config import VehicleConfig
from gps_module import GPSModule
from vision_module import VisionModule
from motor_controller import MotorController
from servo_controller import ServoController
from alarm import AlarmModule
from web_api import run_web_api
from bmduino_controller import BMduinoController

class SafetyVehicle:
    """自動安全警示車主類別"""
    
    def __init__(self):
        """初始化所有模組"""
        self.config = VehicleConfig()
        self.running = False
        
        # 初始化各模組
        self.gps = GPSModule(
            self.config.GPS_SERIAL_PORT,
            self.config.GPS_BAUDRATE
        )
        
        self.vision = VisionModule(
            self.config.CAMERA_INDEX,
            self.config.OBSTACLE_MIN_AREA,
            self.config.VISION_CONFIDENCE_THRESHOLD
        )
        
        # 與 BMduino 建立序列連線，用於控制馬達、伺服、警報與 LED
        try:
            self.bm = BMduinoController(
                self.config.BMDUINO_PORT,
                self.config.BMDUINO_BAUDRATE
            )
            print(f\"BMduino 控制器已就緒: {self.config.BMDUINO_PORT} @ {self.config.BMDUINO_BAUDRATE}\")
        except Exception as e:
            print(f\"警告: 無法初始化 BMduino 控制器: {e}\")
            self.bm = None
        
        self.motor = MotorController(
            self.config.MOTOR_LEFT_PWM_PIN,
            self.config.MOTOR_LEFT_IN1_PIN,
            self.config.MOTOR_LEFT_IN2_PIN,
            self.config.MOTOR_RIGHT_PWM_PIN,
            self.config.MOTOR_RIGHT_IN3_PIN,
            self.config.MOTOR_RIGHT_IN4_PIN
        )
        
        self.servo = ServoController(
            self.config.SERVO_1_PIN,
            self.config.SERVO_2_PIN
        )
        self.servo.set_raise_angle(self.config.SERVO_RAISE_ANGLE)
        self.servo.set_lower_angle(self.config.SERVO_LOWER_ANGLE)
        
        self.alarm = AlarmModule(self.config.ALARM_PIN)
        
        # 狀態變數
        self.target_distance = 0
        self.current_speed_limit = None
        self.original_direction = 'backward'  # 預設往後移動
        
        # 註冊信號處理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """處理中斷信號"""
        print("\n收到中斷信號，正在關閉...")
        self.cleanup()
        sys.exit(0)
    
    def determine_road_type(self) -> int:
        """
        判斷道路類型並回傳目標距離
        
        Returns:
            int: 目標距離（公尺）
        """
        # 這裡可以整合 GPS 地圖 API 或使用者輸入
        # 目前使用預設值或從配置讀取
        # 實際應用中可以：
        # 1. 使用 Google Maps API 查詢速限
        # 2. 使用 OpenStreetMap 資料
        # 3. 使用者手動輸入
        
        # 預設使用城市道路距離
        return self.config.CITY_ROAD_DISTANCE
    
    def determine_target_distance(self, speed_limit: Optional[int] = None) -> int:
        """
        根據速限判斷目標距離
        
        Args:
            speed_limit: 速限（km/h），None 則使用預設
        
        Returns:
            int: 目標距離（公尺）
        """
        if speed_limit is None:
            # 使用預設道路類型
            return self.determine_road_type()
        
        if speed_limit >= 100:  # 高速公路
            return self.config.HIGHWAY_DISTANCE
        elif speed_limit > 60:  # 快速道路或速限 > 60
            return self.config.EXPRESSWAY_DISTANCE
        elif speed_limit >= 50:  # 速限 50-60
            return self.config.CITY_ROAD_DISTANCE
        else:  # 速限 < 50
            return self.config.LOCAL_ROAD_DISTANCE
    
    def initialize_system(self) -> bool:
        """
        初始化系統
        
        Returns:
            bool: 初始化是否成功
        """
        print("=" * 50)
        print("自動安全警示車系統啟動")
        print("=" * 50)
        
        # 初始化 GPS
        print("\n[1/5] 初始化 GPS 模組...")
        if not self.gps.connect():
            print("警告: GPS 連接失敗，將使用模擬模式")
        else:
            if not self.gps.wait_for_fix(timeout=30):
                print("警告: GPS 定位失敗，將使用模擬模式")
        
        # 初始化視覺辨識
        print("\n[2/5] 初始化視覺辨識模組...")
        if not self.vision.initialize_camera():
            print("錯誤: 攝影機初始化失敗")
            return False
        
        # 馬達控制器已在 __init__ 中初始化
        print("\n[3/6] 馬達控制器已就緒")
        
        # 伺服控制器已在 __init__ 中初始化
        print("\n[4/6] 伺服控制器已就緒")
        
        # 警示音模組已在 __init__ 中初始化
        print("\n[5/6] 警示音模組已就緒")
        
        # 啟動 Web API 伺服器（在背景執行緒中）
        print("\n[6/6] 啟動 Web API 伺服器...")
        try:
            # 將 vision 實例傳給 web_api
            from web_api import set_vision_instance
            set_vision_instance(self.vision)
            
            self.web_api_thread = threading.Thread(
                target=run_web_api,
                args=(self.config.WEB_API_HOST, self.config.WEB_API_PORT, False),
                daemon=True
            )
            self.web_api_thread.start()
            print(f"Web API 伺服器已啟動: http://{self.config.WEB_API_HOST}:{self.config.WEB_API_PORT}")
        except Exception as e:
            print(f"警告: Web API 伺服器啟動失敗: {e}")
        
        print("\n系統初始化完成！")
        self.running = True
        return True
    
    def set_accident_location(self) -> bool:
        """
        設定事故位置（起點）
        
        Returns:
            bool: 是否成功設定
        """
        print("\n設定事故位置...")
        
        if self.gps.serial_connection and self.gps.serial_connection.is_open:
            if self.gps.set_start_position():
                print("事故位置已記錄")
                return True
            else:
                print("警告: 無法取得 GPS 位置，使用模擬位置")
                # 使用模擬位置
                self.gps.start_latitude = 25.0330
                self.gps.start_longitude = 121.5654
                self.gps.current_latitude = 25.0330
                self.gps.current_longitude = 121.5654
                self.gps.last_position = (25.0330, 121.5654)
                return True
        else:
            print("警告: GPS 未連接，使用模擬位置")
            self.gps.start_latitude = 25.0330
            self.gps.start_longitude = 121.5654
            self.gps.current_latitude = 25.0330
            self.gps.current_longitude = 121.5654
            self.gps.last_position = (25.0330, 121.5654)
            return True
    
    def report_accident(self, injured_count: int = 0) -> bool:
        """
        上報事故資料到後端
        
        Returns:
            bool: 是否成功上報
        """
        print("\n上報事故資料到後端...")
        
        # 取得目前位置
        position = self.gps.get_start_position()
        if not position:
            position = (self.gps.start_latitude, self.gps.start_longitude)
        
        # 取得影像
        frame = self.vision.get_frame()
        image_data = None
        if frame is not None:
            # 將影像編碼為 base64
            _, buffer = cv2.imencode('.jpg', frame)
            image_data = base64.b64encode(buffer).decode('utf-8')
        
        # 準備資料
        accident_data = {
            'latitude': position[0],
            'longitude': position[1],
            'timestamp': time.time(),
            'image': image_data,
            'device_id': 'vehicle_001',
            # 受傷人數（由視覺模組偵測到的人形數量）
            'injured_count': max(0, int(injured_count))
        }
        
        try:
            # 發送 POST 請求
            response = requests.post(
                f"{self.config.BACKEND_URL}/api/report_accident",
                json=accident_data,
                headers={'Authorization': f'Bearer {self.config.API_TOKEN}'},
                timeout=10
            )
            
            if response.status_code == 200:
                print("事故資料上報成功")
                return True
            else:
                print(f"事故資料上報失敗: {response.status_code}")
                return False
        except Exception as e:
            print(f"事故資料上報錯誤: {e}")
            return False
    
    def avoid_obstacle(self, direction: str):
        """
        執行避障動作
        
        Args:
            direction: 避障方向 ('left', 'right')
        """
        print(f"執行避障動作: {direction}")
        
        # 執行避障轉向
        self.motor.avoid_obstacle(direction, self.config.MOTOR_SPEED_AVOID)
        
        # 避障時間（可根據實際情況調整）
        time.sleep(1.0)
        
        # 回歸原路徑（繼續往後移動）
        print("回歸原路徑")
        self.motor.move_backward(self.config.MOTOR_SPEED_NORMAL)
    
    def run_movement_loop(self):
        """執行移動循環（包含避障）"""
        print(f"\n開始移動，目標距離: {self.target_distance} 公尺")
        print("按 Ctrl+C 可隨時停止")
        
        self.running = True
        last_distance = 0.0
        
        while self.running:
            # 更新 GPS 距離
            current_distance = self.gps.update_distance()
            
            # 顯示進度
            if abs(current_distance - last_distance) > 1.0:  # 每 1 公尺更新一次
                print(f"已移動距離: {current_distance:.2f} 公尺 / {self.target_distance} 公尺")
                last_distance = current_distance
            
            # 檢查是否達到目標距離
            if current_distance >= self.target_distance:
                print(f"\n已達到目標距離: {current_distance:.2f} 公尺")
                self.motor.stop()
                break
            
            # 視覺辨識偵測障礙物
            frame = self.vision.get_frame()
            if frame is not None:
                obstacles = self.vision.detect_obstacles(frame)
                
                if obstacles:
                    print(f"偵測到 {len(obstacles)} 個障礙物")
                    # 計算避障路徑
                    avoidance_direction = self.vision.calculate_avoidance_path(frame, obstacles)
                    
                    if avoidance_direction != 'forward':
                        self.avoid_obstacle(avoidance_direction)
                    else:
                        # 繼續移動
                        self.motor.move_backward(self.config.MOTOR_SPEED_NORMAL)
                else:
                    # 無障礙物，繼續移動
                    self.motor.move_backward(self.config.MOTOR_SPEED_NORMAL)
            else:
                # 無法取得影像，繼續移動
                self.motor.move_backward(self.config.MOTOR_SPEED_NORMAL)
            
            # 短暫延遲
            time.sleep(0.1)
    
    def execute_safety_protocol(self, speed_limit: Optional[int] = None):
        """
        執行完整安全警示流程
        
        Args:
            speed_limit: 道路速限（km/h）
        """
        try:
            # 1. 初始化系統
            if not self.initialize_system():
                print("系統初始化失敗")
                return
            
            # 2. 設定事故位置
            if not self.set_accident_location():
                print("無法設定事故位置")
                return
            
            # 3. 程式啟動後立即上報一次事故（受傷人數 0）
            print("\n程式啟動，立即上報初始事故（injured_count=0）...")
            self.report_accident(injured_count=0)
            
            # 4. 進入偵測人形的監控迴圈
            print("\n開始人體偵測監控，偵測到人時會再次上報事故...")
            self.running = True
            last_report_time = 0.0
            report_interval = 10.0  # 至少間隔 10 秒再上報一次，避免過於頻繁
            
            while self.running:
                result = self.vision.get_frame_with_detections()
                if result is not None:
                    # frame 目前僅用於即時影像串流疊加，這裡只需要人物列表計算人數
                    _, people = result
                    injured_count = len(people)
                    
                    if injured_count > 0:
                        now = time.time()
                        if now - last_report_time >= report_interval:
                            print(f"偵測到人形 {injured_count} 個，進行事故上報...")
                            self.report_accident(injured_count=injured_count)
                            last_report_time = now
                            
                            # 透過 BMduino 觸發實體警示（若可用）
                            if self.bm is not None:
                                try:
                                    self.bm.raise_sign()
                                    self.bm.play_alarm(3.0)
                                    self.bm.set_led_brightness(255)
                                except Exception as e:
                                    print(f"BMduino 警示觸發失敗: {e}")
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n使用者中斷")
        except Exception as e:
            print(f"\n發生錯誤: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.cleanup()
    
    def cleanup(self):
        """清理所有資源"""
        print("\n清理系統資源...")
        self.running = False
        
        # 停止馬達與降下警示牌（優先透過 BMduino 控制）
        try:
            if hasattr(self, 'bm') and self.bm is not None:
                self.bm.stop_motor()
                self.bm.lower_sign()
        except Exception as e:
            print(f"BMduino 清理失敗: {e}")
        
        # 清理各模組（不調用 GPIO.cleanup，統一在最後清理）
        self.vision.release_camera()
        self.gps.disconnect()
        
        # 若仍在使用樹莓派 GPIO 控制，可保留原本的清理邏輯
        try:
            self.motor.cleanup()
            self.servo.cleanup()
            self.alarm.cleanup()
        except Exception:
            pass
        
        # 關閉 BMduino 連線
        try:
            if hasattr(self, 'bm') and self.bm is not None:
                self.bm.close()
        except Exception:
            pass
        
        print("系統已關閉")

def main():
    """主函式"""
    vehicle = SafetyVehicle()
    
    # 可以從命令列參數取得速限，或使用預設值
    speed_limit = None
    if len(sys.argv) > 1:
        try:
            speed_limit = int(sys.argv[1])
        except ValueError:
            print("警告: 無效的速限參數，使用預設值")
    
    # 執行安全警示流程
    vehicle.execute_safety_protocol(speed_limit)

if __name__ == '__main__':
    main()

