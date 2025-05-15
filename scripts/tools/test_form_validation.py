# scripts/tools/test_form_validation.py

"""
Run this script to test form type validation and normalization using the form_type_rules.yaml.

Usage:
    python scripts/tools/test_form_validation.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from utils.form_type_validator import FormTypeValidator
from config.config_loader import ConfigLoader
from utils.report_logger import log_info


def test_form_validation():
    """Test form type validation against rules from form_type_rules.yaml"""
    test_groups = [
        # Common forms
        ["10-K", "10-Q", "8-K", "S-1"],
        # Variations
        ["10-K/A", "8-K/A", "S-1/A"],
        # Proxy forms
        ["DEF 14A", "DEFA14A", "PRE 14A", "DEFM14A"],
        # Mix of valid and invalid
        ["10-K", "XYZ", "ABC"],
        # Tender offers
        ["SC TO-I", "SC TO-T"],
        # Empty list
        []
    ]
    
    log_info("=== Form Validation Test ===")
    
    for group in test_groups:
        validated = FormTypeValidator.validate_form_types(group)
        log_info(f"Group: {group}")
        log_info(f"Validated: {validated}")
        log_info("")
    
    log_info("\n")


def test_load_form_rules():
    """Test loading rules from form_type_rules.yaml"""
    log_info("=== Form Rules Loading Test ===")
    
    rules = ConfigLoader.load_form_type_rules()
    
    # Print basic info
    include_amendments = rules.get("include_amendments", False)
    log_info(f"Include amendments: {include_amendments}")
    
    # Extract form types
    all_forms = ConfigLoader.extract_filing_forms(rules)
    log_info(f"Loaded {len(all_forms)} form types from rules")
    log_info(f"Sample forms: {list(all_forms)[:10]}")
    
    # Test getting all variations
    FormTypeValidator._load_form_type_rules()  # Force loading rules
    all_known_forms = FormTypeValidator.get_all_form_types()
    log_info(f"Total forms supported: {len(all_known_forms)}")
    
    # Show some important forms and whether they're valid
    important_forms = ["10-K", "10-K/A", "DEF 14A", "DEFA14A", "PRE 14A", "S-1/A"]
    log_info("Validation status for important forms:")
    for form in important_forms:
        is_valid = FormTypeValidator.is_valid_form_type(form)
        log_info(f"  '{form}' is valid: {is_valid}")
    
    log_info("\n")


def test_code_preservation():
    """Test that original form codes are preserved"""
    test_forms = {
        "10-K": "10-K",
        "10K": "10K",
        "DEFA14A": "DEFA14A",
        "S-1/A": "S-1/A",
        "s-1": "s-1"  # Lowercase should be preserved
    }
    
    log_info("=== Form Code Preservation Test ===")
    
    for original, expected in test_forms.items():
        result = FormTypeValidator.get_validated_form_types([original])[0]
        preserved = result == expected
        log_info(f"Original: '{original}' → Result: '{result}' → Preserved: {preserved}")
    
    log_info("\n")


def test_cli_scenario():
    """Test typical CLI usage scenario"""
    log_info("=== CLI Usage Scenario Test ===")
    
    # Simulate CLI arguments
    cli_args = ["10K", "8k", "DEFA14A", "s-1/a"]
    
    # Process through validator
    validated_forms = FormTypeValidator.get_validated_form_types(cli_args)
    
    log_info(f"CLI args: {cli_args}")
    log_info(f"Validated forms: {validated_forms}")
    
    # Test fallback to defaults
    with_defaults = FormTypeValidator.get_validated_form_types(None)
    log_info(f"Default forms: {with_defaults}")
    
    log_info("\n")


if __name__ == "__main__":
    log_info("🔍 Form Type Validation Test")
    log_info("===============================")
    
    # Run all tests
    test_load_form_rules()
    test_form_validation()
    test_code_preservation()
    test_cli_scenario()
    
    log_info("✅ Tests completed")