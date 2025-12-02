import gradio as gr
import json
from datetime import datetime, timedelta
import os
import hashlib
from huggingface_hub import HfApi, hf_hub_download, upload_file
import secrets
import threading

# Hugging Face 設定
HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO = os.getenv("SPACE_ID")
USERS_FILE = 'users.json'
DATA_DIR = 'user_data'
SESSIONS_FILE = 'sessions.json'

# 商店和兌換途徑選項
STORE_OPTIONS = ['7-11', '全家', '星巴克']
REDEEM_METHODS = ['遠傳', 'Line禮物', '7-11', '全家', '星巴克']

# 兌換連結對應
REDEEM_LINKS = {
    '遠傳': {
        'app': 'fetnet://',
        'name': '遠傳心生活'
    },
    'Line禮物': {
        'app': 'https://line.me/R/shop/gift/category/coffee',
        'name': 'Line 禮物'
    },
    '7-11': {
        'app': 'openpointapp://gofeature?featureId=HOMACB02',
        'name': 'OPENPOINT'
    },
    '全家': {
        'app': 'familymart://action.go/preorder/myproduct',
        'name': '全家便利商店'
    },
    '星巴克': {
        'app': 'starbucks://',
        'name': '星巴克'
    }
}

# CSS 樣式
CUSTOM_CSS = """
/* 隱藏 Hugging Face Space 頂部標題欄 */
#huggingface-space-header {
    display: none !important;
}

/* 移除頂部間距 */
body {
    padding-top: 0 !important;
}

.contain {
    padding-top: 0 !important;
}

/* 隱藏下拉選單的游標和禁用輸入 */
.dropdown-readonly input {
    caret-color: transparent !important;
    cursor: pointer !important;
    user-select: none !important;
}

.dropdown-readonly input:focus {
    caret-color: transparent !important;
}

/* 防止文字選取 */
.dropdown-readonly * {
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
}
"""

# 確保資料目錄存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Hugging Face API
api = HfApi()

# 記憶體快取
cache = {
    'users': None,
    'sessions': {},
    'deposits': {},
    'last_sync': {},
    'loading': set()
}

# 快取鎖
cache_lock = threading.Lock()

# 全域變數用於儲存 label 到 id 的映射
deposit_label_to_id = {}

def download_from_hf(filename):
    """從 Hugging Face Space 下載檔案"""
    try:
        if HF_TOKEN and HF_REPO:
            local_path = hf_hub_download(
                repo_id=HF_REPO,
                filename=filename,
                repo_type="space",
                token=HF_TOKEN,
                force_download=False
            )
            return local_path
    except Exception as e:
        print(f"下載 {filename} 失敗: {e}")
    return None

def upload_to_hf_async(filepath):
    """非同步上傳到 Hugging Face"""
    def upload():
        try:
            if HF_TOKEN and HF_REPO:
                upload_file(
                    path_or_fileobj=filepath,
                    path_in_repo=filepath,
                    repo_id=HF_REPO,
                    repo_type="space",
                    token=HF_TOKEN
                )
                print(f"✅ 已上傳 {filepath}")
        except Exception as e:
            print(f"❌ 上傳 {filepath} 失敗: {e}")
    
    thread = threading.Thread(target=upload, daemon=True)
    thread.start()

