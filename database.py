import os
import json
import threading
from huggingface_hub import HfApi, hf_hub_download, upload_file
import config  # 匯入剛剛建立的 config

# 確保資料目錄存在
if not os.path.exists(config.DATA_DIR):
    os.makedirs(config.DATA_DIR)

api = HfApi()

# 記憶體快取與鎖
cache = {
    'users': None,
    'sessions': {},
    'deposits': {},
    'loading': set()
}
cache_lock = threading.Lock()

def download_from_hf(filename):
    """從 Hugging Face Space 下載檔案"""
    try:
        if config.HF_TOKEN and config.HF_REPO:
            return hf_hub_download(
                repo_id=config.HF_REPO,
                filename=filename,
                repo_type="space",
                token=config.HF_TOKEN,
                force_download=False
            )
    except Exception as e:
        print(f"下載 {filename} 失敗: {e}")
    return None

def upload_to_hf_async(filepath):
    """非同步上傳到 Hugging Face"""
    def upload():
        try:
            if config.HF_TOKEN and config.HF_REPO:
                upload_file(
                    path_or_fileobj=filepath,
                    path_in_repo=filepath,
                    repo_id=config.HF_REPO,
                    repo_type="space",
                    token=config.HF_TOKEN
                )
                print(f"✅ 已上傳 {filepath}")
        except Exception as e:
            print(f"❌ 上傳 {filepath} 失敗: {e}")
    threading.Thread(target=upload, daemon=True).start()

def load_users():
    with cache_lock:
        if cache['users'] is not None: return cache['users']
    
    if os.path.exists(config.USERS_FILE):
        try:
            with open(config.USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with cache_lock: cache['users'] = data
                return data
        except: pass
    
    # 若本地沒有，嘗試從 HF 下載 (簡化版，邏輯同原檔)
    hf_file = download_from_hf(config.USERS_FILE)
    if hf_file and os.path.exists(hf_file):
        try:
            with open(hf_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(config.USERS_FILE, 'w', encoding='utf-8') as local_f:
                json.dump(data, local_f, ensure_ascii=False, indent=2)
            with cache_lock: cache['users'] = data
            return data
        except: pass

    with cache_lock:
        if cache['users'] is None: cache['users'] = {}
        return cache['users']

def save_users(users):
    try:
        with cache_lock: cache['users'] = users
        with open(config.USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        upload_to_hf_async(config.USERS_FILE)
        return True
    except Exception as e:
        print(f"儲存使用者資料錯誤: {e}")
        return False

def load_sessions():
    with cache_lock:
        if cache['sessions']: return cache['sessions']
    # ... (載入 Session 的邏輯同原檔，省略重複代碼，請參照原檔 load_sessions) ...
    # 建議將原檔 load_sessions 的完整內容複製過來
    return {}

def save_sessions(sessions):
    # ... (儲存 Session 的邏輯同原檔) ...
    try:
        with cache_lock: cache['sessions'] = sessions
        with open(config.SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
        upload_to_hf_async(config.SESSIONS_FILE)
        return True
    except: return False

def get_user_data_file(username):
    if not username: return None
    return os.path.join(config.DATA_DIR, f'{username}.json')

def load_deposits(username):
    # ... (載入寄杯資料的邏輯同原檔，請複製原檔 load_deposits) ...
    # 注意：請將 DATA_DIR 替換為 config.DATA_DIR
    if not username: return []
    with cache_lock:
        if username in cache['deposits']: return cache['deposits'][username]
    
    # (此處需補完原檔 load_deposits 的實作)
    # 為了版面簡潔，請複製原檔內容，並確保變數引用 config
    return []

def save_deposits(username, deposits):
    data_file = get_user_data_file(username)
    if not data_file: return False
    try:
        with cache_lock: cache['deposits'][username] = deposits
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(deposits, f, ensure_ascii=False, indent=2)
        upload_to_hf_async(data_file)
        return True
    except Exception as e:
        return False