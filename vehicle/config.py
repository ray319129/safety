"""
車載端配置模組
讀取環境變數並提供配置參數
"""

import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class VehicleConfig:
    """車載端配置類別"""
    
    # GPS 配置
    GPS_SERIAL_PORT = os.getenv('GPS_SERIAL_PORT', '/dev/ttyAMA0')
    GPS_BAUDRATE = int(os.getenv('GPS_BAUDRATE', '9600'))
    
    # 馬達控制 GPIO 腳位
    MOTOR_LEFT_PWM_PIN = int(os.getenv('MOTOR_LEFT_PWM_PIN', '18'))
    MOTOR_LEFT_IN1_PIN = int(os.getenv('MOTOR_LEFT_IN1_PIN', '17'))
    MOTOR_LEFT_IN2_PIN = int(os.getenv('MOTOR_LEFT_IN2_PIN', '27'))
    MOTOR_RIGHT_PWM_PIN = int(os.getenv('MOTOR_RIGHT_PWM_PIN', '19'))
    MOTOR_RIGHT_IN3_PIN = int(os.getenv('MOTOR_RIGHT_IN3_PIN', '22'))
    MOTOR_RIGHT_IN4_PIN = int(os.getenv('MOTOR_RIGHT_IN4_PIN', '23'))
    
    # 伺服控制 GPIO 腳位
    SERVO_1_PIN = int(os.getenv('SERVO_1_PIN', '12'))
    SERVO_2_PIN = int(os.getenv('SERVO_2_PIN', '13'))
    SERVO_RAISE_ANGLE = int(os.getenv('SERVO_RAISE_ANGLE', '90'))
    SERVO_LOWER_ANGLE = int(os.getenv('SERVO_LOWER_ANGLE', '0'))
    
    # 警示音 GPIO 腳位
    ALARM_PIN = int(os.getenv('ALARM_PIN', '24'))
    
    # 後端 API 配置
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
    API_TOKEN = os.getenv('API_TOKEN', 'your_api_token_here')
    
    # 視覺辨識配置
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', '0'))
    VISION_CONFIDENCE_THRESHOLD = float(os.getenv('VISION_CONFIDENCE_THRESHOLD', '0.5'))
    OBSTACLE_MIN_AREA = int(os.getenv('OBSTACLE_MIN_AREA', '500'))
    
    # 道路類型與距離配置（單位：公尺）
    HIGHWAY_DISTANCE = int(os.getenv('HIGHWAY_DISTANCE', '100'))
    EXPRESSWAY_DISTANCE = int(os.getenv('EXPRESSWAY_DISTANCE', '80'))
    CITY_ROAD_DISTANCE = int(os.getenv('CITY_ROAD_DISTANCE', '50'))
    LOCAL_ROAD_DISTANCE = int(os.getenv('LOCAL_ROAD_DISTANCE', '30'))
    
    # 馬達速度配置（PWM 值 0-100）
    MOTOR_SPEED_NORMAL = 60
    MOTOR_SPEED_TURN = 40
    MOTOR_SPEED_AVOID = 50

