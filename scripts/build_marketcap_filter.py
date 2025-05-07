# scripts/build_marketcap_filter.py

import argparse
from orchestrators.market_cap_filter_orchestrator import build_cik_allowlist_by_market_cap

def main():
    parser = argparse.ArgumentParser(description="Build CIK allowlist by market cap.")
    parser.add_argument("--min_cap", type=float, default=10_000_000_000,
                        help="Minimum market cap in USD (e.g., 10000000000 for $10B)")
    parser.add_argument("--mapping_file", type=str, default="data/raw/company_tickers.json",
                        help="Path to company_tickers.json")
    parser.add_argument("--output_file", type=str, default="data/raw/cik_allowlist_by_market_cap.json",
                        help="Output path for CIK allowlist JSON")

    args = parser.parse_args()

    build_cik_allowlist_by_market_cap(
        mapping_file=args.mapping_file,
        min_market_cap=args.min_cap,
        output_file=args.output_file
    )

if __name__ == "__main__":
    main()
