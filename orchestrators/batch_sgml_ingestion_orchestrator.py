from orchestrators.base_orchestrator import BaseOrchestrator
from collectors.daily_index_collector import DailyIndexCollector
from orchestrators.sgml_doc_orchestrator import SgmlDocOrchestrator
from writers.parsed_sgml_writer import ParsedSgmlWriter
from utils.config_loader import ConfigLoader
from utils.report_logger import append_ingestion_report, log_info, log_warn, log_error, append_batch_summary, log_debug
from datetime import datetime, timezone, timedelta
from utils.field_mapper import (
    get_accession_full, get_cik, get_form_type, get_filing_date
)
from schemas.parsed_result_model import ParsedResultModel
import uuid

'''
# ⚠️ ACCESSION_ USAGE POLICY
# This project uses field_mapper.py for field normalization.
# `accession_clean` must ONLY be used locally where required (e.g., URL construction or filenames).
# It should NOT be added to parsed metadata dicts, passed to writer modules, or stored in the database.

'''

class BatchSgmlIngestionOrchestrator(BaseOrchestrator):
    def __init__(self, date_str: str, limit: int = None):
        super().__init__()
        self.date_str = date_str
        self.limit = limit

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

        log_info(f"Launching Batch SGML Ingestion for {target_date}")
        filings_metadata = self.collector.collect(date=target_date)

        if limit:
            filings_metadata = filings_metadata[:limit]
            log_info(f"Limiting to first {limit} filings for testing.")

        log_info(f"Processing {len(filings_metadata)} filings from {target_date}...")

        # ⏳ Track counters
        attempted = len(filings_metadata)
        skipped = 0
        failed = 0
        succeeded = 0

        for meta in filings_metadata:
            accession_full = get_accession_full(meta)
            accession_number = accession_full  # ✅ Needed for writer compatibility
            cik = get_cik(meta)
            form_type = get_form_type(meta)
            filing_date = get_filing_date(meta)

            if not (accession_full and cik and form_type):
                log_warn(f"[SKIPPED] Incomplete metadata: {meta}")
                continue

            result = self.single_orchestrator.run(
                cik=cik,
                accession_full=accession_full,
                form_type=form_type,
                filing_date=filing_date
            )

            if not result:
                log_warn(f"[SKIPPED] No result returned for: {accession_full}")
                continue

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

                # Write to DB
                write_success = self.parsed_writer.write_metadata(metadata_flat)
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

        # ✅ After loop ends
        append_batch_summary(
            total=attempted,
            skipped=skipped,
            failed=failed,
            succeeded=succeeded,
            log_date=target_date
        )            

    def run_backfill(self, start_date: str, end_date: str):
        """Run ingestion for a date range."""
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


