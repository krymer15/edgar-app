import os

def build_raw_filepath(subpath: str) -> str:
    """
    Builds a full filepath under the /data/raw/ directory.
    """
    subpath_normalized = os.path.normpath(subpath)
    return os.path.join("data", "raw", subpath_normalized)

def build_processed_filepath(subpath: str) -> str:
    """
    Builds a full filepath under the /data/processed/ directory.
    """
    subpath_normalized = os.path.normpath(subpath)
    return os.path.join("data", "processed", subpath_normalized)
