# Tools Scripts

This directory contains utility scripts for debugging, testing, and maintenance tasks in the EDGAR data processing system. These tools are not part of the primary ingestion pipeline but provide valuable debugging and configuration validation capabilities.

## Available Tools

### Form Type Validation Tools

These scripts help debug and test the form type validation and filtering functionality:

#### debug_form_filtering.py

This script troubleshoots how form type filtering is applied to database queries:

- Connects to the database and displays form type distribution for a specific date
- Simulates the same SQL filtering that would be applied with `--include_forms` in pipeline scripts
- Verifies that filtered results match expectations

```bash
# Show form type distribution for a specific date
python -m scripts.tools.debug_form_filtering --date 2025-05-12

# Simulate filtering with specific form types
python -m scripts.tools.debug_form_filtering --date 2025-05-12 --include_forms 10-K 8-K
```

#### debug_form_validation.py

This script tests form type validation for potentially problematic form types:

- Focuses on amendments and proxy forms, which have special handling
- Verifies that original form codes are preserved during validation
- Tests problem forms like "10-K/A", "8-K/A", "DEF 14A", etc.
- Ensures flexible validation accepts common variations like "10K" and "10-K"

```bash
# Run all form validation tests
python -m scripts.tools.debug_form_validation
```

#### test_form_validation.py

This script provides comprehensive testing of the form type validation system:

- Tests form validation against rules from `form_type_rules.yaml`
- Verifies rule loading and extraction from configuration
- Tests preservation of original form codes in different scenarios
- Simulates typical CLI usage with validation and normalization

```bash
# Run all form validation tests
python -m scripts.tools.test_form_validation
```

### Backfill Scripts

#### backfill_xml_exhibits.py

This utility script helps with backfilling XML metadata for existing exhibits:

- Scans the `exhibit_metadata` table for XML documents 
- Logs them to the `xml_metadata` table to track XML documents
- Targets specific form types (3, 4, 5, 10-K, 10-Q, 8-K)
- Is archived and references the archived `xml_backfill_utils.py` module

```bash
# Run XML backfill
python -m scripts.tools.backfill_xml_exhibits
```

> **Note**: This script depends on archived modules and may require updates before use.

## Relationship with Other Scripts

These tools have the following relationships with the main pipeline scripts:

1. **Form Validation Integration**: The form type validation tools test the `FormTypeValidator` class, which is used in `scripts/crawler_idx/run_daily_pipeline_ingest.py` to validate and normalize form types provided via the `--include_forms` parameter.

2. **Configuration Testing**: These tools test the validation rules in `config/form_type_rules.yaml`, which define which form types are considered valid and how they should be normalized.

3. **Diagnostic Purpose**: Unlike the main pipeline scripts that directly process SEC data, these scripts are primarily for debugging configuration, validation, and database interactions.

## When to Use

- **During Development**: Use these tools when implementing changes to form type validation or filtering
- **For Troubleshooting**: When encountering unexpected behavior in form type filtering
- **After Configuration Changes**: After modifying `form_type_rules.yaml`, run these tools to verify the changes work as expected
- **For Data Exploration**: Use `debug_form_filtering.py` to explore form type distribution in the database