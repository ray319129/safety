"""
伺服馬達控制模組
控制兩個 360 度伺服馬達升起警示牌
"""

import RPi.GPIO as GPIO
import time

class ServoController:
    """伺服馬達控制類別"""
    
    def __init__(self, servo1_pin: int = 12, servo2_pin: int = 13, frequency: int = 50):
        """
        初始化伺服控制器
        
        Args:
            servo1_pin: 伺服 1 GPIO 腳位
            servo2_pin: 伺服 2 GPIO 腳位
            frequency: PWM 頻率 (Hz)，標準伺服為 50Hz
        """
        # GPIO 設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.servo1_pin = servo1_pin
        self.servo2_pin = servo2_pin
        self.frequency = frequency
        
        # 設定 GPIO 為輸出
        GPIO.setup(self.servo1_pin, GPIO.OUT)
        GPIO.setup(self.servo2_pin, GPIO.OUT)
        
        # 建立 PWM 物件
        self.servo1_pwm = GPIO.PWM(self.servo1_pin, self.frequency)
        self.servo2_pwm = GPIO.PWM(self.servo2_pin, self.frequency)
        
        # 啟動 PWM（初始角度為 0）
        self.servo1_pwm.start(0)
        self.servo2_pwm.start(0)
        
        # 角度範圍（360 度伺服）
        self.min_angle = 0
        self.max_angle = 180
        
        # 預設角度
        self.raise_angle = 90
        self.lower_angle = 0
        
        print("伺服控制器已初始化")
    
    def set_angle(self, servo_num: int, angle: float):
        """
        設定伺服角度
        
        Args:
            servo_num: 伺服編號 (1 或 2)
            angle: 角度 (0-180)
        """
        try:
            # 確保 GPIO mode 已設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
        except RuntimeError:
            # 如果已經設定過，則忽略
            pass
        
        # 限制角度範圍
        angle = max(self.min_angle, min(self.max_angle, angle))
        
        # 計算 duty cycle
        # 對於 50Hz PWM：
        # 0 度 = 2.5% duty cycle
        # 90 度 = 7.5% duty cycle
        # 180 度 = 12.5% duty cycle
        duty_cycle = 2.5 + (angle / 180.0) * 10.0
        
        try:
            if servo_num == 1:
                self.servo1_pwm.ChangeDutyCycle(duty_cycle)
            elif servo_num == 2:
                self.servo2_pwm.ChangeDutyCycle(duty_cycle)
        except RuntimeError:
            # 如果 GPIO 已被清理，重新設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.servo1_pin, GPIO.OUT)
            GPIO.setup(self.servo2_pin, GPIO.OUT)
            # 重新建立 PWM 物件
            self.servo1_pwm = GPIO.PWM(self.servo1_pin, self.frequency)
            self.servo2_pwm = GPIO.PWM(self.servo2_pin, self.frequency)
            self.servo1_pwm.start(0)
            self.servo2_pwm.start(0)
            # 重新執行操作
            if servo_num == 1:
                self.servo1_pwm.ChangeDutyCycle(duty_cycle)
            elif servo_num == 2:
                self.servo2_pwm.ChangeDutyCycle(duty_cycle)
        
        # 等待伺服轉動
        time.sleep(0.3)
    
    def set_raise_angle(self, angle: float):
        """
        設定升起角度
        
        Args:
            angle: 角度 (0-180)
        """
        self.raise_angle = angle
    
    def set_lower_angle(self, angle: float):
        """
        設定降下角度
        
        Args:
            angle: 角度 (0-180)
        """
        self.lower_angle = angle
    
    def raise_sign(self):
        """升起警示牌"""
        print("升起警示牌...")
        self.set_angle(1, self.raise_angle)
        self.set_angle(2, self.raise_angle)
        print("警示牌已升起")
    
    def lower_sign(self):
        """降下警示牌"""
        print("降下警示牌...")
        self.set_angle(1, self.lower_angle)
        self.set_angle(2, self.lower_angle)
        print("警示牌已降下")
    
    def cleanup(self):
        """清理 GPIO 資源（只清理本模組，不調用 GPIO.cleanup）"""
        try:
            # 停止 PWM
            self.servo1_pwm.stop()
            self.servo2_pwm.stop()
        except Exception:
            # 如果 PWM 已被停止，則忽略錯誤
            pass
        print("伺服控制器已清理")