def hash_password(password):
    """密碼加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """載入使用者資料（優先使用快取）"""
    with cache_lock:
        if cache['users'] is not None:
            return cache['users']
    
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with cache_lock:
                    cache['users'] = data
                return data
        except:
            pass
    
    def load_from_hf():
        hf_file = download_from_hf(USERS_FILE)
        if hf_file and os.path.exists(hf_file):
            try:
                with open(hf_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with open(USERS_FILE, 'w', encoding='utf-8') as local_f:
                        json.dump(data, local_f, ensure_ascii=False, indent=2)
                    with cache_lock:
                        cache['users'] = data
            except:
                pass
    
    thread = threading.Thread(target=load_from_hf, daemon=True)
    thread.start()
    
    with cache_lock:
        if cache['users'] is None:
            cache['users'] = {}
        return cache['users']

def save_users(users):
    """儲存使用者資料"""
    try:
        with cache_lock:
            cache['users'] = users
        
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        upload_to_hf_async(USERS_FILE)
        return True
    except Exception as e:
        print(f"儲存使用者資料錯誤: {e}")
        return False

def load_sessions():
    """載入 Session 資料（優先使用快取）"""
    with cache_lock:
        if cache['sessions']:
            return cache['sessions']
    
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with cache_lock:
                    cache['sessions'] = data
                return data
        except:
            pass
    
    def load_from_hf():
        hf_file = download_from_hf(SESSIONS_FILE)
        if hf_file and os.path.exists(hf_file):
            try:
                with open(hf_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with open(SESSIONS_FILE, 'w', encoding='utf-8') as local_f:
                        json.dump(data, local_f, ensure_ascii=False, indent=2)
                    with cache_lock:
                        cache['sessions'] = data
            except:
                pass
    
    thread = threading.Thread(target=load_from_hf, daemon=True)
    thread.start()
    
    return {}

def save_sessions(sessions):
    """儲存 Session 資料"""
    try:
        with cache_lock:
            cache['sessions'] = sessions
        
        with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
        
        upload_to_hf_async(SESSIONS_FILE)
        return True
    except:
        return False

def create_session(username, request: gr.Request):
    """創建 Session Token"""
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    
    with cache_lock:
        sessions = cache['sessions'] if cache['sessions'] else load_sessions()
    
    now = datetime.now()
    sessions = {k: v for k, v in sessions.items() 
                if datetime.fromisoformat(v['expires_at']) > now}
    
    sessions[session_id] = {
        'username': username,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
    }
    save_sessions(sessions)
    
    print(f"✅ 創建 Session: {session_id} for {username}")
    return session_id

def get_session_id(request: gr.Request):
    """獲取當前客戶端的 Session ID"""
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    return session_id

def validate_session(session_id):
    """驗證 Session（快速檢查）"""
    with cache_lock:
        sessions = cache['sessions'] if cache['sessions'] else load_sessions()
    
    if session_id not in sessions:
        return None
    
    session = sessions[session_id]
    try:
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            del sessions[session_id]
            save_sessions(sessions)
            return None
        
        return session['username']
    except:
        return None

def delete_session(session_id):
    """刪除 Session"""
    with cache_lock:
        sessions = cache['sessions'] if cache['sessions'] else load_sessions()
    
    if session_id in sessions:
        del sessions[session_id]
        save_sessions(sessions)

def get_user_data_file(username):
    """取得使用者資料檔案路徑"""
    if not username:
        return None
    return os.path.join(DATA_DIR, f'{username}.json')

def load_deposits(username):
    """載入寄杯資料（優先使用快取）"""
    if not username:
        return []
    
    with cache_lock:
        if username in cache['deposits']:
            return cache['deposits'][username]
    
    data_file = get_user_data_file(username)
    
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with cache_lock:
                    cache['deposits'][username] = data
                return data
        except:
            pass
    
    def load_from_hf():
        hf_path = f"{DATA_DIR}/{username}.json"
        hf_file = download_from_hf(hf_path)
        if hf_file and os.path.exists(hf_file):
            try:
                with open(hf_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with open(data_file, 'w', encoding='utf-8') as local_f:
                        json.dump(data, local_f, ensure_ascii=False, indent=2)
                    with cache_lock:
                        cache['deposits'][username] = data
            except:
                pass
    
    if username not in cache.get('loading', set()):
        with cache_lock:
            cache['loading'].add(username)
        thread = threading.Thread(target=load_from_hf, daemon=True)
        thread.start()
    
    return []

def save_deposits(username, deposits):
    """儲存寄杯資料"""
    data_file = get_user_data_file(username)
    if not data_file:
        return False
    
    try:
        with cache_lock:
            cache['deposits'][username] = deposits
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(deposits, f, ensure_ascii=False, indent=2)
        
        upload_to_hf_async(data_file)
        return True
    except Exception as e:
        print(f"儲存寄杯資料錯誤: {e}")
        return False

def register_user(username, password, confirm_password):
    """註冊新使用者"""
    if not username or not password:
        return "❌ 請填寫使用者名稱和密碼", gr.update(visible=True), gr.update(visible=False)
    
    if len(username) < 3:
        return "❌ 使用者名稱至少需要 3 個字元", gr.update(visible=True), gr.update(visible=False)
    
    if len(password) < 6:
        return "❌ 密碼至少需要 6 個字元", gr.update(visible=True), gr.update(visible=False)
    
    if password != confirm_password:
        return "❌ 兩次密碼輸入不一致", gr.update(visible=True), gr.update(visible=False)
    
    users = load_users()
    
    if username in users:
        return "❌ 使用者名稱已存在", gr.update(visible=True), gr.update(visible=False)
    
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    if save_users(users):
        user_file = get_user_data_file(username)
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        upload_to_hf_async(user_file)
        
        return "✅ 註冊成功！請登入", gr.update(visible=True), gr.update(visible=False)
    else:
        return "❌ 註冊失敗，請稍後再試", gr.update(visible=True), gr.update(visible=False)

def login_user(username, password, remember_me, request: gr.Request):
    """使用者登入"""
    if not username or not password:
        return "❌ 請填寫使用者名稱和密碼", gr.update(visible=True), gr.update(visible=False), None
    
    users = load_users()
    
    if username not in users:
        return "❌ 使用者不存在", gr.update(visible=True), gr.update(visible=False), None
    
    if users[username]['password'] != hash_password(password):
        return "❌ 密碼錯誤", gr.update(visible=True), gr.update(visible=False), None
    
    if remember_me:
        create_session(username, request)
    
    return f"✅ 歡迎回來，{username}！", gr.update(visible=False), gr.update(visible=True), username

def auto_login(request: gr.Request):
    """自動登入檢查（快速）"""
    session_id = get_session_id(request)
    username = validate_session(session_id)
    
    if username:
        print(f"✅ 自動登入: {username}")
        return username, gr.update(visible=False), gr.update(visible=True)
    
    return None, gr.update(visible=True), gr.update(visible=False)

def logout_user(request: gr.Request):
    """使用者登出"""
    session_id = get_session_id(request)
    delete_session(session_id)
    return gr.update(visible=True), gr.update(visible=False), None, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])

def is_expiring_soon(expiry_date_str):
    """檢查是否即將到期（7天內）"""
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        today = datetime.now()
        days_until_expiry = (expiry - today).days
        return 0 <= days_until_expiry <= 7
    except:
        return False

def is_expired(expiry_date_str):
    """檢查是否已過期"""
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        return expiry < datetime.now()
    except:
        return False

def format_date(date_str):
    """格式化日期"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y/%m/%d')
    except:
        return date_str

