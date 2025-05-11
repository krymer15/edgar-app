# downloaders/sgml_downloader.py

'''
# Role: Downloads SGML .txt using inherited retry logic
- Uses caching to mitigate using SgmlDownloader twice upon parsing metadata and then writing sgml to disk.
'''

import os
import time
from downloaders.sec_downloader import SECDownloader
from utils.path_manager import build_cache_path
from utils.url_builder import construct_sgml_txt_url
from utils.report_logger import log_info, log_warn, log_error

class SgmlDownloader(SECDownloader):
    def __init__(self, user_agent: str, request_delay_seconds: float = 1.0, use_cache: bool = True):
        super().__init__(user_agent=user_agent, request_delay_seconds=request_delay_seconds)
        self.use_cache = use_cache

    def is_stale(self, path: str, max_age_seconds: int) -> bool:
        try:
            modified = os.path.getmtime(path)
            return (time.time() - modified) > max_age_seconds
        except OSError:
            return True  # Treat unreadable or missing file as stale

    def is_cached(self, cik: str, accession_number: str) -> bool:
        return os.path.exists(build_cache_path(cik, accession_number))

    def read_from_cache(self, cik: str, accession_number: str) -> str:
        path = build_cache_path(cik, accession_number)
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Cache read failed at {path}: {str(e)}")

    def write_to_cache(self, cik: str, accession_number: str, content: str):
        path = build_cache_path(cik, accession_number)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def download_sgml(self, cik: str, accession_number: str) -> str:
        path = build_cache_path(cik, accession_number)
        
        if self.use_cache and self.is_cached(cik, accession_number):
            if not self.is_stale(path, max_age_seconds=86400):  # 24-hour TTL cache invalidation
                log_info(f"⚡ Cache hit for SGML: {accession_number}")
                return self.read_from_cache(cik, accession_number)
            else:
                log_info(f"♻️ Cache stale for SGML: {accession_number} — re-downloading.")

        url = construct_sgml_txt_url(cik, accession_number)
        log_info(f"📥 Downloading SGML from SEC for {accession_number}")
        content = self.download_html(url)

        if self.use_cache:
            self.write_to_cache(cik, accession_number, content)

        return content