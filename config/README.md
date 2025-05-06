# App Configuration File

## `app_config.yaml` file and parameters:
| Use Case        | `apply_global_filter` | Write to `daily_index_metadata` | Parse/write to `parsed_sgml_metadata` |
| --------------- | --------------------- | ------------------------------- | ------------------------------------- |
| Dev (test all)  | `false`               | ✅ All                           | ✅ Only filtered (with fix)            |
| Prod (targeted) | `true`                | ✅ Filtered                      | ✅ Filtered                            |

| Path    | Setting        | How                                      |
| ------- | -------------- | ---------------------------------------- |
| Dev CLI | `./test_data/` | Set `BASE_DATA_PATH=./test_data/` in CLI |
| Prod    | `./data/`      | Set via `.env`, defaults in config       |

# SEC Form Priority Configuration

This directory contains `form_priority.yaml`, a structured configuration of SEC filing types useful for financial ingestion pipelines. It maps each form to a category, data format, and analysis priority.

## Files

- `form_priority.yaml`: List of SEC forms, categorized by:
  - `Form`: The SEC form identifier (e.g., 10-K, Form 4)
  - `Category`: Logical grouping (e.g., Core Financial, Insider Activity)
  - `Data_Format`: Expected format (e.g., HTML, XML, XBRL)
  - `Priority`: High / Medium / Low — guides ingestion and parser focus
  - `Key_Use`: Primary use case for investment analysis

## Load the YAML (Python)

```python
import yaml
from pathlib import Path

def load_form_priority_config(filepath="config/form_priority.yaml"):
    with open(Path(filepath), "r") as f:
        return yaml.safe_load(f)

forms_config = load_form_priority_config()
```
Now `forms_config` is a list of dicts you can iterate over or query.

## Use in app. Example: Get high-priority forms
# Filter forms by priority:
```python
high_priority_forms = [f["Form"] for f in forms_config if f["Priority"] == "High"]
```
# Route to parser modules:
```python
form_to_parser = {
    "10-K": "form10k_parser.py",
    "Form 4": "form4_parser.py",
    # etc.
}
if current_form in [f["Form"] for f in forms_config]:
    parser_module = form_to_parser.get(current_form)
    # import and use dynamically if needed
```
## Add to `app_config.yaml` layer and pass it into orchestrators, filter managers or parser managers via dependency injection or config loaders.
```python
form_config_path: "config/form_priority.yaml"
```

## Use for Dynamic Filtering in Pipelines. Modify filter logic like this:
```python
if apply_global_filter:
    allowed_forms = {f["Form"] for f in forms_config if f["Priority"] in ("High", "Medium")}
    filings_metadata = [f for f in filings_metadata if f["form_type"] in allowed_forms]
```

## Use Cases

- Filter which forms to ingest from EDGAR
- Map form types to parser modules
- Prioritize which filings to vectorize or summarize
- Route filings through different analysis pipelines

You can modify this file to include custom tags or additional metadata as needed.
