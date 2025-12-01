import gradio as gr
import json
from datetime import datetime, timedelta
import os
import hashlib

# 資料檔案路徑
USERS_FILE = 'users.json'
DATA_DIR = 'user_data'

# 商店和兌換途徑選項
STORE_OPTIONS = ['7-11', '全家', '星巴克']
REDEEM_METHODS = ['遠傳', 'Line禮物', '7-11', '全家', '星巴克']

# 兌換連結對應
REDEEM_LINKS = {
    '遠傳': {
        'app': 'fetnet://',
        'web': 'https://www.fetnet.net/content/cbu/tw/index.html',
        'name': '遠傳心生活'
    },
    'Line禮物': {
        'app': 'https://line.me/R/shop/gift/category/coffee',
        'web': 'https://gift.line.me/category/coffee',
        'name': 'Line 禮物'
    },
    '7-11': {
        'app': 'openpoint://',
        'web': 'https://www.7-11.com.tw/',
        'name': 'OPENPOINT'
    },
    '全家': {
        'app': 'fami://',
        'web': 'https://www.family.com.tw/',
        'name': '全家便利商店'
    },
    '星巴克': {
        'app': 'starbucks://',
        'web': 'https://www.starbucks.com.tw/',
        'name': '星巴克'
    }
}

# 確保資料目錄存在
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def hash_password(password):
    """密碼加密"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """載入使用者資料"""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    """儲存使用者資料"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

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
    
    users = load_users()
    
    if username in users:
        return "❌ 使用者名稱已存在", gr.update(visible=True), gr.update(visible=False)
    
    users[username] = {
        'password': hash_password(password),
        'created_at': datetime.now().isoformat()
    }
    
    if save_users(users):
        # 建立使用者資料檔案
        user_file = os.path.join(DATA_DIR, f'{username}.json')
        with open(user_file, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return "✅ 註冊成功！請登入", gr.update(visible=True), gr.update(visible=False)
    else:
        return "❌ 註冊失敗，請稍後再試", gr.update(visible=True), gr.update(visible=False)

def login_user(username, password):
    """使用者登入"""
    if not username or not password:
        return "❌ 請填寫使用者名稱和密碼", gr.update(visible=True), gr.update(visible=False), None
    
    users = load_users()
    
    if username not in users:
        return "❌ 使用者不存在", gr.update(visible=True), gr.update(visible=False), None
    
    if users[username]['password'] != hash_password(password):
        return "❌ 密碼錯誤", gr.update(visible=True), gr.update(visible=False), None
    
    return f"✅ 歡迎回來，{username}！", gr.update(visible=False), gr.update(visible=True), username

def logout_user():
    """使用者登出"""
    return gr.update(visible=True), gr.update(visible=False), None, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])

def get_user_data_file(username):
    """取得使用者資料檔案路徑"""
    if not username:
        return None
    return os.path.join(DATA_DIR, f'{username}.json')

def load_deposits(username):
    """載入寄杯資料"""
    data_file = get_user_data_file(username)
    if not data_file or not os.path.exists(data_file):
        return []
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入資料錯誤: {e}")
        return []

def save_deposits(username, deposits):
    """儲存寄杯資料"""
    data_file = get_user_data_file(username)
    if not data_file:
        return False
    try:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(deposits, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"儲存資料錯誤: {e}")
        return False

def is_expiring_soon(expiry_date_str):
    """檢查是否即將到期（7天內）"""
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        today = datetime.now()
        days_until_expiry = (expiry - today).days
        return 0 <= days_until_expiry <= 7
    except:
        return False

def is_expired(expiry_date_str):
    """檢查是否已過期"""
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        return expiry < datetime.now()
    except:
        return False

def format_date(date_str):
    """格式化日期"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y/%m/%d')
    except:
        return date_str

def add_deposit(username, item, quantity, store, redeem_method, expiry_date):
    """新增寄杯記錄"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not all([item, store, redeem_method, expiry_date]):
        return "❌ 請填寫所有欄位", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return "❌ 數量必須大於 0", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    except:
        return "❌ 數量格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    # 處理日期格式 - 支援多種格式
    try:
        if isinstance(expiry_date, str):
            # 移除時間部分
            if 'T' in expiry_date:
                expiry_date = expiry_date.split('T')[0]
            if ' ' in expiry_date:
                expiry_date = expiry_date.split(' ')[0]
            # 驗證日期格式
            datetime.strptime(expiry_date, '%Y-%m-%d')
        elif hasattr(expiry_date, 'strftime'):
            # 如果是 datetime 物件
            expiry_date = expiry_date.strftime('%Y-%m-%d')
        else:
            return "❌ 日期格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    except Exception as e:
        print(f"日期處理錯誤: {e}, 輸入值: {expiry_date}, 類型: {type(expiry_date)}")
        return "❌ 日期格式錯誤", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = load_deposits(username)
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item.strip(),
        'quantity': quantity,
        'store': store,
        'redeemMethod': redeem_method,
        'expiryDate': expiry_date,
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    
    if save_deposits(username, deposits):
        return "✅ 新增成功！", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        return "❌ 儲存失敗", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def get_deposit_choices(username):
    """取得寄杯記錄選項"""
    if not username:
        return gr.update(choices=[], value=None)
    
    deposits = load_deposits(username)
    if not deposits:
        return gr.update(choices=[], value=None)
    
    choices = []
    for d in deposits:
        expired_tag = " [已過期]" if is_expired(d['expiryDate']) else ""
        expiring_tag = " [即將到期]" if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate']) else ""
        label = f"{d['item']} - {d['store']} ({d['quantity']}杯) - 到期:{format_date(d['expiryDate'])}{expired_tag}{expiring_tag}"
        choices.append((label, d['id']))
    
    return gr.update(choices=choices, value=None)

