import requests
import time
from utils.config_loader import ConfigLoader
from utils.url_builder import construct_sgml_txt_url
from parsers.sgml_filing_parser import SgmlFilingParser
from writers.sgml_doc_writer import SgmlDocWriter
from utils.path_utils import build_path_args
from utils.path_manager import build_raw_filepath
from collectors.daily_index_collector import DailyIndexCollector

class SgmlDocOrchestrator:
    def __init__(self, save_raw: bool = True):
        self.config = ConfigLoader.load_config()
        self.base_data_path = self.config.get("storage", {}).get("base_data_path", "./data/")
        print(f"[DEBUG] base_data_path resolved to: {self.base_data_path}")
        self.user_agent = self.config.get("sec_downloader", {}).get("user_agent")
        self.save_raw = save_raw

    def run(self, cik: str, accession_full: str, form_type: str, filing_date: str):
        year = filing_date[:4]
        accession_clean = accession_full.replace("-", "")
        sgml_filename = f"{accession_full}.txt"

        sgml_url = construct_sgml_txt_url(cik, accession_clean)
        headers = {
            "User-Agent": self.user_agent,
            "Accept-Encoding": "gzip, deflate",
            "Host": "www.sec.gov"
        }

        print(f"\n📥 Attempting download of .txt SGML filing from: {sgml_url}")
        response = requests.get(sgml_url, headers=headers)

        if response.status_code != 200:
            print(f"⚠️ First attempt failed with status {response.status_code}. Retrying in 1s...")
            time.sleep(1)
            response = requests.get(sgml_url, headers=headers)

        if response.status_code != 200:
            print(f"[ERROR] Failed to download .txt after retry: {sgml_url}")
            print(f"[DEBUG] Response code: {response.status_code}")
            return

        sgml_contents = response.text

        if self.save_raw:
            print("[DEBUG] save_raw is True. Preparing to write SGML.")
            writer = SgmlDocWriter(base_data_path=self.base_data_path)
            writer.save_raw_sgml(
                sgml_contents=sgml_contents,
                year=year,
                cik=cik,
                form_type=form_type,
                accession_clean=accession_clean,
                accession_full=accession_full,
                filename=sgml_filename
            )
            print("[DEBUG] SGML file write complete.")

        parser = SgmlFilingParser(cik=cik, accession=accession_clean, form_type=form_type)
        result = parser.parse(sgml_contents)

        print(f"\n🧾 Exhibits Found:")
        for ex in result["exhibits"]:
            tag = "✅" if ex.get("accessible", True) else "❌"
            print(f" {tag} {ex['filename']} | {ex['description']} | {ex['type']}")

        print(f"\n🔗 Likely Primary Document URL:\n{result['primary_document_url']}\n")
        return result

    def process_idx_file(self, date: str, limit=None):
        from writers.daily_index_writer import DailyIndexWriter

        print(f"📅 Processing crawler.idx for {date}")
        collector = DailyIndexCollector(user_agent=ConfigLoader().load_config("sec_downloader.user_agent"))
        filings = collector.collect(date)
        DailyIndexWriter().write_to_postgres(filings)

        if limit:
            filings = filings[:limit]

        for f in filings:
            print(f"\n🔄 Processing filing: {f['cik']} | {f['accession_number']} | {f['form_type']}")
            try:
                self.run(
                    cik=f["cik"],
                    accession=f["accession_number"],
                    form_type=f["form_type"],
                    filing_date=f["filing_date"]
                )
            except Exception as e:
                print(f"[ERROR] Failed on {f['accession_number']}: {e}")