import sys
import os

# Automatically add the edgar-app root directory to sys.path
if os.getcwd().endswith("notebooks"):
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))
