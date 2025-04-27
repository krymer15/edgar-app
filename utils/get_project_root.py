# get_project_root.py

import os

def get_project_root() -> str:
    """
    Returns the absolute path to the root of the project (edgar-app/).
    Assumes this file lives somewhere inside the edgar-app project tree.
    """
    current_path = os.path.abspath(__file__)
    project_root = os.path.abspath(os.path.join(current_path, "..", ".."))
    return project_root
