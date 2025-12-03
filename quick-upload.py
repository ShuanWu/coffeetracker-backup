# quick_upload.py
from huggingface_hub import HfApi

api = HfApi()

# 上傳整個資料夾
api.upload_folder(
    folder_path=".",
    repo_id="ShuanWu/CoffeeCount",
    repo_type="space",
    ignore_patterns=[
        ".git/*",
        "__pycache__/*",
        "*.pyc",
        "data/*",
        "data_backup/*",
        "*.backup",
        ".env"
    ],
    commit_message="重構：模組化架構"
)

print("✅ 上傳完成！")