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

    
    ### Code below added for /config/form_type_rules.yaml functionality. Also see `config/app_config.yaml` ###
    '''
    Usage example below:
        from utils.config_loader import ConfigLoader

        form_rules = ConfigLoader.load_form_type_rules()
        allowed_forms = ConfigLoader.extract_filing_forms(form_rules, include_optional=True)
    '''

    @staticmethod
    def load_form_type_rules(config_filename: str = "config/form_type_rules.yaml") -> dict:
        project_root = get_project_root()
        config_path = os.path.join(project_root, config_filename)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Form type rules not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        return config.get("form_type_rules", {})

    @staticmethod
    def extract_filing_forms(form_type_rules: dict, include_optional: bool = False) -> set:
        def flatten(d):
            for v in d.values():
                if isinstance(v, dict):
                    yield from flatten(v)
                elif isinstance(v, list):
                    yield from v

        allowed = set(flatten(form_type_rules.get("core", {})))
        if include_optional:
            allowed |= set(flatten(form_type_rules.get("optional", {})))
        return allowed
