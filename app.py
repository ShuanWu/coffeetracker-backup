# app.py
from frontend.main import launch_app
from backend import database # 確保資料庫初始化 (CommitScheduler 啟動)

if __name__ == "__main__":
    # 確保資料夾存在
    import os
    os.makedirs('data', exist_ok=True)
    
    app = launch_app()
    app.launch()