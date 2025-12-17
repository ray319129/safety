// 前端主應用程式

// 配置
const CONFIG = {
    API_URL: 'http://localhost:5000/api',  // 本地開發使用
    VIDEO_STREAM_URL: 'http://localhost:5000/api/video/vehicle_001',  // 本地開發使用
    UPDATE_INTERVAL: 5000, // 5 秒更新一次
    MAP_CENTER: [25.0330, 121.5654], // 預設位置（台北）[緯度, 經度]
    MAP_ZOOM: 13
};

// 全域變數
let map = null;
let markers = [];
let isAdmin = false;
let adminToken = null;
let videoStreamInterval = null;

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('前端初始化中...');
    console.log('API URL:', CONFIG.API_URL);
    
    // 初始化地圖（Leaflet 不需要等待回調）
    initMap();
    
    // 設定事件監聽器
    setupEventListeners();
    
    // 載入資料
    loadAccidents();
    startVideoStream();
    setInterval(loadAccidents, CONFIG.UPDATE_INTERVAL);
});

// 初始化 Leaflet 地圖
function initMap() {
    // 檢查 Leaflet 是否已載入
    if (typeof L === 'undefined') {
        console.error('Leaflet 尚未載入，請稍候...');
        setTimeout(initMap, 200);
        return;
    }
    
    // 檢查地圖容器是否存在
    const mapElement = document.getElementById('map');
    if (!mapElement) {
        console.error('找不到地圖容器元素 #map');
        return;
    }
    
    try {
        // 初始化 Leaflet 地圖
        map = L.map('map').setView(CONFIG.MAP_CENTER, CONFIG.MAP_ZOOM);
        
        // 添加 OpenStreetMap 圖層
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19
        }).addTo(map);
        
        console.log('Leaflet 地圖初始化成功');
    } catch (error) {
        console.error('Leaflet 地圖初始化失敗:', error);
        console.error('錯誤詳情:', error.message, error.stack);
    }
}

// 設定事件監聽器
function setupEventListeners() {
    // 登入按鈕
    document.getElementById('loginBtn').addEventListener('click', () => {
        document.getElementById('loginModal').classList.remove('hidden');
    });

    // 登出按鈕
    document.getElementById('logoutBtn').addEventListener('click', () => {
        logout();
    });

    // 登入表單
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleLogin();
    });

    // 關閉登入模態框（點擊背景）
    document.getElementById('loginModal').addEventListener('click', (e) => {
        if (e.target.id === 'loginModal') {
            document.getElementById('loginModal').classList.add('hidden');
        }
    });

    // 偵測框開關
    document.getElementById('overlayToggle').addEventListener('change', (e) => {
        const showOverlay = e.target.checked;
        updateVideoStream(showOverlay);
    });
}

// 處理登入
async function handleLogin() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const url = `${CONFIG.API_URL}/login`;
        console.log('登入請求:', url);
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            adminToken = data.token;
            isAdmin = true;
            document.getElementById('loginModal').classList.add('hidden');
            updateUIForAdmin();
            showNotification('登入成功', 'success');
        } else {
            showNotification(data.error || '登入失敗', 'error');
        }
    } catch (error) {
        showNotification('連線錯誤', 'error');
        console.error('Login error:', error);
    }
}

// 登出
function logout() {
    adminToken = null;
    isAdmin = false;
    updateUIForUser();
    showNotification('已登出', 'info');
}

// 更新 UI（管理員模式）
function updateUIForAdmin() {
    document.getElementById('loginBtn').classList.add('hidden');
    document.getElementById('logoutBtn').classList.remove('hidden');
    document.getElementById('adminControls').classList.remove('hidden');
    
    // 為事故卡片添加刪除按鈕
    updateAccidentCards();
}

// 更新 UI（一般使用者模式）
function updateUIForUser() {
    document.getElementById('loginBtn').classList.remove('hidden');
    document.getElementById('logoutBtn').classList.add('hidden');
    document.getElementById('adminControls').classList.add('hidden');
    
    // 移除刪除按鈕
    updateAccidentCards();
}

