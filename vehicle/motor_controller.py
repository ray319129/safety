"""
履帶馬達控制模組
使用 L298N 驅動雙馬達履帶
實作 PWM 速度控制與方向控制
"""

import RPi.GPIO as GPIO
import time
from typing import Literal

class MotorController:
    """履帶馬達控制類別"""
    
    def __init__(self, 
                 left_pwm_pin: int = 18,
                 left_in1_pin: int = 17,
                 left_in2_pin: int = 27,
                 right_pwm_pin: int = 19,
                 right_in3_pin: int = 22,
                 right_in4_pin: int = 23):
        """
        初始化馬達控制器
        
        Args:
            left_pwm_pin: 左馬達 PWM 腳位
            left_in1_pin: 左馬達 IN1 腳位
            left_in2_pin: 左馬達 IN2 腳位
            right_pwm_pin: 右馬達 PWM 腳位
            right_in3_pin: 右馬達 IN3 腳位
            right_in4_pin: 右馬達 IN4 腳位
        """
        # GPIO 設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # 左馬達腳位
        self.left_pwm_pin = left_pwm_pin
        self.left_in1_pin = left_in1_pin
        self.left_in2_pin = left_in2_pin
        
        # 右馬達腳位
        self.right_pwm_pin = right_pwm_pin
        self.right_in3_pin = right_in3_pin
        self.right_in4_pin = right_in4_pin
        
        # 設定 GPIO 為輸出
        GPIO.setup(self.left_in1_pin, GPIO.OUT)
        GPIO.setup(self.left_in2_pin, GPIO.OUT)
        GPIO.setup(self.left_pwm_pin, GPIO.OUT)
        GPIO.setup(self.right_in3_pin, GPIO.OUT)
        GPIO.setup(self.right_in4_pin, GPIO.OUT)
        GPIO.setup(self.right_pwm_pin, GPIO.OUT)
        
        # 建立 PWM 物件（頻率 1000 Hz）
        self.left_pwm = GPIO.PWM(self.left_pwm_pin, 1000)
        self.right_pwm = GPIO.PWM(self.right_pwm_pin, 1000)
        
        # 啟動 PWM（初始速度為 0）
        self.left_pwm.start(0)
        self.right_pwm.start(0)
        
        print("馬達控制器已初始化")
    
    def set_left_motor(self, direction: Literal['forward', 'backward', 'stop'], speed: int = 60):
        """
        控制左馬達
        
        Args:
            direction: 方向 ('forward', 'backward', 'stop')
            speed: 速度 (0-100)
        """
        try:
            # 確保 GPIO mode 已設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
        except RuntimeError:
            # 如果已經設定過，則忽略
            pass
        
        speed = max(0, min(100, speed))  # 限制速度範圍
        
        try:
            if direction == 'forward':
                GPIO.output(self.left_in1_pin, GPIO.HIGH)
                GPIO.output(self.left_in2_pin, GPIO.LOW)
                self.left_pwm.ChangeDutyCycle(speed)
            elif direction == 'backward':
                GPIO.output(self.left_in1_pin, GPIO.LOW)
                GPIO.output(self.left_in2_pin, GPIO.HIGH)
                self.left_pwm.ChangeDutyCycle(speed)
            else:  # stop
                GPIO.output(self.left_in1_pin, GPIO.LOW)
                GPIO.output(self.left_in2_pin, GPIO.LOW)
                self.left_pwm.ChangeDutyCycle(0)
        except RuntimeError:
            # 如果 GPIO 已被清理，重新設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.left_in1_pin, GPIO.OUT)
            GPIO.setup(self.left_in2_pin, GPIO.OUT)
            # 重新執行操作
            if direction == 'forward':
                GPIO.output(self.left_in1_pin, GPIO.HIGH)
                GPIO.output(self.left_in2_pin, GPIO.LOW)
                self.left_pwm.ChangeDutyCycle(speed)
            elif direction == 'backward':
                GPIO.output(self.left_in1_pin, GPIO.LOW)
                GPIO.output(self.left_in2_pin, GPIO.HIGH)
                self.left_pwm.ChangeDutyCycle(speed)
            else:  # stop
                GPIO.output(self.left_in1_pin, GPIO.LOW)
                GPIO.output(self.left_in2_pin, GPIO.LOW)
                self.left_pwm.ChangeDutyCycle(0)
    
    def set_right_motor(self, direction: Literal['forward', 'backward', 'stop'], speed: int = 60):
        """
        控制右馬達
        
        Args:
            direction: 方向 ('forward', 'backward', 'stop')
            speed: 速度 (0-100)
        """
        try:
            # 確保 GPIO mode 已設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
        except RuntimeError:
            # 如果已經設定過，則忽略
            pass
        
        speed = max(0, min(100, speed))  # 限制速度範圍
        
        try:
            if direction == 'forward':
                GPIO.output(self.right_in3_pin, GPIO.HIGH)
                GPIO.output(self.right_in4_pin, GPIO.LOW)
                self.right_pwm.ChangeDutyCycle(speed)
            elif direction == 'backward':
                GPIO.output(self.right_in3_pin, GPIO.LOW)
                GPIO.output(self.right_in4_pin, GPIO.HIGH)
                self.right_pwm.ChangeDutyCycle(speed)
            else:  # stop
                GPIO.output(self.right_in3_pin, GPIO.LOW)
                GPIO.output(self.right_in4_pin, GPIO.LOW)
                self.right_pwm.ChangeDutyCycle(0)
        except RuntimeError:
            # 如果 GPIO 已被清理，重新設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.right_in3_pin, GPIO.OUT)
            GPIO.setup(self.right_in4_pin, GPIO.OUT)
            # 重新執行操作
            if direction == 'forward':
                GPIO.output(self.right_in3_pin, GPIO.HIGH)
                GPIO.output(self.right_in4_pin, GPIO.LOW)
                self.right_pwm.ChangeDutyCycle(speed)
            elif direction == 'backward':
                GPIO.output(self.right_in3_pin, GPIO.LOW)
                GPIO.output(self.right_in4_pin, GPIO.HIGH)
                self.right_pwm.ChangeDutyCycle(speed)
            else:  # stop
                GPIO.output(self.right_in3_pin, GPIO.LOW)
                GPIO.output(self.right_in4_pin, GPIO.LOW)
                self.right_pwm.ChangeDutyCycle(0)
    
    def move_forward(self, speed: int = 60):
        """
        前進
        
        Args:
            speed: 速度 (0-100)
        """
        self.set_left_motor('forward', speed)
        self.set_right_motor('forward', speed)
    
    def move_backward(self, speed: int = 60):
        """
        後退
        
        Args:
            speed: 速度 (0-100)
        """
        self.set_left_motor('backward', speed)
        self.set_right_motor('backward', speed)
    
    def turn_left(self, speed: int = 40):
        """
        左轉（原地旋轉）
        
        Args:
            speed: 速度 (0-100)
        """
        self.set_left_motor('backward', speed)
        self.set_right_motor('forward', speed)
    
    def turn_right(self, speed: int = 40):
        """
        右轉（原地旋轉）
        
        Args:
            speed: 速度 (0-100)
        """
        self.set_left_motor('forward', speed)
        self.set_right_motor('backward', speed)
    
    def turn_left_soft(self, speed: int = 60):
        """
        軟左轉（左馬達減速）
        
        Args:
            speed: 速度 (0-100)
        """
        self.set_left_motor('forward', speed // 2)
        self.set_right_motor('forward', speed)
    
    def turn_right_soft(self, speed: int = 60):
        """
        軟右轉（右馬達減速）
        
        Args:
            speed: 速度 (0-100)
        """
        self.set_left_motor('forward', speed)
        self.set_right_motor('forward', speed // 2)
    
    def stop(self):
        """停止所有馬達"""
        try:
            # 確保 GPIO mode 已設定
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            self.set_left_motor('stop')
            self.set_right_motor('stop')
        except RuntimeError:
            # 如果 GPIO 已被清理，重新設定並停止馬達
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            # 重新設定 GPIO 腳位
            GPIO.setup(self.left_in1_pin, GPIO.OUT)
            GPIO.setup(self.left_in2_pin, GPIO.OUT)
            GPIO.setup(self.right_in3_pin, GPIO.OUT)
            GPIO.setup(self.right_in4_pin, GPIO.OUT)
            # 設定為停止狀態
            GPIO.output(self.left_in1_pin, GPIO.LOW)
            GPIO.output(self.left_in2_pin, GPIO.LOW)
            GPIO.output(self.right_in3_pin, GPIO.LOW)
            GPIO.output(self.right_in4_pin, GPIO.LOW)
            # 停止 PWM
            try:
                self.left_pwm.ChangeDutyCycle(0)
                self.right_pwm.ChangeDutyCycle(0)
            except Exception:
                pass
        except Exception:
            # 其他錯誤則忽略
            pass
    
    def avoid_obstacle(self, direction: Literal['left', 'right'], speed: int = 50):
        """
        避障動作
        
        Args:
            direction: 避障方向 ('left', 'right')
            speed: 速度 (0-100)
        """
        if direction == 'left':
            # 左轉避障
            self.turn_left_soft(speed)
        else:
            # 右轉避障
            self.turn_right_soft(speed)
    
    def cleanup(self):
        """清理 GPIO 資源（只清理本模組，不調用 GPIO.cleanup）"""
        try:
            # 停止馬達
            self.stop()
            # 停止 PWM
            self.left_pwm.stop()
            self.right_pwm.stop()
        except Exception:
            # 如果 PWM 已被停止，則忽略錯誤
            pass
        print("馬達控制器已清理")

