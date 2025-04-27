# utils/config_loader.py

import yaml
import os

from utils.get_project_root import get_project_root

class ConfigLoader:
    @staticmethod
    def load_config(config_filename: str = "config/app_config.yaml") -> dict:
        project_root = get_project_root()
        config_path = os.path.join(project_root, config_filename)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        return config
