"""
警示音控制模組
使用 ISD1820 模組播放警示音
"""

import RPi.GPIO as GPIO
import time

class AlarmModule:
    """警示音模組類別"""
    
    def __init__(self, alarm_pin: int = 24):
        """
        初始化警示音模組
        
        Args:
            alarm_pin: ISD1820 PLAY 腳位連接的 GPIO 腳位
        """
        # GPIO 設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        self.alarm_pin = alarm_pin
        
        # 設定 GPIO 為輸出
        GPIO.setup(self.alarm_pin, GPIO.OUT)
        GPIO.output(self.alarm_pin, GPIO.LOW)
        
        print("警示音模組已初始化")
    
    def play_alarm(self, duration: float = 3.0):
        """
        播放警示音
        
        Args:
            duration: 播放持續時間（秒）
        """
        print(f"播放警示音 ({duration} 秒)...")
        
        # ISD1820 觸發播放：將 PLAY 腳位拉高
        GPIO.output(self.alarm_pin, GPIO.HIGH)
        
        # 等待播放完成
        time.sleep(duration)
        
        # 停止播放：將 PLAY 腳位拉低
        GPIO.output(self.alarm_pin, GPIO.LOW)
        
        print("警示音播放完成")
    
    def play_alarm_loop(self, times: int = 3, interval: float = 1.0):
        """
        循環播放警示音
        
        Args:
            times: 播放次數
            interval: 每次播放間隔（秒）
        """
        for i in range(times):
            self.play_alarm()
            if i < times - 1:
                time.sleep(interval)
    
    def cleanup(self):
        """清理 GPIO 資源"""
        GPIO.output(self.alarm_pin, GPIO.LOW)
        GPIO.cleanup()
        print("警示音模組已清理")

