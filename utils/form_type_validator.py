# utils/form_type_validator.py

from typing import List, Set, Optional, Dict
from utils.report_logger import log_info, log_warn
from config.config_loader import ConfigLoader

class FormTypeValidator:
    """
    Validates SEC form types and provides standardized form type handling.
    Uses form_type_rules.yaml for validation and normalization.
    """
    
    # Flag to load rules once and cache
    _rules_loaded = False
    _known_form_types = set()  # All known valid form types
    _validation_map = {}  # Maps normalized forms to original forms for validation
    
    @classmethod
    def _load_form_type_rules(cls):
        """Load form types from the form_type_rules.yaml file"""
        if cls._rules_loaded:
            return
            
        try:
            # Load form type rules
            rules = ConfigLoader.load_form_type_rules()
            include_amendments = rules.get("include_amendments", True)
            
            # Extract form types
            base_forms = set()
            
            # Process core form types
            core_rules = rules.get("form_type_rules", {}).get("core", {})
            
            def extract_forms(section):
                forms = []
                if isinstance(section, list):
                    forms.extend(section)
                elif isinstance(section, dict):
                    for k, v in section.items():
                        forms.extend(extract_forms(v))
                return forms
            
            # Extract all forms from all sections
            for section_name, section in core_rules.items():
                section_forms = extract_forms(section)
                base_forms.update(section_forms)
            
            # Add some common forms explicitly if not already included
            common_forms = {
                "10-K", "10-Q", "8-K", "S-1", "3", "4", "5", "13D", "13G", 
                "20-F", "6-K", "13F-HR", "424B1", "S-4", "DEF 14A", "PRE 14A", 
                "SC TO-I", "SC TO-T", "DEFA14A", "DEFM14A", "DEFR14A", "PRE14A"
            }
            base_forms.update(common_forms)
            
            # Initialize known form types with base forms
            known_forms = set(base_forms)
            
            # Add amendments if enabled
            if include_amendments:
                for form in base_forms:
                    known_forms.add(f"{form}/A")
                    
                    # For certain form types, include other common variations
                    if form.startswith("DEF ") or form.startswith("PRE "):
                        # Remove space for variant (e.g., "DEF 14A" -> "DEFA14A")
                        if " " in form:
                            parts = form.split(" ", 1)
                            no_space_variant = f"{parts[0]}{parts[1]}"
                            known_forms.add(no_space_variant)
            
            # Special case for SC TO series
            known_forms.update(["SC TO-I", "SC TO-T", "SC 13D", "SC 13G"])
            
            # Build validation map for more flexible validation
            validation_map = {}
            
            # Add all known forms to validation map
            for form in known_forms:
                # Normalized form (uppercase, no trailing whitespace)
                normalized = form.strip().upper()
                
                # Add to validation map
                validation_map[normalized] = form
                
                # For forms with hyphens, add variant without hyphen
                if "-" in normalized:
                    no_hyphen = normalized.replace("-", "")
                    validation_map[no_hyphen] = form
                
                # For forms with spaces, add variant without space
                if " " in normalized:
                    no_space = normalized.replace(" ", "")
                    validation_map[no_space] = form
            
            # Store in class variables
            cls._known_form_types = known_forms
            cls._validation_map = validation_map
            cls._rules_loaded = True
            
            log_info(f"[FORM] Loaded {len(cls._known_form_types)} form types from rules")
            
        except Exception as e:
            log_warn(f"[FORM] Error loading form type rules: {e}")
            # Fallback to basic common forms if rules file can't be loaded
            fallback_forms = {
                "10-K", "10-Q", "8-K", "S-1", "3", "4", "5", "13D", "13G", 
                "20-F", "6-K", "13F-HR", "424B1", "S-4", "DEF 14A", "PRE 14A", 
                "SC TO-I", "SC TO-T", "DEFA14A", "DEFM14A", "DEFR14A", "PRE14A",
                # Amendments
                "10-K/A", "10-Q/A", "8-K/A", "S-1/A", "S-4/A",
            }
            
            # Build basic validation map
            validation_map = {}
            for form in fallback_forms:
                normalized = form.strip().upper()
                validation_map[normalized] = form
                
                # For forms with hyphens, add variant without hyphen
                if "-" in normalized:
                    no_hyphen = normalized.replace("-", "")
                    validation_map[no_hyphen] = form
                
                # For forms with spaces, add variant without space
                if " " in normalized:
                    no_space = normalized.replace(" ", "")
                    validation_map[no_space] = form
            
            cls._known_form_types = fallback_forms
            cls._validation_map = validation_map
            cls._rules_loaded = True
    
    @classmethod
    def validate_form_types(cls, form_types: Optional[List[str]]) -> List[str]:
        """
        Validates a list of form types, warning about any unknown types.
        IMPORTANT: Returns the original form types without normalization.
        
        Args:
            form_types: List of form types to validate
            
        Returns:
            The original list of form types (for function chaining)
        """
        if not form_types:
            return []
            
        # Ensure rules are loaded
        cls._load_form_type_rules()
        
        # Check each form against known forms
        unknown_forms = []
        for form in form_types:
            # Get normalized form for validation (but don't change the original)
            normalized = cls._get_normalized_for_validation(form)
            
            # Check if it's a known form
            if normalized not in cls._validation_map:
                # Try with common patterns for flexibility
                if not cls._is_likely_valid_form(normalized):
                    unknown_forms.append(form)
        
        if unknown_forms:
            log_warn(f"[WARN] Potentially unknown SEC form types: {unknown_forms}")
            log_warn(f"[WARN] Will still include these forms, but verify they are valid SEC form types")
            
        return form_types
    
    @classmethod
    def _get_normalized_for_validation(cls, form: str) -> str:
        """
        Normalize a form type for validation purposes only.
        This is internal and doesn't change what's returned to users.
        """
        if not form:
            return ""
            
        # Remove spaces and convert to uppercase
        return form.strip().upper()
    
    @classmethod
    def _is_likely_valid_form(cls, normalized_form: str) -> bool:
        """
        Check if a form is likely valid based on common patterns.
        This provides more flexible validation for variations.
        """
        # Common form patterns
        if normalized_form.endswith('/A'):  # Amendment
            base_form = normalized_form[:-2]
            return base_form in cls._validation_map
            
        # Common SEC form number patterns
        common_patterns = [
            "10-", "8-", "6-", "S-", "F-",  # Registration and reports
            "13", "14", "15", "16", "17",   # Beneficial ownership and proxies
            "424",                         # Prospectus
            "3", "4", "5",                 # Insider trading
            "SC TO", "SC 13"               # Tender offers
        ]
        
        # Check if form starts with a common pattern
        for pattern in common_patterns:
            if normalized_form.startswith(pattern):
                return True
                
        # Known prefixes for proxy forms
        proxy_prefixes = ["DEF", "DEFA", "DEFM", "DEFR", "PRE", "PREM"]
        for prefix in proxy_prefixes:
            if normalized_form.startswith(prefix) and "14" in normalized_form:
                return True
                
        return False
    
    @classmethod
    def get_validated_form_types(cls, form_types: Optional[List[str]]) -> List[str]:
        """
        Validates form types but maintains original form codes.
        If form_types is None, returns default form types from config.
        
        Args:
            form_types: List of form types to process
            
        Returns:
            List of validated form types (preserving original form codes)
        """
        if form_types is None:
            return ConfigLoader.get_default_include_forms()
            
        return cls.validate_form_types(form_types)
    
    @classmethod
    def get_all_form_types(cls) -> Set[str]:
        """
        Returns the set of all known form types.
        Useful for documentation or debugging.
        
        Returns:
            Set of all known form types
        """
        cls._load_form_type_rules()
        return cls._known_form_types
        
    @classmethod
    def is_valid_form_type(cls, form_type: str) -> bool:
        """
        Check if a specific form type is valid.
        
        Args:
            form_type: The form type to check
            
        Returns:
            True if valid, False otherwise
        """
        cls._load_form_type_rules()
        
        # Get normalized form for validation
        normalized = cls._get_normalized_for_validation(form_type)
        
        # Check if it's in validation map
        if normalized in cls._validation_map:
            return True
            
        # Try pattern matching for more flexibility
        return cls._is_likely_valid_form(normalized)