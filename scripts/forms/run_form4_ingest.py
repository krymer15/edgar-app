# scripts/forms/run_form4_ingest.py

"""
Run Form 4 data processing for a specific date or accession numbers.

This script processes Form 4 filings by:
1. Finding Form 4 SGML files on disk (from Pipeline 3)
2. Parsing them using the specialized Form4SgmlIndexer
3. Writing the parsed data to the form4_filings, form4_relationships, and form4_transactions tables

Usage:
    python scripts/forms/run_form4_ingest.py --date 2025-05-12
    python scripts/forms/run_form4_ingest.py --date 2025-05-12 --reprocess
    python scripts/forms/run_form4_ingest.py --accessions 0000123456-25-000123 0000123456-25-000124
    python scripts/forms/run_form4_ingest.py --date 2025-05-12 --write-xml
"""

import argparse
import sys
import os
from datetime import datetime
from orchestrators.forms.form4_orchestrator import Form4Orchestrator
from utils.report_logger import log_info, log_error, log_warn

def main():
    """
    Command-line interface for Form 4 ingestion.
    Provides options for date-based or accession-based processing.
    """
    parser = argparse.ArgumentParser(description="Run Form 4 data processing")

    # Date or accession options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--date", type=str, help="Target date (YYYY-MM-DD)")
    input_group.add_argument("--accessions", nargs="+", help="Specific accession numbers to process")

    # Processing options
    parser.add_argument("--limit", type=int, help="Limit number of records processed")
    parser.add_argument("--reprocess", action="store_true", help="Reprocess records even if already processed")
    parser.add_argument("--write-xml", action="store_true", help="Write raw XML content to disk")
    parser.add_argument("--cache", action="store_true", help="Use file cache (default is False for pipelines)")

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = Form4Orchestrator(
        use_cache=args.cache,
        write_cache=args.cache  # Align read/write cache settings
    )

    try:
        started_at = datetime.now()

        if args.date:
            log_info(f"[FORM4-CLI] Starting Form 4 processing for date {args.date}")
            target_date = args.date
            accession_filters = None
        else:
            log_info(f"[FORM4-CLI] Starting Form 4 processing for accessions: {args.accessions}")
            target_date = None
            accession_filters = args.accessions

        # Run the orchestrator
        results = orchestrator.run(
            target_date=target_date,
            accession_filters=accession_filters,
            limit=args.limit,
            reprocess=args.reprocess,
            write_raw_xml=args.write_xml
        )

        # Report results
        duration = (datetime.now() - started_at).total_seconds()

        log_info(f"🎯 Form 4 processing complete in {duration:.2f} seconds")
        log_info(f"   - Processed: {results.get('processed', 0)}")
        log_info(f"   - Succeeded: {results.get('succeeded', 0)}")
        log_info(f"   - Failed: {results.get('failed', 0)}")

        # Show failures if any
        if results.get('failures'):
            log_warn(f"Failures ({len(results['failures'])})")
            for failure in results['failures']:
                log_warn(f"  - {failure['accession_number']}: {failure['error']}")

        # Exit with error code if any failures
        if results.get('failed', 0) > 0:
            sys.exit(1)

    except Exception as e:
        log_error(f"[FORM4-CLI] Error running Form 4 processor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()