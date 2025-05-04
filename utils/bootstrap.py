# utils/bootstrap.py

import sys
import os
from utils.get_project_root import get_project_root

def add_project_root_to_sys_path():
    """
    Ensures the project root is included in sys.path for all relative imports.
    Use this at the top of scripts or test files.
    """
    project_root = get_project_root()
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


'''
Add the code below to scripts with `ModuleNoFoundError`:

# At the top of test_single_sgml_orchestrator.py, test_batch_sgml_ingestion_orchestrator.py, etc.

from utils.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

'''