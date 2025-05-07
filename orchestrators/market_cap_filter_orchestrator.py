import json
from pathlib import Path
from market_data import get_market_cap
from utils.ticker_cik_mapper import TickerCIKMapper
from utils.get_project_root import get_project_root


def build_cik_allowlist_by_market_cap(
    mapping_file: str = "data/raw/company_tickers.json",
    min_market_cap: float = 10_000_000_000,
    output_file: str = "data/raw/cik_allowlist_by_market_cap.json"
):
    """
    Builds a filtered CIK allowlist based on market cap threshold.

    Args:
        mapping_file (str): Path to SEC company_tickers.json.
        min_market_cap (float): Minimum market cap in dollars.
        output_file (str): Output path for CIK allowlist.
    """
    mapping_path = Path(get_project_root()) / mapping_file
    with open(mapping_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    tickers = [entry["ticker"] for entry in raw.values() if "ticker" in entry]

    mapper = TickerCIKMapper()
    allowlist = []

    for ticker in tickers:
        market_cap = get_market_cap(ticker)
        if market_cap and market_cap >= min_market_cap:
            try:
                cik = mapper.get_cik(ticker)
                allowlist.append(cik)
                print(f"✅ {ticker.upper()} (Market Cap: ${market_cap:,}) → {cik}")
            except ValueError as ve:
                print(f"⚠️ {ve}")

    output_path = Path(get_project_root()) / output_file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(allowlist, f, indent=2)

    print(f"\n📝 Wrote {len(allowlist)} CIKs to {output_file}")
