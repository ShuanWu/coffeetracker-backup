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

# 管理員設定
# 在這裡定義管理員的帳號名稱列表
# 管理員設定（建議從環境變數讀取）
import os
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # 請在環境變數中設定