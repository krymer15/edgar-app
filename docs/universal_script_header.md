import sys
import os

# ✅ Ensure project root is in sys.path — supports running from /scripts or /tests
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.insert(0, project_root)  # insert(0) gives it import priority
