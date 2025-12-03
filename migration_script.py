import os
import json
from huggingface_hub import hf_hub_download, upload_file, HfApi

# 設定
OLD_SPACE_ID = "你的舊Space_ID" # 例如 user/coffee-app
NEW_DATASET_ID = "你的新Dataset_ID" # 例如 user/coffee-data
HF_TOKEN = "你的HF_TOKEN" # 必須有寫入權限

def migrate():
    print("🚀 開始遷移資料...")
    api = HfApi(token=HF_TOKEN)
    
    # 1. 建立臨時目錄
    os.makedirs("migration_temp/user_records", exist_ok=True)
    
    # 2. 下載舊資料 (users.json)
    try:
        print("下載 users.json...")
        hf_hub_download(repo_id=OLD_SPACE_ID, filename="users.json", repo_type="space", local_dir="migration_temp", token=HF_TOKEN)
        
        # 讀取用戶列表以知道要下載哪些用戶資料
        with open("migration_temp/users.json", "r", encoding="utf-8") as f:
            users = json.load(f)
            
        # 3. 下載每個用戶的資料
        for username in users.keys():
            old_filename = f"user_data/{username}.json" # 舊路徑
            new_filename = f"user_records/{username}.json" # 新結構
            
            try:
                print(f"處理用戶: {username}")
                # 下載舊檔案
                path = hf_hub_download(repo_id=OLD_SPACE_ID, filename=old_filename, repo_type="space", token=HF_TOKEN)
                
                # 讀取並存入新結構
                with open(path, "r", encoding="utf-8") as f_data:
                    user_data = json.load(f_data)
                
                with open(f"migration_temp/{new_filename}", "w", encoding="utf-8") as f_out:
                    json.dump(user_data, f_out, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                print(f"⚠️ 找不到用戶 {username} 的資料或是路徑不同: {e}")

        # 4. 上傳到新的 Dataset
        print("📤 上傳資料到新的 Dataset...")
        api.upload_folder(
            folder_path="migration_temp",
            repo_id=NEW_DATASET_ID,
            repo_type="dataset",
            path_in_repo="data" # 對應 config.py 的 DATA_DIR
        )
        print("✅ 遷移完成！")
        
    except Exception as e:
        print(f"❌ 遷移失敗: {e}")

if __name__ == "__main__":
    migrate()