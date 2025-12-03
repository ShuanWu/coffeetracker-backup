import os

# Hugging Face 設定
HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO = os.getenv("SPACE_ID")

# 檔案路徑
USERS_FILE = 'users.json'
DATA_DIR = 'user_data'
SESSIONS_FILE = 'sessions.json'

# 選項設定
STORE_OPTIONS = ['7-11', '全家', '星巴克']
REDEEM_METHODS = ['7-11', '全家', 'Line禮物', '全家酷碰劵', '遠傳', '星巴克']

# 兌換連結對應
REDEEM_LINKS = {
    '7-11': {'app': 'openpointapp://gofeature?featureId=HOMACB02', 'name': 'OPENPOINT'},
    '全家': {'app': 'familymart://action.go/preorder/myproduct', 'name': '全家便利商店'},    
    '遠傳': {'app': 'fetnet://', 'name': '遠傳心生活'},
    'Line禮物': {'app': 'https://line.me/R/shop/gift/category/coffee', 'name': 'Line 禮物'},
    '全家酷碰劵': {'app': 'familymart://action.go/preorder/coupon', 'name': '全家酷碰劵'},    
    '星巴克': {'app': 'starbucks://', 'name': '星巴克'}
}

# CSS 樣式 (原文太長，這裡保留關鍵部分，請將原 app.py 的 CUSTOM_CSS 完整貼過來)
CUSTOM_CSS = """
/* ... 請在此處貼上原 app.py 中的完整 CUSTOM_CSS 內容 ... */
#expiry_date_picker .timebox input:first-child { display: none !important; }
/* ... (省略以節省版面，請務必複製完整 CSS) ... */
"""