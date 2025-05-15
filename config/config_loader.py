# utils/config_loader.py

import yaml
import os
from dotenv import load_dotenv  
from utils.get_project_root import get_project_root
from utils.report_logger import log_warn
import logging

class ConfigLoader:
    @staticmethod
    def load_config(config_filename: str = "config/app_config.yaml") -> dict:
        load_dotenv()  # ✅ Ensures .env is loaded before expanding vars
        project_root = get_project_root()
        
        # Check for env override
        config_filename = config_filename or os.environ.get("APP_CONFIG", "config/app_config.yaml")
        config_path = os.path.join(project_root, config_filename)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as file:
            raw = file.read()

        expanded = os.path.expandvars(raw)
        config = yaml.safe_load(expanded)

        return config

    @staticmethod
    def get_default_include_forms() -> list:
        """
        Returns the default list of form types to include from the config.
        This is a convenience method to use across the codebase.
        """
        config = ConfigLoader.load_config()
        return config.get("crawler_idx", {}).get("include_forms_default", [])
    
    @staticmethod
    def load_form_type_rules(config_filename: str = "config/form_type_rules.yaml") -> dict:
        """
        Load form type rules from yaml file.
        
        Args:
            config_filename: Path to form_type_rules.yaml 
            
        Returns:
            Dict containing form type rules
        """
        project_root = get_project_root()
        config_path = os.path.join(project_root, config_filename)

        if not os.path.exists(config_path):
            log_warn(f"Form type rules not found: {config_path}")
            return {"form_type_rules": {}, "include_amendments": True}

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                raw = f.read()
                
            expanded = os.path.expandvars(raw)
            config = yaml.safe_load(expanded)
            
            return config or {"form_type_rules": {}}
            
        except Exception as e:
            log_warn(f"Error loading form type rules: {e}")
            return {"form_type_rules": {}, "include_amendments": True}

    @staticmethod
    def extract_filing_forms(form_type_rules: dict, include_optional: bool = False) -> set:
        """
        Extract all form types from the form_type_rules structure.
        
        Args:
            form_type_rules: Dict containing form type rules
            include_optional: Whether to include optional form types
            
        Returns:
            Set of all form types
        """
        def flatten(d):
            if isinstance(d, list):
                return d
                
            result = []
            for v in d.values():
                if isinstance(v, dict):
                    result.extend(flatten(v))
                elif isinstance(v, list):
                    result.extend(v)
            return result

        core = form_type_rules.get("form_type_rules", {}).get("core", {})
        allowed = set(flatten(core))
        
        if include_optional:
            optional = form_type_rules.get("form_type_rules", {}).get("optional", {})
            allowed |= set(flatten(optional))
            
        return allowed
        
    @staticmethod
    def get_all_form_types(include_optional: bool = False) -> set:
        """
        Convenience method to get all form types from rules.
        
        Args:
            include_optional: Whether to include optional form types
            
        Returns:
            Set of all form types
        """
        rules = ConfigLoader.load_form_type_rules()
        return ConfigLoader.extract_filing_forms(rules, include_optional)