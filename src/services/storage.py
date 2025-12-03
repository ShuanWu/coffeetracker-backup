# src/services/storage.py

import os
import json
from pathlib import Path
from huggingface_hub import CommitScheduler, snapshot_download
from ..config import settings

# 1. 確保本地資料目錄存在
os.makedirs(settings.USER_DATA_DIR, exist_ok=True)

# 2. 初始化：從 Dataset 下載現有資料 (啟動時執行一次)
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
    print(f"初次下載資料略過 (可能是第一次建立): {e}")

# 3. 設定 CommitScheduler (自動背景同步)
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
    # 使用 CommitScheduler 的 lock 確保線程安全
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