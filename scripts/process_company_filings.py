# process_company_filings.py

import os
from utils.get_project_root import get_project_root
from utils.ticker_cik_mapper import TickerCIKMapper
from downloaders.sec_downloader import SECDownloader
from utils.file_saver import save_html_to_file, save_text_blocks_to_file, save_metadata_to_json
from utils.config_loader import ConfigLoader
from parsers.exhibit_parser import ExhibitParser

import datetime

# Log folder setup
logs_dir = os.path.join(get_project_root(), "logs")
os.makedirs(logs_dir, exist_ok=True)

# Load app configuration
config = ConfigLoader.load_config()

def process_company_filings(ticker: str, num_filings: int = 5):
    """
    Orchestrates downloading, saving, and parsing multiple filings for a company.
    
    Args:
        ticker (str): Stock ticker symbol.
        num_filings (int): Number of recent filings to process (default is 5).
    """

    # Setup failure log file specific to ticker and today's date
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    failures_logfile = os.path.join(logs_dir, f"{ticker.lower()}_{today_str}_failures.log")

    # 1. Instantiate TickerCIKMapper and map ticker to CIK
    mapper = TickerCIKMapper()
    cik = mapper.get_cik(ticker)

    if cik is None:
        raise ValueError(f"CIK not found for ticker '{ticker}'.")

    # 2. Instantiate SECDownloader
    downloader = SECDownloader(
        cik=cik,
        user_agent=config["sec_downloader"]["user_agent"],
        request_delay_seconds=config["sec_downloader"]["request_delay_seconds"]
    )

    # 3. Fetch submissions
    downloader.fetch_submissions()

    # 4. Extract recent filings
    downloader.extract_recent_filings()

    # 5. Build filing URLs (e.g., 8-K and 10-K forms)
    filings = downloader.build_filing_urls(forms_filter=["8-K", "10-K"])

    if not filings:
        raise Exception(f"No matching filings found for ticker '{ticker}'.")

    # 6. Process up to 'num_filings' filings
    processed_count = 0
    for filing in filings:
        if processed_count >= num_filings:
            break

        accession_number = filing["accessionNumber"].replace("-", "")
        filing_date = filing["filingDate"]
        form_type = filing["form"]
        filing_url = filing["filing_url"]

        try:
            print(f"\n🔎 Trying to download: {filing_url}")
            raw_html = downloader.download_html(filing_url)
            print(f"✅ Successfully downloaded {filing_url}")

            # Prepare target directories only after first successful download
            raw_dir = os.path.join(get_project_root(), "data", "raw", cik)
            processed_dir = os.path.join(get_project_root(), "data", "processed", cik)
            os.makedirs(raw_dir, exist_ok=True)
            os.makedirs(processed_dir, exist_ok=True)

            # Save raw HTML
            raw_html_filename = f"{filing_date}_{form_type}_{accession_number}.html"
            raw_html_path = os.path.join(raw_dir, raw_html_filename)
            save_html_to_file(raw_html, raw_html_path)
            print(f"✅ Saved raw HTML to {raw_html_path}")

            # Save filing metadata (single filing metadata)
            single_metadata = {
                "accessionNumber": filing.get("accessionNumber"),
                "primaryDocument": filing.get("primaryDocument"),
                "filingDate": filing.get("filingDate"),
                "form": filing.get("form"),
                "items": (
                    [item.strip() for item in filing.get("items").split(",")]
                    if filing.get("items")
                    else []
                ),
                "isXBRL": filing.get("isXBRL")
            }
            metadata_filename = f"{filing_date}_{form_type}_{accession_number}_metadata.json"
            metadata_path = os.path.join(raw_dir, metadata_filename)
            save_metadata_to_json(single_metadata, metadata_path)
            print(f"✅ Saved filing metadata to {metadata_path}")

            # Parse HTML
            parser = ExhibitParser(html_content=raw_html)
            parser.parse()
            cleaned_text = parser.get_cleaned_text()

            # Save parsed text blocks
            text_blocks = cleaned_text.split("\n\n")
            blocks_filename = f"{filing_date}_{form_type}_{accession_number}_blocks.txt"
            blocks_path = os.path.join(processed_dir, blocks_filename)
            save_text_blocks_to_file(text_blocks, blocks_path)
            print(f"✅ Saved parsed text blocks to {blocks_path}")

            processed_count += 1

        except Exception as e:
            print(f"⚠️ Failed to process filing {filing_url}: {e}")
            # Continue to next filing without raising

            # Log the failure
            with open(failures_logfile, "a", encoding="utf-8") as log_f:
                log_entry = f"{datetime.datetime.now().isoformat()} | Failed Filing: {filing_url} | Error: {str(e)}\n"
                log_f.write(log_entry)

            print(f"⚠️ Logged failed filing to {failures_logfile}")

    print(f"\n🏁 Finished processing {processed_count} filings for {ticker} ({cik}).")

# Example usage
if __name__ == "__main__":
    process_company_filings("MRVL", num_filings=5)
