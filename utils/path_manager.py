import os
from config.config_loader import ConfigLoader
from utils.report_logger import log_debug, log_warn

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
    safe_form_type = form_type.replace("/", "_")
    subfolder = subfolder_template.format(
        year=year,
        cik=cik,
        form_type=safe_form_type,
        accession_or_subtype=accession_or_subtype
    )

    full_path = os.path.join(base_path, subfolder, filename)
    log_debug(f"📁 [Debug] Saving to: {full_path}")
    return full_path

def build_raw_filepath_by_type(
    # Example: build_raw_filepath_by_type("sgml", "2024", "0000320193", "10-K", "000032019324000011", "submission.txt")

    file_type: str,  # One of: "sgml", "html_index", "exhibits", "xml"
    year: str,
    cik: str,
    form_type: str,
    accession_or_subtype: str,
    filename: str,
    force_base_path: str = None
) -> str:
    """
    Builds a full structured filepath for a given raw file type under /data/raw/{file_type}/.
    Example: /data/raw/sgml/CIK/year/accession/file.txt
    """
    if file_type not in ("sgml", "html_index", "exhibits", "xml"):
        raise ValueError(f"Unsupported file_type: {file_type}")

    base_path = (
        force_base_path
        or STORAGE_CONFIG.get("base_data_path", "data/")
    )

    subfolder_template = "{cik}/{year}/{form_type}/{accession_or_subtype}/"
    safe_form_type = form_type.replace("/", "_")
    subfolder = subfolder_template.format(
        file_type=file_type,
        cik=cik,
        year=year,
        form_type=safe_form_type,
        accession_or_subtype=accession_or_subtype
    )

    full_path = os.path.join(base_path, "raw", subfolder, filename)
    log_debug(f"📁 [Debug] Saving to ({file_type}): {full_path}")
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
    safe_form_type = form_type.replace("/", "_")
    subfolder = subfolder_template.format(
        year=year,
        cik=cik,
        form_type=safe_form_type,
        accession_or_subtype=accession_or_subtype
    )

    full_path = os.path.join(base_path, subfolder, filename)
    log_debug(f"📁 [Debug] Saving to: {full_path}")
    return full_path

def build_cache_path(cik: str, accession: str, year: str = None) -> str:
    """
    Returns full path to cached SGML .txt file for a given CIK and accession.
    E.g. /data/cache_sgml/YYYY/CIK/accession.txt
    Requires `year` from filing metadata (do not derive from accession).
    """
    if not year:
        # Fail loudly during dev or testing
        log_warn(f"[CachePath] ⚠️ No year provided for {accession}; skipping cache path.")
        return None# gracefully aborts caching

    base_path = STORAGE_CONFIG.get("base_data_path", "data/")
    cache_dir = os.path.join(base_path, "cache_sgml", year, cik)
    filename = f"{accession}.txt"
    return os.path.join(cache_dir, filename)

