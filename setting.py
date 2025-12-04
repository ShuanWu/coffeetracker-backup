import os
import gradio as gr

MAINTENANCE = os.getenv("MAINTENANCE", "false").lower() == "true"

if MAINTENANCE:
    # 顯示維修頁面
    demo = gr.Blocks()
    with demo:
        gr.Markdown("# 🔧 系統維護中\n\n請稍後再試...")
else:
    # 正常應用
    demo = create_normal_app()

demo.launch()