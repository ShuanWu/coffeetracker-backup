# src/services/deposit_service.py

import gradio as gr
from datetime import datetime, timedelta
from . import storage
from ..utils import date_utils

# 全域變數用於儲存 label 到 id 的映射
deposit_label_to_id = {}

def toggle_expiry_input(method):
    """切換到期日輸入方式"""
    if method == "選擇日期":
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)

def get_deposit_choices(username):
    """取得寄杯記錄選項"""
    if not username:
        return gr.update(choices=[], value=None)
    
    deposits = storage.load_deposits(username)
    if not deposits:
        return gr.update(choices=[], value=None)
    
    global deposit_label_to_id
    deposit_label_to_id = {}
    choices_list = []
    
    for d in deposits:
        # 判斷狀態標籤
        if date_utils.is_expired(d['expiryDate']):
            status_tag = " [已過期]"
        elif date_utils.is_expiring_today(d['expiryDate']):
            status_tag = " [今天到期]"
        elif date_utils.is_expiring_soon(d['expiryDate']):
            status_tag = " [即將到期]"
        else:
            status_tag = ""
        
        label = f"{d['item']} - {d['store']} ({d['quantity']}杯) - 到期:{date_utils.format_date(d['expiryDate'])}{status_tag}"
        
        deposit_label_to_id[label] = d['id']
        choices_list.append(label)
    
    return gr.update(choices=choices_list, value=None)

def add_deposit(username, item, quantity, store, redeem_method, expiry_method, expiry_date, days_until):
    """新增寄杯記錄"""
    if not username:
        return "❌ 請先登入", None, None, None
    
    if not all([item, store, redeem_method]):
        return "❌ 請填寫所有欄位", None, None, None
    
    # 處理到期日
    if expiry_method == "選擇日期":
        final_expiry_date = expiry_date
        if not final_expiry_date or final_expiry_date.strip() == "":
            return "❌ 請選擇到期日", None, None, None
    else:
        if not days_until or days_until < 1:
            return "❌ 請輸入有效的天數（至少 1 天）", None, None, None
        try:
            final_expiry_date = (datetime.now() + timedelta(days=int(days_until))).strftime('%Y-%m-%d')
        except:
            return "❌ 天數格式錯誤", None, None, None
    
    try:
        quantity = int(quantity)
        if quantity < 1:
            return "❌ 數量必須大於 0", None, None, None
    except:
        return "❌ 數量格式錯誤", None, None, None
    
    # 驗證並清理日期格式
    try:
        if isinstance(final_expiry_date, str):
            final_expiry_date = final_expiry_date.strip()
            
            if 'T' in final_expiry_date:
                final_expiry_date = final_expiry_date.split('T')[0]
            if ' ' in final_expiry_date:
                final_expiry_date = final_expiry_date.split(' ')[0]
            
            datetime.strptime(final_expiry_date, '%Y-%m-%d')
        elif hasattr(final_expiry_date, 'strftime'):
            final_expiry_date = final_expiry_date.strftime('%Y-%m-%d')
        else:
            return "❌ 日期格式錯誤", None, None, None
    except Exception as e:
        print(f"日期處理錯誤: {e}, 收到的日期: {final_expiry_date}")
        return f"❌ 日期格式錯誤（請確認已選擇日期）", None, None, None
    
    deposits = storage.load_deposits(username)
    new_deposit = {
        'id': str(int(datetime.now().timestamp() * 1000)),
        'item': item.strip(),
        'quantity': quantity,
        'store': store,
        'redeemMethod': redeem_method,
        'expiryDate': final_expiry_date,
        'createdAt': datetime.now().isoformat()
    }
    deposits.append(new_deposit)
    
    if storage.save_deposits(username, deposits):
        return "✅ 新增成功！", None, None, None
    else:
        return "❌ 儲存失敗", None, None, None

def redeem_one(username, deposit_label):
    """兌換一杯"""
    if not username:
        return "❌ 請先登入", None, None, None
    
    if not deposit_label:
        return "❌ 請選擇要兌換的記錄", None, None, None
    
    deposit_id = deposit_label_to_id.get(deposit_label)
    if not deposit_id:
        return "❌ 找不到該記錄", None, None, None
    
    deposits = storage.load_deposits(username)
    updated = False
    deposit_name = ""
    
    for i, deposit in enumerate(deposits):
        if deposit['id'] == deposit_id:
            deposit_name = deposit['item']
            if deposit['quantity'] > 1:
                deposits[i]['quantity'] -= 1
                message = f"✅ 已兌換一杯 {deposit_name}，剩餘 {deposits[i]['quantity']} 杯"
            else:
                deposits = [d for d in deposits if d['id'] != deposit_id]
                message = f"✅ 已兌換最後一杯 {deposit_name}，記錄已刪除"
            updated = True
            break
    
    if updated:
        storage.save_deposits(username, deposits)
        return message, None, None, None
    else:
        return "❌ 找不到該記錄", None, None, None

def delete_deposit(username, deposit_label):
    """刪除寄杯記錄"""
    if not username:
        return "❌ 請先登入", None, None, None
    
    if not deposit_label:
        return "❌ 請選擇要刪除的記錄", None, None, None
    
    deposit_id = deposit_label_to_id.get(deposit_label)
    if not deposit_id:
        return "❌ 找不到該記錄", None, None, None
    
    deposits = storage.load_deposits(username)
    deposit_name = ""
    
    for d in deposits:
        if d['id'] == deposit_id:
            deposit_name = d['item']
            break
    
    deposits = [d for d in deposits if d['id'] != deposit_id]
    storage.save_deposits(username, deposits)
    
    return f"✅ 已刪除 {deposit_name} 的記錄", None, None, None

def refresh_display(username):
    """重新整理顯示"""
    return None, None, None