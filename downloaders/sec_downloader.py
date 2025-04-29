# downloaders/sec_downloader.py (refactored)

import time
import requests
from downloaders.base_downloader import BaseDownloader

class SECDownloader(BaseDownloader):
    def __init__(self, user_agent: str, request_delay_seconds: float = 1.0):
        """
        Initializes the SECDownloader with a user agent and polite request delay.
        """
        if not user_agent:
            raise ValueError("user_agent must be provided to SECDownloader.")

        self.user_agent = user_agent
        self.delay = request_delay_seconds
        self.last_request_time = None

    def download(self, url: str) -> str:
        return self.download_html(url)

    def _throttle(self):
        """Ensure polite delay between SEC requests."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.delay:
                time.sleep(self.delay - elapsed)

    def _make_request(self, url: str) -> requests.Response:
        """Internal method to make a GET request with headers."""
        headers = {"User-Agent": self.user_agent}
        response = requests.get(url, headers=headers, timeout=10)
        return response

    def download_html(self, url: str) -> str:
        """
        Downloads raw HTML from the given SEC URL.
        Returns HTML content as a string.
        """
        self._throttle()
        try:
            response = self._make_request(url)
            self.last_request_time = time.time()

            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Network error occurred while fetching {url}: {str(e)}")

    def download_json(self, url: str) -> dict:
        """
        Downloads JSON data from a given SEC URL.
        """
        self._throttle()
        try:
            response = self._make_request(url)
            self.last_request_time = time.time()

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to fetch URL: {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Network error occurred while fetching {url}: {str(e)}")
