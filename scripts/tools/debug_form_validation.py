# scripts/tools/debug_form_validation.py

"""
Run this script to debug form type validation for specific problematic forms.
It focuses on testing amendments and proxy forms while preserving original codes.

Usage:
    python scripts/tools/debug_form_validation.py
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from utils.form_type_validator import FormTypeValidator
from utils.report_logger import log_info, log_warn


def test_original_code_preservation():
    """Test that original form codes are preserved"""
    test_cases = [
        # Original form -> Expected after validation
        ("10-K", "10-K"),
        ("10K", "10K"),  # Should remain as 10K, not normalized to 10-K
        ("DEFA14A", "DEFA14A"),  # Should remain as DEFA14A, not normalized to DEF 14A
        ("DEF 14A", "DEF 14A"),
        ("S-1/A", "S-1/A"),
        ("s-1/a", "s-1/a"),  # Should preserve case
    ]
    
    log_info("== Testing Original Code Preservation ==")
    
    for original, expected in test_cases:
        # Run the form through validation
        validated = FormTypeValidator.get_validated_form_types([original])
        result = validated[0] if validated else ""
        
        preserved = result == original
        log_info(f"Original: '{original}' → After validation: '{result}' → Preserved: {preserved}")


def test_problem_forms():
    """Test the forms that were flagged as problematic"""
    problem_forms = [
        # Amendments
        "10-K/A", "8-K/A", "S-1/A",
        # Proxy forms
        "PRE 14A", "DEFA14A", "DEFM14A", "DEFR14A", "PRE14A",
        # Tender offers
        "SC TO-I", "SC TO-T"
    ]
    
    # Force load rules
    FormTypeValidator._load_form_type_rules()
    
    log_info("\n== Testing Individual Problem Forms ==")
    for form in problem_forms:
        is_valid = FormTypeValidator.is_valid_form_type(form)
        
        log_info(f"Form: '{form}' → Valid: {is_valid}")
    
    # Test validation in groups
    log_info("\n== Testing Problem Form Groups ==")
    groups = [
        ["10-K/A", "8-K/A", "S-1/A"],
        ["DEF 14A", "DEFA14A", "PRE 14A", "DEFM14A"],
        ["SC TO-I", "SC TO-T"]
    ]
    
    for group in groups:
        log_info(f"Group: {group}")
        validator_result = FormTypeValidator.validate_form_types(group)
        
        # Check that original forms are preserved
        for i, form in enumerate(group):
            if i < len(validator_result):
                preserved = validator_result[i] == form
                log_info(f"  '{form}' → preserved: {preserved}")
        
        # Check for warnings (we shouldn't have any for these valid forms)
        log_info(f"  Validation passed without warnings: {len(validator_result) == len(group)}")
        log_info("")


def test_flexible_validation():
    """Test that validation is flexible with common variations"""
    variations = [
        # Common variations that should all be valid
        "10-K", "10K", "10-k", "10k",
        "8-K", "8K", "8-k", "8k",
        "DEF 14A", "DEF14A", "DEFA14A", 
        "PRE 14A", "PRE14A",
        "13F-HR", "13FHR"
    ]
    
    log_info("\n== Testing Flexible Validation ==")
    for form in variations:
        is_valid = FormTypeValidator.is_valid_form_type(form)
        log_info(f"Form variation: '{form}' → Valid: {is_valid}")
    
    # Test some invalid forms for comparison
    invalid_forms = ["XYZ", "ABC", "NOT-A-FORM"]
    for form in invalid_forms:
        is_valid = FormTypeValidator.is_valid_form_type(form)
        log_info(f"Invalid form: '{form}' → Valid: {is_valid} (expected: False)")


def test_all_forms_coverage():
    """Check if all forms in the validator are covered"""
    # Get all forms
    all_forms = FormTypeValidator.get_all_form_types()
    log_info(f"\n== Total forms supported: {len(all_forms)} ==")
    
    # Test a sample of important forms
    important_forms = [
        "10-K", "10-K/A", "10-Q", "10-Q/A", "8-K", "8-K/A", 
        "S-1", "S-1/A", "S-3", "S-4", 
        "3", "4", "5",
        "13D", "13G", "13F-HR",
        "DEF 14A", "DEFA14A", "PRE 14A", "PRE14A", "DEFM14A",
        "SC TO-I", "SC TO-T",
        "424B1", "424B3", "424B4", "424B5"
    ]
    
    log_info("\n== Testing Important Form Coverage ==")
    missing_forms = []
    for form in important_forms:
        if not FormTypeValidator.is_valid_form_type(form):
            missing_forms.append(form)
            
    if missing_forms:
        log_warn(f"Missing important forms: {missing_forms}")
    else:
        log_info("All important forms are covered ✅")


if __name__ == "__main__":
    log_info("🔍 Form Type Validation Debug")
    log_info("===============================")
    
    # Run tests
    test_original_code_preservation()
    test_problem_forms()
    test_flexible_validation()
    test_all_forms_coverage()
    
    log_info("\n✅ Debug tests completed")