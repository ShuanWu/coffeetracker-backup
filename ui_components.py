from config import REDEEM_LINKS
from utils import is_expired, is_expiring_today, is_expiring_soon, format_date
from deposit import load_deposits


# CSS 樣式保持不變（太長，這裡省略）
CUSTOM_CSS = """./* ===== 只隱藏時間輸入框，保留日期輸入框 ===== */

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

# /* Chrome/Edge 日曆樣式 */
# input[type="date"]::-webkit-datetime-edit,
# input[type="datetime-local"]::-webkit-datetime-edit {
#     padding: 0 !important;
# }

# input[type="date"]::-webkit-datetime-edit-fields-wrapper,
# input[type="datetime-local"]::-webkit-datetime-edit-fields-wrapper {
#     padding: 0 !important;
# }

# /* 確保日期選擇器在所有瀏覽器中都能正常顯示 */
# input[type="date"],
# input[type="datetime-local"] {
#     position: relative !important;
#     z-index: 1 !important;
# }


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



/* JavaScript 初始化 - 點擊輸入框時自動打開日曆 */
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
"""  # 使用原本的 CSS


def get_deposits_display(username):
    """取得寄杯記錄顯示"""
    if not username:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">🔒</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">請先登入</p>
            <p style="font-size: 16px; color: #9ca3af;">登入後即可查看您的寄杯記錄</p>
        </div>
        """
    
    deposits = load_deposits(username)
    
    if not deposits:
        return """
        <div style="text-align: center; padding: 60px 20px; background: white; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="font-size: 64px; margin-bottom: 20px;">☕</div>
            <p style="font-size: 20px; color: #6b7280; margin-bottom: 10px;">還沒有寄杯記錄</p>
            <p style="font-size: 16px; color: #9ca3af;">點擊上方「新增寄杯記錄」開始記錄吧！</p>
        </div>
        """
    
    deposits.sort(key=lambda x: x.get('expiryDate', '9999-12-31'))
    
    html = '<div style="display: flex; flex-direction: column; gap: 20px;">'
    
    for deposit in deposits:
        expired = is_expired(deposit['expiryDate'])
        expiring_today = is_expiring_today(deposit['expiryDate'])
        expiring_soon = is_expiring_soon(deposit['expiryDate']) and not expired and not expiring_today
        
        if expired:
            card_style = "background: #fef2f2; border: 2px solid #fca5a5;"
            status_text = "（已過期）"
            status_color = "#dc2626"
            status_emoji = "❌"
        elif expiring_today:
            card_style = "background: #fff4ed; border: 2px solid #fb923c;"
            status_text = "（今天到期）"
            status_color = "#ea580c"
            status_emoji = "⚠️"
        elif expiring_soon:
            card_style = "background: #fefce8; border: 2px solid #fde047;"
            status_text = "（即將到期）"
            status_color = "#ca8a04"
            status_emoji = "⏰"
        else:
            card_style = "background: white; border: 1px solid #e5e7eb;"
            status_text = ""
            status_color = "#6b7280"
            status_emoji = ""
        
        redeem_info = REDEEM_LINKS.get(deposit['redeemMethod'], {
            'app': '#',
            'name': deposit['redeemMethod']
        })
        app_link = redeem_info['app']
        app_name = redeem_info['name']
        google_maps_link = f"https://www.google.com/maps/search/{deposit['store']}"
        
        html += f"""
        <div style="padding: 24px; border-radius: 16px; {card_style} box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <div style="margin-bottom: 16px;">
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap;">
                    <h3 style="font-size: 24px; font-weight: bold; color: #1f2937; margin: 0;">{deposit['item']}</h3>
                    <span style="background: #fef3c7; color: #92400e; padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 600;">
                        {deposit['quantity']} 杯
                    </span>
                </div>
                <div style="color: #4b5563; line-height: 2; font-size: 15px;">
                    <div style="margin-bottom: 6px;">📍 <strong>商店：</strong>{deposit['store']}</div>
                    <div style="margin-bottom: 6px;">📦 <strong>兌換途徑：</strong>{deposit['redeemMethod']}</div>
                    <div>📅 <strong>到期日：</strong>{format_date(deposit['expiryDate'])} 
                        <span style="color: {status_color}; font-weight: 600;">{status_emoji} {status_text}</span>
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px;">
                <a href="{app_link}" target="_blank" 
                   style="background: #9333ea; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s; box-shadow: 0 2px 4px rgba(147, 51, 234, 0.3);">
                    📱 開啟 {app_name} App
                </a>
                <a href="{google_maps_link}" target="_blank" 
                   style="background: #2563eb; color: white; padding: 10px 18px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; display: inline-block; transition: all 0.2s;">
                    🗺️ 查看商店位置
                </a>
            </div>
            <div style="padding: 12px; background: #f9fafb; border-radius: 8px; font-size: 12px; color: #6b7280;">
                💡 <strong>提示：</strong>點擊「開啟 App」會嘗試開啟對應的手機應用程式
            </div>
        </div>
        """
    
    html += '</div>'
    return html


def get_statistics(username):
    """取得統計資訊"""
    if not username:
        return ""
    
    deposits = load_deposits(username)
    
    if not deposits:
        return ""
    
    total_cups = sum(d['quantity'] for d in deposits)
    valid_records = len([d for d in deposits if not is_expired(d['expiryDate'])])
    expired_records = len([d for d in deposits if is_expired(d['expiryDate'])])
    expiring_today = len([d for d in deposits if is_expiring_today(d['expiryDate'])])
    expiring_soon = len([d for d in deposits if is_expiring_soon(d['expiryDate']) and not is_expired(d['expiryDate']) and not is_expiring_today(d['expiryDate'])])
    
    html = f"""
    <div style="background: white; padding: 24px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-top: 24px;">
        <h3 style="font-size: 20px; font-weight: bold; color: #1f2937; margin-bottom: 20px;">📊 統計資訊</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 16px; text-align: center;">
            <div style="padding: 16px; background: #fffbeb; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #d97706; margin: 0;">{total_cups}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">總杯數</p>
            </div>
            <div style="padding: 16px; background: #f0fdf4; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #16a34a; margin: 0;">{valid_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">有效記錄</p>
            </div>
            <div style="padding: 16px; background: #fff4ed; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #ea580c; margin: 0;">{expiring_today}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">今天到期</p>
            </div>
            <div style="padding: 16px; background: #fefce8; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #ca8a04; margin: 0;">{expiring_soon}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">即將到期</p>
            </div>
            <div style="padding: 16px; background: #fef2f2; border-radius: 12px;">
                <p style="font-size: 36px; font-weight: bold; color: #dc2626; margin: 0;">{expired_records}</p>
                <p style="font-size: 14px; color: #6b7280; margin-top: 8px; font-weight: 500;">已過期</p>
            </div>
        </div>
    </div>
    """
    return html
