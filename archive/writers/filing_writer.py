# writers/filing_writer.py

from writers.base_writer import BaseWriter
from utils.path_manager import build_raw_filepath
import os

class FilingWriter(BaseWriter):
    def __init__(self):
        pass  # No base_dir needed; full filepath is passed in

    def write_metadata(self, *args, **kwargs):
        """
        Not implemented for filings. Metadata writing is handled separately (e.g., DailyIndexWriter).
        """
        raise NotImplementedError("FilingWriter does not handle metadata writing.")

    def write_content(self, parsed_content, filepath=None):
        """
        Write parsed filing content (e.g., text blocks) to disk.

        Args:
            parsed_content (dict): Must contain a 'content' key.
            filepath (str): Full destination path. Required and overrides parsed_content['filepath'].
        """
        content = parsed_content.get("content")
        if content is None or filepath is None:
            raise ValueError("write_content requires both 'content' and 'filepath' arguments.")

        # Ensure the parent directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Saved parsed content to {filepath}")

    # Function below deprecated or used by an unknown orchestrator
    def write_filing(self, raw_html: str, year: str, cik: str, form_type: str, accession_number: str, filename: str = "primarydoc.html"):
        """
        Writes raw filing HTML to /data/raw/
        """
        filepath = build_raw_filepath(
            year=year,
            cik=cik,
            form_type=form_type,
            accession_or_subtype=accession_number,
            filename=filename
        )
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(raw_html)

        print(f"✅ Saved raw filing to {filepath}")

    def write_filing_from_filepath(self, raw_html: str, filepath: str):
        """
        Writes raw HTML filing to disk using a fully specified filepath.
        This is used by orchestrators that already resolved the path (e.g., daily index).
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(raw_html)
        print(f"✅ Saved raw filing to {filepath}")
