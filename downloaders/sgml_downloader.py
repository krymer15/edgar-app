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
        """
        Initializes the SGML downloader.

        Parameters:
            user_agent (str): User agent string to include in SEC requests.
            use_cache (bool): 
                If True, enables reading and writing to the local file-based SGML cache.
                If False, disables all disk-based cache behavior (default).
        """        
        super().__init__(user_agent=user_agent, request_delay_seconds=request_delay_seconds)
        self.use_cache = use_cache
        self.memory_cache = {} # key: (cik, accession, year) → value: SgmlTextDocument
        self.url_cache = {}   # key: url → value: content

    def clear_memory_cache(self):
        """Clear both memory caches."""
        self.memory_cache.clear()
        self.url_cache.clear()

    def has_in_memory_cache(self, url: str) -> bool:
        """Check if a URL is in the memory cache."""
        return url in self.url_cache

    def get_from_memory_cache(self, url: str) -> str:
        """Get content from memory cache by URL."""
        return self.url_cache.get(url, "")

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
        """
        Attempts to read an SGML file from the local cache directory.

        Returns:
            str or None: The file content if found, else None.

        Notes:
            This method is only used if `use_cache` is True.
        """
        path = build_cache_path(cik, accession_number, year)
        if not path:
            raise ValueError(f"[read_from_cache] Missing cache path for {accession_number}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def write_to_cache(self, cik: str, accession_number: str, content: str, year: str):
        """
        Writes the SGML content to the local cache directory.

        Parameters:
            content (str): The raw SGML text to save.

        Notes:
            This is gated by `use_cache` or overridden via `write_cache=True`.
        """
        path = build_cache_path(cik, accession_number, year)
        log_info(f"[WRITE] Caching SGML: {accession_number} → {path}")

        if not path:
            log_warn(f"[write_to_cache] No cache path for {accession_number}, skipping write.")
            return
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def download_sgml(self, cik: str, accession_number: str, year: str = None, *, write_cache: bool = None) -> SgmlTextDocument:
        """
        Downloads the SGML submission text file for a given filing.

        This method supports optional in-memory caching (always enabled by default)
        and optional file-based caching (deprecated by default unless explicitly enabled).

        Parameters:
            cik (str): Central Index Key of the company.
            accession_number (str): Accession number of the filing.
            year (str): Four-digit year of the filing.
            write_cache (bool, optional): 
                If True, writes the downloaded SGML to disk (cache_sgml/).
                If False, disables disk write even if self.use_cache is True.
                If None (default), uses the value of self.use_cache to decide.

        Returns:
            SgmlTextDocument: An object containing the SGML content and metadata.

        Notes:
            - If `self.use_cache` is False, no file-based caching will be used regardless of write_cache.
            - If the SGML is already in memory (from a prior download), it will be reused directly.
            - Disk caching is primarily retained for testing and offline debugging.
        """
        # If year wasn't provided, extract it from accession
        if year is None and len(accession_number) >= 10:
            year_short = accession_number.split('-')[1] if '-' in accession_number else accession_number[2:4]
            year = f"20{year_short}"  # Assuming all years are 2000+
            
        key = (cik, accession_number, year)
        url = construct_sgml_txt_url(cik, accession_number.replace('-', ''))
        
        # Update url_cache with this URL for future lookups
        if key in self.memory_cache:
            # Also update the URL cache for direct lookups
            content = self.memory_cache[key].content
            self.url_cache[url] = content
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
                self.url_cache[url] = content  # Also update the URL cache
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
        self.url_cache[url] = content  # Also update the URL cache
        return doc