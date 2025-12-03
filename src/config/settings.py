# src/config/settings.py

import os

# Hugging Face 設定
HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO = os.getenv("SPACE_ID")  # 這是程式碼所在的 Space
# 資料儲存專用的 Dataset ID
DATA_REPO = "ShuanWu/coffee-data"

# 檔案路徑設定
# 統一將所有資料放在 data 資料夾下，方便同步
DATA_DIR = 'data' 
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
SESSIONS_FILE = os.path.join(DATA_DIR, 'sessions.json')
USER_DATA_DIR = os.path.join(DATA_DIR, 'user_records')  # 用戶個別資料夾