import os
from utils.config_loader import ConfigLoader

# Load config once at module import
CONFIG = ConfigLoader.load_config()
STORAGE_CONFIG = CONFIG.get("storage", {})

def build_raw_filepath(year: str, cik: str, form_type: str, accession_or_subtype: str, filename: str) -> str:
    """
    Builds a full structured filepath under the /data/raw/ directory.
    """
    subfolder_template = STORAGE_CONFIG.get("raw_subfolder_template", "{year}/{cik}/{form_type}/{accession_or_subtype}/")
    subfolder = subfolder_template.format(
        year=year,
        cik=cik,
        form_type=form_type,
        accession_or_subtype=accession_or_subtype
    )
    return os.path.join("data", "raw", subfolder, filename)

def build_processed_filepath(year: str, cik: str, form_type: str, accession_or_subtype: str, filename: str) -> str:
    """
    Builds a full structured filepath under the /data/processed/ directory.
    """
    subfolder_template = STORAGE_CONFIG.get("processed_subfolder_template", "{year}/{cik}/{form_type}/{accession_or_subtype}/")
    subfolder = subfolder_template.format(
        year=year,
        cik=cik,
        form_type=form_type,
        accession_or_subtype=accession_or_subtype
    )
    return os.path.join("data", "processed", subfolder, filename)
