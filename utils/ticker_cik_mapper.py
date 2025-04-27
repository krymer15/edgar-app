# edgar-app/utils/ticker_cik_mapper.py

import os
import json
from typing import Optional
from utils.get_project_root import get_project_root

class TickerCIKMapper:
    """
    Utility class to map stock tickers to SEC CIK numbers.
    Loads from the SEC's company_tickers.json file.
    """

    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize the mapper by loading the ticker to CIK mapping.
        Defaults to 'data/raw/company_tickers.json' relative to project root.
        
        Args:
            mapping_file (str): Optional path to a custom mapping JSON file.
        """
        if mapping_file is None:
            mapping_file = os.path.join(get_project_root(), "data/raw/company_tickers.json")

        self.ticker_to_cik = self._load_mapping(mapping_file)

    def _load_mapping(self, filepath: str) -> dict:
        """
        Load ticker to CIK mapping from a JSON file.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            dict: A dictionary mapping lowercased tickers to 10-digit padded CIKs.
        """
        mapping = {}
        try:
            with open(filepath, mode='r', encoding='utf-8') as jsonfile:
                data = json.load(jsonfile)

            for entry in data.values():
                ticker = entry.get("ticker", "").strip().lower()
                cik = str(entry.get("cik_str", "")).zfill(10)  # Always 10 digits
                if ticker and cik:
                    mapping[ticker] = cik

            return mapping
        except FileNotFoundError:
            raise FileNotFoundError(f"Mapping file not found at {filepath}")
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise ValueError(f"Error parsing the company_tickers.json file: {e}")

    def get_cik(self, ticker: str) -> str:
        """
        Get the CIK for a given stock ticker.

        Args:
            ticker (str): The stock ticker symbol.

        Returns:
            str: The corresponding 10-digit CIK.

        Raises:
            ValueError: If the ticker is not found.
        """
        if not ticker:
            raise ValueError("Ticker cannot be empty.")

        normalized_ticker = ticker.strip().lower()
        cik = self.ticker_to_cik.get(normalized_ticker)

        if cik is None:
            raise ValueError(f"Ticker '{ticker}' not found in mapping.")

        return cik
