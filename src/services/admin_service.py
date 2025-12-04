# src/services/admin_service.py

import os
import gradio as gr
from ..config import settings
from . import storage
from ..utils import date_utils

def is_admin(username):
    """檢查是否為管理員"""
    return username in settings.ADMIN_USERS

def get_system_stats():
    """計算全系統統計數據"""
    users = storage.load_users()
    user_files = storage.get_all_user_files()
    
    total_users = len(users)
    total_cups = 0
    total_expired = 0
    total_active_deposits = 0
    
    # 遍歷所有用戶資料檔案進行統計
    # 注意：如果用戶量極大，這裡可能需要優化（例如改用資料庫或快取）
    for filename in user_files:
        username = filename.replace('.json', '')
        deposits = storage.load_deposits(username)
        
        for d in deposits:
            qty = d.get('quantity', 0)
            expiry = d.get('expiryDate', '')
            
            total_cups += qty
            if date_utils.is_expired(expiry):
                total_expired += qty
            else:
                total_active_deposits += qty

    html = f"""
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; text-align: center;">
        <div style="padding: 20px; background: #eff6ff; border-radius: 12px; border: 1px solid #bfdbfe;">
            <div style="font-size: 40px;">👥</div>
            <div style="font-size: 24px; font-weight: bold; color: #1e40af;">{total_users}</div>
            <div style="color: #60a5fa;">總用戶數</div>
        </div>
        <div style="padding: 20px; background: #fff7ed; border-radius: 12px; border: 1px solid #fed7aa;">
            <div style="font-size: 40px;">☕</div>
            <div style="font-size: 24px; font-weight: bold; color: #9a3412;">{total_cups}</div>
            <div style="color: #fb923c;">系統總杯數</div>
        </div>
        <div style="padding: 20px; background: #f0fdf4; border-radius: 12px; border: 1px solid #bbf7d0;">
            <div style="font-size: 40px;">✅</div>
            <div style="font-size: 24px; font-weight: bold; color: #166534;">{total_active_deposits}</div>
            <div style="color: #4ade80;">有效庫存</div>
        </div>
        <div style="padding: 20px; background: #fef2f2; border-radius: 12px; border: 1px solid #fecaca;">
            <div style="font-size: 40px;">🗑️</div>
            <div style="font-size: 24px; font-weight: bold; color: #991b1b;">{total_expired}</div>
            <div style="color: #f87171;">已過期總數</div>
        </div>
    </div>
    """
    return html

def get_users_list_dataframe():
    """取得用戶列表 DataFrame"""
    users = storage.load_users()
    data = []
    for username, info in users.items():
        # 簡單計算該用戶的記錄數
        deposits = storage.load_deposits(username)
        record_count = len(deposits)
        data.append([username, info.get('created_at', '未知'), record_count])
    
    return data

def delete_user(admin_user, target_username):
    """管理員刪除用戶"""
    if not is_admin(admin_user):
        return "❌ 權限不足", get_users_list_dataframe()
    
    if target_username in settings.ADMIN_USERS:
        return "❌ 不能刪除管理員帳號", get_users_list_dataframe()
    
    if storage.delete_user_from_db(target_username):
        return f"✅ 已刪除用戶：{target_username}", get_users_list_dataframe()
    else:
        return f"❌ 刪除失敗：{target_username}", get_users_list_dataframe()

def view_user_deposits(target_username):
    """查看特定用戶的寄杯（複用 components 的顯示邏輯）"""
    from ..ui import components
    
    if not target_username:
        return "請輸入用戶名稱", ""
    
    users = storage.load_users()
    if target_username not in users:
        return "❌ 找不到該用戶", ""
        
    deposits_html = components.get_deposits_display(target_username)
    stats_html = components.get_statistics(target_username)
    
    return deposits_html, stats_html