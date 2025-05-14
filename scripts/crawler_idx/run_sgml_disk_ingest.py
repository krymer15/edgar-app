# scripts/crawler_idx/run_sgml_disk_ingest.py

import argparse
from orchestrators.crawler_idx.sgml_disk_orchestrator import SgmlDiskOrchestrator
from utils.report_logger import log_info

def main():
    """
    Standalone CLI for Pipeline 3: This script runs Pipeline 3 in isolation (no meta-orchestration). `write_cache=True` is explcitly set in SgmlDiskOrchestrator instantiation.
    """
    parser = argparse.ArgumentParser(description="Run SGML Disk Ingest")
    parser.add_argument("--date", type=str, required=True, help="Target date (YYYY-MM-DD)")
    parser.add_argument("--no-cache", action="store_true", help="Disable SGML cache usage")

    args = parser.parse_args()

    orchestrator = SgmlDiskOrchestrator(
        use_cache=not args.no_cache,
        write_cache=True # Explicitly allow writing to cache when run standalone
        )
    written_files = orchestrator.orchestrate(args.date)

    log_info(f"🎯 Ingestion complete. {len(written_files)} files written.")
    for path in written_files:
        print(f" - {path}")

if __name__ == "__main__":
    main()
