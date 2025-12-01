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
        return "❌ 請填寫所有欄位", create_deposits_ui(), get_statistics()
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return "❌ 數量必須大於 0", create_deposits_ui(), get_statistics()
    except:
        return "❌ 數量格式錯誤", create_deposits_ui(), get_statistics()
    
    # 處理日期格式
    try:
        if isinstance(expiry_date, str):
            if 'T' in expiry_date:
                expiry_date = expiry_date.split('T')[0]
            datetime.strptime(expiry_date, '%Y-%m-%d')
        else:
            return "❌ 日期格式錯誤", create_deposits_ui(), get_statistics()
    except:
        return "❌ 日期格式錯誤", create_deposits_ui(), get_statistics()
    
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
        return "✅ 新增成功！", create_deposits_ui(), get_statistics()
    else:
        return "❌ 儲存失敗", create_deposits_ui(), get_statistics()

def redeem_one(deposit_id):
    """兌換一杯"""
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
        return message, create_deposits_ui(), get_statistics()
    else:
        return "❌ 找不到該記錄", create_deposits_ui(), get_statistics()

def delete_deposit(deposit_id):
    """刪除寄杯記錄"""
    deposits = load_deposits()
    deposit_name = ""
    
    for d in deposits:
        if d['id'] == deposit_id:
            deposit_name = d['item']
            break
    
    deposits = [d for d in deposits if d['id'] != deposit_id]
    save_deposits(deposits)
    
    return f"✅ 已刪除 {deposit_name} 的記錄", create_deposits_ui(), get_statistics()

def create_deposits_ui():
    """建立寄杯記錄的互動式 UI"""
    deposits = load_deposits()
    
    if not deposits:
        empty_html = gr.HTML("""
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
            <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯記錄」開始記錄吧！</p>
        </div>
        """)
        return [empty_html]
    
    # 按到期日排序
    deposits.sort(key=lambda x: x.get('expiryDate', '9999-12-31'))
    
    components = []
    
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
        
        # 建立卡片 HTML
        card_html = f"""
        <div style="padding: 24px; border-radius: 16px; {card_style} box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;">
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
        </div>
        """
        
        with gr.Row():
            with gr.Column(scale=4):
                components.append(gr.HTML(card_html))
            with gr.Column(scale=1):
                # 建立按鈕組
                with gr.Column():
                    redeem_btn = gr.Button(
                        "☕ 兌換一杯",
                        variant="primary",
                        size="sm",
                        elem_id=f"redeem_{deposit['id']}"
                    )
                    
                    link_btn = gr.Button(
                        "🔗 前往兌換頁面",
                        variant="secondary",
                        size="sm",
                        link=redeem_link
                    )
                    
                    map_btn = gr.Button(
                        "🗺️ 查看商店位置",
                        variant="secondary",
                        size="sm",
                        link=google_maps_link
                    )
                    
                    delete_btn = gr.Button(
                        "🗑️ 刪除記錄",
                        variant="stop",
                        size="sm",
                        elem_id=f"delete_{deposit['id']}"
                    )
                    
                    components.extend([redeem_btn, link_btn, map_btn, delete_btn])
    
    return components

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

def refresh_all():
    """重新整理所有顯示"""
    return create_deposits_ui(), get_statistics()

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
        
        with gr.Row():
            add_btn = gr.Button("💾 儲存記錄", variant="primary", size="lg", scale=2)
            refresh_btn = gr.Button("🔄 重新整理", size="lg", scale=1)
    
    gr.Markdown("---")
    gr.Markdown("### 📋 寄杯記錄列表")
    
    action_status = gr.Markdown()
    
    # 寄杯記錄顯示區域
    deposits_container = gr.Column()
    
    statistics_display = gr.HTML(value=get_statistics())
    
    # 初始化顯示
    with deposits_container:
        deposits = load_deposits()
        if not deposits:
            gr.HTML("""
            <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
                <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
                <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯記錄」開始記錄吧！</p>
            </div>
            """)
        else:
            deposits.sort(key=lambda x: x.get('expiryDate', '9999-12-31'))
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
                
                redeem_link = REDEEM_LINKS.get(deposit['redeemMethod'], '#')
                google_maps_link = f"https://www.google.com/maps/search/{deposit['store']}"
                
                with gr.Row():
                    with gr.Column(scale=3):
                        gr.HTML(f"""
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
                        </div>
                        """)
                    
                    with gr.Column(scale=1, min_width=160):
                        redeem_btn = gr.Button("☕ 兌換一杯", variant="primary", size="sm")
                        gr.HTML(f'<a href="{redeem_link}" target="_blank" style="display: block; margin: 8px 0;"><button style="width: 100%; padding: 8px; background: #9333ea; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">🔗 前往兌換頁面</button></a>')
                        gr.HTML(f'<a href="{google_maps_link}" target="_blank" style="display: block; margin: 8px 0;"><button style="width: 100%; padding: 8px; background: #2563eb; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px;">🗺️ 查看商店位置</button></a>')
                        delete_btn = gr.Button("🗑️ 刪除記錄", variant="stop", size="sm")
                        
                        # 綁定事件
                        redeem_btn.click(
                            fn=lambda did=deposit['id']: redeem_one(did),
                            outputs=[action_status, deposits_container, statistics_display]
                        )
                        
                        delete_btn.click(
                            fn=lambda did=deposit['id']: delete_deposit(did),
                            outputs=[action_status, deposits_container, statistics_display]
                        )
    
    # 事件處理
    add_btn.click(
        fn=add_deposit,
        inputs=[item_input, quantity_input, store_input, redeem_method_input, expiry_date_input],
        outputs=[add_status, deposits_container, statistics_display]
    )
    
    refresh_btn.click(
        fn=lambda: ("", *refresh_all()),
        outputs=[action_status, deposits_container, statistics_display]
    )

if __name__ == "__main__":
    app.launch()
