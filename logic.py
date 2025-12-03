import hashlib
import gradio as gr
from datetime import datetime, timedelta
import config
import database

# 全域變數用於儲存 label 到 id 的映射
deposit_label_to_id = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# === 日期相關工具 ===
def format_date(date_str):
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y/%m/%d')
    except: return date_str

def is_expired(expiry_date_str):
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return today > expiry
    except: return False

def is_expiring_soon(expiry_date_str):
    # ... (複製原檔 is_expiring_soon) ...
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_until_expiry = (expiry_date - today).days
        return 0 <= days_until_expiry <= 7
    except: return False

def is_expiring_today(expiry_date_str):
    # ... (複製原檔 is_expiring_today) ...
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return expiry_date == today
    except: return False

# === 認證邏輯 ===
def register_user(username, password, confirm_password):
    # ... (邏輯同原檔，但使用 database.load_users 等) ...
    if not username or not password:
        return "❌ 請填寫使用者名稱和密碼", gr.update(visible=True), gr.update(visible=False)
    # (省略部分驗證邏輯)
    users = database.load_users()
    if username in users:
        return "❌ 使用者名稱已存在", gr.update(visible=True), gr.update(visible=False)
    
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    if database.save_users(users):
        user_file = database.get_user_data_file(username)
        with open(user_file, 'w', encoding='utf-8') as f:
            import json
            json.dump([], f)
        database.upload_to_hf_async(user_file)
        return "✅ 註冊成功！請登入", gr.update(visible=True), gr.update(visible=False)
    return "❌ 註冊失敗", gr.update(visible=True), gr.update(visible=False)

def login_user(username, password, remember_me, request: gr.Request):
    if not username or not password:
        return "❌ 請填寫資料", gr.update(visible=True), gr.update(visible=False), None
    users = database.load_users()
    if username not in users or users[username]['password'] != hash_password(password):
        return "❌ 帳號或密碼錯誤", gr.update(visible=True), gr.update(visible=False), None
    
    if remember_me:
        create_session(username, request)
    return f"✅ 歡迎回來，{username}！", gr.update(visible=False), gr.update(visible=True), username

def create_session(username, request: gr.Request):
    # ... (複製原檔 create_session，使用 database.load_sessions) ...
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    sessions = database.load_sessions()
    sessions[session_id] = {
        'username': username,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
    }
    database.save_sessions(sessions)
    return session_id

def get_session_id(request: gr.Request):
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    return hashlib.sha256(client_id.encode()).hexdigest()[:16]

def validate_session(session_id):
    # ... (複製原檔 validate_session，使用 database.load_sessions) ...
    sessions = database.load_sessions()
    if session_id in sessions:
        # 檢查是否過期
        return sessions[session_id]['username']
    return None

def logout_user(request: gr.Request):
    try:
        session_id = get_session_id(request)
        sessions = database.load_sessions()
        if session_id in sessions:
            del sessions[session_id]
            database.save_sessions(sessions)
    except: pass
    return gr.update(visible=True), gr.update(visible=False), None, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])

def auto_login(request: gr.Request):
    session_id = get_session_id(request)
    username = validate_session(session_id)
    if username:
        return username, gr.update(visible=False), gr.update(visible=True)
    return None, gr.update(visible=True), gr.update(visible=False)

# === 寄杯邏輯 ===
def add_deposit(username, item, quantity, store, redeem_method, expiry_method, expiry_date, days_until):
    # ... (複製原檔 add_deposit，注意日期處理邏輯) ...
    # 這裡省略具體實作，請複製原檔並將 save_deposits 改為 database.save_deposits
    if not username: return "❌ 請先登入", get_deposits_display(None), "", gr.update(choices=[])
    
    # 處理日期邏輯 (同原檔)
    final_expiry_date = expiry_date # (需加入原本的判斷邏輯)
    if expiry_method != "選擇日期":
         final_expiry_date = (datetime.now() + timedelta(days=int(days_until))).strftime('%Y-%m-%d')

    deposits = database.load_deposits(username)
    # ... 建構 new_deposit ...
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item, 'quantity': int(quantity), 'store': store,
        'redeemMethod': redeem_method, 'expiryDate': str(final_expiry_date),
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    
    if database.save_deposits(username, deposits):
        return "✅ 新增成功！", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    return "❌ 失敗", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def get_deposit_choices(username):
    # ... (複製原檔 get_deposit_choices) ...
    if not username: return gr.update(choices=[], value=None)
    deposits = database.load_deposits(username)
    # 這裡需要用到全域變數 deposit_label_to_id
    global deposit_label_to_id
    deposit_label_to_id = {}
    choices_list = []
    for d in deposits:
        # ... (標籤生成邏輯) ...
        label = f"{d['item']} - {d['store']}" # 簡化範例
        deposit_label_to_id[label] = d['id']
        choices_list.append(label)
    return gr.update(choices=choices_list, value=None)

def redeem_one(username, deposit_label):
    # ... (複製原檔 redeem_one) ...
    # 請使用 database.load_deposits 和 logic.deposit_label_to_id
    return "邏輯需複製原檔", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def delete_deposit(username, deposit_label):
    # ... (複製原檔 delete_deposit) ...
    return "邏輯需複製原檔", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

# === UI 生成邏輯 ===
def get_deposits_display(username):
    # ... (複製原檔 get_deposits_display，使用 database.load_deposits 和 config.REDEEM_LINKS) ...
    if not username: return "請先登入"
    return "HTML 內容 (請複製原檔)"

def get_statistics(username):
    # ... (複製原檔 get_statistics) ...
    return "HTML 內容 (請複製原檔)"

def refresh_display(username):
    return get_deposits_display(username), get_statistics(username), get_deposit_choices(username)