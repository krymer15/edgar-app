# scripts/crawler_idx/run_sgml_disk_ingest.py

"""
Run SGML disk ingestion for a specific date.

Usage:
    python scripts/crawler_idx/run_sgml_disk_ingest.py --date 2025-05-12
    python scripts/crawler_idx/run_sgml_disk_ingest.py --date 2025-05-12 --include_forms 10-K 8-K
"""

import argparse, os, sys
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator
from utils.report_logger import log_info, log_error

def main():
    """
    Standalone CLI for Pipeline 3: This script runs Pipeline 3 in isolation (no meta-orchestration). 
    `write_cache=True` is explcitly set in SgmlDiskOrchestrator instantiation.
    """
    parser = argparse.ArgumentParser(description="Run SGML Disk Ingest")
    parser.add_argument("--date", type=str, required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--include_forms", nargs="*", help="Only include specific form types (e.g. 10-K 8-K)")

    args = parser.parse_args()

    orchestrator = SgmlDiskOrchestrator(
        use_cache=False,
        write_cache=True # for isolated runs
        )
    try:
        log_info(f"[CLI] Starting SGML disk ingest for {args.date}")
        written_files = orchestrator.orchestrate(target_date=args.date, include_forms=args.include_forms)
        
        log_info(f"🎯 Ingestion complete. {len(written_files)} files written.")
        for path in written_files:
            print(f" - {path}")
    except Exception as e:
        log_error(f"[CLI] SGML disk ingest failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
