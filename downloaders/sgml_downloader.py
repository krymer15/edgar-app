# downloaders/sgml_downloader.py

'''
# Role: Downloads SGML .txt using inherited retry logic
- Uses caching to mitigate using SgmlDownloader twice upon parsing metadata from sgml and then writing sgml to disk.
'''

import os
import time
from downloaders.sec_downloader import SECDownloader
from models.dataclasses.sgml_text_document import SgmlTextDocument
from utils.path_manager import build_cache_path
from utils.url_builder import construct_sgml_txt_url
from utils.report_logger import log_info, log_warn, log_error

class SgmlDownloader(SECDownloader):
    def __init__(self, user_agent: str, request_delay_seconds: float = 1.0, use_cache: bool = True):
        super().__init__(user_agent=user_agent, request_delay_seconds=request_delay_seconds)
        self.use_cache = use_cache
        self.memory_cache = {} # key: (cik, accession, year) → value: SgmlTextDocument

    def clear_memory_cache(self):
        self.memory_cache.clear()

    def is_stale(self, path: str, max_age_seconds: int) -> bool:
        try:
            modified = os.path.getmtime(path)
            return (time.time() - modified) > max_age_seconds
        except OSError:
            return True  # Treat unreadable or missing file as stale

    def is_cached(self, cik: str, accession_number: str, year: str) -> bool:
        path = build_cache_path(cik, accession_number, year)
        return path is not None and os.path.exists(path)

    def read_from_cache(self, cik: str, accession_number: str, year: str) -> str:
        path = build_cache_path(cik, accession_number, year)
        if not path:
            raise ValueError(f"[read_from_cache] Missing cache path for {accession_number}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_to_cache(self, cik: str, accession_number: str, content: str, year: str):
        path = build_cache_path(cik, accession_number, year)
        log_info(f"[WRITE] Caching SGML: {accession_number} → {path}")

        if not path:
            log_warn(f"[write_to_cache] No cache path for {accession_number}, skipping write.")
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def download_sgml(self, cik: str, accession_number: str, year: str, write_cache: bool = True) -> SgmlTextDocument:
        key = (cik, accession_number, year)
        if key in self.memory_cache:
            log_info(f"🔁 Reusing in-memory SGML for {accession_number}")
            return self.memory_cache[key]

        log_info(f"[DEBUG] Checking SGML cache for: {accession_number}, year={year}")
        path = build_cache_path(cik, accession_number, year)
        log_info(f"[DEBUG] Cache path resolved: {path}")

        if not path:
            log_warn(f"[download_sgml] Cannot resolve cache path for {accession_number}")
            return SgmlTextDocument(cik=cik, accession_number=accession_number, content="")

        if self.use_cache and self.is_cached(cik, accession_number, year):
            if not self.is_stale(path, max_age_seconds=86400):
                log_info(f"⚡ Cache hit for SGML: {accession_number}")
                content = self.read_from_cache(cik, accession_number, year)
                doc = SgmlTextDocument(cik=cik, accession_number=accession_number, content=content)
                self.memory_cache[key] = doc
                return doc
            else:
                log_info(f"♻️ Cache stale for SGML: {accession_number} — re-downloading.")

        url = construct_sgml_txt_url(cik, accession_number)
        log_info(f"📥 Downloading SGML from SEC for {accession_number}")
        content = self.download_html(url)

        if self.use_cache and write_cache:
            self.write_to_cache(cik, accession_number, content, year)

        doc = SgmlTextDocument(cik=cik, accession_number=accession_number, content=content)
        self.memory_cache[key] = doc
        return doc