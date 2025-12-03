import gradio as gr
import threading
import config
import database
import logic  # 匯入我們剛拆出來的邏輯

# 預載入資料
def preload_data():
    print("🔄 預載入資料中...")
    database.load_users()
    database.load_sessions()
    print("✅ 預載入完成")

threading.Thread(target=preload_data, daemon=True).start()

# 建立 Gradio 介面
with gr.Blocks(
    title="咖啡寄杯記錄",
    theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
    css=config.CUSTOM_CSS
) as app:
    
    current_user = gr.State(None)
    
    gr.HTML("""... (標題 HTML) ...""")
    
    with gr.Column(visible=True) as login_area:
        with gr.Tabs():
            with gr.Tab("🔐 登入"):
                login_status = gr.Markdown()
                login_username = gr.Textbox(label="使用者名稱")
                login_password = gr.Textbox(label="密碼", type="password")
                remember_me_checkbox = gr.Checkbox(label="記住我", value=True)
                login_btn = gr.Button("登入", variant="primary")
            
            with gr.Tab("📝 註冊"):
                register_status = gr.Markdown()
                register_username = gr.Textbox(label="使用者名稱")
                register_password = gr.Textbox(label="密碼", type="password")
                register_confirm = gr.Textbox(label="確認密碼", type="password")
                register_btn = gr.Button("註冊", variant="primary")
    
    with gr.Column(visible=False) as main_area:
        with gr.Row():
            user_info = gr.Markdown()
            logout_btn = gr.Button("🚪 登出", size="sm")
        
        # ... (中間的新增/兌換 UI 結構，請複製原 app.py 的結構) ...
        # 注意：Dropdown 的 choices 引用 config.STORE_OPTIONS
        
        deposits_display = gr.HTML()
        statistics_display = gr.HTML()
        deposit_selector = gr.Dropdown(label="選擇記錄") # 暫時為空，由邏輯填充

    # === 事件綁定 (這是最重要的部分) ===
    
    # 頁面載入
    def on_load(request: gr.Request):
        user, login_vis, main_vis = logic.auto_login(request)
        if user:
            return (user, login_vis, main_vis, f"👤 {user}", 
                    logic.get_deposits_display(user), 
                    logic.get_statistics(user), 
                    logic.get_deposit_choices(user))
        return (None, login_vis, main_vis, "", 
                logic.get_deposits_display(None), 
                logic.get_statistics(None), 
                gr.update(choices=[]))

    app.load(
        fn=on_load,
        outputs=[current_user, login_area, main_area, user_info, 
                 deposits_display, statistics_display, deposit_selector]
    )
    
    # 註冊與登入
    register_btn.click(
        fn=logic.register_user,
        inputs=[register_username, register_password, register_confirm],
        outputs=[register_status, login_area, main_area]
    )
    
    login_btn.click(
        fn=logic.login_user,
        inputs=[login_username, login_password, remember_me_checkbox],
        outputs=[login_status, login_area, main_area, current_user, user_info, 
                 deposits_display, statistics_display, deposit_selector]
    )
    
    # 登出
    logout_btn.click(
        fn=logic.logout_user,
        outputs=[login_area, main_area, current_user, user_info, 
                 deposits_display, statistics_display, deposit_selector]
    )

    # ... (請依此模式綁定 add_btn, redeem_btn, delete_btn, refresh_btn) ...
    # 範例：
    # add_btn.click(fn=logic.add_deposit, inputs=[...], outputs=[...])

if __name__ == "__main__":
    app.launch()