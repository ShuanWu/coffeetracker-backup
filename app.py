# 建立 Gradio 介面
with gr.Blocks(
    title="☕ 咖啡寄杯記錄",
    theme=gr.themes.Soft(primary_hue="orange", secondary_hue="amber"),
) as app:
    
    current_user = gr.State(None)
    
    gr.HTML("""
        <div style="background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 24px;">
            <h1 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">
                咖啡寄杯記錄系統
            </h1>
            <p style="color: #6b7280; margin-top: 8px; font-size: 14px;">管理你的咖啡寄杯，不怕忘記兌換 ☕✨</p>
        </div>
    """)
    
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
            
            try:
                expiry_date_input = gr.DateTime(
                    label="📅 到期日",
                    include_time=False,
                    type="string"
                )
            except:
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
    
    # 事件處理 - 登入（修正這裡）
    def login_and_update(username, password):
        """登入並更新所有相關狀態"""
        message, login_vis, main_vis, user = login_user(username, password)
        
        if user:  # 登入成功
            user_display = f"👤 使用者：**{user}**"
            deposits = get_deposits_display(user)
            stats = get_statistics(user)
            choices = get_deposit_choices(user)
            return message, login_vis, main_vis, user, user_display, deposits, stats, choices
        else:  # 登入失敗
            return message, login_vis, main_vis, None, "", get_deposits_display(None), get_statistics(None), gr.update(choices=[])
    
    login_btn.click(
        fn=login_and_update,
        inputs=[login_username, login_password],
        outputs=[login_status, login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 登出
    logout_btn.click(
        fn=logout_user,
        outputs=[login_area, main_area, current_user, user_info, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 新增記錄（確保使用 current_user）
    def add_and_refresh(user, item, quantity, store, redeem_method, expiry_date):
        """新增記錄並刷新顯示"""
        message, deposits, stats, choices = add_deposit(user, item, quantity, store, redeem_method, expiry_date)
        return message, deposits, stats, choices
    
    add_btn.click(
        fn=add_and_refresh,
        inputs=[current_user, item_input, quantity_input, store_input, redeem_method_input, expiry_date_input],
        outputs=[add_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 兌換
    def redeem_and_refresh(user, deposit_id):
        """兌換並刷新顯示"""
        message, deposits, stats, choices = redeem_one(user, deposit_id)
        return message, deposits, stats, choices
    
    redeem_btn.click(
        fn=redeem_and_refresh,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 刪除
    def delete_and_refresh(user, deposit_id):
        """刪除並刷新顯示"""
        message, deposits, stats, choices = delete_deposit(user, deposit_id)
        return message, deposits, stats, choices
    
    delete_btn.click(
        fn=delete_and_refresh,
        inputs=[current_user, deposit_selector],
        outputs=[action_status, deposits_display, statistics_display, deposit_selector]
    )
    
    # 事件處理 - 重新整理
    def refresh_all(user):
        """重新整理所有顯示"""
        deposits, stats, choices = refresh_display(user)
        return deposits, stats, choices
    
    refresh_btn.click(
        fn=refresh_all,
        inputs=[current_user],
        outputs=[deposits_display, statistics_display, deposit_selector]
    )

if __name__ == "__main__":
    app.launch()
