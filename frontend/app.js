// 前端主應用程式

// 配置
const CONFIG = {
    API_URL: 'http://localhost:5000/api',  // 本地開發使用
    VIDEO_STREAM_URL: 'http://localhost:5000/api/video/vehicle_001',  // 本地開發使用
    UPDATE_INTERVAL: 5000, // 5 秒更新一次
    MAP_CENTER: { lat: 25.0330, lng: 121.5654 }, // 預設位置（台北）
    MAP_ZOOM: 13
};

// 全域變數
let map = null;
let markers = [];
let isAdmin = false;
let adminToken = null;
let videoStreamInterval = null;

// 地圖準備就緒的回調
window.onMapReady = function() {
    console.log('地圖已準備就緒，開始載入資料...');
    loadAccidents();
    startVideoStream();
    setInterval(loadAccidents, CONFIG.UPDATE_INTERVAL);
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('前端初始化中...');
    console.log('API URL:', CONFIG.API_URL);
    
    // 設定事件監聽器（不依賴地圖）
    setupEventListeners();
    
    // 檢查 Google Maps API 是否已經載入
    if (typeof google !== 'undefined' && typeof google.maps !== 'undefined' && typeof google.maps.Map !== 'undefined') {
        console.log('Google Maps API 已載入，立即初始化地圖');
        initMap();
    } else {
        console.log('等待 Google Maps API 載入...');
        // initMap 會由 Google Maps API 的 callback 參數自動調用
        // 如果 API 已經載入但 callback 還沒執行，手動調用
        let checkCount = 0;
        const checkInterval = setInterval(() => {
            checkCount++;
            if (typeof google !== 'undefined' && typeof google.maps !== 'undefined' && typeof google.maps.Map !== 'undefined') {
                console.log('檢測到 Google Maps API 已載入，初始化地圖');
                clearInterval(checkInterval);
                if (!map) {
                    initMap();
                }
            } else if (checkCount > 50) {
                // 10 秒後停止檢查
                console.error('Google Maps API 載入超時');
                clearInterval(checkInterval);
            }
        }, 200);
    }
});

// 初始化 Google Maps（由 Google Maps API 回調函數調用）
function initMap() {
    console.log('initMap 被調用');
    console.log('google 物件:', typeof google);
    console.log('google.maps 物件:', typeof google?.maps);
    console.log('google.maps.Map:', typeof google?.maps?.Map);
    
    // 檢查 Google Maps API 是否已完全載入
    if (typeof google === 'undefined' || typeof google.maps === 'undefined' || typeof google.maps.Map === 'undefined') {
        console.error('Google Maps API 尚未完全載入，請稍候...');
        // 如果 API 尚未載入，等待一段時間後重試
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
        map = new google.maps.Map(mapElement, {
            center: CONFIG.MAP_CENTER,
            zoom: CONFIG.MAP_ZOOM,
            styles: [
                {
                    featureType: 'all',
                    elementType: 'geometry',
                    stylers: [{ color: '#f5f5f5' }]
                },
                {
                    featureType: 'water',
                    elementType: 'geometry',
                    stylers: [{ color: '#c9c9c9' }]
                },
                {
                    featureType: 'road',
                    elementType: 'geometry',
                    stylers: [{ color: '#ffffff' }]
                }
            ]
        });
        console.log('Google Maps 初始化成功');
        
        // 初始化完成後，執行其他初始化任務
        if (window.onMapReady) {
            window.onMapReady();
        }
    } catch (error) {
        console.error('Google Maps 初始化失敗:', error);
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
        const response = await fetch(url);
        
        if (!response.ok) {
            console.error('HTTP 錯誤:', response.status, response.statusText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();

        if (response.ok) {
            displayAccidents(data.accidents);
            updateMapMarkers(data.accidents);
            document.getElementById('activeAccidentsCount').textContent = data.accidents.length;
        } else {
            console.error('Failed to load accidents:', data.error);
        }
    } catch (error) {
        console.error('Error loading accidents:', error);
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
                map.setCenter({ lat: accident.latitude, lng: accident.longitude });
                map.setZoom(16);
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
    // 清除舊標記
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    // 添加新標記
    accidents.forEach(accident => {
        const marker = new google.maps.Marker({
            position: { lat: accident.latitude, lng: accident.longitude },
            map: map,
            title: `事故 #${accident._id.slice(-6)}`,
            icon: {
                url: 'data:image/svg+xml;charset=UTF-8,' + encodeURIComponent(`
                    <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="16" cy="16" r="12" fill="#ef4444" stroke="white" stroke-width="2"/>
                        <text x="16" y="20" font-size="12" fill="white" text-anchor="middle" font-weight="bold">!</text>
                    </svg>
                `),
                scaledSize: new google.maps.Size(32, 32),
                anchor: new google.maps.Point(16, 16)
            }
        });

        // 資訊視窗
        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="padding: 8px;">
                    <h3 style="margin: 0 0 8px 0; font-weight: bold;">事故 #${accident._id.slice(-6)}</h3>
                    <p style="margin: 4px 0; font-size: 12px;">時間: ${new Date(accident.timestamp * 1000).toLocaleString('zh-TW')}</p>
                    <p style="margin: 4px 0; font-size: 12px;">裝置: ${accident.device_id || 'N/A'}</p>
                </div>
            `
        });

        marker.addListener('click', () => {
            infoWindow.open(map, marker);
        });

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
    
    const overlayParam = showOverlay ? 'true' : 'false';
    const streamUrl = `${CONFIG.VIDEO_STREAM_URL}?overlay=${overlayParam}`;
    
    videoImg.src = streamUrl;
    videoImg.classList.remove('hidden');
    placeholder.classList.add('hidden');
    
    // 處理影像載入錯誤
    videoImg.onerror = () => {
        videoImg.classList.add('hidden');
        placeholder.classList.remove('hidden');
        placeholder.textContent = '無法連接影像串流';
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

