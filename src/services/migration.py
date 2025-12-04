# src/services/migration.py

from datetime import datetime
from . import storage

def migrate_user_data():
    """自動補全舊用戶資料欄位"""
    users = storage.load_users()
    updated = False
    
    for username, user_info in users.items():
        if 'email' not in user_info:
            user_info['email'] = None
            updated = True
            print(f"✅ 為用戶 {username} 補全 email 欄位")
        
        if 'last_login' not in user_info:
            user_info['last_login'] = user_info.get('created_at', datetime.now().isoformat())
            updated = True
            print(f"✅ 為用戶 {username} 補全 last_login 欄位")
        
        if 'password_version' not in user_info:
            user_info['password_version'] = 'v1'
            updated = True
            print(f"✅ 為用戶 {username} 補全 password_version 欄位")
    
    if updated:
        storage.save_users(users)
        print("✅ 用戶資料遷移完成")
    else:
        print("ℹ️ 所有用戶資料已是最新格式，無需遷移")
    
    return users
