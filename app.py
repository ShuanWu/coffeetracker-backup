# app.py - 重構版本
import gradio as gr

# ========== 維護模式開關 ==========
MAINTENANCE = False  # 改成 True 啟用維護
# =================================

if MAINTENANCE:
    # 維修頁面（帶旋轉動畫）
    maintenance_page = """
    <style>
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        .maintenance-container {
            text-align: center;
            padding: 80px 20px;
            font-family: Arial, sans-serif;
        }
        .icon {
            font-size: 100px;
            margin-bottom: 30px;
            display: inline-block;
            animation: rotate 3s linear infinite;
        }
        .title {
            font-size: 42px;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .message {
            font-size: 20px;
            color: #5a6c7d;
            margin-bottom: 15px;
        }
        .sub-message {
            font-size: 16px;
            color: #95a5a6;
            margin-top: 30px;
        }
    </style>
    
    <div class="maintenance-container">
        <div class="icon">⚙️</div>
        <h1 class="title">系統維護中</h1>
        <p class="message">我們正在進行系統升級</p>
        <p class="sub-message">預計很快完成，感謝等待 🙏</p>
    </div>
    """
    
    with gr.Blocks(title="系統維護中") as demo:
        gr.HTML(maintenance_page)
    
    demo.launch()
    
    # 結束程式，不執行下面的主程式
    import sys
    sys.exit(0)

# ========== 以下是你的正常主程式 ==========



from datetime import datetime

# 導入配置
from src.config import ui_config

# 導入服務
from src.services import auth, deposit_service, storage

# 導入 UI 組件
from src.ui import components

# 導入工具函數
from src.utils import date_utils

# 初始化：載入用戶資料
storage.load_users()

