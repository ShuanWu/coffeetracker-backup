import gradio as gr
import json
from datetime import datetime, timedelta
import os

# 資料檔案路徑
DATA_FILE = 'deposits.json'

# 商店和兌換途徑選項
STORE_OPTIONS = ['7-11', '全家', '星巴克']
REDEEM_METHODS = ['遠傳', 'Line禮物', '7-11', '全家', '星巴克']

# 兌換連結對應
REDEEM_LINKS = {
    '遠傳': 'https://www.fetnet.net/content/cbu/tw/index.html',
    'Line禮物': 'https://gift.line.me/category/coffee',
    '7-11': 'https://www.7-11.com.tw/',
    '全家': 'https://www.family.com.tw/',
    '星巴克': 'https://www.starbucks.com.tw/'
}

def load_deposits():
    """載入寄杯資料"""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"載入資料錯誤: {e}")
        return []

def save_deposits(deposits):
    """儲存寄杯資料"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
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

def add_deposit(item, quantity, store, redeem_method, expiry_date):
    """新增寄杯記錄"""
    if not all([item, store, redeem_method, expiry_date]):
        return "❌ 請填寫所有欄位", get_deposits_display(), get_statistics(), get_deposit_choices()
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return "❌ 數量必須大於 0", get_deposits_display(), get_statistics(), get_deposit_choices()
    except:
        return "❌ 數量格式錯誤", get_deposits_display(), get_statistics(), get_deposit_choices()
    
    # 處理日期格式
    try:
        if isinstance(expiry_date, str):
            if 'T' in expiry_date:
                expiry_date = expiry_date.split('T')[0]
            datetime.strptime(expiry_date, '%Y-%m-%d')
        else:
            return "❌ 日期格式錯誤", get_deposits_display(), get_statistics(), get_deposit_choices()
    except:
        return "❌ 日期格式錯誤", get_deposits_display(), get_statistics(), get_deposit_choices()
    
    deposits = load_deposits()
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
    
    if save_deposits(deposits):
        return "✅ 新增成功！", get_deposits_display(), get_statistics(), get_deposit_choices()
    else:
        return "❌ 儲存失敗", get_deposits_display(), get_statistics(), get_deposit_choices()

def get_deposit_choices():
    """取得寄杯記錄選項（用於下拉選單）"""
    deposits = load_deposits()
    if not deposits:
        return gr.update(choices=[], value=None)
    
    choices = []
    for d in deposits:
        expired_tag = " [已過期]" if is_expired(d['expiryDate']) else ""
        expiring_tag = " [即將到期]" if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate']) else ""
        label = f"{d['item']} - {d['store']} ({d['quantity']}杯) - 到期:{format_date(d['expiryDate'])}{expired_tag}{expiring_tag}"
        choices.append((label, d['id']))
    
    return gr.update(choices=choices, value=None)

def redeem_one(deposit_id):
    """兌換一杯"""
    if not deposit_id:
        return "❌ 請選擇要兌換的記錄", get_deposits_display(), get_statistics(), get_deposit_choices()
    
    deposits = load_deposits()
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
        save_deposits(deposits)
        return message, get_deposits_display(), get_statistics(), get_deposit_choices()
    else:
        return "❌ 找不到該記錄", get_deposits_display(), get_statistics(), get_deposit_choices()

def delete_deposit(deposit_id):
    """刪除寄杯記錄"""
    if not deposit_id:
        return "❌ 請選擇要刪除的記錄", get_deposits_display(), get_statistics(), get_deposit_choices()
    
    deposits = load_deposits()
    deposit_name = ""
    
    for d in deposits:
        if d['id'] == deposit_id:
            deposit_name = d['item']
            break
    
    deposits = [d for d in deposits if d['id'] != deposit_id]
    save_deposits(deposits)
    
    return f"✅ 已刪除 {deposit_name} 的記錄", get_deposits_display(), get_statistics(), get_deposit_choices()

def get_deposits_display():
    """取得寄杯記錄顯示"""
    deposits = load_deposits()
    
    if not deposits:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
            <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯記錄」開始記錄吧！</p>
        </div>
        """
    
    # 按到期日排序
    deposits.sort(key=lambda x: x.get('expiryDate', '9999-12-31'))
    
    html = '<div style="display: flex; flex-direction: column; gap: 20px;">'
    
    for deposit in deposits:
        expired = is_expired(deposit['expiryDate'])
        expiring = is_expiring_soon(deposit['expiryDate']) and not expired
        
        # 決定卡片樣式
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
        
        redeem_link = REDEEM_LINKS.get(deposit['redeemMethod'], '#')
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
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <a href="{redeem_link}" target="_blank" 
                   style="background: #9333ea; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🔗 前往兌換頁面
                </a>
                <a href="{google_maps_link}" target="_blank" 
                   style="background: #2563eb; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🗺️ 查看商店位置
                </a>
            </div>
            <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af;">
                記錄 ID: {deposit['id'][:8]}... | 建立時間: {deposit.get('createdAt', 'N/A')[:10]}
            </div>
        </div>
        """
    
    html += '</div>'
    return html

def get_statistics():
    """取得統計資訊"""
    deposits = load_deposits()
    
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

def refresh_display():
    """重新整理顯示"""
    return get_deposits_display(), get_statistics(), get_deposit_choices()

# 建立 Gradio 介面
with gr.Blocks(
    title="☕ 咖啡寄杯記錄",
    theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
) as app:
    
    gr.HTML("""
        <div style="background: white; padding: 28px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 20px; flex-wrap: wrap;">
                <div style="background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); padding: 18px; border-radius: 14px; box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3);">
                    <span style="font-size: 40px;">☕</span>
                </div>
                <div style="flex: 1;">
                    <h1 style="font-size: 36px; font-weight: bold; color: #1f2937; margin: 0; background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                        咖啡寄杯記錄系統
                    </h1>
                    <p style="color: #6b7280; margin-top: 8px; font-size: 16px;">管理你的咖啡寄杯，不怕忘記兌換 ☕✨</p>
                </div>
            </div>
        </div>
    """)
    
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
                scale=1
            )
            redeem_method_input = gr.Dropdown(
                label="📦 兌換途徑", 
                choices=REDEEM_METHODS,
                scale=1
            )
        
        expiry_date_input = gr.DateTime(
            label="📅 到期日",
            include_time=False,
            type="string"
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
    
    deposits_display = gr.HTML(value=get_deposits_display())
    statistics_display = gr.HTML(value=get_statistics())
    
    # 事件處理
    add_btn.click(
        fn=add_deposit,
        inputs=[item_input, quantity_input, store_input, redeem_method_input, expiry_date_input],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    
    redeem_btn.click(
        fn=redeem_one,
        inputs=[deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    delete_btn.click(
        fn=delete_deposit,
        inputs=[deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    refresh_btn.click(
        fn=refresh_display,
        outputs=[deposits_display, statistics_display, deposit_selector]
    )
    
    # 初始載入
    app.load(
        fn=refresh_display,
        outputs=[deposits_display, statistics_display, deposit_selector]
    )

if __name__ == "__main__":
    app.launch()
