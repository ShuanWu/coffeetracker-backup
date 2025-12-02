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
                    value=STORE_OPTIONS[0],
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
                redeem_method_input = gr.Dropdown(
                    label="📦 兌換途徑", 
                    choices=REDEEM_METHODS,
                    value=REDEEM_METHODS[0],
                    interactive=True,
                    elem_classes=["dropdown-readonly"],
                    scale=1
                )
            
            # 使用 DateTime 元件作為日期選擇器
            expiry_date_input = gr.DateTime(
                label="📅 到期日",
                include_time=False,
                type="string",
                elem_classes=["datepicker-readonly"]
            )
            
            add_status = gr.Markdown()
            add_btn = gr.Button("💾 儲存記錄", variant="primary", size="lg")
