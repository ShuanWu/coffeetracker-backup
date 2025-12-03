import os
import json
import threading
from huggingface_hub import HfApi, hf_hub_download, upload_file
import config

# 確保資料目錄存在
if not os.path.exists(config.DATA_DIR):
    os.makedirs(config.DATA_DIR)

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

def download_from_hf(filename):
    """從 Hugging Face Space 下載檔案"""
    try:
        if config.HF_TOKEN and config.HF_REPO:
            local_path = hf_hub_download(
                repo_id=config.HF_REPO,
                filename=filename,
                repo_type="space",
                token=config.HF_TOKEN,
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
    
    thread = threading.Thread(target=upload, daemon=True)
    thread.start()

def load_users():
    """載入使用者資料（優先使用快取）"""
    with cache_lock:
        if cache['users'] is not None:
            return cache['users']
    
    if os.path.exists(config.USERS_FILE):
        try:
            with open(config.USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with cache_lock:
                    cache['users'] = data
                return data
        except:
            pass
    
    def load_from_hf():
        hf_file = download_from_hf(config.USERS_FILE)
        if hf_file and os.path.exists(hf_file):
            try:
                with open(hf_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with open(config.USERS_FILE, 'w', encoding='utf-8') as local_f:
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
        
        with open(config.USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        
        upload_to_hf_async(config.USERS_FILE)
        return True
    except Exception as e:
        print(f"儲存使用者資料錯誤: {e}")
        return False

def load_sessions():
    """載入 Session 資料（優先使用快取）"""
    with cache_lock:
        if cache['sessions']:
            return cache['sessions']
    
    if os.path.exists(config.SESSIONS_FILE):
        try:
            with open(config.SESSIONS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                with cache_lock:
                    cache['sessions'] = data
                return data
        except:
            pass
    
    def load_from_hf():
        hf_file = download_from_hf(config.SESSIONS_FILE)
        if hf_file and os.path.exists(hf_file):
            try:
                with open(hf_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with open(config.SESSIONS_FILE, 'w', encoding='utf-8') as local_f:
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
        
        with open(config.SESSIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(sessions, f, ensure_ascii=False, indent=2)
        
        upload_to_hf_async(config.SESSIONS_FILE)
        return True
    except:
        return False

def get_user_data_file(username):
    """取得使用者資料檔案路徑"""
    if not username:
        return None
    return os.path.join(config.DATA_DIR, f'{username}.json')

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
        hf_path = f"{config.DATA_DIR}/{username}.json"
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