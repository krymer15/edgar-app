import os
import requests
from utils.path_manager import build_raw_filepath, build_processed_filepath
from parsers.embedded_doc_parser import EmbeddedDocParser

class EmbeddedDocOrchestrator:
    def __init__(self, base_path="./test_data"):
        self.base_path = base_path

    def run(self, accession, cik, form_type, filing_date, embedded_url):
        import re
        year = filing_date[:4]

        # 🧼 Final cleanup of embedded URL before usage
        embedded_url = embedded_url.strip()
        embedded_url = re.sub(r"\s+", "", embedded_url)

        filename = os.path.basename(embedded_url).split("?")[0]
        if filename.endswith(".xml"):
            print(f"[SKIPPED] XML document detected: {filename} — logging only.")
            return

        raw_path = build_raw_filepath(year, cik, form_type, accession, filename)
        processed_path = build_processed_filepath(year, cik, form_type, accession, filename)

        # 🛡️ Assert and log for final defense
        assert " " not in embedded_url, f"🛑 Space still found in URL: {repr(embedded_url)}"
        print(f"📥 Downloading: {embedded_url}")
        print(f"🧪 [DEBUG repr] embedded_url = {repr(embedded_url)}")
        print(f"🧪 [DEBUG hex]    last segment = {[hex(ord(c)) for c in embedded_url[-20:]]}")

        response = requests.get(embedded_url)

        if response.status_code != 200:
            print(f"[ERROR] Failed to download: {embedded_url}")
            return

        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        with open(raw_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ Saved raw embedded doc to {raw_path}")

        parser = EmbeddedDocParser(response.text, embedded_url)
        parsed_text = parser.parse()

        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        with open(processed_path, "w", encoding="utf-8") as f:
            f.write(parsed_text)
        print(f"✅ Parsed and saved cleaned doc to {processed_path}")
