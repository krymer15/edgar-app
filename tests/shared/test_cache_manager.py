
import os, sys

# point to the edgar-app root and add it to sys.path
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
    )
)

import shutil
import pytest
from utils.cache_manager import clear_sgml_cache, get_cache_root

@pytest.fixture
def setup_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("utils.path_manager.STORAGE_CONFIG", {"base_data_path": str(tmp_path)})
    cache_root = get_cache_root()
    os.makedirs(os.path.join(cache_root, "2025", "0000000000"), exist_ok=True)
    file1 = os.path.join(cache_root, "2025", "0000000000", "20250101000001.txt")
    file2 = os.path.join(cache_root, "2025", "0000000000", "20250101000002.txt")
    for path in [file1, file2]:
        with open(path, "w") as f:
            f.write("test")
    return cache_root

def test_clear_all_files(setup_cache):
    deleted = clear_sgml_cache()
    assert deleted == 2

    # Check all .txt files are gone, not the root folder
    remaining_files = [
        f for root, dirs, files in os.walk(setup_cache) for f in files if f.endswith(".txt")
    ]
    assert len(remaining_files) == 0

