"""
Flask 後端主應用程式
提供 REST API 端點
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import BackendConfig
from backend.models import AccidentModel, DeviceModel
from backend.auth import admin_required, login

app = Flask(__name__)
config = BackendConfig()

# 設定 CORS
CORS(app, origins=config.CORS_ORIGINS)

# 全域錯誤處理器
@app.errorhandler(Exception)
def handle_exception(e):
    """處理所有未捕獲的異常，確保返回 JSON"""
    print(f'未處理的異常: {e}')
    import traceback
    traceback.print_exc()
    return jsonify({'error': f'伺服器錯誤: {str(e)}'}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """
    管理員登入
    
    Request Body:
        {
            "username": "admin",
            "password": "admin123"
        }
    
    Returns:
        {
            "token": "jwt_token_here",
            "message": "登入成功"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': '缺少使用者名稱或密碼'}), 400
        
        token = login(data['username'], data['password'])
        
        if token:
            return jsonify({
                'token': token,
                'message': '登入成功'
            }), 200
        else:
            return jsonify({'error': '使用者名稱或密碼錯誤'}), 401
    except Exception as e:
        print(f'登入錯誤: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'登入處理失敗: {str(e)}'}), 500

@app.route('/api/report_accident', methods=['POST'])
def api_report_accident():
    """
    車子上報事故
    
    Request Body:
        {
            "latitude": 25.0330,
            "longitude": 121.5654,
            "timestamp": 1234567890,
            "image": "base64_encoded_image",
            "device_id": "vehicle_001"
        }
    
    Returns:
        {
            "accident_id": "accident_id_here",
            "message": "事故已記錄"
        }
    """
    data = request.get_json()
    
    # 驗證必要欄位
    required_fields = ['latitude', 'longitude']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'缺少必要欄位: {field}'}), 400
    
    try:
        accident_id = AccidentModel.create(data)
        return jsonify({
            'accident_id': accident_id,
            'message': '事故已記錄'
        }), 200
    except Exception as e:
        return jsonify({'error': f'建立事故記錄失敗: {str(e)}'}), 500

@app.route('/api/update_device', methods=['POST'])
def api_update_device():
    """
    更新車輛位置
    
    Request Body:
        {
            "device_id": "vehicle_001",
            "latitude": 25.0330,
            "longitude": 121.5654
        }
    
    Returns:
        {
            "message": "裝置位置已更新"
        }
    """
    data = request.get_json()
    
    if 'device_id' not in data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({'error': '缺少必要欄位'}), 400
    
    try:
        DeviceModel.update_position(
            data['device_id'],
            data['latitude'],
            data['longitude']
        )
        return jsonify({'message': '裝置位置已更新'}), 200
    except Exception as e:
        return jsonify({'error': f'更新裝置位置失敗: {str(e)}'}), 500

@app.route('/api/get_accidents', methods=['GET'])
def api_get_accidents():
    """
    一般使用者取得事故列表
    
    Query Parameters:
        active_only: true/false (預設: true)
    
    Returns:
        {
            "accidents": [
                {
                    "_id": "accident_id",
                    "latitude": 25.0330,
                    "longitude": 121.5654,
                    "timestamp": 1234567890,
                    "device_id": "vehicle_001",
                    "status": "active"
                },
                ...
            ]
        }
    """
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    try:
        accidents = AccidentModel.get_all(active_only=active_only)
        return jsonify({'accidents': accidents}), 200
    except Exception as e:
        return jsonify({'error': f'取得事故列表失敗: {str(e)}'}), 500

@app.route('/api/delete_accident/<accident_id>', methods=['DELETE'])
@admin_required
def api_delete_accident(accident_id):
    """
    管理員刪除事故（需要管理員權限）
    
    Returns:
        {
            "message": "事故已刪除"
        }
    """
    try:
        success = AccidentModel.delete(accident_id)
        if success:
            return jsonify({'message': '事故已刪除'}), 200
        else:
            return jsonify({'error': '事故不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'刪除事故失敗: {str(e)}'}), 500


@app.route('/api/clear_accidents', methods=['DELETE'])
@admin_required
def api_clear_accidents():
    """
    管理員一鍵清除所有事故記錄

    Returns:
        {
            "deleted": 10,
            "message": "所有事故已清除"
        }
    """
    try:
        deleted_count = AccidentModel.clear_all()
        return jsonify({
            'deleted': deleted_count,
            'message': '所有事故已清除'
        }), 200
    except Exception as e:
        return jsonify({'error': f'清除事故列表失敗: {str(e)}'}), 500

@app.route('/api/video/<device_id>', methods=['GET'])
def api_video(device_id):
    """
    即時影像串流（需支援 query parameter ?overlay=true/false）
    
    Query Parameters:
        overlay: true/false - 是否顯示偵測框
    
    Returns:
        MJPEG 影像串流
    """
    overlay = request.args.get('overlay', 'false').lower() == 'true'
    
    # 從車載端取得影像串流
    vehicle_url = f'http://{config.VEHICLE_HOST}:{config.VEHICLE_PORT}/video_stream?overlay={str(overlay).lower()}'
    
    try:
        # 代理影像串流
        response = requests.get(vehicle_url, stream=True, timeout=5)
        
        return Response(
            response.iter_content(chunk_size=1024),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive'
            }
        )
    except Exception as e:
        return jsonify({'error': f'無法取得影像串流: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """
    健康檢查端點
    
    Returns:
        {
            "status": "ok"
        }
    """
    return jsonify({'status': 'ok'}), 200

@app.route('/', methods=['GET'])
def index():
    """
    根路徑 - API 資訊頁面
    
    Returns:
        API 資訊 JSON
    """
    return jsonify({
        'name': '自動安全警示車後端 API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'health': '/api/health',
            'login': '/api/login',
            'report_accident': '/api/report_accident',
            'get_accidents': '/api/get_accidents',
            'delete_accident': '/api/delete_accident/<id>',
            'video_stream': '/api/video/<device_id>',
            'update_device': '/api/update_device'
        },
        'documentation': '/docs/api.md',
        'message': '請使用 /api/* 端點訪問 API 功能'
    }), 200

if __name__ == '__main__':
    print(f"啟動 Flask 後端伺服器: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    app.run(host=config.FLASK_HOST, port=config.FLASK_PORT, debug=config.FLASK_DEBUG)

