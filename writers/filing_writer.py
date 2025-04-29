# writers/filing_writer.py

from writers.base_writer import BaseWriter
import os

class FilingWriter(BaseWriter):
    def __init__(self, base_dir: str = "data/raw/"):
        self.base_dir = base_dir

    def write_metadata(self, *args, **kwargs):
        """
        Not implemented for filings. Metadata writing is handled separately (e.g., DailyIndexWriter).
        """
        raise NotImplementedError("FilingWriter does not handle metadata writing.")

    def write_content(self, parsed_content):
        """
        Write parsed filing content (e.g., text blocks) to disk.
        parsed_content is expected to be a dict with { 'filepath': ..., 'content': ... }
        """
        filepath = parsed_content.get("filepath")
        content = parsed_content.get("content")

        if not filepath or content is None:
            raise ValueError("Parsed content must include 'filepath' and 'content'.")

        full_path = os.path.join(self.base_dir, filepath)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Saved parsed content to {full_path}")

    def write_filing(self, cik: str, accession_number: str, form_type: str, filing_date: str, raw_html: str):
        """
        Save raw filing HTML to disk organized by CIK and filing date.
        """
        cik_path = os.path.join(self.base_dir, cik)
        os.makedirs(cik_path, exist_ok=True)

        filename = f"{filing_date}_{form_type}_{accession_number.replace('-', '')}.html"
        full_path = os.path.join(cik_path, filename)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(raw_html)

        print(f"✅ Saved raw filing to {full_path}")
