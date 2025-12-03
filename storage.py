import json
import os
import threading
from huggingface_hub import HfApi, hf_hub_download, upload_file
from config import HF_TOKEN, HF_REPO, DATA_DIR, USERS_FILE, SESSIONS_FILE

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


def load_json_file(filename, cache_key=None):
    """通用 JSON 載入函數（優先使用快取）"""
    if cache_key:
        with cache_lock:
            if cache.get(cache_key) is not None:
                return cache[cache_key]
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if cache_key:
                    with cache_lock:
                        cache[cache_key] = data
                return data
        except:
            pass
    
    def load_from_hf():
        hf_file = download_from_hf(filename)
        if hf_file and os.path.exists(hf_file):
            try:
                with open(hf_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with open(filename, 'w', encoding='utf-8') as local_f:
                        json.dump(data, local_f, ensure_ascii=False, indent=2)
                    if cache_key:
                        with cache_lock:
                            cache[cache_key] = data
            except:
                pass
    
    thread = threading.Thread(target=load_from_hf, daemon=True)
    thread.start()
    
    return {} if cache_key else []


def save_json_file(filename, data, cache_key=None):
    """通用 JSON 儲存函數"""
    try:
        if cache_key:
            with cache_lock:
                cache[cache_key] = data
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        upload_to_hf_async(filename)
        return True
    except Exception as e:
        print(f"儲存 {filename} 錯誤: {e}")
        return False


def get_user_data_file(username):
    """取得使用者資料檔案路徑"""
    if not username:
        return None
    return os.path.join(DATA_DIR, f'{username}.json')


def preload_data():
    """預載入常用資料"""
    print("🔄 預載入資料中...")
    load_json_file(USERS_FILE, 'users')
    load_json_file(SESSIONS_FILE, 'sessions')
    print("✅ 預載入完成")


# 啟動預載入
threading.Thread(target=preload_data, daemon=True).start()
