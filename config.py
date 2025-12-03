import os

# Hugging Face 設定
HF_TOKEN = os.getenv("HF_TOKEN")
HF_REPO = os.getenv("SPACE_ID")

# 檔案路徑
USERS_FILE = 'users.json'
DATA_DIR = 'user_data'
SESSIONS_FILE = 'sessions.json'

# 商店和兌換選項
STORE_OPTIONS = ['7-11', '全家', '星巴克']
REDEEM_METHODS = ['7-11', '全家', 'Line禮物', '全家酷碰劵', '遠傳', '星巴克']

# 兌換連結對應
REDEEM_LINKS = {
    '7-11': {
        'app': 'openpointapp://gofeature?featureId=HOMACB02',
        'name': 'OPENPOINT'
    },
    '全家': {
        'app': 'familymart://action.go/preorder/myproduct',
        'name': '全家便利商店'
    },
    '遠傳': {
        'app': 'fetnet://',
        'name': '遠傳心生活'
    },
    'Line禮物': {
        'app': 'https://line.me/R/shop/gift/category/coffee',
        'name': 'Line 禮物'
    },
    '全家酷碰劵': {
        'app': 'familymart://action.go/preorder/coupon',
        'name': '全家酷碰劵'
    },
    '星巴克': {
        'app': 'starbucks://',
        'name': '星巴克'
    }
}

# Session 設定
SESSION_EXPIRE_DAYS = 30
