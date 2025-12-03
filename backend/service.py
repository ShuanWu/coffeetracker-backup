# backend/service.py
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from . import database # 相對路徑引用同目錄下的 database.py
import config

# === 基礎邏輯 ===
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_login(username, password):
    """驗證登入，回傳結果 Dict"""
    if not username or not password:
        return {"success": False, "message": "❌ 請輸入帳號密碼"}
    
    users = database.load_users()
    if username not in users:
        return {"success": False, "message": "❌ 使用者不存在"}
        
    if users[username]['password'] != hash_password(password):
        return {"success": False, "message": "❌ 密碼錯誤"}
        
    return {"success": True, "message": f"✅ 歡迎，{username}", "username": username}

def register_user(username, password, confirm):
    """註冊邏輯"""
    if not username or len(username) < 3:
        return {"success": False, "message": "❌ 帳號至少 3 字元"}
    if len(password) < 6:
        return {"success": False, "message": "❌ 密碼至少 6 字元"}
    if password != confirm:
        return {"success": False, "message": "❌ 密碼不一致"}
        
    users = database.load_users()
    if username in users:
        return {"success": False, "message": "❌ 帳號已存在"}
        
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    if database.save_users(users):
        database.save_deposits(username, []) # 初始化空資料
        return {"success": True, "message": "✅ 註冊成功"}
    return {"success": False, "message": "❌ 系統錯誤"}

# === 資料存取 ===
def get_user_deposits(username):
    return database.load_deposits(username)

def add_deposit(username, item, quantity, store, method, expiry_date):
    if not username: return {"success": False, "message": "請先登入"}
    
    try:
        qty = int(quantity)
        if qty < 1: raise ValueError
    except:
        return {"success": False, "message": "❌ 數量錯誤"}
        
    deposits = database.load_deposits(username)
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item,
        'quantity': qty,
        'store': store,
        'redeemMethod': method,
        'expiryDate': expiry_date,
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    
    if database.save_deposits(username, deposits):
        return {"success": True, "message": "✅ 新增成功"}
    return {"success": False, "message": "❌ 儲存失敗"}

# === Dashboard 統計邏輯 (新增) ===
def get_dashboard_data(username):
    """計算全系統數據，僅管理員可用"""
    if username not in config.ADMIN_USERS:
        return None

    users = database.load_users()
    all_records = []
    
    # 讀取所有人的資料
    for user in users:
        user_deposits = database.load_deposits(user)
        for d in user_deposits:
            d['username'] = user
            all_records.append(d)
    
    total_users = len(users)
    total_cups = sum(d['quantity'] for d in all_records) if all_records else 0
    
    # 準備圖表資料
    if not all_records:
        return {
            "kpi": {"users": total_users, "cups": 0},
            "store_df": pd.DataFrame(columns=["store", "count"]),
            "item_df": pd.DataFrame(columns=["item", "count"])
        }

    df = pd.DataFrame(all_records)
    
    # 1. 商店分佈
    store_stats = df.groupby('store')['quantity'].sum().reset_index()
    store_stats.columns = ['store', 'count']
    
    # 2. 熱門品項 (Top 5)
    item_stats = df.groupby('item')['quantity'].sum().reset_index()
    item_stats = item_stats.sort_values('count', ascending=False).head(5)
    
    return {
        "kpi": {"users": total_users, "cups": int(total_cups)},
        "store_df": store_stats,
        "item_df": item_stats
    }