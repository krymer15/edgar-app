import os
from config.config_loader import ConfigLoader
from utils.report_logger import log_debug

# Load config once at module import
CONFIG = ConfigLoader.load_config()
STORAGE_CONFIG = CONFIG.get("storage", {})

# Paths are resolved using base_data_path from app_config.yaml

def build_path_args(metadata: dict, filename: str) -> tuple:
    """
    Returns a tuple used to build storage paths:
    (year, cik, form_type, accession_or_subtype, filename)

    Handles variation in 'accession_number' key casing across Submissions and DailyIndex.
    """
    return (
        metadata["filing_date"][:4],
        metadata["cik"],
        metadata["form_type"],
        metadata.get("accession_number") or metadata.get("accessionNumber"),
        filename
    )

def build_raw_filepath(
    year: str,
    cik: str,
    form_type: str,
    accession_or_subtype: str,
    filename: str,
    force_base_path: str = None
) -> str:
    """
    Builds a full structured filepath under the /data/raw/ or ./test_data/raw/ directory.
    Priority: force_base_path > base_data_path > raw_html_base_path.
    """
    base_path = (
        force_base_path
        or STORAGE_CONFIG.get("base_data_path")
        or STORAGE_CONFIG.get("raw_html_base_path", "data/raw/")
    )

    subfolder_template = STORAGE_CONFIG.get("raw_subfolder_template", "{year}/{cik}/{form_type}/{accession_or_subtype}/")
    subfolder = subfolder_template.format(
        year=year,
        cik=cik,
        form_type=form_type,
        accession_or_subtype=accession_or_subtype
    )

    full_path = os.path.join(base_path, subfolder, filename)
    log_debug(f"📁 [Debug] Saving to: {full_path}")
    return full_path

def build_processed_filepath(
    year: str,
    cik: str,
    form_type: str,
    accession_or_subtype: str,
    filename: str,
    force_base_path: str = None
) -> str:
    """
    Builds a full structured filepath under the /data/processed/ or ./test_data/processed/ directory.
    Priority: force_base_path > base_data_path > processed_text_base_path.
    """
    base_path = (
        force_base_path
        or STORAGE_CONFIG.get("base_data_path")
        or STORAGE_CONFIG.get("processed_text_base_path", "data/processed/")
    )

    subfolder_template = STORAGE_CONFIG.get("processed_subfolder_template", "{year}/{cik}/{form_type}/{accession_or_subtype}/")
    subfolder = subfolder_template.format(
        year=year,
        cik=cik,
        form_type=form_type,
        accession_or_subtype=accession_or_subtype
    )

    full_path = os.path.join(base_path, subfolder, filename)
    log_debug(f"📁 [Debug] Saving to: {full_path}")
    return full_path

def build_cache_path(cik: str, accession: str) -> str:
    """
    Returns full path to cached SGML .txt file for a given CIK and accession.
    E.g. /data/cache_sgml/YYYY/CIK/accession.txt
    """
    year = accession[:4]  # Assumes accession starts with YYYY
    base_path = STORAGE_CONFIG.get("base_data_path", "data/")
    cache_dir = os.path.join(base_path, "cache_sgml", year, cik)
    filename = f"{accession}.txt"
    return os.path.join(cache_dir, filename)

