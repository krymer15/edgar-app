# scripts/crawler_idx/run_daily_pipeline_ingest.py

"""
Run full daily ingestion: metadata → document index → SGML .txt download.

Usage:
    python scripts/crawler_idx/run_daily_pipeline_ingest.py --date 2025-05-12 --limit 5
    python scripts/crawler_idx/run_daily_pipeline_ingest.py --date 2025-05-12 --job-id <uuid>
    python scripts/crawler_idx/run_daily_pipeline_ingest.py --retry-failed --job-id <uuid>
    python scripts/crawler_idx/run_daily_pipeline_ingest.py --accessions 0001234567-25-000001 0001234567-25-000002
"""

import argparse
import sys, os
from datetime import datetime

# === [Universal Header] Add project root to path ===
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)))

from orchestrators.crawler_idx.daily_ingestion_pipeline import DailyIngestionPipeline
from utils.report_logger import log_info, log_error
from utils.filing_calendar import is_valid_filing_day
from utils.form_type_validator import FormTypeValidator
from utils.job_tracker import get_job_progress

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid date format. Use YYYY-MM-DD.")

def main():
    parser = argparse.ArgumentParser(description="Run full daily ingestion pipeline with robust processing")
    
    # Date and filtering options
    parser.add_argument("--date", type=validate_date, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Max records to process per run")
    parser.add_argument("--include-forms", nargs="*", help="Only include specific form types (e.g. 10-K 8-K)")
    
    # Job control options
    parser.add_argument("--job-id", type=str, help="Job ID for continuing an existing job")
    parser.add_argument("--retry-failed", action="store_true", help="Retry failed records")
    
    # Specific accession processing
    parser.add_argument("--accessions", nargs="*", help="Process specific accession numbers")
    
    # Pipeline options
    parser.add_argument("--no-cache", action="store_true", help="Disable SGML cache usage")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.date and not args.job_id and not args.accessions:
        log_error("[CLI] Must specify at least one: --date, --job-id, or --accessions")
        sys.exit(1)
    
    if args.retry_failed and not args.job_id:
        log_error("[CLI] --retry-failed requires --job-id")
        sys.exit(1)
    
    # Check if date is a valid SEC filing day
    if args.date:
        target_date_obj = datetime.strptime(args.date, "%Y-%m-%d").date()
        if not is_valid_filing_day(target_date_obj):
            log_info(f"[CLI] {args.date} is not a valid SEC filing day. Skipping.")
            sys.exit(0)
    
    # Validate and normalize form types if provided
    validated_forms = None
    if args.include_forms:
        validated_forms = FormTypeValidator.get_validated_form_types(args.include_forms)
        log_info(f"[CLI] Form types to include: {validated_forms}")
    
    # Show job progress if continuing an existing job
    if args.job_id:
        job_progress = get_job_progress(args.job_id)
        log_info(f"[CLI] Job {args.job_id} status: {job_progress['completed']}/{job_progress['total']} completed, {job_progress['failed']} failed")
    
    try:
        log_info(f"[CLI] 🔁 Launching DailyIngestionPipeline (date={args.date}, limit={args.limit}, job_id={args.job_id})")
        pipeline = DailyIngestionPipeline(use_cache=not args.no_cache)
        
        if args.accessions:
            pipeline.run(
                target_date=None,  # Not date-based in this mode
                process_only=args.accessions,
                limit=None,  # No limit when processing specific accessions
                include_forms=validated_forms
            )
        else:
            pipeline.run(
                target_date=args.date,
                limit=args.limit,
                include_forms=validated_forms,
                retry_failed=args.retry_failed,
                job_id=args.job_id
            )
    except Exception as e:
        log_error(f"[CLI] Daily pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()