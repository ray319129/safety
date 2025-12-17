#!/bin/bash
# 測試影像串流腳本

echo "測試車載端影像串流..."
echo ""

# 測試 1: 檢查端點是否響應
echo "1. 檢查端點響應..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/video_stream)
if [ "$HTTP_CODE" == "200" ]; then
    echo "✓ 端點正常響應 (HTTP $HTTP_CODE)"
else
    echo "✗ 端點響應異常 (HTTP $HTTP_CODE)"
fi

# 測試 2: 檢查 Content-Type
echo ""
echo "2. 檢查 Content-Type..."
CONTENT_TYPE=$(curl -s -I http://localhost:8080/video_stream | grep -i "content-type" | cut -d' ' -f2 | tr -d '\r\n')
if [[ "$CONTENT_TYPE" == *"multipart/x-mixed-replace"* ]]; then
    echo "✓ Content-Type 正確: $CONTENT_TYPE"
else
    echo "✗ Content-Type 異常: $CONTENT_TYPE"
fi

# 測試 3: 檢查是否可以接收數據
echo ""
echo "3. 測試數據接收（5秒）..."
timeout 5 curl -s http://localhost:8080/video_stream > /dev/null
if [ $? -eq 0 ] || [ $? -eq 124 ]; then
    echo "✓ 可以接收數據"
else
    echo "✗ 無法接收數據"
fi

echo ""
echo "測試完成！"
echo ""
echo "提示："
echo "- 在瀏覽器中訪問: http://你的樹莓派IP:8080/video_stream"
echo "- 或使用後端代理: http://後端IP:5000/api/video/vehicle_001"

