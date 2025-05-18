# Form Type Rules

This file defines a comprehensive database of SEC form types used primarily for validation and categorization.

## Overview

The `form_type_rules.yaml` file contains a well-structured catalog of SEC form types organized by category and relevance. It serves multiple important purposes:

1. **Comprehensive Validation**: Provides a reference database of valid SEC form types
2. **Form Type Categorization**: Organizes forms by business purpose (registration, reporting, ownership, etc.)
3. **Normalization**: Supports handling variations in form type formatting (e.g., "10-K", "10K", "10k")
4. **Amendment Support**: Automatically includes amendment variants (e.g., 10-K/A)

## Active Usage

This file is actively used by the `FormTypeValidator` class to:

1. **Validate user-provided form types** in CLI scripts and application code
2. **Normalize variations** of the same form type
3. **Enable flexible validation** of form types with different formatting
4. **Support amendment handling** for all form types

The validation is particularly important for CLI scripts that accept user-provided form types, ensuring only valid SEC forms are processed.

## Relationship with app_config.yaml

While `form_type_rules.yaml` provides the comprehensive form database for validation, the actual filtering defaults come from `app_config.yaml`:

- **form_type_rules.yaml**: Used by `FormTypeValidator` for form validation, normalization, and categorization
- **app_config.yaml**: Contains `crawler_idx.include_forms_default` list for default form filtering

## Structure

The file is organized hierarchically:

```yaml
include_amendments: true  # Whether to include amendments of listed forms (e.g., 10-K/A)

form_type_rules:
  core:  # Primary form types of high interest
    registration:  # IPOs, follow-ons, shelf registrations
      - "S-1"
      - "424B1"
      # More forms...
    
    ownership:  # Insider and beneficial ownership forms
      insider:
        - "3"
        - "4"
        - "5"
      beneficial:
        - "13D"
        - "13G"
        # More forms...
```

## Integration in Code

The `FormTypeValidator` class uses this configuration through the `ConfigLoader`:

```python
from utils.form_type_validator import FormTypeValidator
from config.config_loader import ConfigLoader

# Load form type rules
rules = ConfigLoader.load_form_type_rules()

# Validate user-provided form types
user_forms = ["10-K", "10k", "S-1/A"]
validated_forms = FormTypeValidator.get_validated_form_types(user_forms)

# Check if a specific form is valid
is_valid = FormTypeValidator.is_valid_form_type("DEFA14A")
```

## Updating

When adding new form types:

1. Add them to the appropriate category
2. Use the canonical SEC form type code (e.g., "10-K" not "10K")
3. Maintain the hierarchical structure
4. Set include_amendments: true if you want to support amendment variants