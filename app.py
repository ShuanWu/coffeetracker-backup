import gradio as gr
import json
from datetime import datetime, timedelta
import pandas as pd

# 全局變數儲存資料
deposits_data = []

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
    try:
        with open('deposits.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def save_deposits(deposits):
    """儲存寄杯資料"""
    with open('deposits.json', 'w', encoding='utf-8') as f:
        json.dump(deposits, f, ensure_ascii=False, indent=2)

def is_expiring_soon(expiry_date_str):
    """檢查是否即將到期（7天內）"""
    expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
    today = datetime.now()
    days_until_expiry = (expiry - today).days
    return 0 <= days_until_expiry <= 7

def is_expired(expiry_date_str):
    """檢查是否已過期"""
    expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
    return expiry < datetime.now()

def format_date(date_str):
    """格式化日期"""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    return date.strftime('%Y/%m/%d')

def add_deposit(item, quantity, store, redeem_method, expiry_date):
    """新增寄杯記錄"""
    if not all([item, store, redeem_method, expiry_date]) or quantity < 1:
        return "❌ 請填寫所有欄位", get_deposits_display(), get_statistics()
    
    deposits = load_deposits()
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item,
        'quantity': int(quantity),
        'store': store,
        'redeemMethod': redeem_method,
        'expiryDate': expiry_date,
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    save_deposits(deposits)
    
    return "✅ 新增成功！", get_deposits_display(), get_statistics()

def delete_deposit(deposit_id):
    """刪除寄杯記錄"""
    deposits = load_deposits()
    deposits = [d for d in deposits if d['id'] != deposit_id]
    save_deposits(deposits)
    return get_deposits_display(), get_statistics()

def redeem_one(deposit_id):
    """兌換一杯"""
    deposits = load_deposits()
    for deposit in deposits:
        if deposit['id'] == deposit_id:
            if deposit['quantity'] > 1:
                deposit['quantity'] -= 1
            else:
                deposits = [d for d in deposits if d['id'] != deposit_id]
            break
    save_deposits(deposits)
    return get_deposits_display(), get_statistics()

def get_deposits_display():
    """取得寄杯記錄顯示"""
    deposits = load_deposits()
    
    if not deposits:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
            <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯」開始記錄吧！</p>
        </div>
        """
    
    # 按到期日排序
    deposits.sort(key=lambda x: x['expiryDate'])
    
    html = ""
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
            status_color = ""
        
        redeem_link = REDEEM_LINKS.get(deposit['redeemMethod'], '#')
        google_maps_link = f"https://www.google.com/maps/search/{deposit['store']}"
        
        html += f"""
        <div style="margin-bottom: 20px; padding: 24px; border-radius: 16px; {card_style} box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 16px;">
                <div>
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                        <h3 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">{deposit['item']}</h3>
                        <span style="background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 20px; font-size: 14px; font-weight: 500;">
                            {deposit['quantity']} 杯
                        </span>
                    </div>
                    <div style="color: #4b5563; line-height: 1.8;">
                        <div style="margin-bottom: 8px;">📍 {deposit['store']}</div>
                        <div style="margin-bottom: 8px;">📦 兌換途徑：{deposit['redeemMethod']}</div>
                        <div>📅 到期日：{format_date(deposit['expiryDate'])} 
                            <span style="color: {status_color}; font-weight: 500;">{status_text}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px;">
                <button onclick="redeem_deposit('{deposit['id']}')" 
                        style="background: #16a34a; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; font-size: 14px; font-weight: 500;">
                    ☕ 兌換一杯
                </button>
                <a href="{redeem_link}" target="_blank" 
                   style="background: #9333ea; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block;">
                    🔗 前往兌換頁面
                </a>
                <a href="{google_maps_link}" target="_blank" 
                   style="background: #2563eb; color: white; padding: 8px 16px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block;">
                    🗺️ 查看商店位置
                </a>
                <button onclick="delete_deposit('{deposit['id']}')" 
                        style="background: #dc2626; color: white; padding: 8px 16px; border-radius: 8px; border: none; cursor: pointer; font-size: 14px; font-weight: 500;">
                    🗑️ 刪除
                </button>
            </div>
        </div>
        """
    
    return html

def get_statistics():
    """取得統計資訊"""
    deposits = load_deposits()
    
    if not deposits:
        return ""
    
    total_cups = sum(d['quantity'] for d in deposits)
    valid_records = len([d for d in deposits if not is_expired(d['expiryDate'])])
    expired_records = len([d for d in deposits if is_expired(d['expiryDate'])])
    
    html = f"""
    <div style="background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 24px;">
        <h3 style="font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 16px;">📊 統計資訊</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; text-align: center;">
            <div>
                <p style="font-size: 36px; font-weight: bold; color: #d97706; margin: 0;">{total_cups}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 4px;">總杯數</p>
            </div>
            <div>
                <p style="font-size: 36px; font-weight: bold; color: #16a34a; margin: 0;">{valid_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 4px;">有效記錄</p>
            </div>
            <div>
                <p style="font-size: 36px; font-weight: bold; color: #dc2626; margin: 0;">{expired_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 4px;">已過期</p>
            </div>
        </div>
    </div>
    """
    return html

# 初始化資料
deposits_data = load_deposits()

# 建立 Gradio 介面
with gr.Blocks(
    theme=gr.themes.Soft(),
    css="""
        .gradio-container {
            max-width: 1200px !important;
            background: linear-gradient(to bottom right, #fffbeb, #fed7aa) !important;
        }
        .main-header {
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 24px;
        }
        button {
            transition: all 0.3s ease !important;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
    """
) as app:
    gr.HTML("""
        <div class="main-header">
            <div style="display: flex; align-items: center; gap: 16px;">
                <div style="background: #d97706; padding: 16px; border-radius: 12px;">
                    <span style="font-size: 32px;">☕</span>
                </div>
                <div>
                    <h1 style="font-size: 32px; font-weight: bold; color: #1f2937; margin: 0;">咖啡寄杯記錄</h1>
                    <p style="color: #6b7280; margin-top: 4px; font-size: 16px;">管理你的咖啡寄杯，不怕忘記兌換</p>
                </div>
            </div>
        </div>
    """)
    
    with gr.Accordion("➕ 新增寄杯記錄", open=False):
        with gr.Row():
            item_input = gr.Textbox(label="咖啡品項", placeholder="例如：美式咖啡、拿鐵")
            quantity_input = gr.Number(label="數量（杯）", value=1, minimum=1, precision=0)
        
        with gr.Row():
            store_input = gr.Dropdown(label="商店名稱", choices=STORE_OPTIONS)
            redeem_method_input = gr.Dropdown(label="兌換途徑", choices=REDEEM_METHODS)
        
        expiry_date_input = gr.Textbox(label="到期日", placeholder="YYYY-MM-DD")
        
        add_status = gr.Markdown()
        add_btn = gr.Button("💾 儲存", variant="primary", size="lg")
    
    deposits_display = gr.HTML(value=get_deposits_display())
    statistics_display = gr.HTML(value=get_statistics())
    
    # JavaScript 處理按鈕點擊
    gr.HTML("""
        <script>
        function redeem_deposit(id) {
            const event = new CustomEvent('redeem', { detail: id });
            document.dispatchEvent(event);
        }
        function delete_deposit(id) {
            const event = new CustomEvent('delete', { detail: id });
            document.dispatchEvent(event);
        }
        </script>
    """)
    
    # 事件處理
    add_btn.click(
        fn=add_deposit,
        inputs=[item_input, quantity_input, store_input, redeem_method_input, expiry_date_input],
        outputs=[add_status, deposits_display, statistics_display]
    )
    
    # 定期重新整理顯示
    app.load(
        fn=lambda: (get_deposits_display(), get_statistics()),
        outputs=[deposits_display, statistics_display]
    )

if __name__ == "__main__":
    app.launch()