def redeem_one(username, deposit_id):
    """兌換一杯"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not deposit_id:
        return "❌ 請選擇要兌換的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = load_deposits(username)
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
        save_deposits(username, deposits)
        return message, get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    else:
        return "❌ 找不到該記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

def delete_deposit(username, deposit_id):
    """刪除寄杯記錄"""
    if not username:
        return "❌ 請先登入", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    if not deposit_id:
        return "❌ 請選擇要刪除的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)
    
    deposits = load_deposits(username)
    deposit_name = ""
    
    for d in deposits:
        if d['id'] == deposit_id:
            deposit_name = d['item']
            break
    
    deposits = [d for d in deposits if d['id'] != deposit_id]
    save_deposits(username, deposits)
    
    return f"✅ 已刪除 {deposit_name} 的記錄", get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

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
    
    deposits = load_deposits(username)
    
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
        expiring = is_expiring_soon(deposit['expiryDate']) and not expired
        
        if expired:
            card_style = "background: #fef2f2; border: 2px solid #fca5a5;"
            status_text = "（已過期）"
            status_color = "#dc2626"
        elif expiring:
            card_style = "background: #fefce8; border: 2px solid #fde047;"
            status_text = "（即將到期）"
            status_color = "#ca8a04"
        else:
            card_style = "background: white; border: 1px solid #e5e7eb;"
            status_text = ""
            status_color = "#6b7280"
        
        redeem_info = REDEEM_LINKS.get(deposit['redeemMethod'], {
            'app': '#',
            'web': '#',
            'name': deposit['redeemMethod']
        })
        app_link = redeem_info['app']
        web_link = redeem_info['web']
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
                        <span style="color: {status_color}; font-weight: 600;">{status_text}</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
                <a href="{app_link}" target="_blank" 
                   style="background: #9333ea; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s; box-shadow: 0 2px 4px rgba(147, 51, 234, 0.3);">
                    📱 開啟 {app_name} App
                </a>
                <a href="{web_link}" target="_blank" 
                   style="background: #7c3aed; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🌐 網頁版
                </a>
                <a href="{google_maps_link}" target="_blank" 
                   style="background: #2563eb; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🗺️ 查看商店位置
                </a>
            </div>
            <div style="padding: 12px; background: #f9fafb; border-radius: 8px; font-size: 12px; color: #6b7280;">
                💡 <strong>提示：</strong>點擊「開啟 App」會嘗試開啟手機 App，如果沒有安裝，請點擊「網頁版」
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af;">
                記錄 ID: {deposit['id'][:8]}... | 建立時間: {deposit.get('createdAt', 'N/A')[:10]}
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def get_statistics(username):
    """取得統計資訊"""
    if not username:
        return ""
    
    deposits = load_deposits(username)
    
    if not deposits:
        return ""
    
    total_cups = sum(d['quantity'] for d in deposits)
    valid_records = len([d for d in deposits if not is_expired(d['expiryDate'])])
    expired_records = len([d for d in deposits if is_expired(d['expiryDate'])])
    expiring_soon = len([d for d in deposits if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate'])])
    
    html = f"""
    <div style="background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 24px;">
        <h3 style="font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 20px;">📊 統計資訊</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 20px; text-align: center;">
            <div style="padding: 16px; background: #fffbeb; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #d97706; margin: 0;">{total_cups}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">總杯數</p>
            </div>
            <div style="padding: 16px; background: #f0fdf4; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #16a34a; margin: 0;">{valid_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">有效記錄</p>
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

def refresh_display(username):
    """重新整理顯示"""
    return get_deposits_display(username), get_statistics(username), get_deposit_choices(username)

# 建立 Gradio 介面
with gr.Blocks(
    title="☕ 咖啡寄杯記錄",
    theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
) as app:
    
    # 儲存當前使用者
    current_user = gr.State(None)
    
    gr.HTML("""
        <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px;">
            <h1 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">
                咖啡寄杯記錄系統
            </h1>
            <p style="color: #6b7280; margin-top: 8px; font-size: 14px;">管理你的咖啡寄杯，不怕忘記兌換 ☕✨</p>
        </div>
    """)
    
    # 登入/註冊區域
    with gr.Column(visible=True) as login_area:
        with gr.Tabs():
            with gr.Tab("🔐 登入"):
                login_status = gr.Markdown()
                login_username = gr.Textbox(label="使用者名稱", placeholder="請輸入使用者名稱")
                login_password = gr.Textbox(label="密碼", type="password", placeholder="請輸入密碼")
                login_btn = gr.Button("登入", variant="primary", size="lg")
            
            with gr.Tab("📝 註冊"):
                register_status = gr.Markdown()
                register_username = gr.Textbox(label="使用者名稱", placeholder="至少 3 個字元")
                register_password = gr.Textbox(label="密碼", type="password", placeholder="至少 6 個字元")
                register_confirm = gr.Textbox(label="確認密碼", type="password", placeholder="再次輸入密碼")
                register_btn = gr.Button("註冊", variant="primary", size="lg")
    
    # 主要功能區域（登入後顯示）
    with gr.Column(visible=False) as main_area:
        with gr.Row():
            user_info = gr.Markdown()
            logout_btn = gr.Button("🚪 登出", size="sm")
        
        gr.Markdown("---")
        
        with gr.Accordion("➕ 新增寄杯記錄", open=True):
            with gr.Row():
                item_input = gr.Textbox(
                    label="☕ 咖啡品項", 
                    placeholder="例如：美式咖啡、拿鐵",
                    scale=2
                )
                quantity_input = gr.Number(
                    label="🔢 數量（杯）", 
                    value=1, 
                    minimum=1, 
                    precision=0,
                    scale=1
                )
            
            with gr.Row():
                store_input = gr.Dropdown(
                    label="🏪 商店名稱", 
                    choices=STORE_OPTIONS,
                    interactive=True,
                    allow_custom_value=False,
                    scale=1
                )
                redeem_method_input = gr.Dropdown(
                    label="📦 兌換途徑", 
                    choices=REDEEM_METHODS,
                    interactive=True,
                    allow_custom_value=False,
                    scale=1
                )
            
            # 使用 DateTime 組件（月曆模式）
            try:
                expiry_date_input = gr.DateTime(
                    label="📅 到期日",
                    include_time=False,
                    type="string"
                )
            except Exception as e:
                print(f"DateTime 組件初始化失敗: {e}")
                # 如果 DateTime 不支援，回退到 Textbox
                expiry_date_input = gr.Textbox(
                    label="📅 到期日",
                    placeholder="格式：YYYY-MM-DD (例如：2025-12-31)",
                    info="請輸入日期，格式為 YYYY-MM-DD"
                )
            
            add_status = gr.Markdown()
            add_btn = gr.Button("💾 儲存記錄", variant="primary", size="lg")
        
        gr.Markdown("---")
        
        with gr.Accordion("☕ 兌換 / 刪除寄杯記錄", open=True):
            gr.Markdown("💡 **提示：** 在下方選擇記錄後，點擊「兌換一杯」或「刪除記錄」按鈕")
            action_status = gr.Markdown()
            deposit_selector = gr.Dropdown(
                label="📋 選擇寄杯記錄",
                choices=[],
                interactive=True
            )
            
            with gr.Row():
                redeem_btn = gr.Button("☕ 兌換一杯", variant="primary", size="lg", scale=2)
                delete_btn = gr.Button("🗑️ 刪除記錄", variant="stop", size="lg", scale=1)
                refresh_btn = gr.Button("🔄 重新整理", size="lg", scale=1)
        
        gr.Markdown("---")
        gr.Markdown("### 📋 所有寄杯記錄")
        
        deposits_display = gr.HTML(value=get_deposits_display(None))
        statistics_display = gr.HTML(value=get_statistics(None))
    
    # 事件處理 - 註冊
    register_btn.click(
        fn=register_user,
        inputs=[register_username, register_password, register_confirm],
        outputs=[register_status, login_area, main_area]
    )
    
    # 事件處理 - 登入
    login_btn.click(
        fn=login_user,
        inputs=[login_username, login_password],
        outputs=[login_status, login_area, main_area, current_user]
    ).then(
        fn=lambda u: (f"👤 使用者：**{u}**" if u else "", get_deposits_display(u), get_statistics(u), get_deposit_choices(u)),
        inputs=[current_user],
        outputs=[user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 登出
    logout_btn.click(
        fn=logout_user,
        outputs=[login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 新增記錄
    add_btn.click(
        fn=add_deposit,
        inputs=[current_user, item_input, quantity_input, store_input, redeem_method_input, expiry_date_input],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 兌換
    redeem_btn.click(
        fn=redeem_one,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 刪除
    delete_btn.click(
        fn=delete_deposit,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 重新整理
    refresh_btn.click(
        fn=refresh_display,
        inputs=[current_user],
        outputs=[deposits_display, statistics_display, deposit_selector]
    )

if __name__ == "__main__":
    app.launch()
