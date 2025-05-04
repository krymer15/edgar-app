# Utilities

Helper modules to support path generation, logging, config loading, and field standardization.

## Modules

- `path_manager.py`: Builds raw and processed paths from CIK, year, accession.
- `report_logger.py`: Appends structured rows to CSV logs. Used by orchestrators and writers.
- `field_mapper.py`: Provides canonical mappings for:
  - `accession_number`
  - `accession_clean`
  - `form_type`
  - `filing_date`
- `config_loader.py`: Loads `app_config.yaml`
- `url_builder.py`: Constructs SEC URLs from CIK and accession.

## Notes
- Do not log `accession_clean` to DB or logs — filenames only.