def add_deposit(username, item, quantity, store, redeem_method, expiry_year, expiry_month, expiry_day):
    """新增寄杯記錄"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not all([item, store, redeem_method, expiry_year, expiry_month, expiry_day]):
        return "❌ 請填寫所有欄位", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    # 組合日期
    try:
        expiry_date = f"{expiry_year}-{expiry_month}-{expiry_day}"
        datetime.strptime(expiry_date, '%Y-%m-%d')  # 驗證日期格式
    except:
        return "❌ 日期格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return "❌ 數量必須大於 0", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    except:
        return "❌ 數量格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = load_deposits(username)
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item.strip(),
        'quantity': quantity,
        'store': store,
        'redeemMethod': redeem_method,
        'expiryDate': expiry_date,
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    
    if save_deposits(username, deposits):
        return "✅ 新增成功！", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        return "❌ 儲存失敗", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def get_deposit_choices(username):
    """取得寄杯記錄選項"""
    if not username:
        return gr.update(choices=[], value=None)
    
    deposits = load_deposits(username)
    if not deposits:
        return gr.update(choices=[], value=None)
    
    global deposit_label_to_id
    deposit_label_to_id = {}
    choices_list = []
    
    for d in deposits:
        expired_tag = " [已過期]" if is_expired(d['expiryDate']) else ""
        expiring_tag = " [即將到期]" if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate']) else ""
        label = f"{d['item']} - {d['store']} ({d['quantity']}杯) - 到期:{format_date(d['expiryDate'])}{expired_tag}{expiring_tag}"
        
        deposit_label_to_id[label] = d['id']
        choices_list.append(label)
    
    return gr.update(choices=choices_list, value=None)

def redeem_one(username, deposit_label):
    """兌換一杯"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not deposit_label:
        return "❌ 請選擇要兌換的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposit_id = deposit_label_to_id.get(deposit_label)
    if not deposit_id:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = load_deposits(username)
    updated = False
    deposit_name = ""
    
    for i, deposit in enumerate(deposits):
        if deposit['id'] == deposit_id:
            deposit_name = deposit['item']
            if deposit['quantity'] > 1:
                deposits[i]['quantity'] -= 1
                message = f"✅ 已兌換一杯 {deposit_name}，剩餘 {deposits[i]['quantity']} 杯"
            else:
                deposits = [d for d in deposits if d['id'] != deposit_id]
                message = f"✅ 已兌換最後一杯 {deposit_name}，記錄已刪除"
            updated = True
            break
    
    if updated:
        save_deposits(username, deposits)
        return message, get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def delete_deposit(username, deposit_label):
    """刪除寄杯記錄"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not deposit_label:
        return "❌ 請選擇要刪除的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposit_id = deposit_label_to_id.get(deposit_label)
    if not deposit_id:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = load_deposits(username)
    deposit_name = ""
    
    for d in deposits:
        if d['id'] == deposit_id:
            deposit_name = d['item']
            break
    
    deposits = [d for d in deposits if d['id'] != deposit_id]
    save_deposits(username, deposits)
    
    return f"✅ 已刪除 {deposit_name} 的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def get_deposits_display(username):
    """取得寄杯記錄顯示"""
    if not username:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">🔒</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">請先登入</p>
            <p style="font-size: 16px; color: #9ca3af;">登入後即可查看您的寄杯記錄</p>
        </div>
        """
    
    deposits = load_deposits(username)
    
    if not deposits:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
            <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯記錄」開始記錄吧！</p>
        </div>
        """
    
    deposits.sort(key=lambda x: x.get('expiryDate', '9999-12-31'))
    
    html = '<div style="display: flex; flex-direction: column; gap: 20px;">'
    
    for deposit in deposits:
        expired = is_expired(deposit['expiryDate'])
        expiring = is_expiring_soon(deposit['expiryDate']) and not expired
        
        if expired:
            card_style = "background: #fef2f2; border: 2px solid #fca5a5;"
            status_text = "（已過期）"
            status_color = "#dc2626"
        elif expiring:
            card_style = "background: #fefce8; border: 2px solid #fde047;"
            status_text = "（即將到期）"
            status_color = "#ca8a04"
        else:
            card_style = "background: white; border: 1px solid #e5e7eb;"
            status_text = ""
            status_color = "#6b7280"
        
        redeem_info = REDEEM_LINKS.get(deposit['redeemMethod'], {
            'app': '#',
            'name': deposit['redeemMethod']
        })
        app_link = redeem_info['app']
        app_name = redeem_info['name']
        google_maps_link = f"https://www.google.com/maps/search/{deposit['store']}"
        
        html += f"""
        <div style="padding: 24px; border-radius: 16px; {card_style} box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap;">
                    <h3 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">{deposit['item']}</h3>
                    <span style="background: #fef3c7; color: #92400e; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 600;">
                        {deposit['quantity']} 杯
                    </span>
                </div>
                <div style="color: #4b5563; line-height: 2; font-size: 15px;">
                    <div style="margin-bottom: 6px;">📍 <strong>商店：</strong>{deposit['store']}</div>
                    <div style="margin-bottom: 6px;">📦 <strong>兌換途徑：</strong>{deposit['redeemMethod']}</div>
                    <div>📅 <strong>到期日：</strong>{format_date(deposit['expiryDate'])} 
                        <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
                <a href="{app_link}" target="_blank" 
                   style="background: #9333ea; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s; box-shadow: 0 2px 4px rgba(147, 51, 234, 0.3);">
                    📱 開啟 {app_name} App
                </a>
                <a href="{google_maps_link}" target="_blank" 
                   style="background: #2563eb; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🗺️ 查看商店位置
                </a>
            </div>
            <div style="padding: 12px; background: #f9fafb; border-radius: 8px; font-size: 12px; color: #6b7280;">
                💡 <strong>提示：</strong>點擊「開啟 App」會嘗試開啟手機 App
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def get_statistics(username):
    """取得統計資訊"""
    if not username:
        return ""
    
    deposits = load_deposits(username)
    
    if not deposits:
        return ""
    
    total_cups = sum(d['quantity'] for d in deposits)
    valid_records = len([d for d in deposits if not is_expired(d['expiryDate'])])
    expired_records = len([d for d in deposits if is_expired(d['expiryDate'])])
    expiring_soon = len([d for d in deposits if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate'])])
    
    html = f"""
    <div style="background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 24px;">
        <h3 style="font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 20px;">📊 統計資訊</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 20px; text-align: center;">
            <div style="padding: 16px; background: #fffbeb; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #d97706; margin: 0;">{total_cups}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">總杯數</p>
            </div>
            <div style="padding: 16px; background: #f0fdf4; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #16a34a; margin: 0;">{valid_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">有效記錄</p>
            </div>
            <div style="padding: 16px; background: #fefce8; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #ca8a04; margin: 0;">{expiring_soon}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">即將到期</p>
            </div>
            <div style="padding: 16px; background: #fef2f2; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #dc2626; margin: 0;">{expired_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">已過期</p>
            </div>
        </div>
    </div>
    """
    return html

def refresh_display(username):
    """重新整理顯示"""
    return get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def preload_data():
    """預載入常用資料"""
    print("🔄 預載入資料中...")
    load_users()
    load_sessions()
    print("✅ 預載入完成")

threading.Thread(target=preload_data, daemon=True).start()

# 建立 Gradio 介面
with gr.Blocks(
    title="☕ 咖啡寄杯記錄",
    theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
    css=CUSTOM_CSS
) as app:
    
    current_user = gr.State(None)
    
    gr.HTML("""
        <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px;">
            <h1 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">
                咖啡寄杯記錄系統
            </h1>
            <p style="color: #6b7280; margin-top: 8px; font-size: 14px;">管理你的咖啡寄杯，不怕忘記兌換 ☕✨</p>
        </div>
    """)
    
    with gr.Column(visible=True) as login_area:
        with gr.Tabs():
            with gr.Tab("🔐 登入"):
                login_status = gr.Markdown()
                login_username = gr.Textbox(label="使用者名稱", placeholder="請輸入使用者名稱")
                login_password = gr.Textbox(label="密碼", type="password", placeholder="請輸入密碼")
                remember_me_checkbox = gr.Checkbox(label="記住我（30天內自動登入）", value=True)
                login_btn = gr.Button("登入", variant="primary", size="lg")
            
            with gr.Tab("📝 註冊"):
                register_status = gr.Markdown()
                register_username = gr.Textbox(label="使用者名稱", placeholder="至少 3 個字元")
                register_password = gr.Textbox(label="密碼", type="password", placeholder="至少 6 個字元")
                register_confirm = gr.Textbox(label="確認密碼", type="password", placeholder="再次輸入密碼")
                register_btn = gr.Button("註冊", variant="primary", size="lg")
    
    with gr.Column(visible=False) as main_area:
        with gr.Row():
            user_info = gr.Markdown()
            logout_btn = gr.Button("🚪 登出", size="sm")
        
        gr.Markdown("---")
        
        with gr.Accordion("➕ 新增寄杯記錄", open=True):
            with gr.Row():
                item_input = gr.Textbox(
                    label="☕ 咖啡品項", 
                    placeholder="例如：美式咖啡、拿鐵",
                    scale=2
                )
                quantity_input = gr.Number(
                    label="🔢 數量（杯）", 
                    value=1, 
                    minimum=1, 
                    precision=0,
                    scale=1
                )
            
            with gr.Row():
                store_input = gr.Dropdown(
                    label="🏪 商店名稱", 
                    choices=STORE_OPTIONS,
                    value=STORE_OPTIONS[0],
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
                redeem_method_input = gr.Dropdown(
                    label="📦 兌換途徑", 
                    choices=REDEEM_METHODS,
                    value=REDEEM_METHODS[0],
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
            
            # 到期日：年、月、日分開選擇
            gr.Markdown("### 📅 到期日")
            with gr.Row():
                expiry_year = gr.Dropdown(
                    label="年",
                    choices=[str(year) for year in range(2024, 2031)],
                    value=str(datetime.now().year),
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
                expiry_month = gr.Dropdown(
                    label="月",
                    choices=[f"{month:02d}" for month in range(1, 13)],
                    value=f"{datetime.now().month:02d}",
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
                expiry_day = gr.Dropdown(
                    label="日",
                    choices=[f"{day:02d}" for day in range(1, 32)],
                    value=f"{datetime.now().day:02d}",
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
            
            add_status = gr.Markdown()
            add_btn = gr.Button("💾 儲存記錄", variant="primary", size="lg")
        
        gr.Markdown("---")
        
        with gr.Accordion("☕ 兌換 / 刪除寄杯記錄", open=True):
            gr.Markdown("💡 **提示：** 在下方選擇記錄後，點擊「兌換一杯」或「刪除記錄」按鈕")
            action_status = gr.Markdown()
            deposit_selector = gr.Dropdown(
                label="📋 選擇寄杯記錄",
                choices=[],
                value=None,
                interactive=True,
                elem_classes=["dropdown-readonly"]
            )
            
            with gr.Row():
                redeem_btn = gr.Button("☕ 兌換一杯", variant="primary", size="lg", scale=2)
                delete_btn = gr.Button("🗑️ 刪除記錄", variant="stop", size="lg", scale=1)
                refresh_btn = gr.Button("🔄 重新整理", size="lg", scale=1)
        
        gr.Markdown("---")
        gr.Markdown("### 📋 所有寄杯記錄")
        
        deposits_display = gr.HTML(value=get_deposits_display(None))
        statistics_display = gr.HTML(value=get_statistics(None))
    
    # 頁面載入時自動登入
    def on_load(request: gr.Request):
        """頁面載入時檢查 Session（快速）"""
        user, login_vis, main_vis = auto_login(request)
        if user:
            user_display = f"👤 使用者：**{user}**"
            deposits = get_deposits_display(user)
            stats = get_statistics(user)
            choices = get_deposit_choices(user)
            return user, login_vis, main_vis, user_display, deposits, stats, choices
        return None, login_vis, main_vis, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])
    
    app.load(
        fn=on_load,
        outputs=[current_user, login_area, main_area, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 註冊
    def register_and_update(username, password, confirm):
        """註冊處理"""
        return register_user(username, password, confirm)
    
    register_btn.click(
        fn=register_and_update,
        inputs=[register_username, register_password, register_confirm],
        outputs=[register_status, login_area, main_area]
    )
    
    register_confirm.submit(
        fn=register_and_update,
        inputs=[register_username, register_password, register_confirm],
        outputs=[register_status, login_area, main_area]
    )
    
    # 事件處理 - 登入
    def login_and_update(username, password, remember_me, request: gr.Request):
        """登入並更新所有相關狀態"""
        message, login_vis, main_vis, user = login_user(username, password, remember_me, request)
        
        if user:
            user_display = f"👤 使用者：**{user}**"
            deposits = get_deposits_display(user)
            stats = get_statistics(user)
            choices = get_deposit_choices(user)
            return message, login_vis, main_vis, user, user_display, deposits, stats, choices
        else:
            return message, login_vis, main_vis, None, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])
    
    login_btn.click(
        fn=login_and_update,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    login_username.submit(
        fn=login_and_update,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    login_password.submit(
        fn=login_and_update,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 登出
    logout_btn.click(
        fn=logout_user,
        outputs=[login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 新增記錄
    def add_and_refresh(user, item, quantity, store, redeem_method, expiry_year, expiry_month, expiry_day):
        """新增記錄並刷新顯示"""
        message, deposits, stats, choices = add_deposit(user, item, quantity, store, redeem_method, expiry_year, expiry_month, expiry_day)
        return message, deposits, stats, choices
    
    add_btn.click(
        fn=add_and_refresh,
        inputs=[current_user, item_input, quantity_input, store_input, redeem_method_input, expiry_year, expiry_month, expiry_day],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    
    item_input.submit(
        fn=add_and_refresh,
        inputs=[current_user, item_input, quantity_input, store_input, redeem_method_input, expiry_year, expiry_month, expiry_day],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 兌換
    def redeem_and_refresh(user, deposit_id):
        """兌換並刷新顯示"""
        message, deposits, stats, choices = redeem_one(user, deposit_id)
        return message, deposits, stats, choices
    
    redeem_btn.click(
        fn=redeem_and_refresh,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 刪除
    def delete_and_refresh(user, deposit_id):
        """刪除並刷新顯示"""
        message, deposits, stats, choices = delete_deposit(user, deposit_id)
        return message, deposits, stats, choices
    
    delete_btn.click(
        fn=delete_and_refresh,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 重新整理
    def refresh_all(user):
        """重新整理所有顯示"""
        deposits, stats, choices = refresh_display(user)
        return deposits, stats, choices
    
    refresh_btn.click(
        fn=refresh_all,
        inputs=[current_user],
        outputs=[deposits_display, statistics_display, deposit_selector]
    )

if __name__ == "__main__":
    app.launch()
