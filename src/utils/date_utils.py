# src/utils/date_utils.py

from datetime import datetime, timedelta

def is_expiring_soon(expiry_date_str):
    """檢查是否即將到期（7天內，包含到期日當天）"""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        days_until_expiry = (expiry_date - today).days
        return 0 <= days_until_expiry <= 7  # 0 表示今天到期（還可以用）
    except:
        return False

def is_expiring_today(expiry_date_str):
    """檢查是否今天到期"""
    try:
        expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        today = datetime.now().date()
        return expiry_date == today
    except:
        return False

def is_expired(expiry_date_str):
    """檢查是否已過期"""
    try:
        expiry = datetime.strptime(expiry_date_str, '%Y-%m-%d')
        today = datetime.now().date()  # 只取日期
        return today > expiry.date()
    except:
        return False

def format_date(date_str):
    """格式化日期"""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
        return date.strftime('%Y/%m/%d')
    except:
        return date_str

def calculate_expiry_date_display(days):
    """根據天數計算到期日並顯示"""
    if not days or days < 1:
        return "請輸入有效天數（至少 1 天）"
    
    try:
        days = int(days)
        expiry_date = datetime.now() + timedelta(days=days)
        formatted_date = expiry_date.strftime('%Y年%m月%d日 (%A)')
        weekday_map = {
            'Monday': '星期一', 'Tuesday': '星期二', 'Wednesday': '星期三',
            'Thursday': '星期四', 'Friday': '星期五', 'Saturday': '星期六', 'Sunday': '星期日'
        }
        for en, zh in weekday_map.items():
            formatted_date = formatted_date.replace(en, zh)
        
        return f"📅 **計算結果：{formatted_date}**"
    except:
        return "❌ 計算錯誤"