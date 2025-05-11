# downloaders/sgml_downloader.py

# Role: Downloads SGML .txt using inherited retry logic

import requests
from downloaders.sec_downloader import SECDownloader
from utils.url_builder import construct_sgml_txt_url
from utils.report_logger import log_info, log_warn, log_error

class SgmlDownloader(SECDownloader):
    def download_sgml(self, cik: str, accession_number: str) -> str:
        url = construct_sgml_txt_url(cik, accession_number)
        log_info(f"📥 Downloading SGML for {accession_number}")
        return self.download_html(url)
