import argparse
import sys
import os

# Insert project root into sys.path
try:
    from utils.get_project_root import get_project_root
    sys.path.insert(0, str(get_project_root()))
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from orchestrators.sgml_doc_orchestrator import SgmlDocOrchestrator

def main():
    parser = argparse.ArgumentParser(description="SGML Filing Ingestion CLI")
    parser.add_argument("--cik", help="CIK of the company")
    parser.add_argument("--accession", help="Accession number of the filing")
    parser.add_argument("--form_type", help="Form type (e.g., 8-K, 10-K)")
    parser.add_argument("--filing_date", help="Filing date in YYYY-MM-DD format")
    parser.add_argument("--save_raw", action="store_true", help="Save raw .txt to disk")
    parser.add_argument("--date", help="Date to process crawler.idx (YYYY-MM-DD)")
    parser.add_argument("--limit", type=int, help="Optional: limit number of filings")

    args = parser.parse_args()

    orchestrator = SgmlDocOrchestrator(save_raw=args.save_raw)

    # ── Single SGML Filing Mode ───────────────────────────────────
    if args.cik and args.accession and args.form_type and args.filing_date:
        orchestrator.run(
            cik=args.cik,
            accession_full=args.accession,
            form_type=args.form_type,
            filing_date=args.filing_date
        )
    # ── Batch idx File Mode ──────────────────────────────────────
    elif args.date:
        orchestrator.process_idx_file(date=args.date, limit=args.limit)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
