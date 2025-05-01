# utils/config_loader.py

import yaml
import os
from dotenv import load_dotenv  # ✅ Add this
from utils.get_project_root import get_project_root

class ConfigLoader:
    @staticmethod
    def load_config(config_filename: str = "config/app_config.yaml") -> dict:
        load_dotenv()  # ✅ Ensures .env is loaded before expanding vars

        project_root = get_project_root()
        config_path = os.path.join(project_root, config_filename)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as file:
            raw = file.read()

        expanded = os.path.expandvars(raw)
        config = yaml.safe_load(expanded)

        return config
