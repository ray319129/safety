"""
管理員驗證模組
使用 Token-based 驗證
"""

import jwt
import time
from functools import wraps
from typing import Optional
from flask import request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import BackendConfig

config = BackendConfig()

def generate_token(username: str) -> str:
    """
    產生 JWT Token
    
    Args:
        username: 使用者名稱
    
    Returns:
        str: JWT Token
    """
    payload = {
        'username': username,
        'exp': int(time.time()) + config.JWT_EXPIRATION
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    """
    驗證 JWT Token
    
    Args:
        token: JWT Token
    
    Returns:
        dict: Token 內容或 None
    """
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def admin_required(f):
    """
    管理員驗證裝飾器
    
    Usage:
        @app.route('/admin/endpoint')
        @admin_required
        def admin_endpoint():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 從 Header 取得 Token
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': '缺少授權標頭'}), 401
        
        # 解析 Token (格式: Bearer <token>)
        try:
            token = auth_header.split(' ')[1]
        except IndexError:
            return jsonify({'error': '無效的授權格式'}), 401
        
        # 驗證 Token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': '無效或過期的 Token'}), 401
        
        # 檢查是否為管理員
        if payload.get('username') != config.ADMIN_USERNAME:
            return jsonify({'error': '權限不足'}), 403
        
        # 將使用者資訊加入 request
        request.admin_user = payload
        
        return f(*args, **kwargs)
    
    return decorated_function

def login(username: str, password: str) -> Optional[str]:
    """
    管理員登入
    
    Args:
        username: 使用者名稱
        password: 密碼
    
    Returns:
        Optional[str]: JWT Token 或 None
    """
    if username == config.ADMIN_USERNAME and password == config.ADMIN_PASSWORD:
        return generate_token(username)
    return None

