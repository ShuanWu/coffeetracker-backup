# src/config/ui_config.py

# 商店和兌換途徑選項
STORE_OPTIONS = ['7-11', '全家', '星巴克']
REDEEM_METHODS = ['7-11', '全家', 'Line禮物', '全家酷碰劵', '遠傳', '星巴克']

# 兌換連結對應
REDEEM_LINKS = {
    '7-11': {
        'app': 'openpointapp://gofeature?featureId=HOMACB02',
        'name': 'OPENPOINT'
    },
    '全家': {
        'app': 'familymart://action.go/preorder/myproduct',
        'name': '全家便利商店'
    },    
    '遠傳': {
        'app': 'fetnet://',
        'name': '遠傳心生活'
    },
    'Line禮物': {
        'app': 'https://line.me/R/shop/gift/category/coffee',
        'name': 'Line 禮物'
    },
    '全家酷碰劵': {
        'app': 'familymart://action.go/preorder/coupon',
        'name': '全家酷碰劵'
    },    
    '星巴克': {
        'app': 'starbucks://',
        'name': '星巴克'
    }
}

# CSS 樣式
CUSTOM_CSS = """
/* ===== 只隱藏時間輸入框，保留日期輸入框 ===== */

/* 只隱藏第一個輸入框（時間） */
#expiry_date_picker .timebox input:first-child {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    visibility: hidden !important;
    position: absolute !important;
}

/* 隱藏日曆按鈕 */
#expiry_date_picker button.calendar {
    display: none !important;
}

/* 確保日期輸入框（第二個）正常顯示 */
#expiry_date_picker .timebox input:nth-child(2),
#expiry_date_picker .timebox input[type="date"] {
    display: block !important;
    width: 100% !important;
    flex: 1 !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
}

/* timebox 容器 */
#expiry_date_picker .timebox {
    display: flex !important;
    width: 100% !important;
}


/* 隱藏 Hugging Face Space 頂部標題欄 */
#huggingface-space-header {
    display: none !important;
}

/* 移除頂部間距 */
body {
    padding-top: 0 !important;
}

.contain {
    padding-top: 0 !important;
}

/* ===== 下拉選單樣式 ===== */
.dropdown-readonly input {
    caret-color: transparent !important;
    cursor: pointer !important;
    user-select: none !important;
}

.dropdown-readonly input:focus {
    caret-color: transparent !important;
}

.dropdown-readonly * {
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
}

/* ===== 日期選擇器樣式 ===== */

/* 日期選擇器容器 */
.datepicker-readonly {
    position: relative !important;
}

/* 日期選擇器輸入框基礎樣式 */
.datepicker-readonly input,
input[type="date"],
input[type="datetime-local"] {
    width: 100% !important;
    padding: 14px 16px !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 12px !important;
    font-size: 16px !important;
    background: white !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    color: #1f2937 !important;
    caret-color: transparent !important;
    user-select: none !important;
}

.datepicker-readonly input:focus,
input[type="date"]:focus,
input[type="datetime-local"]:focus {
    outline: none !important;
    border-color: #f97316 !important;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1) !important;
    caret-color: transparent !important;
}

/* 防止文字選取 */
.datepicker-readonly *,
input[type="date"],
input[type="datetime-local"] {
    user-select: none !important;
    -webkit-user-select: none !important;
    -moz-user-select: none !important;
    -ms-user-select: none !important;
}

/* 日期選擇器按鈕 */
.datepicker-readonly button {
    pointer-events: auto !important;
    cursor: pointer !important;
}

/* 桌面版樣式 */
@media (min-width: 769px) {
    .datepicker-readonly input,
    input[type="date"],
    input[type="datetime-local"] {
        padding: 12px 16px !important;
        min-height: 44px !important;
    }
}

/* 手機版優化 */
@media (max-width: 768px) {
    .datepicker-readonly input,
    input[type="date"],
    input[type="datetime-local"] {
        min-height: 52px !important;
        font-size: 16px !important;
        padding: 14px 48px 14px 16px !important;
        -webkit-appearance: none !important;
        appearance: none !important;
    }
    
    /* 添加自定義日曆圖標 */
    .datepicker-readonly input,
    input[type="date"],
    input[type="datetime-local"] {
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='%23f97316' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'%3E%3C/rect%3E%3Cline x1='16' y1='2' x2='16' y2='6'%3E%3C/line%3E%3Cline x1='8' y1='2' x2='8' y2='6'%3E%3C/line%3E%3Cline x1='3' y1='10' x2='21' y2='10'%3E%3C/line%3E%3C/svg%3E") !important;
        background-repeat: no-repeat !important;
        background-position: right 14px center !important;
        background-size: 28px 28px !important;
    }
    
    /* 隱藏原生日曆圖標（但保持可點擊） */
    input[type="date"]::-webkit-calendar-picker-indicator,
    input[type="datetime-local"]::-webkit-calendar-picker-indicator {
        position: absolute !important;
        right: 0 !important;
        width: 52px !important;
        height: 100% !important;
        opacity: 0 !important;
        cursor: pointer !important;
    }
    
    /* 移除原生的清除按鈕和旋轉按鈕 */
    input[type="date"]::-webkit-inner-spin-button,
    input[type="date"]::-webkit-clear-button,
    input[type="datetime-local"]::-webkit-inner-spin-button,
    input[type="datetime-local"]::-webkit-clear-button {
        display: none !important;
    }
    
    /* 日期選擇器容器間距 */
    .date-picker-container {
        position: relative !important;
        margin-bottom: 8px !important;
    }
    
    .date-picker-container .gr-form {
        margin-bottom: 0 !important;
    }
}

/* ===== 日期選擇器彈出日曆樣式（原生瀏覽器日曆）===== */

/* Chrome/Edge 日曆樣式 */
input[type="date"]::-webkit-datetime-edit,
input[type="datetime-local"]::-webkit-datetime-edit {
    padding: 0 !important;
}

input[type="date"]::-webkit-datetime-edit-fields-wrapper,
input[type="datetime-local"]::-webkit-datetime-edit-fields-wrapper {
    padding: 0 !important;
}

/* 確保日期選擇器在所有瀏覽器中都能正常顯示 */
input[type="date"],
input[type="datetime-local"] {
    position: relative !important;
    z-index: 1 !important;
}


/* ===== 原生日曆彈窗優化（有限支援）===== */
input[type="date"]::-webkit-calendar-picker-indicator {
    z-index: 999 !important;
}

/* 日期輸入框獲得焦點時的效果 */
input[type="date"]:focus,
input[type="datetime-local"]:focus {
    border-color: #f97316 !important;
    box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1), 0 4px 12px rgba(0, 0, 0, 0.1) !important;
}

/* 日期輸入框懸停效果 */
input[type="date"]:hover,
input[type="datetime-local"]:hover {
    border-color: #fb923c !important;
    box-shadow: 0 2px 8px rgba(249, 115, 22, 0.1) !important;
}
"""

# JS 初始化腳本
JS_INIT_SCRIPT = """
<script>
document.addEventListener('DOMContentLoaded', function() {
    // 監聽所有 datepicker-readonly 元素
    const observers = [];
    
    function initDatePicker() {
        const dateInputs = document.querySelectorAll('.datepicker-readonly input');
        
        dateInputs.forEach(input => {
            // 點擊輸入框時自動打開日曆
            input.addEventListener('click', function(e) {
                // 找到對應的 flatpickr 實例
                if (this._flatpickr) {
                    this._flatpickr.open();
                }
            });
            
            // 防止輸入框被編輯
            input.addEventListener('keydown', function(e) {
                e.preventDefault();
            });
        });
    }
    
    // 初始化
    initDatePicker();
    
    // 監聽 DOM 變化，處理動態添加的元素
    const observer = new MutationObserver(function(mutations) {
        initDatePicker();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
</script>
"""