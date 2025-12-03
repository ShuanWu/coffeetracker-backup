import sqlite3
import os
import config
from datetime import datetime

# 確保資料目錄存在
if not os.path.exists(config.DATA_DIR):
    try:
        os.makedirs(config.DATA_DIR)
    except OSError:
        pass

def get_db():
    """建立資料庫連線"""
    conn = sqlite3.connect(config.DB_FILE)
    conn.row_factory = sqlite3.Row  # 讓回傳結果可以像 dict 一樣操作
    return conn

def init_db():
    """初始化資料庫表格"""
    conn = get_db()
    c = conn.cursor()
    
    # 使用者表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    
    # Session 表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            created_at TEXT,
            expires_at TEXT
        )
    ''')
    
    # 寄杯記錄表格
    c.execute('''
        CREATE TABLE IF NOT EXISTS deposits (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            item TEXT,
            quantity INTEGER,
            store TEXT,
            redeem_method TEXT,
            expiry_date TEXT,
            created_at TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ 資料庫已初始化: {config.DB_FILE}")

# === 使用者相關操作 ===

def get_user(username):
    """取得單一使用者資料"""
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(username, password_hash, created_at):
    """建立新使用者"""
    conn = get_db()
    try:
        conn.execute(
            'INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)',
            (username, password_hash, created_at)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# === Session 相關操作 ===

def save_session(session_id, username, created_at, expires_at):
    """儲存 Session"""
    conn = get_db()
    conn.execute(
        'INSERT OR REPLACE INTO sessions (session_id, username, created_at, expires_at) VALUES (?, ?, ?, ?)',
        (session_id, username, created_at, expires_at)
    )
    conn.commit()
    conn.close()

def get_session(session_id):
    """取得 Session"""
    conn = get_db()
    session = conn.execute('SELECT * FROM sessions WHERE session_id = ?', (session_id,)).fetchone()
    conn.close()
    return dict(session) if session else None

def delete_session(session_id):
    """刪除 Session"""
    conn = get_db()
    conn.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    conn.commit()
    conn.close()

def cleanup_expired_sessions():
    """清除過期 Session"""
    conn = get_db()
    now = datetime.now().isoformat()
    conn.execute('DELETE FROM sessions WHERE expires_at < ?', (now,))
    conn.commit()
    conn.close()

# === 寄杯記錄相關操作 ===

def get_user_deposits(username):
    """取得使用者的所有寄杯記錄"""
    conn = get_db()
    rows = conn.execute('SELECT * FROM deposits WHERE username = ?', (username,)).fetchall()
    conn.close()
    
    # 轉換成 List[dict] 格式以相容原本的邏輯
    results = []
    for row in rows:
        d = dict(row)
        # 資料庫欄位轉換 (snake_case -> camelCase) 若前端需要
        results.append({
            'id': d['id'],
            'username': d['username'],
            'item': d['item'],
            'quantity': d['quantity'],
            'store': d['store'],
            'redeemMethod': d['redeem_method'], # 注意這裡對應 config/logic 的命名
            'expiryDate': d['expiry_date'],
            'createdAt': d['created_at']
        })
    return results

def add_deposit(deposit_data):
    """新增寄杯記錄"""
    conn = get_db()
    try:
        conn.execute(
            '''INSERT INTO deposits 
               (id, username, item, quantity, store, redeem_method, expiry_date, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                deposit_data['id'],
                deposit_data['username'],
                deposit_data['item'],
                deposit_data['quantity'],
                deposit_data['store'],
                deposit_data['redeemMethod'],
                deposit_data['expiryDate'],
                deposit_data['createdAt']
            )
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"新增失敗: {e}")
        return False
    finally:
        conn.close()

def update_deposit_quantity(deposit_id, new_quantity):
    """更新寄杯數量"""
    conn = get_db()
    conn.execute('UPDATE deposits SET quantity = ? WHERE id = ?', (new_quantity, deposit_id))
    conn.commit()
    conn.close()

def delete_deposit(deposit_id):
    """刪除寄杯記錄"""
    conn =