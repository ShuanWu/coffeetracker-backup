import gradio as gr
import hashlib
import json
import os
from datetime import datetime, timedelta
import config
import database

# 全域變數用於儲存 label 到 id 的映射
deposit_label_to_id = {}

def hash_password(password):
    """密碼加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(username, request: gr.Request):
    """創建 Session Token"""
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    
    sessions = database.load_sessions()
    
    now = datetime.now()
    sessions = {k: v for k, v in sessions.items() 
                if datetime.fromisoformat(v['expires_at']) > now}
    
    sessions[session_id] = {
        'username': username,
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(days=30)).isoformat()
    }
    database.save_sessions(sessions)
    
    print(f"✅ 創建 Session: {session_id} for {username}")
    return session_id

def get_session_id(request: gr.Request):
    """獲取當前客戶端的 Session ID"""
    client_id = f"{request.client.host}_{request.headers.get('user-agent', '')}"
    session_id = hashlib.sha256(client_id.encode()).hexdigest()[:16]
    return session_id

def validate_session(session_id):
    """驗證 Session（快速檢查）"""
    sessions = database.load_sessions()
    
    if session_id not in sessions:
        return None
    
    session = sessions[session_id]
    try:
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        if datetime.now() > expires_at:
            del sessions[session_id]
            database.save_sessions(sessions)
            return None
        
        return session['username']
    except:
        return None

def delete_session(session_id):
    """刪除 Session"""
    sessions = database.load_sessions()
    if session_id in sessions:
        del sessions[session_id]
        database.save_sessions(sessions)

def register_user(username, password, confirm_password):
    """註冊新使用者"""
    if not username or not password:
        return "❌ 請填寫使用者名稱和密碼", gr.update(visible=True), gr.update(visible=False)
    
    if len(username) < 3:
        return "❌ 使用者名稱至少需要 3 個字元", gr.update(visible=True), gr.update(visible=False)
    
    if len(password) < 6:
        return "❌ 密碼至少需要 6 個字元", gr.update(visible=True), gr.update(visible=False)
    
    if password != confirm_password:
        return "❌ 兩次密碼輸入不一致", gr.update(visible=True), gr.update(visible=False)
    
    users = database.load_users()
    
    if username in users:
        return "❌ 使用者名稱已存在", gr.update(visible=True), gr.update(visible=False)
    
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    if database.save_users(users):
        user_file = database.get_user_data_file(username)
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        database.upload_to_hf_async(user_file)
        
        return "✅ 註冊成功！請登入", gr.update(visible=True), gr.update(visible=False)
    else:
        return "❌ 註冊失敗，請稍後再試", gr.update(visible=True), gr.update(visible=False)

def login_user(username, password, remember_me, request: gr.Request):
    """使用者登入"""
    if not username or not password:
        return "❌ 請填寫使用者名稱和密碼", gr.update(visible=True), gr.update(visible=False), None
    
    users = database.load_users()
    
    if username not in users:
        return "❌ 使用者不存在", gr.update(visible=True), gr.update(visible=False), None
    
    if users[username]['password'] != hash_password(password):
        return "❌ 密碼錯誤", gr.update(visible=True), gr.update(visible=False), None
    
    if remember_me:
        create_session(username, request)
    
    return f"✅ 歡迎回來，{username}！", gr.update(visible=False), gr.update(visible=True), username

def auto_login(request: gr.Request):
    """自動登入檢查（快速）"""
    session_id = get_session_id(request)
    username = validate_session(session_id)
    
    if username:
        print(f"✅ 自動登入: {username}")
        return username, gr.update(visible=False), gr.update(visible=True)
    
    return None, gr.update(visible=True), gr.update(visible=False)

def logout_user(request: gr.Request):
    """使用者登出"""
    try:
        session_id = get_session_id(request)
        delete_session(session_id)
    except:
        pass
    return gr.update(visible=True), gr.update(visible=False), None, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])

def is_expiring_soon(expiry_date_str):
    """檢查是否即將到期（7天內，包含到期日當天）"""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_until_expiry = (expiry_date - today).days
        return 0 <= days_until_expiry <= 7  # ✅ 0 表示今天到期（還可以用）
    except:
        return False
    
def is_expiring_today(expiry_date_str):
    """檢查是否今天到期"""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return expiry_date == today
    except:
        return False

def is_expired(expiry_date_str):
    """檢查是否已過期"""
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        today = datetime.now().date()  # 只取日期
        return today > expiry.date()
    except:
        return False

def format_date(date_str):
    """格式化日期"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y/%m/%d')
    except:
        return date_str

