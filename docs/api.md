# API 文件

## 基礎資訊

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **認證方式**: Bearer Token (JWT)

## 端點列表

### 1. 管理員登入

**POST** `/api/login`

取得管理員 JWT Token。

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response (200 OK):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "message": "登入成功"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "使用者名稱或密碼錯誤"
}
```

---

### 2. 上報事故

**POST** `/api/report_accident`

車載端上報事故資料。

**Request Body:**
```json
{
  "latitude": 25.0330,
  "longitude": 121.5654,
  "timestamp": 1234567890,
  "image": "base64_encoded_image_string",
  "device_id": "vehicle_001"
}
```

**Response (200 OK):**
```json
{
  "accident_id": "507f1f77bcf86cd799439011",
  "message": "事故已記錄"
}
```

**Response (400 Bad Request):**
```json
{
  "error": "缺少必要欄位: latitude"
}
```

---

### 3. 更新裝置位置

**POST** `/api/update_device`

更新車輛即時位置。

**Request Body:**
```json
{
  "device_id": "vehicle_001",
  "latitude": 25.0330,
  "longitude": 121.5654
}
```

**Response (200 OK):**
```json
{
  "message": "裝置位置已更新"
}
```

---

### 4. 取得事故列表

**GET** `/api/get_accidents`

取得所有事故記錄（一般使用者可訪問）。

**Query Parameters:**
- `active_only` (optional): `true` 或 `false`，預設 `true`

**Example:**
```
GET /api/get_accidents?active_only=true
```

**Response (200 OK):**
```json
{
  "accidents": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "latitude": 25.0330,
      "longitude": 121.5654,
      "timestamp": 1234567890,
      "image": "base64_string",
      "device_id": "vehicle_001",
      "status": "active",
      "created_at": 1234567890,
      "updated_at": 1234567890
    }
  ]
}
```

---

### 5. 刪除事故

**DELETE** `/api/delete_accident/<accident_id>`

刪除指定事故（需要管理員權限）。

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200 OK):**
```json
{
  "message": "事故已刪除"
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "缺少授權標頭"
}
```

**Response (403 Forbidden):**
```json
{
  "error": "權限不足"
}
```

**Response (404 Not Found):**
```json
{
  "error": "事故不存在"
}
```

---

### 6. 即時影像串流

**GET** `/api/video/<device_id>`

取得車輛即時影像串流（MJPEG 格式）。

**Query Parameters:**
- `overlay` (optional): `true` 或 `false`，是否顯示視覺辨識框，預設 `false`

**Example:**
```
GET /api/video/vehicle_001?overlay=true
```

**Response:**
- Content-Type: `multipart/x-mixed-replace; boundary=frame`
- 持續串流的 MJPEG 影像

**使用方式:**
```html
<img src="http://localhost:5000/api/video/vehicle_001?overlay=true" />
```

---

### 7. 健康檢查

**GET** `/api/health`

檢查 API 服務狀態。

**Response (200 OK):**
```json
{
  "status": "ok"
}
```

---

## 錯誤處理

所有錯誤回應都遵循以下格式：

```json
{
  "error": "錯誤訊息"
}
```

### HTTP 狀態碼

- `200 OK`: 請求成功
- `400 Bad Request`: 請求參數錯誤
- `401 Unauthorized`: 未授權（需要登入）
- `403 Forbidden`: 權限不足
- `404 Not Found`: 資源不存在
- `500 Internal Server Error`: 伺服器錯誤

---

## 認證流程

1. 使用管理員帳號密碼呼叫 `/api/login`
2. 取得 JWT Token
3. 在後續請求的 Header 中加入：
   ```
   Authorization: Bearer <jwt_token>
   ```
4. Token 有效期為 24 小時

---

## 資料模型

### Accident (事故)

```json
{
  "_id": "ObjectId",
  "latitude": 25.0330,
  "longitude": 121.5654,
  "timestamp": 1234567890,
  "image": "base64_encoded_string",
  "device_id": "vehicle_001",
  "status": "active",
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

### Device (裝置)

```json
{
  "_id": "ObjectId",
  "device_id": "vehicle_001",
  "latitude": 25.0330,
  "longitude": 121.5654,
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

---

## 範例程式碼

### Python (車載端)

```python
import requests

# 上報事故
data = {
    'latitude': 25.0330,
    'longitude': 121.5654,
    'timestamp': 1234567890,
    'device_id': 'vehicle_001'
}

response = requests.post(
    'http://localhost:5000/api/report_accident',
    json=data
)
print(response.json())
```

### JavaScript (前端)

```javascript
// 取得事故列表
fetch('http://localhost:5000/api/get_accidents')
  .then(response => response.json())
  .then(data => {
    console.log(data.accidents);
  });

// 管理員登入
fetch('http://localhost:5000/api/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
})
  .then(response => response.json())
  .then(data => {
    const token = data.token;
    // 儲存 token 供後續使用
  });
```

