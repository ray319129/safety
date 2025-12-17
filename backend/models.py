"""
MongoDB 資料模型
"""

from datetime import datetime
from typing import Optional
from pymongo import MongoClient
from pymongo.collection import Collection
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import BackendConfig

class Database:
    """資料庫連接類別"""
    
    def __init__(self):
        """初始化資料庫連接"""
        self.config = BackendConfig()
        try:
            self.client = MongoClient(self.config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            # 測試連接
            self.client.server_info()
            self.db = self.client[self.config.MONGODB_DB_NAME]
            print(f'MongoDB 連接成功: {self.config.MONGODB_DB_NAME}')
        except Exception as e:
            print(f'MongoDB 連接失敗: {e}')
            print('將使用空資料庫模式（資料不會被保存）')
            # 建立一個假的資料庫物件以避免後續錯誤
            self.client = None
            self.db = None
        
    def get_collection(self, name: str) -> Collection:
        """
        取得集合
        
        Args:
            name: 集合名稱
        
        Returns:
            Collection: MongoDB 集合物件
        """
        if self.db is None:
            raise Exception('MongoDB 未連接')
        return self.db[name]

# 全域資料庫實例
db = Database()

class AccidentModel:
    """事故資料模型"""
    
    @staticmethod
    def create(accident_data: dict) -> str:
        """
        建立事故記錄
        
        Args:
            accident_data: 事故資料
        
        Returns:
            str: 事故 ID
        """
        collection = db.get_collection('accidents')
        
        accident_doc = {
            'latitude': accident_data['latitude'],
            'longitude': accident_data['longitude'],
            'timestamp': datetime.fromtimestamp(accident_data.get('timestamp', datetime.now().timestamp())),
            'image': accident_data.get('image', ''),
            'device_id': accident_data.get('device_id', ''),
            # 新增受傷人數欄位，預設為 0，確保向後相容
            'injured_count': accident_data.get('injured_count', 0),
            'status': 'active',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = collection.insert_one(accident_doc)
        return str(result.inserted_id)
    
    @staticmethod
    def get_all(active_only: bool = True) -> list:
        """
        取得所有事故記錄
        
        Args:
            active_only: 是否只取得活動中的事故
        
        Returns:
            list: 事故記錄列表
        """
        try:
            collection = db.get_collection('accidents')
            
            query = {}
            if active_only:
                query['status'] = 'active'
            
            accidents = list(collection.find(query).sort('created_at', -1))
            
            # 轉換 ObjectId 為字串
            for accident in accidents:
                accident['_id'] = str(accident['_id'])
                if isinstance(accident.get('timestamp'), datetime):
                    accident['timestamp'] = accident['timestamp'].timestamp()
                if isinstance(accident.get('created_at'), datetime):
                    accident['created_at'] = accident['created_at'].timestamp()
                if isinstance(accident.get('updated_at'), datetime):
                    accident['updated_at'] = accident['updated_at'].timestamp()
            
            return accidents
        except Exception as e:
            print(f'MongoDB 查詢錯誤: {e}')
            # 如果 MongoDB 連接失敗，返回空列表而不是拋出異常
            return []
    
    @staticmethod
    def get_by_id(accident_id: str) -> Optional[dict]:
        """
        根據 ID 取得事故記錄
        
        Args:
            accident_id: 事故 ID
        
        Returns:
            Optional[dict]: 事故記錄或 None
        """
        from bson import ObjectId
        
        collection = db.get_collection('accidents')
        
        try:
            accident = collection.find_one({'_id': ObjectId(accident_id)})
            if accident:
                accident['_id'] = str(accident['_id'])
                if isinstance(accident.get('timestamp'), datetime):
                    accident['timestamp'] = accident['timestamp'].timestamp()
                if isinstance(accident.get('created_at'), datetime):
                    accident['created_at'] = accident['created_at'].timestamp()
                if isinstance(accident.get('updated_at'), datetime):
                    accident['updated_at'] = accident['updated_at'].timestamp()
            return accident
        except:
            return None
    
    @staticmethod
    def delete(accident_id: str) -> bool:
        """
        刪除事故記錄
        
        Args:
            accident_id: 事故 ID
        
        Returns:
            bool: 是否成功刪除
        """
        from bson import ObjectId
        
        collection = db.get_collection('accidents')
        
        try:
            result = collection.delete_one({'_id': ObjectId(accident_id)})
            return result.deleted_count > 0
        except:
            return False
    
    @staticmethod
    def update_status(accident_id: str, status: str) -> bool:
        """
        更新事故狀態
        
        Args:
            accident_id: 事故 ID
            status: 新狀態
        
        Returns:
            bool: 是否成功更新
        """
        from bson import ObjectId
        
        collection = db.get_collection('accidents')
        
        try:
            result = collection.update_one(
                {'_id': ObjectId(accident_id)},
                {'$set': {'status': status, 'updated_at': datetime.now()}}
            )
            return result.modified_count > 0
        except:
            return False

class DeviceModel:
    """裝置資料模型"""
    
    @staticmethod
    def update_position(device_id: str, latitude: float, longitude: float):
        """
        更新裝置位置
        
        Args:
            device_id: 裝置 ID
            latitude: 緯度
            longitude: 經度
        """
        collection = db.get_collection('devices')
        
        collection.update_one(
            {'device_id': device_id},
            {
                '$set': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'updated_at': datetime.now()
                },
                '$setOnInsert': {
                    'device_id': device_id,
                    'created_at': datetime.now()
                }
            },
            upsert=True
        )
    
    @staticmethod
    def get_all() -> list:
        """
        取得所有裝置
        
        Returns:
            list: 裝置列表
        """
        collection = db.get_collection('devices')
        
        devices = list(collection.find())
        
        # 轉換 ObjectId 為字串
        for device in devices:
            device['_id'] = str(device['_id'])
            if isinstance(device.get('created_at'), datetime):
                device['created_at'] = device['created_at'].timestamp()
            if isinstance(device.get('updated_at'), datetime):
                device['updated_at'] = device['updated_at'].timestamp()
        
        return devices

