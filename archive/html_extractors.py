from lxml import html
from typing import Optional

def extract_embedded_url(raw_html: str) -> Optional[str]:
    """
    Backup method for extracting embedded document URLs using XPath.
    Currently not used in pipeline — primary logic lives in index_page_parser.py.
    """
    try:
        tree = html.fromstring(raw_html)
        hrefs = tree.xpath("//a/@href")
        for href in hrefs:
            clean_href = href.strip().replace(" ", "")
            if "Archives/edgar/data" in clean_href and (
                "primary_doc" in clean_href or
                clean_href.endswith(".xml") or
                clean_href.endswith(".htm") or
                clean_href.endswith(".html")
            ):
                if "/ix?doc=" in clean_href:
                    clean_href = clean_href.split("/ix?doc=")[-1]
                    clean_href = f"https://www.sec.gov{clean_href}"
                elif clean_href.startswith("/"):
                    clean_href = f"https://www.sec.gov{clean_href}"
                return clean_href
        return None
    except Exception as e:
        print(f"[ERROR] Failed to extract embedded URL: {e}")
        return None
