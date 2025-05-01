import shutil
import os

folders_to_delete = [
    "test_data",  # <-- remove this instead of /raw or /processed
]

for folder in folders_to_delete:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"✅ Deleted: {folder}")
    else:
        print(f"ℹ️ Skipped (not found): {folder}")
