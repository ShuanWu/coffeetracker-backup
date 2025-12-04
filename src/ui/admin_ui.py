# src/ui/admin_ui.py

import gradio as gr
from ..services import admin_service

def create_admin_tab(current_user_state):
    """建立管理員專用頁面"""
    
    with gr.Tab("🛡️ 管理者後台", visible=False) as admin_tab:
        gr.Markdown("### 🔧 系統管理中心")
        
        with gr.Tabs():
            # 分頁 1: 系統概況
            with gr.Tab("📊 系統概況"):
                refresh_stats_btn = gr.Button("🔄 重新整理數據")
                stats_display = gr.HTML()
            
            # 分頁 2: 用戶管理
            with gr.Tab("👥 用戶管理"):
                with gr.Row():
                    user_list = gr.Dataframe(
                        headers=["使用者名稱", "註冊時間", "記錄筆數"],
                        datatype=["str", "str", "number"],
                        label="所有註冊用戶",
                        interactive=False
                    )
                
                with gr.Row():
                    target_del_user = gr.Textbox(label="輸入要刪除的用戶名", placeholder="請謹慎操作")
                    del_user_btn = gr.Button("🗑️ 刪除該用戶", variant="stop")
                
                del_status = gr.Markdown()
                
            # 分頁 3: 查閱用戶資料
            with gr.Tab("🔍 查閱用戶資料"):
                gr.Markdown("輸入用戶名稱以查看其寄杯記錄（唯讀模式）")
                with gr.Row():
                    search_user_input = gr.Textbox(label="用戶名稱", scale=4)
                    search_user_btn = gr.Button("🔍 搜尋", scale=1)
                
                target_user_deposits = gr.HTML(label="寄杯列表")
                target_user_stats = gr.HTML(label="統計")

        # === 事件綁定 ===
        
        # 1. 載入統計
        refresh_stats_btn.click(
            fn=admin_service.get_system_stats,
            outputs=[stats_display]
        )
        
        # 2. 刪除用戶
        del_user_btn.click(
            fn=admin_service.delete_user,
            inputs=[current_user_state, target_del_user],
            outputs=[del_status, user_list]
        )
        
        # 3. 搜尋用戶
        search_user_btn.click(
            fn=admin_service.view_user_deposits,
            inputs=[search_user_input],
            outputs=[target_user_deposits, target_user_stats]
        )

        # 4. 初始化載入用戶列表
        refresh_users_btn = gr.Button("🔄 重新整理列表", visible=False) # 隱藏按鈕用於觸發
        refresh_users_btn.click(
            fn=admin_service.get_users_list_dataframe,
            outputs=[user_list]
        )
        
    return admin_tab, stats_display, user_list