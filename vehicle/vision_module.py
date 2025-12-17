"""
視覺辨識模組
使用 OpenCV 進行障礙物偵測
實作避障邏輯與路徑規劃
"""

import cv2
import numpy as np
from typing import Tuple, Optional, List
import time

class VisionModule:
    """視覺辨識模組類別"""
    
    def __init__(self, camera_index: int = 0, min_area: int = 500, confidence_threshold: float = 0.5):
        """
        初始化視覺辨識模組
        
        Args:
            camera_index: 攝影機索引
            min_area: 最小障礙物面積（像素）
            confidence_threshold: 信心度閾值
        """
        self.camera_index = camera_index
        self.min_area = min_area
        self.confidence_threshold = confidence_threshold
        self.cap = None
        self.show_overlay = False  # 是否顯示偵測框
        
        # 影像處理參數
        self.blur_kernel_size = 5
        self.canny_low = 50
        self.canny_high = 150
        
        # HOG 行人偵測器（用於人體偵測）
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        
    def initialize_camera(self) -> bool:
        """
        初始化攝影機
        
        Returns:
            bool: 初始化是否成功
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"無法開啟攝影機 {self.camera_index}")
                return False
            
            # 設定攝影機參數
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"攝影機已初始化: {self.camera_index}")
            return True
        except Exception as e:
            print(f"攝影機初始化失敗: {e}")
            return False
    
    def release_camera(self):
        """釋放攝影機資源"""
        if self.cap:
            self.cap.release()
            print("攝影機已釋放")
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        影像預處理（去噪）
        
        Args:
            frame: 原始影像
        
        Returns:
            np.ndarray: 處理後的影像
        """
        # 轉換為灰階
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (self.blur_kernel_size, self.blur_kernel_size), 0)
        
        return blurred
    
    def detect_obstacles_contour(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        使用輪廓偵測方法偵測障礙物
        
        Args:
            frame: 輸入影像
        
        Returns:
            List[Tuple[int, int, int, int]]: 障礙物邊界框列表 [(x, y, w, h), ...]
        """
        # 預處理
        processed = self.preprocess_frame(frame)
        
        # Canny 邊緣偵測
        edges = cv2.Canny(processed, self.canny_low, self.canny_high)
        
        # 形態學操作（閉合）
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        
        # 尋找輪廓
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        obstacles = []
        frame_height, frame_width = frame.shape[:2]
        center_x = frame_width // 2
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # 過濾小面積的輪廓
            if area < self.min_area:
                continue
            
            # 取得邊界框
            x, y, w, h = cv2.boundingRect(contour)
            
            # 只考慮畫面中央區域的障礙物（前方）
            obstacle_center_x = x + w // 2
            if abs(obstacle_center_x - center_x) < frame_width * 0.4:
                obstacles.append((x, y, w, h))
        
        return obstacles
    
    def detect_obstacles_blob(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        使用 Blob Detection 方法偵測障礙物
        
        Args:
            frame: 輸入影像
        
        Returns:
            List[Tuple[int, int, int, int]]: 障礙物邊界框列表
        """
        # 預處理
        processed = self.preprocess_frame(frame)
        
        # 設定 Blob Detector 參數
        params = cv2.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = self.min_area
        params.filterByCircularity = False
        params.filterByConvexity = False
        params.filterByInertia = False
        
        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(processed)
        
        obstacles = []
        frame_height, frame_width = frame.shape[:2]
        center_x = frame_width // 2
        
        for kp in keypoints:
            x = int(kp.pt[0] - kp.size / 2)
            y = int(kp.pt[1] - kp.size / 2)
            w = h = int(kp.size)
            
            # 只考慮畫面中央區域
            obstacle_center_x = x + w // 2
            if abs(obstacle_center_x - center_x) < frame_width * 0.4:
                obstacles.append((x, y, w, h))
        
        return obstacles
    
    def detect_obstacles(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        偵測障礙物（主要方法，結合多種演算法）
        
        Args:
            frame: 輸入影像
        
        Returns:
            List[Tuple[int, int, int, int]]: 障礙物邊界框列表
        """
        # 使用輪廓偵測（主要方法）
        obstacles = self.detect_obstacles_contour(frame)
        
        # 如果沒有偵測到，嘗試 Blob Detection
        if len(obstacles) == 0:
            obstacles = self.detect_obstacles_blob(frame)
        
        return obstacles
    
    def calculate_avoidance_path(self, frame: np.ndarray, obstacles: List[Tuple[int, int, int, int]]) -> Optional[str]:
        """
        計算避障路徑
        
        Args:
            frame: 輸入影像
            obstacles: 障礙物列表
        
        Returns:
            Optional[str]: 避障方向 ('left', 'right', 'forward') 或 None
        """
        if not obstacles:
            return 'forward'
        
        frame_height, frame_width = frame.shape[:2]
        center_x = frame_width // 2
        
        # 分析障礙物位置
        left_obstacles = []
        right_obstacles = []
        center_obstacles = []
        
        for x, y, w, h in obstacles:
            obstacle_center_x = x + w // 2
            obstacle_center_y = y + h // 2
            
            # 分類障礙物位置
            if obstacle_center_x < center_x - frame_width * 0.15:
                left_obstacles.append((x, y, w, h))
            elif obstacle_center_x > center_x + frame_width * 0.15:
                right_obstacles.append((x, y, w, h))
            else:
                center_obstacles.append((x, y, w, h))
        
        # 決策邏輯
        if center_obstacles:
            # 中央有障礙物，選擇較少障礙物的一側
            if len(left_obstacles) < len(right_obstacles):
                return 'left'
            else:
                return 'right'
        elif left_obstacles and not right_obstacles:
            return 'right'
        elif right_obstacles and not left_obstacles:
            return 'left'
        else:
            return 'forward'
    
    def detect_people(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        使用 HOG+SVM 偵測畫面中的人形。
        
        Args:
            frame: 輸入 BGR 影像
        
        Returns:
            List[Tuple[int, int, int, int]]: 人物邊界框列表
        """
        h, w = frame.shape[:2]
        scale = 640.0 / max(w, h)
        if scale < 1.0:
            resized = cv2.resize(frame, (int(w * scale), int(h * scale)))
        else:
            resized = frame

        rects, weights = self.hog.detectMultiScale(
            resized,
            winStride=(8, 8),
            padding=(8, 8),
            scale=1.05
        )

        people: List[Tuple[int, int, int, int]] = []

        for (x, y, rw, rh), score in zip(rects, weights):
            if score < self.confidence_threshold:
                continue

            if scale < 1.0:
                x = int(x / scale)
                y = int(y / scale)
                rw = int(rw / scale)
                rh = int(rh / scale)

            people.append((x, y, rw, rh))

        return people
    
    def draw_detections(self, frame: np.ndarray, obstacles: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        在影像上繪製偵測框
        
        Args:
            frame: 原始影像
            obstacles: 障礙物列表
        
        Returns:
            np.ndarray: 繪製後的影像
        """
        if not self.show_overlay:
            return frame
        
        result_frame = frame.copy()
        
        for x, y, w, h in obstacles:
            # 繪製邊界框
            cv2.rectangle(result_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # 標註文字（以 Person 顯示，表示偵測到的人形）
            cv2.putText(result_frame, 'Person', (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result_frame
    
    def get_frame(self) -> Optional[np.ndarray]:
        """
        取得目前影像幀
        
        Returns:
            Optional[np.ndarray]: 影像幀或 None
        """
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def set_overlay(self, show: bool):
        """
        設定是否顯示偵測框
        
        Args:
            show: 是否顯示
        """
        self.show_overlay = show
    
    def get_frame_with_detections(self) -> Optional[Tuple[np.ndarray, List[Tuple[int, int, int, int]]]]:
        """
        取得帶有偵測結果的影像幀
        
        Returns:
            Optional[Tuple[np.ndarray, List]]: (影像, 障礙物列表) 或 None
        """
        frame = self.get_frame()
        if frame is None:
            return None
        
        # 使用人體偵測取得人形邊界框，供串流疊加與受傷人數計算
        people = self.detect_people(frame)
        frame_with_detections = self.draw_detections(frame, people)
        
        return (frame_with_detections, people)