def calculate_expiry_date_display(days):
    """根據天數計算到期日並顯示"""
    if not days or days < 1:
        return "請輸入有效天數（至少 1 天）"
    
    try:
        days = int(days)
        expiry_date = datetime.now() + timedelta(days=days)
        formatted_date = expiry_date.strftime('%Y年%m月%d日 (%A)')
        weekday_map = {
            'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三',
            'Thursday': '星期四', 'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期日'
        }
        for en, zh in weekday_map.items():
            formatted_date = formatted_date.replace(en, zh)
        
        return f"📅 **計算結果：{formatted_date}**"
    except:
        return "❌ 計算錯誤"

def toggle_expiry_input(method):
    """切換到期日輸入方式"""
    if method == "選擇日期":
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)

def get_deposits_display(username):
    """取得寄杯記錄顯示"""
    if not username:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">🔒</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">請先登入</p>
            <p style="font-size: 16px; color: #9ca3af;">登入後即可查看您的寄杯記錄</p>
        </div>
        """
    
    deposits = database.load_deposits(username)
    
    if not deposits:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
            <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯記錄」開始記錄吧！</p>
        </div>
        """
    
    deposits.sort(key=lambda x: x.get('expiryDate', '9999-12-31'))
    
    html = '<div style="display: flex; flex-direction: column; gap: 20px;">'
    
    for deposit in deposits:
        expired = is_expired(deposit['expiryDate'])
        expiring_today = is_expiring_today(deposit['expiryDate'])
        expiring_soon = is_expiring_soon(deposit['expiryDate']) and not expired and not expiring_today
        
        # 根據狀態設置樣式
        if expired:
            card_style = "background: #fef2f2; border: 2px solid #fca5a5;"
            status_text = "（已過期）"
            status_color = "#dc2626"
            status_emoji = "❌"
        elif expiring_today:
            card_style = "background: #fff4ed; border: 2px solid #fb923c;"
            status_text = "（今天到期）"
            status_color = "#ea580c"
            status_emoji = "⚠️"
        elif expiring_soon:
            card_style = "background: #fefce8; border: 2px solid #fde047;"
            status_text = "（即將到期）"
            status_color = "#ca8a04"
            status_emoji = "⏰"
        else:
            card_style = "background: white; border: 1px solid #e5e7eb;"
            status_text = ""
            status_color = "#6b7280"
            status_emoji = ""
        
        redeem_info = config.REDEEM_LINKS.get(deposit['redeemMethod'], {
            'app': '#',
            'name': deposit['redeemMethod']
        })
        app_link = redeem_info['app']
        app_name = redeem_info['name']
        google_maps_link = f"https://www.google.com/maps/search/{deposit['store']}"
        
        html += f"""
        <div style="padding: 24px; border-radius: 16px; {card_style} box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap;">
                    <h3 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">{deposit['item']}</h3>
                    <span style="background: #fef3c7; color: #92400e; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 600;">
                        {deposit['quantity']} 杯
                    </span>
                </div>
                <div style="color: #4b5563; line-height: 2; font-size: 15px;">
                    <div style="margin-bottom: 6px;">📍 <strong>商店：</strong>{deposit['store']}</div>
                    <div style="margin-bottom: 6px;">📦 <strong>兌換途徑：</strong>{deposit['redeemMethod']}</div>
                    <div>📅 <strong>到期日：</strong>{format_date(deposit['expiryDate'])} 
                        <span style="color: {status_color}; font-weight: 600;">{status_emoji} {status_text}</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
                <a href="{app_link}" target="_blank" 
                   style="background: #9333ea; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s; box-shadow: 0 2px 4px rgba(147, 51, 234, 0.3);">
                    📱 開啟 {app_name} App
                </a>
                <a href="{google_maps_link}" target="_blank" 
                   style="background: #2563eb; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🗺️ 查看商店位置
                </a>
            </div>
            <div style="padding: 12px; background: #f9fafb; border-radius: 8px; font-size: 12px; color: #6b7280;">
                💡 <strong>提示：</strong>點擊「開啟 App」會嘗試開啟對應的手機應用程式
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def get_statistics(username):
    """取得統計資訊"""
    if not username:
        return ""
    
    deposits = database.load_deposits(username)
    
    if not deposits:
        return ""
    
    total_cups = sum(d['quantity'] for d in deposits)
    valid_records = len([d for d in deposits if not is_expired(d['expiryDate'])])
    expired_records = len([d for d in deposits if is_expired(d['expiryDate'])])
    expiring_today = len([d for d in deposits if is_expiring_today(d['expiryDate'])])
    expiring_soon = len([d for d in deposits if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate']) and not is_expiring_today(d['expiryDate'])])
    
    html = f"""
    <div style="background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 24px;">
        <h3 style="font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 20px;">📊 統計資訊</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 16px; text-align: center;">
            <div style="padding: 16px; background: #fffbeb; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #d97706; margin: 0;">{total_cups}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">總杯數</p>
            </div>
            <div style="padding: 16px; background: #f0fdf4; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #16a34a; margin: 0;">{valid_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">有效記錄</p>
            </div>
            <div style="padding: 16px; background: #fff4ed; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #ea580c; margin: 0;">{expiring_today}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">今天到期</p>
            </div>
            <div style="padding: 16px; background: #fefce8; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #ca8a04; margin: 0;">{expiring_soon}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">即將到期</p>
            </div>
            <div style="padding: 16px; background: #fef2f2; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #dc2626; margin: 0;">{expired_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">已過期</p>
            </div>
        </div>
    </div>
    """
    return html

def get_deposit_choices(username):
    """取得寄杯記錄選項"""
    if not username:
        return gr.update(choices=[], value=None)
    
    deposits = database.load_deposits(username)
    if not deposits:
        return gr.update(choices=[], value=None)
    
    global deposit_label_to_id
    deposit_label_to_id = {}
    choices_list = []
    
    for d in deposits:
        # 判斷狀態標籤
        if is_expired(d['expiryDate']):
            status_tag = " [已過期]"
        elif is_expiring_today(d['expiryDate']):
            status_tag = " [今天到期]"
        elif is_expiring_soon(d['expiryDate']):
            status_tag = " [即將到期]"
        else:
            status_tag = ""
        
        label = f"{d['item']} - {d['store']} ({d['quantity']}杯) - 到期:{format_date(d['expiryDate'])}{status_tag}"
        
        deposit_label_to_id[label] = d['id']
        choices_list.append(label)
    
    return gr.update(choices=choices_list, value=None)

def add_deposit(username, item, quantity, store, redeem_method, expiry_method, expiry_date, days_until):
    """新增寄杯記錄"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not all([item, store, redeem_method]):
        return "❌ 請填寫所有欄位", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    # 處理到期日
    if expiry_method == "選擇日期":
        final_expiry_date = expiry_date
        if not final_expiry_date or final_expiry_date.strip() == "":
            return "❌ 請選擇到期日", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        if not days_until or days_until < 1:
            return "❌ 請輸入有效的天數（至少 1 天）", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
        try:
            final_expiry_date = (datetime.now() + timedelta(days=int(days_until))).strftime('%Y-%m-%d')
        except:
            return "❌ 天數格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return "❌ 數量必須大於 0", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    except:
        return "❌ 數量格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    # 驗證並清理日期格式
    try:
        if isinstance(final_expiry_date, str):
            # 移除可能的空白和特殊字符
            final_expiry_date = final_expiry_date.strip()
            
            # 處理各種可能的日期格式
            if 'T' in final_expiry_date:
                final_expiry_date = final_expiry_date.split('T')[0]
            if ' ' in final_expiry_date:
                final_expiry_date = final_expiry_date.split(' ')[0]
            
            # 驗證日期格式
            datetime.strptime(final_expiry_date, '%Y-%m-%d')
        elif hasattr(final_expiry_date, 'strftime'):
            final_expiry_date = final_expiry_date.strftime('%Y-%m-%d')
        else:
            return "❌ 日期格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    except Exception as e:
        print(f"日期處理錯誤: {e}, 收到的日期: {final_expiry_date}")
        return f"❌ 日期格式錯誤（請確認已選擇日期）", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = database.load_deposits(username)
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item.strip(),
        'quantity': quantity,
        'store': store,
        'redeemMethod': redeem_method,
        'expiryDate': final_expiry_date,
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    
    if database.save_deposits(username, deposits):
        return "✅ 新增成功！", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        return "❌ 儲存失敗", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def redeem_one(username, deposit_label):
    """兌換一杯"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not deposit_label:
        return "❌ 請選擇要兌換的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposit_id = deposit_label_to_id.get(deposit_label)
    if not deposit_id:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = database.load_deposits(username)
    updated = False
    deposit_name = ""
    
    for i, deposit in enumerate(deposits):
        if deposit['id'] == deposit_id:
            deposit_name = deposit['item']
            if deposit['quantity'] > 1:
                deposits[i]['quantity'] -= 1
                message = f"✅ 已兌換一杯 {deposit_name}，剩餘 {deposits[i]['quantity']} 杯"
            else:
                deposits = [d for d in deposits if d['id'] != deposit_id]
                message = f"✅ 已兌換最後一杯 {deposit_name}，記錄已刪除"
            updated = True
            break
    
    if updated:
        database.save_deposits(username, deposits)
        return message, get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def delete_deposit(username, deposit_label):
    """刪除寄杯記錄"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not deposit_label:
        return "❌ 請選擇要刪除的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposit_id = deposit_label_to_id.get(deposit_label)
    if not deposit_id:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = database.load_deposits(username)
    deposit_name = ""
    
    for d in deposits:
        if d['id'] == deposit_id:
            deposit_name = d['item']
            break
    
    deposits = [d for d in deposits if d['id'] != deposit_id]
    database.save_deposits(username, deposits)
    
    return f"✅ 已刪除 {deposit_name} 的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def refresh_display(username):
    """重新整理顯示"""
    return get_deposits_display(username), get_statistics(username), get_deposit_choices(username)