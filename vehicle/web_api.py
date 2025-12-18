"""
車載端 Web API 模組
提供即時影像串流服務（MJPEG）
支援接收參數控制是否顯示偵測框
"""

from flask import Flask, Response, request
import cv2
from vision_module import VisionModule
from config import VehicleConfig

app = Flask(__name__)
config = VehicleConfig()
vision = None
vision_module_instance = None  # 儲存主程式中的 vision 實例

def set_vision_instance(vision_instance):
    """設定視覺辨識模組實例（由主程式傳入）"""
    global vision_module_instance
    vision_module_instance = vision_instance

def initialize_vision():
    """初始化視覺辨識模組"""
    global vision
    # 優先使用主程式傳入的實例
    if vision_module_instance is not None:
        return vision_module_instance
    
    # 如果沒有傳入實例，則建立新的
    if vision is None:
        vision = VisionModule(
            config.CAMERA_INDEX,
            config.OBSTACLE_MIN_AREA,
            config.VISION_CONFIDENCE_THRESHOLD
        )
        vision.initialize_camera()
    return vision

def generate_frames(show_overlay: bool = False):
    """
    產生 MJPEG 影像串流
    
    Args:
        show_overlay: 是否顯示偵測框
    """
    vision_module = initialize_vision()
    vision_module.set_overlay(show_overlay)
    
    while True:
        result = vision_module.get_frame_with_detections()
        if result is None:
            continue
        
        frame, obstacles = result
        
        # 編碼為 JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # MJPEG 格式
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_stream')
def video_stream():
    """
    即時影像串流端點
    
    Query Parameters:
        overlay: true/false - 是否顯示偵測框
    """
    overlay = request.args.get('overlay', 'false').lower() == 'true'
    
    return Response(
        generate_frames(show_overlay=overlay),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def run_web_api(host='0.0.0.0', port=8080, debug=False):
    """
    啟動 Web API 伺服器
    
    Args:
        host: 主機地址
        port: 埠號
        debug: 除錯模式
    """
    print(f"啟動車載端 Web API 伺服器: http://{host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    run_web_api()

