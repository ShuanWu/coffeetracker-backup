# frontend/user_ui.py
import gradio as gr
import config
from backend import service
from datetime import datetime

def render_deposit_list(username):
    """將寄杯資料轉為 HTML (View Logic)"""
    if not username: return "<div>請先登入</div>"
    deposits = service.get_user_deposits(username)
    if not deposits: return "<div>尚無記錄</div>"
    
    html = '<div style="display: flex; flex-direction: column; gap: 15px;">'
    for d in deposits:
        # 簡單的 HTML 卡片樣式
        html += f"""
        <div style="padding: 15px; border: 1px solid #eee; border-radius: 10px; background: white;">
            <h3 style="margin:0;">{d['item']} <span style="font-size:0.8em; color:#888">x{d['quantity']}</span></h3>
            <p style="margin:5px 0;">🏪 {d['store']} | 📅 {d['expiryDate']}</p>
        </div>
        """
    html += "</div>"
    return html

def create_ui():
    """建立使用者介面 UI"""
    with gr.Column(visible=True) as login_panel:
        with gr.Tab("登入"):
            user_in = gr.Textbox(label="帳號")
            pass_in = gr.Textbox(label="密碼", type="password")
            login_btn = gr.Button("登入", variant="primary")
        with gr.Tab("註冊"):
            reg_user = gr.Textbox(label="帳號")
            reg_pass = gr.Textbox(label="密碼", type="password")
            reg_confirm = gr.Textbox(label="確認密碼", type="password")
            reg_btn = gr.Button("註冊")
            reg_msg = gr.Markdown()

    with gr.Column(visible=False) as app_panel:
        welcome_msg = gr.Markdown()
        logout_btn = gr.Button("登出", size="sm")
        
        with gr.Tab("我的寄杯"):
            deposit_html = gr.HTML()
            refresh_list_btn = gr.Button("重新整理")
            
        with gr.Tab("新增"):
            item = gr.Textbox(label="品項")
            qty = gr.Number(value=1, label="數量")
            store = gr.Dropdown(choices=config.STORE_OPTIONS, label="商店", value=config.STORE_OPTIONS[0])
            method = gr.Dropdown(choices=config.REDEEM_METHODS, label="兌換方式", value=config.REDEEM_METHODS[0])
            # 簡化範例：直接用日期字串
            expiry = gr.Textbox(label="到期日 (YYYY-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"))
            add_btn = gr.Button("儲存", variant="primary")
            add_msg = gr.Markdown()

    return {
        "login_panel": login_panel, "login_inputs": [user_in, pass_in], "login_btn": login_btn,
        "reg_inputs": [reg_user, reg_pass, reg_confirm], "reg_btn": reg_btn, "reg_msg": reg_msg,
        "app_panel": app_panel, "welcome_msg": welcome_msg, "logout_btn": logout_btn,
        "deposit_html": deposit_html, "refresh_list_btn": refresh_list_btn,
        "add_inputs": [item, qty, store, method, expiry], "add_btn": add_btn, "add_msg": add_msg
    }