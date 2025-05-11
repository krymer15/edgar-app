import os
import shutil
from utils.path_manager import STORAGE_CONFIG

def get_cache_root() -> str:
    return os.path.join(STORAGE_CONFIG.get("base_data_path", "data/"), "cache_sgml")

def clear_sgml_cache(cik: str = None, year: str = None) -> int:
    """
    Deletes SGML cache files by optional cik or year.
    Returns count of deleted files.
    """
    cache_root = get_cache_root()
    deleted = 0

    if not os.path.exists(cache_root):
        return 0

    for root, dirs, files in os.walk(cache_root):
        for file in files:
            if not file.endswith(".txt"):
                continue
            path = os.path.join(root, file)

            if cik and cik not in path:
                continue
            if year and f"{os.sep}{year}{os.sep}" not in path:
                continue

            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                print(f"⚠️ Failed to delete {path}: {e}")

    return deleted