// 載入事故列表
async function loadAccidents() {
    try {
        const url = `${CONFIG.API_URL}/get_accidents?active_only=true`;
        console.log('載入事故列表:', url);
        
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            console.error('HTTP 錯誤:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('錯誤詳情:', errorText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('事故列表載入成功:', data);

        if (data.accidents) {
            displayAccidents(data.accidents);
            updateMapMarkers(data.accidents);
            document.getElementById('activeAccidentsCount').textContent = data.accidents.length;
        } else {
            console.warn('API 回應格式異常:', data);
            displayAccidents([]);
            updateMapMarkers([]);
        }
    } catch (error) {
        console.error('載入事故列表失敗:', error);
        // 顯示錯誤訊息給使用者
        const listContainer = document.getElementById('accidentsList');
        if (listContainer) {
            listContainer.innerHTML = `
                <div class="text-red-500 text-center py-8">
                    <p>無法連接到後端伺服器</p>
                    <p class="text-sm mt-2">請確認後端伺服器正在運行 (http://localhost:5000)</p>
                </div>
            `;
        }
    }
}

// 顯示事故列表
function displayAccidents(accidents) {
    const listContainer = document.getElementById('accidentsList');
    
    if (accidents.length === 0) {
        listContainer.innerHTML = '<div class="text-gray-500 text-center py-8">目前沒有活動中的事故</div>';
        return;
    }

    listContainer.innerHTML = accidents.map(accident => {
        const date = new Date(accident.timestamp * 1000);
        const dateStr = date.toLocaleString('zh-TW');
        
        return `
            <div class="accident-card animate-slide-in-blur" data-id="${accident._id}">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <div class="flex items-center space-x-2 mb-2">
                            <div class="w-3 h-3 bg-red-500 rounded-full"></div>
                            <h3 class="font-semibold text-gray-800">事故 #${accident._id.slice(-6)}</h3>
                        </div>
                        <div class="text-sm text-gray-600 space-y-1">
                            <div>時間: ${dateStr}</div>
                            <div>位置: ${accident.latitude.toFixed(6)}, ${accident.longitude.toFixed(6)}</div>
                            <div>裝置: ${accident.device_id || 'N/A'}</div>
                            <div>受傷人數: ${(accident.injured_count ?? 0)} 人</div>
                        </div>
                    </div>
                    ${isAdmin ? `
                        <button class="admin-btn ml-4" onclick="deleteAccident('${accident._id}')">
                            刪除
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');

    // 添加點擊事件（聚焦地圖）
    document.querySelectorAll('.accident-card').forEach(card => {
        card.addEventListener('click', () => {
            const accidentId = card.dataset.id;
            const accident = accidents.find(a => a._id === accidentId);
            if (accident && map) {
                map.setView([accident.latitude, accident.longitude], 16);
                // 打開對應標記的彈出視窗
                const marker = markers.find(m => {
                    const latlng = m.getLatLng();
                    return Math.abs(latlng.lat - accident.latitude) < 0.0001 &&
                           Math.abs(latlng.lng - accident.longitude) < 0.0001;
                });
                if (marker) {
                    marker.openPopup();
                }
            }
        });
    });
}

// 更新事故卡片（添加/移除管理員功能）
function updateAccidentCards() {
    loadAccidents();
}

// 更新地圖標記
function updateMapMarkers(accidents) {
    // 檢查地圖是否已初始化
    if (!map || typeof L === 'undefined') {
        console.warn('地圖尚未初始化，無法更新標記');
        return;
    }
    
    // 清除舊標記
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];

    // 添加新標記
    accidents.forEach(accident => {
        // 建立自訂圖示
        const customIcon = L.divIcon({
            className: 'custom-marker',
            html: `
                <div style="
                    width: 32px;
                    height: 32px;
                    background-color: #ef4444;
                    border: 2px solid white;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 16px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                ">!</div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        });

        // 建立標記
        const marker = L.marker([accident.latitude, accident.longitude], {
            icon: customIcon,
            title: `事故 #${accident._id.slice(-6)}`
        }).addTo(map);

        // 建立彈出視窗
        const popup = L.popup({
            maxWidth: 250
        }).setContent(`
            <div style="padding: 8px;">
                <h3 style="margin: 0 0 8px 0; font-weight: bold;">事故 #${accident._id.slice(-6)}</h3>
                <p style="margin: 4px 0; font-size: 12px;">時間: ${new Date(accident.timestamp * 1000).toLocaleString('zh-TW')}</p>
                <p style="margin: 4px 0; font-size: 12px;">裝置: ${accident.device_id || 'N/A'}</p>
                <p style="margin: 4px 0; font-size: 12px;">受傷人數: ${(accident.injured_count ?? 0)} 人</p>
            </div>
        `);

        marker.bindPopup(popup);
        markers.push(marker);
    });
}

// 刪除事故（管理員功能）
async function deleteAccident(accidentId) {
    if (!isAdmin || !adminToken) {
        showNotification('需要管理員權限', 'error');
        return;
    }

    if (!confirm('確定要刪除此事故嗎？')) {
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_URL}/delete_accident/${accidentId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${adminToken}`
            }
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('事故已刪除', 'success');
            loadAccidents();
        } else {
            showNotification(data.error || '刪除失敗', 'error');
        }
    } catch (error) {
        showNotification('連線錯誤', 'error');
        console.error('Delete error:', error);
    }
}

// 啟動影像串流
function startVideoStream() {
    updateVideoStream(false);
}

// 更新影像串流
function updateVideoStream(showOverlay) {
    const videoImg = document.getElementById('videoStream');
    const placeholder = document.getElementById('videoPlaceholder');
    
    if (!videoImg || !placeholder) {
        console.error('找不到影像串流元素');
        return;
    }
    
    const overlayParam = showOverlay ? 'true' : 'false';
    const streamUrl = `${CONFIG.VIDEO_STREAM_URL}?overlay=${overlayParam}`;
    
    console.log('更新影像串流:', streamUrl);
    
    // 重置狀態
    videoImg.classList.add('hidden');
    placeholder.classList.remove('hidden');
    placeholder.textContent = '正在連接影像串流...';
    
    // 設置影像源
    videoImg.src = streamUrl;
    
    // 處理影像載入成功
    videoImg.onload = () => {
        console.log('影像串流連接成功');
        videoImg.classList.remove('hidden');
        placeholder.classList.add('hidden');
    };
    
    // 處理影像載入錯誤
    videoImg.onerror = () => {
        console.error('影像串流載入失敗:', streamUrl);
        console.error('請確認：');
        console.error('1. 後端伺服器正在運行 (http://localhost:5000)');
        console.error('2. 車載端 web_api.py 正在運行 (http://localhost:8080)');
        videoImg.classList.add('hidden');
        placeholder.classList.remove('hidden');
        placeholder.textContent = '無法連接影像串流（請確認後端和車載端服務正在運行）';
    };
}

// 顯示通知
function showNotification(message, type = 'info') {
    // 建立通知元素
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 animate-slide-in-blur`;
    
    const colors = {
        success: 'bg-green-500 text-white',
        error: 'bg-red-500 text-white',
        info: 'bg-blue-500 text-white'
    };
    
    notification.className += ` ${colors[type] || colors.info}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // 3 秒後移除
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transition = 'opacity 0.3s';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

