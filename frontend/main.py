# frontend/main.py
import gradio as gr
import config
from frontend import user_ui, admin_ui
from backend import service

def launch_app():
    with gr.Blocks(css=config.CUSTOM_CSS, title="咖啡寄杯系統") as app:
        
        # 1. 全域狀態
        current_user = gr.State(None)

        # 2. 載入元件
        u = user_ui.create_ui() # 取得所有 User UI 元件
        # 取得 Admin UI 元件 (tab, 按鈕, 輸出欄位, 更新函式)
        adm_tab, adm_refresh, adm_outputs, adm_update_fn = admin_ui.create_dashboard()

        # 3. 處理事件邏輯

        # --- 登入邏輯 (核心控制器) ---
        def handle_login(u_name, u_pass):
            res = service.verify_login(u_name, u_pass)
            if res["success"]:
                username = res["username"]
                is_admin = username in config.ADMIN_USERS
                
                # 登入成功：切換面板，並根據權限顯示 Admin Tab
                return (
                    gr.update(visible=False), # 隱藏登入
                    gr.update(visible=True),  # 顯示 App
                    gr.update(value=f"👤 {username}"), # 歡迎詞
                    user_ui.render_deposit_list(username), # 更新清單
                    gr.update(visible=is_admin), # Admin Tab 可見性
                    username # 更新 State
                )
            else:
                return (gr.update(), gr.update(), gr.update(value=res["message"]), gr.update(), gr.update(), None)

        u["login_btn"].click(
            fn=handle_login,
            inputs=u["login_inputs"],
            outputs=[u["login_panel"], u["app_panel"], u["welcome_msg"], u["deposit_html"], adm_tab, current_user]
        )

        # --- 登出邏輯 ---
        def handle_logout():
            return (
                gr.update(visible=True), gr.update(visible=False), 
                gr.update(visible=False), None
            )
        u["logout_btn"].click(fn=handle_logout, outputs=[u["login_panel"], u["app_panel"], adm_tab, current_user])

        # --- 註冊邏輯 ---
        def handle_reg(u_n, p1, p2):
            res = service.register_user(u_n, p1, p2)
            return res["message"]
        u["reg_btn"].click(fn=handle_reg, inputs=u["reg_inputs"], outputs=u["reg_msg"])

        # --- 新增寄杯 ---
        def handle_add(user, item, qty, store, method, date):
            res = service.add_deposit(user, item, qty, store, method, date)
            # 新增後順便更新清單
            new_list = user_ui.render_deposit_list(user) if res["success"] else gr.NoValue()
            return res["message"], new_list
        
        u["add_btn"].click(
            fn=handle_add,
            inputs=[current_user] + u["add_inputs"],
            outputs=[u["add_msg"], u["deposit_html"]]
        )

        # --- 管理者看板更新 ---
        adm_refresh.click(
            fn=adm_update_fn,
            inputs=[current_user],
            outputs=adm_outputs
        )

    return app