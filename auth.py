import hashlib
from datetime import datetime, timedelta
import gradio as gr
from storage import load_json_file, save_json_file, get_user_data_file, upload_to_hf_async, cache, cache_lock
from config import USERS_FILE, SESSIONS_FILE, SESSION_EXPIRE_DAYS
import json


def hash_password(password):
    """密碼加密"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_session(username, request: gr.Request):
    """創建 Session Token"""
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    
    with cache_lock:
        sessions = cache['sessions'] if cache['sessions'] else load_json_file(SESSIONS_FILE, 'sessions')
    
    now = datetime.now()
    sessions = {k: v for k, v in sessions.items() 
                if datetime.fromisoformat(v['expires_at']) > now}
    
    sessions[session_id] = {
        'username': username,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=SESSION_EXPIRE_DAYS)).isoformat()
    }
    save_json_file(SESSIONS_FILE, sessions, 'sessions')
    
    print(f"✅ 創建 Session: {session_id} for {username}")
    return session_id


def get_session_id(request: gr.Request):
    """獲取當前客戶端的 Session ID"""
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    return session_id


def validate_session(session_id):
    """驗證 Session"""
    with cache_lock:
        sessions = cache['sessions'] if cache['sessions'] else load_json_file(SESSIONS_FILE, 'sessions')
    
    if session_id not in sessions:
        return None
    
    session = sessions[session_id]
    try:
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            del sessions[session_id]
            save_json_file(SESSIONS_FILE, sessions, 'sessions')
            return None
        
        return session['username']
    except:
        return None


def delete_session(session_id):
    """刪除 Session"""
    with cache_lock:
        sessions = cache['sessions'] if cache['sessions'] else load_json_file(SESSIONS_FILE, 'sessions')
    
    if session_id in sessions:
        del sessions[session_id]
        save_json_file(SESSIONS_FILE, sessions, 'sessions')


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
    
    users = load_json_file(USERS_FILE, 'users')
    
    if username in users:
        return "❌ 使用者名稱已存在", gr.update(visible=True), gr.update(visible=False)
    
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    if save_json_file(USERS_FILE, users, 'users'):
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
    
    users = load_json_file(USERS_FILE, 'users')
    
    if username not in users:
        return "❌ 使用者不存在", gr.update(visible=True), gr.update(visible=False), None
    
    if users[username]['password'] != hash_password(password):
        return "❌ 密碼錯誤", gr.update(visible=True), gr.update(visible=False), None
    
    if remember_me:
        create_session(username, request)
    
    return f"✅ 歡迎回來，{username}！", gr.update(visible=False), gr.update(visible=True), username


def auto_login(request: gr.Request):
    """自動登入檢查"""
    session_id = get_session_id(request)
    username = validate_session(session_id)
    
    if username:
        print(f"✅ 自動登入: {username}")
        return username, gr.update(visible=False), gr.update(visible=True)
    
    return None, gr.update(visible=True), gr.update(visible=False)


def logout_user(request: gr.Request):
    """使用者登出"""
    try:
        session_id = get_session_id(request)
        delete_session(session_id)
    except:
        pass
