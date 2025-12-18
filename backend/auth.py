"""
管理員驗證模組
使用 Token-based 驗證
"""

import time
from functools import wraps
from typing import Optional
from flask import request, jsonify
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 確保導入正確的 PyJWT
# 先嘗試直接導入 PyJWT，避免與其他 jwt 模組衝突
try:
    # 方法 1: 直接導入 PyJWT（推薦）
    from jwt import encode as jwt_encode, decode as jwt_decode, ExpiredSignatureError, InvalidTokenError
    # 建立一個模擬物件以保持相容性
    class PyJWTWrapper:
        encode = staticmethod(jwt_encode)
        decode = staticmethod(jwt_decode)
        ExpiredSignatureError = ExpiredSignatureError
        InvalidTokenError = InvalidTokenError
    pyjwt = PyJWTWrapper()
except ImportError:
    try:
        # 方法 2: 使用別名導入
        import jwt as pyjwt
        # 驗證是否為正確的 PyJWT
        if not hasattr(pyjwt, 'encode'):
            raise ImportError('導入的 jwt 模組不是 PyJWT')
    except (ImportError, AttributeError):
        raise ImportError('請安裝 PyJWT: pip install PyJWT')

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
    try:
        payload = {
            'username': username,
            'exp': int(time.time()) + config.JWT_EXPIRATION
        }
        token = pyjwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
        # PyJWT 2.x 返回字串，確保返回字串類型
        if isinstance(token, bytes):
            return token.decode('utf-8')
        return str(token)
    except Exception as e:
        print(f'產生 Token 錯誤: {e}')
        raise

def verify_token(token: str) -> dict:
    """
    驗證 JWT Token
    
    Args:
        token: JWT Token
    
    Returns:
        dict: Token 內容或 None
    """
    try:
        payload = pyjwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return None
    except InvalidTokenError:
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

