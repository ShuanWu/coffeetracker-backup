# src/services/storage.py

import os
import json
import shutil
from pathlib import Path
from huggingface_hub import CommitScheduler, snapshot_download
from ..config import settings

# 1. 確保本地資料目錄存在
os.makedirs(settings.USER_DATA_DIR, exist_ok=True)

# 2. 初始化：從 Dataset 下載現有資料
try:
    print("正在從 Dataset 同步資料...")
    snapshot_download(
        repo_id=settings.DATA_REPO,
        repo_type="dataset",
        local_dir=settings.DATA_DIR,
        token=settings.HF_TOKEN
    )
    print("資料同步完成")
except Exception as e:
    print(f"初次下載資料略過: {e}")

# 3. 設定 CommitScheduler
scheduler = CommitScheduler(
    repo_id=settings.DATA_REPO,
    repo_type="dataset",
    folder_path=settings.DATA_DIR,
    path_in_repo=".",
    every=1,
    token=settings.HF_TOKEN
)

# === 通用讀寫函式 ===

def _load_json(filepath, default=None):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default if default is not None else {}
    return default if default is not None else {}

def _save_json(filepath, data):
    with scheduler.lock:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# === 業務邏輯函式 ===

def load_users():
    return _load_json(settings.USERS_FILE, {})

def save_users(users):
    try:
        _save_json(settings.USERS_FILE, users)
        return True
    except Exception as e:
        print(f"儲存用戶錯誤: {e}")
        return False

def delete_user_from_db(username):
    """刪除用戶及其所有資料"""
    # 1. 刪除 users.json 中的條目
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
    
    # 2. 刪除該用戶的資料檔案
    user_file = get_user_data_file(username)
    if os.path.exists(user_file):
        with scheduler.lock:
            try:
                os.remove(user_file)
            except OSError as e:
                print(f"刪除用戶檔案失敗: {e}")
                return False
    return True

def load_sessions():
    return _load_json(settings.SESSIONS_FILE, {})

def save_sessions(sessions):
    try:
        _save_json(settings.SESSIONS_FILE, sessions)
        return True
    except:
        return False

def get_user_data_file(username):
    return os.path.join(settings.USER_DATA_DIR, f'{username}.json')

def load_deposits(username):
    if not username: return []
    filepath = get_user_data_file(username)
    return _load_json(filepath, [])

def save_deposits(username, deposits):
    if not username: return False
    filepath = get_user_data_file(username)
    try:
        _save_json(filepath, deposits)
        return True
    except Exception as e:
        print(f"儲存寄杯錯誤: {e}")
        return False

def get_all_user_files():
    """取得所有用戶資料檔案列表（供管理員統計用）"""
    if not os.path.exists(settings.USER_DATA_DIR):
        return []
    return [f for f in os.listdir(settings.USER_DATA_DIR) if f.endswith('.json')]