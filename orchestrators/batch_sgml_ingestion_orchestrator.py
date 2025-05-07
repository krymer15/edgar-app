from orchestrators.base_orchestrator import BaseOrchestrator
from collectors.daily_index_collector import DailyIndexCollector
from orchestrators.sgml_doc_orchestrator import SgmlDocOrchestrator
from writers.parsed_sgml_writer import ParsedSgmlWriter
from writers.daily_index_writer import DailyIndexWriter
from utils.config_loader import ConfigLoader
from utils.report_logger import append_ingestion_report, log_info, log_warn, log_error, append_batch_summary, log_debug
from datetime import datetime, timezone, timedelta
from utils.field_mapper import (
    get_accession_full, get_cik, get_form_type, get_filing_date
)
from schemas.parsed_result_model import ParsedResultModel
import uuid
from utils.filtered_cik_manager import FilteredCikManager


'''
# ⚠️ ACCESSION_ USAGE POLICY
# This project uses field_mapper.py for field normalization.
# `accession_clean` must ONLY be used locally where required (e.g., URL construction or filenames).
# It should NOT be added to parsed metadata dicts, passed to writer modules, or stored in the database.

'''

class BatchSgmlIngestionOrchestrator(BaseOrchestrator):
    def __init__(self, date_str: str, limit: int = None, override_filter: bool = None):
        super().__init__()
        self.date_str = date_str
        self.limit = limit
        self.override_filter = override_filter

        config = ConfigLoader.load_config() 
        user_agent = config.get("sec_downloader", {}).get("user_agent", "SafeHarborBot/1.0")

        self.collector = DailyIndexCollector(user_agent=user_agent)
        self.parsed_writer = ParsedSgmlWriter()
        self.single_orchestrator = SgmlDocOrchestrator(save_raw=True, write_to_db=False)

    def orchestrate(self):
        """Top-level entry point required by BaseOrchestrator."""
        self.run(self.date_str, self.limit)
    
    def run(self, date_str: str, limit: int = None):
        """Ingest all SGML filings for a given date from SEC's crawler.idx."""

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: '{date_str}' — use YYYY-MM-DD")

        # Pull and parse crawler.idx for target_date.
        log_info(f"Launching Batch SGML Ingestion for {target_date}")
        full_filing_metadata = self.collector.collect(date=target_date)

        index_writer = DailyIndexWriter()

        config = ConfigLoader.load_config()
        form_types_to_track = config.get("ingestion", {}).get("filing_forms_to_track", [])
        cik_allowlist_path = config.get("storage", {}).get("company_mapping_path", "data/raw/company_tickers.json")

        apply_filter = config.get("ingestion", {}).get("apply_global_filter", True)
        if self.override_filter is not None:
            apply_filter = self.override_filter

        if apply_filter:
            filter_mgr = FilteredCikManager(
                cik_allowlist_path=cik_allowlist_path,
                allowed_form_types=form_types_to_track
            )
            filtered_metadata = filter_mgr.filter(full_filing_metadata)
            log_info(f"🔍 Filtered {len(full_filing_metadata)} → {len(filtered_metadata)} filings based on CIK + form_type")
            index_writer.write(filtered_metadata) # Write only filtered to `daily_index_metadata`
        else:
            log_info("⚠️ Skipping global filter...")
            index_writer.write(full_filing_metadata) # Write all to `daily_index_metadata` before filtering
            filtered_metadata = FilteredCikManager(
                cik_allowlist_path=cik_allowlist_path,
                allowed_form_types=form_types_to_track
            ).filter(full_filing_metadata)  # ✅ still filter for parsing

        # Dev Testing Only; defaults to None
        if limit:
            full_filing_metadata = full_filing_metadata[:limit]
            log_info(f"Limiting to first {limit} filings for testing.")

        log_info(f"Processing {len(full_filing_metadata)} filings from {target_date}...")

        # ⏳ Track counters
        attempted = len(filtered_metadata)
        skipped = 0
        failed = 0
        succeeded = 0

        # Main Parsing Loop
        for meta in filtered_metadata:
            # Extract key fields from metadata dict.
            accession_full = get_accession_full(meta)
            accession_number = accession_full  # ✅ Needed for writer compatibility
            cik = get_cik(meta)
            form_type = get_form_type(meta)
            filing_date = get_filing_date(meta)

            # Skip entries with missing fields.
            if not (accession_full and cik and form_type):
                log_warn(f"[SKIPPED] Incomplete metadata: {meta}")
                continue

            # Run SgmlDocOrchestrator: download SGML, parse it using SgmlFilingParser and return result dict with `primary_doc_url` and `exhibits`.
            result = self.single_orchestrator.run(
                cik=cik,
                accession_full=accession_full,
                form_type=form_type,
                filing_date=filing_date
            )

            if not result:
                log_warn(f"[SKIPPED] No result returned for: {accession_full}")
                continue

            ## Post-parse validation and DB Write
            # Wraps into a Pydantic model for validation.
            parsed_result = {
                "metadata": {
                    "cik": cik,
                    "accession_number": accession_number,
                    "form_type": form_type,
                    "filing_date": filing_date,
                    "primary_doc_url": result.get("primary_document_url"),
                },
                "exhibits": result.get("exhibits", []),
            }

            log_debug(f"[DEBUG] Parsed metadata for {accession_number}:")
            log_debug(f"  cik: {cik}")
            log_debug(f"  form_type: {form_type}")
            log_debug(f"  filing_date: {filing_date}")
            log_debug(f"  primary_doc_url: {result.get('primary_document_url')}")

            # 🔐 Validate before DB write
            try:
                validated = ParsedResultModel(**parsed_result)

                # Flatten metadata for writing
                metadata_flat = validated.metadata.model_dump()

                # Write to `parsed_sgml_metadata` table.
                write_success = self.parsed_writer.write_metadata(metadata_flat)
                
                # Write exhibits to `exhibit_metadata` ONLY IF metadata write above succeeded.
                if write_success:
                    self.parsed_writer.write_exhibits(
                        exhibits=[ex.model_dump() for ex in validated.exhibits],
                        accession_number=metadata_flat.get("accession_number", ""),
                        cik=metadata_flat.get("cik", ""),
                        form_type=metadata_flat.get("form_type", ""),
                        filing_date=metadata_flat.get("filing_date", ""),
                        primary_doc_url=metadata_flat.get("primary_document_url", "")
                    )
                    succeeded += 1
                else:
                    log_warn(f"⚠️ Skipping exhibit write — no parsed_sgml_metadata row found for: {accession_number}")
                    failed += 1

            except Exception as e:
                log_error(f"[ERROR] Failed to validate or write parsed result: {e}")
                failed += 1
                continue

        # Batch Summary Logging after Parsing Loop ends. Appends totals to the daily log CSV report.
        append_batch_summary(
            total=attempted,
            skipped=skipped,
            failed=failed,
            succeeded=succeeded,
            log_date=target_date
        )            

    def run_backfill(self, start_date: str, end_date: str):
        # Run ingestion for a date range. Repeatedly calls `run()` over a date range using `timedelta(days-1)`
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Invalid date format — use YYYY-MM-DD")

        if start > end:
            raise ValueError("Start date must be before or equal to end date")

        current = start
        while current <= end:
            self.run(date_str=current.isoformat(), limit=self.limit)
            current += timedelta(days=1)


