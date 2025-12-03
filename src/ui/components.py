# src/ui/components.py

import gradio as gr
from ..config import ui_config
from ..services import storage
from ..utils import date_utils

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
    
    deposits = storage.load_deposits(username)
    
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
        expired = date_utils.is_expired(deposit['expiryDate'])
        expiring_today = date_utils.is_expiring_today(deposit['expiryDate'])
        expiring_soon = date_utils.is_expiring_soon(deposit['expiryDate']) and not expired and not expiring_today
        
        # 根據狀態設置樣式
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
        
        redeem_info = ui_config.REDEEM_LINKS.get(deposit['redeemMethod'], {
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
                    <div style="margin-bottom: 6px;">🏪 <strong>商店：</strong>{deposit['store']}</div>
                    <div style="margin-bottom: 6px;">📦 <strong>兌換途徑：</strong>{deposit['redeemMethod']}</div>
                    <div>📅 <strong>到期日：</strong>{date_utils.format_date(deposit['expiryDate'])} 
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
    
    deposits = storage.load_deposits(username)
    
    if not deposits:
        return ""
    
    total_cups = sum(d['quantity'] for d in deposits)
    valid_records = len([d for d in deposits if not date_utils.is_expired(d['expiryDate'])])
    expired_records = len([d for d in deposits if date_utils.is_expired(d['expiryDate'])])
    expiring_today = len([d for d in deposits if date_utils.is_expiring_today(d['expiryDate'])])
    expiring_soon = len([d for d in deposits if date_utils.is_expiring_soon(d['expiryDate']) and not date_utils.is_expired(d['expiryDate']) and not date_utils.is_expiring_today(d['expiryDate'])])
    
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