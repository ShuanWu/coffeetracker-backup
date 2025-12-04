import gradio as gr

maintenance_page = """
<style>
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .maintenance-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        padding: 40px 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
    }
    .icon {
        font-size: 100px;
        margin-bottom: 30px;
        animation: rotate 3s linear infinite;
    }
    .title {
        font-size: 42px;
        font-weight: 700;
        color: #2c3e50;
        margin-bottom: 20px;
    }
    .message {
        font-size: 20px;
        color: #5a6c7d;
        margin-bottom: 15px;
        text-align: center;
        max-width: 600px;
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
    <p class="message">
        我們正在進行系統升級，以提供更好的服務體驗
    </p>
    <p class="message" style="font-size: 18px;">
        預計很快就會完成，請稍後再回來查看
    </p>
    <p class="sub-message">
        感謝您的耐心等待 🙏
    </p>
</div>
"""

with gr.Blocks(title="系統維護中", theme=gr.themes.Soft()) as demo:
    gr.HTML(maintenance_page)

demo.launch()