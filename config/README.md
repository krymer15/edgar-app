# Configuration

This directory contains configuration files and loaders for the EDGAR data processing system. These configurations control system behavior, define file paths, and specify form type filtering rules.

## Core Configuration Files

### app_config.yaml

The main configuration file for the application, controlling all aspects of the EDGAR data processing system.

```yaml
# Key sections in app_config.yaml
app:
  name: "Safe Harbor EDGAR AI Platform"
  environment: "development"  # Options: development, staging, production
  log_level: "DEBUG"  # Affects logging verbosity throughout the application

database:
  url: ${DATABASE_URL}  # Uses environment variable

storage:
  base_data_path: "./data/"  # Base path for all data storage
  # Additional storage path configuration...

sec_downloader:
  user_agent: "SafeHarborBot/1.0"  # Required for SEC API access
  request_delay_seconds: 0.2  # Rate limiting for SEC API

crawler_idx:
  # Default form types to process when no specific filter is provided
  include_forms_default: [
    "8-K", "10-K", "10-Q", "S-1", "3", "4", "5", "13D", "13G", "20-F", 
    "6-K", "13F-HR", "424B1", "S-4", "DEF 14A", "SC TO-I",
    "424B3", "424B4", "424B5"
  ]
```

#### Usage

```python
from config.config_loader import ConfigLoader

# Load the entire configuration
config = ConfigLoader.load_config()

# Access specific sections
log_level = config["app"]["log_level"]
user_agent = config["sec_downloader"]["user_agent"]
base_path = config["storage"]["base_data_path"]

# Get default form types
default_forms = config["crawler_idx"]["include_forms_default"]
```

### form_type_rules.yaml

This file contains a structured hierarchy of SEC form types organized by category. It supports advanced form type validation and normalization.

```yaml
include_amendments: true  # Auto-include "/A" amendments

form_type_rules:
  core:
    registration:  # IPOs, follow-ons, shelf registrations
      - "S-1"
      - "424B1"
      # More form types...
      
    ownership:  # Insider and beneficial ownership forms
      insider:
        - "3"
        - "4"
        - "5"
      beneficial:
        - "13D"
        - "13G"
        # More form types...
        
    # More categories...
```

#### Usage with FormTypeValidator

```python
from utils.form_type_validator import FormTypeValidator

# Validate and normalize form types
form_types = ["10-K", "10k", "S-1/A"]
validated = FormTypeValidator.get_validated_form_types(form_types)

# Check if a specific form type is valid
is_valid = FormTypeValidator.is_valid_form_type("8-K")
```

## Config Loader

### config_loader.py

Provides utility methods for loading and accessing configuration:

```python
# Load the main configuration
config = ConfigLoader.load_config()

# Load form type rules
rules = ConfigLoader.load_form_type_rules()

# Get default form types
default_forms = ConfigLoader.get_default_include_forms()
```

## Configuration Priority and Usage

### Form Type Filtering and Validation

The system uses a dual approach to form type handling:

1. **Form Type Filtering**: The `include_forms_default` list in `app_config.yaml` is used directly by the orchestrators and collectors when no specific form filter is provided. This defines which forms are processed by default.

2. **Form Type Validation**: The `FormTypeValidator` class uses the structured rules in `form_type_rules.yaml` for advanced form type validation, normalization, and categorization. This provides several benefits:
   - Comprehensive database of SEC forms organized by category (registration, ownership, governance, etc.)
   - Standardized normalization for form type variations (e.g., "10-K", "10K", "10k" are all recognized)
   - Support for amendment variants ("/A") 
   - Pattern-based validation for uncommon but valid form types

### File Roles and Interaction

- **app_config.yaml** → Provides the default list of forms to filter by when processing filings (`include_forms_default`)
- **form_type_rules.yaml** → Provides a comprehensive database of SEC forms with categorization and validation rules

The system typically follows this flow:
1. Scripts accept user-provided form types via CLI arguments
2. `FormTypeValidator` validates these against rules in `form_type_rules.yaml`
3. The validated forms are passed to orchestrators for filtering
4. If no forms are provided, the default list from `app_config.yaml` is used

### Command-Line Override

Scripts can override the default form types:

```bash
python -m scripts.crawler_idx.run_daily_pipeline_ingest --date 2025-05-12 --include-forms 10-K 8-K
```

This will validate the provided form types using `FormTypeValidator` before passing them to the pipeline.

### Storage Paths

The system uses the storage configuration in `app_config.yaml` for all file path generation:

```python
from utils.path_manager import build_raw_filepath

filepath = build_raw_filepath(
    year="2025",
    cik="0001234567",
    form_type="10-K",
    accession_or_subtype="000123456725000123",
    filename="filing.html"
)
```

The path structure follows the templates defined in `app_config.yaml`.

## Current vs. Deprecated Configuration

### Current

- **app_config.yaml**: Primary configuration file actively used throughout the codebase
- **form_type_rules.yaml**: Rich database of SEC forms used by FormTypeValidator
- **ConfigLoader.load_config()**: Main method for accessing configuration
- **ConfigLoader.load_form_type_rules()**: Method for loading form type rules
- **crawler_idx.include_forms_default**: Main source of form type filtering defaults
- **FormTypeValidator**: Active class for form type validation, normalization and categorization

### Deprecated/Limited Usage

The following sections in `app_config.yaml` appear to have limited or no active usage in the current codebase:

- **ingestion.use_form_type_rules**: Flag not actively used in the codebase
- **ingestion.use_rss_feed**: Not currently implemented
- **ingestion.use_daily_index**: Not actively referenced
- **ingestion.apply_global_filter**: Only used in archived code
- **ingestion.filing_forms_to_track**: Superseded by crawler_idx.include_forms_default

## Environment Variables

The configuration system supports environment variable substitution using the `${VAR_NAME}` syntax in YAML files. This is particularly useful for sensitive information like database credentials:

```yaml
database:
  url: ${DATABASE_URL}
```

You can set these variables in a `.env` file or in your environment.

## Testing Configuration

For testing, you can modify the storage paths:

```yaml
storage:
  base_data_path: "./test_data/"  # Change for testing
```

This will direct all file operations to a test directory rather than the production data path.