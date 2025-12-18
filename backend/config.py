"""
後端配置模組
"""

import os
from dotenv import load_dotenv

load_dotenv()

class BackendConfig:
    """後端配置類別"""
    
    # Flask 配置
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this')
    
    # MongoDB 配置
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'safety_db')
    
    # JWT 配置
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-jwt-secret-change-this')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION = 86400  # 24 小時
    
    # 管理員配置
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', 'admin-token-change-this')
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Ngrok 配置
    NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN', '')
    NGROK_DOMAIN = os.getenv('NGROK_DOMAIN', '')
    
    # 車載端配置（影像串流）
    VEHICLE_HOST = os.getenv('VEHICLE_HOST', 'localhost')
    VEHICLE_PORT = int(os.getenv('VEHICLE_PORT', '8080'))

