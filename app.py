import gradio as gr

simple_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            padding: 20px;
            background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1 { color: #92400e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☕ 咖啡寄杯追蹤器</h1>
        <p>測試頁面 - 如果你看到這個，代表基本 HTML 可以運作</p>
        <button onclick="alert('按鈕有效!')">測試按鈕</button>
    </div>
</body>
</html>
"""

demo = gr.Interface(
    fn=lambda: simple_html,
    inputs=None,
    outputs=gr.HTML(),
    title="測試"
)

demo.launch()
