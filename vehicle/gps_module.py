"""
GPS 定位與距離計算模組
使用 NEO-M8 GPS 模組取得位置資訊
實作 Haversine 公式計算距離
"""

import serial
import pynmea2
import time
import math
from typing import Optional, Tuple
from geopy.distance import geodesic

class GPSModule:
    """GPS 定位模組類別"""
    
    def __init__(self, serial_port: str = '/dev/ttyAMA0', baudrate: int = 9600):
        """
        初始化 GPS 模組
        
        Args:
            serial_port: 序列埠路徑
            baudrate: 傳輸速率
        """
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.serial_connection = None
        self.current_latitude = None
        self.current_longitude = None
        self.start_latitude = None
        self.start_longitude = None
        self.total_distance = 0.0
        self.last_position = None
        
    def connect(self) -> bool:
        """
        連接 GPS 模組
        
        Returns:
            bool: 連接是否成功
        """
        try:
            self.serial_connection = serial.Serial(
                self.serial_port,
                self.baudrate,
                timeout=1
            )
            print(f"GPS 模組已連接: {self.serial_port}")
            return True
        except Exception as e:
            print(f"GPS 連接失敗: {e}")
            return False
    
    def disconnect(self):
        """斷開 GPS 連接"""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("GPS 模組已斷開")
    
    def read_gps_data(self) -> Optional[Tuple[float, float]]:
        """
        讀取 GPS 資料並解析位置
        
        Returns:
            Optional[Tuple[float, float]]: (緯度, 經度) 或 None
        """
        if not self.serial_connection or not self.serial_connection.is_open:
            return None
        
        try:
            # 讀取 NMEA 資料
            line = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
            
            if not line:
                return None
            
            # 同時支援 GP/GN 前綴與 RMC/GGA 訊息
            if line.startswith(('$GPRMC', '$GNRMC', '$GPGGA', '$GNGGA')):
                msg = pynmea2.parse(line)

                # 如果是 RMC 訊息，檢查狀態（A=有效，V=無效）
                if hasattr(msg, 'status') and msg.status != 'A':
                    # 例如你現在看到的 $GNRMC,,V,... → 代表尚未定位成功
                    return None
                
                if hasattr(msg, 'latitude') and hasattr(msg, 'longitude'):
                    lat = msg.latitude
                    lon = msg.longitude
                    # 過濾 0,0 假定位
                    if lat and lon and (lat != 0.0 or lon != 0.0):
                        self.current_latitude = lat
                        self.current_longitude = lon
                        return (self.current_latitude, self.current_longitude)
            
            return None
        except Exception as e:
            print(f"GPS 讀取錯誤: {e}")
            return None
    
    def wait_for_fix(self, timeout: int = 300) -> bool:
        """
        等待 GPS 取得定位
        
        Args:
            timeout: 超時時間（秒）
        
        Returns:
            bool: 是否成功取得定位
        """
        start_time = time.time()
        print("等待 GPS 定位...")
        
        while time.time() - start_time < timeout:
            position = self.read_gps_data()
            if position:
                print(f"GPS 定位成功: {position[0]:.6f}, {position[1]:.6f}")
                return True
            time.sleep(1)
        
        print("GPS 定位超時")
        return False
    
    def set_start_position(self):
        """設定起始位置（事故發生位置）"""
        position = self.read_gps_data()
        if position:
            self.start_latitude = position[0]
            self.start_longitude = position[1]
            self.last_position = position
            self.total_distance = 0.0
            print(f"起始位置已設定: {self.start_latitude:.6f}, {self.start_longitude:.6f}")
            return True
        return False
    
    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        使用 Haversine 公式計算兩點間距離（公尺）
        
        Args:
            lat1: 起點緯度
            lon1: 起點經度
            lat2: 終點緯度
            lon2: 終點經度
        
        Returns:
            float: 距離（公尺）
        """
        # 使用 geopy 的 geodesic 函式（更精確）
        return geodesic((lat1, lon1), (lat2, lon2)).meters
    
    def update_distance(self) -> float:
        """
        更新累積移動距離
        
        Returns:
            float: 累積距離（公尺）
        """
        current_position = self.read_gps_data()
        
        if current_position and self.last_position:
            # 計算與上次位置的距離
            segment_distance = self.haversine_distance(
                self.last_position[0],
                self.last_position[1],
                current_position[0],
                current_position[1]
            )
            
            # 累積總距離
            self.total_distance += segment_distance
            self.last_position = current_position
        
        elif current_position and not self.last_position:
            # 第一次更新
            self.last_position = current_position
        
        return self.total_distance
    
    def get_distance_from_start(self) -> float:
        """
        取得從起始位置到目前位置的距離
        
        Returns:
            float: 距離（公尺）
        """
        if not self.start_latitude or not self.start_longitude:
            return 0.0
        
        current_position = self.read_gps_data()
        if not current_position:
            return self.total_distance  # 回傳累積距離
        
        return self.haversine_distance(
            self.start_latitude,
            self.start_longitude,
            current_position[0],
            current_position[1]
        )
    
    def get_current_position(self) -> Optional[Tuple[float, float]]:
        """
        取得目前位置
        
        Returns:
            Optional[Tuple[float, float]]: (緯度, 經度) 或 None
        """
        return self.read_gps_data()
    
    def get_start_position(self) -> Optional[Tuple[float, float]]:
        """
        取得起始位置
        
        Returns:
            Optional[Tuple[float, float]]: (緯度, 經度) 或 None
        """
        if self.start_latitude and self.start_longitude:
            return (self.start_latitude, self.start_longitude)
        return None

