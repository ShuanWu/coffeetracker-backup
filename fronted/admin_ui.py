# frontend/admin_ui.py
import gradio as gr
from backend import service

def create_dashboard():
    """建立管理者儀表板 UI"""
    # 預設隱藏，由 main.py 控制顯示
    with gr.Tab("📊 管理者看板", visible=False) as admin_tab:
        gr.Markdown("### 🚀 系統營運概況")
        
        with gr.Row():
            kpi_users = gr.Number(label="👥 總用戶數", interactive=False)
            kpi_cups = gr.Number(label="☕ 系統總庫存 (杯)", interactive=False)
            
        with gr.Row():
            # 使用原生 BarPlot
            plot_store = gr.BarPlot(
                label="庫存分佈 (依商店)",
                x="store", y="count",
                title="各商店累積杯數",
                tooltip=["store", "count"],
                y_lim=[0, None]
            )
            plot_item = gr.BarPlot(
                label="熱門品項 Top 5",
                x="item", y="count",
                title="最多人寄的品項",
                tooltip=["item", "count"]
            )
            
        refresh_btn = gr.Button("🔄 重新整理數據")

        # 定義更新資料的行為
        def update_view(username):
            data = service.get_dashboard_data(username)
            if not data:
                return [gr.update()] * 4
            
            return (
                data['kpi']['users'],
                data['kpi']['cups'],
                data['store_df'],
                data['item_df']
            )
            
        # 綁定事件 (需要 main.py 傳入 current_user)
        # 這裡只回傳元件，讓 main.py 去綁定 click
        return admin_tab, refresh_btn, [kpi_users, kpi_cups, plot_store, plot_item], update_view