# 建立 Gradio 介面
with gr.Blocks(
    title="咖啡寄杯記錄",
    theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
    css=ui_config.CUSTOM_CSS
) as app:
    
    current_user = gr.State(None)
    
    gr.HTML(ui_config.JS_INIT_SCRIPT)
    
    gr.HTML("""
        <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px;">
            <h1 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">
                咖啡寄杯記錄系統
            </h1>
            <p style="color: #6b7280; margin-top: 8px; font-size: 14px;">管理你的咖啡寄杯，不怕忘記兌換</p>
        </div>
    """)
    
    # === 登入/註冊區域 ===
    with gr.Column(visible=True) as login_area:
        with gr.Tabs():
            with gr.Tab("🔓 登入"):
                login_status = gr.Markdown()
                login_username = gr.Textbox(label="使用者名稱", placeholder="請輸入使用者名稱")
                login_password = gr.Textbox(label="密碼", type="password", placeholder="請輸入密碼")
                remember_me_checkbox = gr.Checkbox(label="記住我（30天內自動登入）", value=True)
                login_btn = gr.Button("登入", variant="primary", size="lg")
            
            with gr.Tab("📝 註冊"):
                register_status = gr.Markdown()
                register_username = gr.Textbox(label="使用者名稱", placeholder="至少 3 個字元")
                register_password = gr.Textbox(label="密碼", type="password", placeholder="至少 6 個字元")
                register_confirm = gr.Textbox(label="確認密碼", type="password", placeholder="再次輸入密碼")
                register_btn = gr.Button("註冊", variant="primary", size="lg")
    
    # === 主功能區域 ===
    with gr.Column(visible=False) as main_area:
        with gr.Row():
            user_info = gr.Markdown()
            logout_btn = gr.Button("🚪 登出", size="sm")
        
        gr.Markdown("---")
        
        # 新增寄杯記錄
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
                    choices=ui_config.STORE_OPTIONS,
                    value=ui_config.STORE_OPTIONS[0],
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
                redeem_method_input = gr.Dropdown(
                    label="📦 兌換途徑", 
                    choices=ui_config.REDEEM_METHODS,
                    value=ui_config.REDEEM_METHODS[0],
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
            
            # 到期日輸入方式選擇
            expiry_input_method = gr.Radio(
                label="📅 到期日輸入方式",
                choices=["選擇日期", "輸入天數"],
                value="選擇日期",
                interactive=True
            )

            # 日期選擇器
            with gr.Column(visible=True) as date_picker_column:
                today = datetime.now().strftime('%Y-%m-%d')
                
                expiry_date_input = gr.DateTime(
                    label="📅 到期日",
                    value=today,
                    include_time=False,
                    type="string",
                    elem_id="expiry_date_picker",
                    elem_classes=["date-picker-container"]
                )
                
                # 特殊樣式處理
                gr.HTML(f"""
                <style>
                #expiry_date_picker .timebox input:first-child {{
                    display: none !important;
                }}
                #expiry_date_picker button.calendar {{
                    display: none !important;
                }}
                #expiry_date_picker .timebox input[type="date"] {{
                    display: block !important;
                    width: 100% !important;
                }}
                </style>
                <script>
                (function() {{
                    function processDatePicker() {{
                        const container = document.querySelector('#expiry_date_picker');
                        if (container) {{
                            const timebox = container.querySelector('.timebox');
                            if (timebox) {{
                                const inputs = timebox.querySelectorAll('input');
                                inputs.forEach((input, index) => {{
                                    if (index === 0) {{
                                        input.style.display = 'none';
                                        input.style.visibility = 'hidden';
                                    }}
                                    else if (index === 1 || input.type === 'date') {{
                                        input.style.display = 'block';
                                        input.style.visibility = 'visible';
                                        input.min = '{today}';
                                    }}
                                }});
                                timebox.style.display = 'flex';
                                timebox.style.width = '100%';
                                return true;
                            }}
                        }}
                        return false;
                    }}
                    setTimeout(processDatePicker, 100);
                    setTimeout(processDatePicker, 500);
                    setTimeout(processDatePicker, 1000);
                }})();
                </script>
                """)

            # 天數輸入
            with gr.Column(visible=False) as days_input_column:
                days_until_expiry = gr.Number(
                    label="⏰ 幾天後到期",
                    value=30,
                    minimum=1,
                    precision=0,
                    info="輸入距離今天幾天後到期（例如：30 表示 30 天後到期）"
                )
                calculated_date_display = gr.Markdown(value="", visible=True)

            add_status = gr.Markdown()
            add_btn = gr.Button("💾 儲存記錄", variant="primary", size="lg")
        
        gr.Markdown("---")
        
        # 兌換/刪除寄杯記錄
        with gr.Accordion("☕ 兌換 / 刪除寄杯記錄", open=True):
            gr.Markdown("💡 **提示：** 在下方選擇記錄後，點擊「兌換一杯」或「刪除記錄」按鈕")
            action_status = gr.Markdown()
            deposit_selector = gr.Dropdown(
                label="📋 選擇寄杯記錄",
                choices=[],
                value=None,
                interactive=True,
                elem_classes=["dropdown-readonly"]
            )
            
            with gr.Row():
                redeem_btn = gr.Button("☕ 兌換一杯", variant="primary", size="lg", scale=2)
                delete_btn = gr.Button("🗑️ 刪除記錄", variant="stop", size="lg", scale=1)
                refresh_btn = gr.Button("🔄 重新整理", size="lg", scale=1)
        
        gr.Markdown("---")
        gr.Markdown("### 📋 所有寄杯記錄")
        
        deposits_display = gr.HTML(value=components.get_deposits_display(None))
        statistics_display = gr.HTML(value=components.get_statistics(None))
    
    # === 事件處理器 ===

    # 頁面載入時自動登入
    def on_load(request: gr.Request):
        user, login_vis, main_vis = auth.auto_login(request)
        if user:
            user_display = f"👤 使用者：**{user}**"
            deposits = components.get_deposits_display(user)
            stats = components.get_statistics(user)
            choices = deposit_service.get_deposit_choices(user)
            return user, login_vis, main_vis, user_display, deposits, stats, choices
        return None, login_vis, main_vis, "", components.get_deposits_display(None), components.get_statistics(None), gr.update(choices=[])
    
    app.load(
        fn=on_load,
        outputs=[current_user, login_area, main_area, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 切換輸入方式
    expiry_input_method.change(
        fn=deposit_service.toggle_expiry_input,
        inputs=[expiry_input_method],
        outputs=[date_picker_column, days_input_column]
    )
    
    # 天數變更時顯示計算結果
    days_until_expiry.change(
        fn=date_utils.calculate_expiry_date_display,
        inputs=[days_until_expiry],
        outputs=[calculated_date_display]
    )
    
    # 註冊事件
    def register_and_update(username, password, confirm):
        return auth.register_user(username, password, confirm)
    
    register_btn.click(
        fn=register_and_update,
        inputs=[register_username, register_password, register_confirm],
        outputs=[register_status, login_area, main_area]
    )
    register_confirm.submit(
        fn=register_and_update,
        inputs=[register_username, register_password, register_confirm],
        outputs=[register_status, login_area, main_area]
    )
    
    # 登入事件
    def login_and_update(username, password, remember_me, request: gr.Request):
        message, login_vis, main_vis, user = auth.login_user(username, password, remember_me, request)
        if user:
            user_display = f"👤 使用者：**{user}**"
            deposits = components.get_deposits_display(user)
            stats = components.get_statistics(user)
            choices = deposit_service.get_deposit_choices(user)
            return message, login_vis, main_vis, user, user_display, deposits, stats, choices
        else:
            return message, login_vis, main_vis, None, "", components.get_deposits_display(None), components.get_statistics(None), gr.update(choices=[])
    
    login_btn.click(
        fn=login_and_update,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    login_username.submit(
        fn=login_and_update,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    login_password.submit(
        fn=login_and_update,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 登出事件
    def logout_and_update(request: gr.Request):
        auth.logout_user(request)
        return gr.update(visible=True), gr.update(visible=False), None, "", components.get_deposits_display(None), components.get_statistics(None), gr.update(choices=[])
    
    logout_btn.click(
        fn=logout_and_update,
        outputs=[login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 新增寄杯事件
    def add_and_refresh(user, item, quantity, store, redeem_method, expiry_method, expiry_date, days_until):
        message, _, _, _ = deposit_service.add_deposit(user, item, quantity, store, redeem_method, expiry_method, expiry_date, days_until)
        deposits = components.get_deposits_display(user)
        stats = components.get_statistics(user)
        choices = deposit_service.get_deposit_choices(user)
        return message, deposits, stats, choices
    
    add_btn.click(
        fn=add_and_refresh,
        inputs=[current_user, item_input, quantity_input, store_input, redeem_method_input, expiry_input_method, expiry_date_input, days_until_expiry],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    item_input.submit(
        fn=add_and_refresh,
        inputs=[current_user, item_input, quantity_input, store_input, redeem_method_input, expiry_input_method, expiry_date_input, days_until_expiry],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 兌換事件
    def redeem_and_refresh(user, deposit_id):
        message, _, _, _ = deposit_service.redeem_one(user, deposit_id)
        deposits = components.get_deposits_display(user)
        stats = components.get_statistics(user)
        choices = deposit_service.get_deposit_choices(user)
        return message, deposits, stats, choices
    
    redeem_btn.click(
        fn=redeem_and_refresh,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 刪除事件
    def delete_and_refresh(user, deposit_id):
        message, _, _, _ = deposit_service.delete_deposit(user, deposit_id)
        deposits = components.get_deposits_display(user)
        stats = components.get_statistics(user)
        choices = deposit_service.get_deposit_choices(user)
        return message, deposits, stats, choices
    
    delete_btn.click(
        fn=delete_and_refresh,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 重新整理事件
    def refresh_display_handler(user):
        deposits = components.get_deposits_display(user)
        stats = components.get_statistics(user)
        choices = deposit_service.get_deposit_choices(user)
        return deposits, stats, choices
    
    refresh_btn.click(
        fn=refresh_display_handler,
        inputs=[current_user],
        outputs=[deposits_display, statistics_display, deposit_selector]
    )

if __name__ == "__main__":
    app.launch()