from parsers.base_parser import BaseParser
from lxml import html
import re
from utils.report_logger import log_debug, log_warn, log_error

class IndexPageParser(BaseParser):
    def parse(self, raw_html: str, url: str = None, cik: str = None, form_type: str = None, filing_date: str = None) -> dict:
        """
        Extract accession number and embedded document URL using lxml for reliable parsing.
        """
        accession_number = None
        if url:
            match = re.search(r'/data/\d+/(\d{10}-\d{2}-\d{6})-index\.htm', url)
            if match:
                accession_number = match.group(1).replace("-", "")
        accession_number = accession_number or "unknown"

        primary_url = None
        try:
            doc = html.fromstring(raw_html)
            rows = doc.xpath('//table[@summary="Document Format Files"]//tr[position() > 1]')

            if rows:
                log_debug("🔍 Embedded doc table row found.")

                # Grab the first row’s document link cell
                first_doc_cell = rows[0].xpath('./td[3]/a')
                if first_doc_cell:
                    raw_element = first_doc_cell[0]
                    raw_href = raw_element.get("href", "")

                    # 🧪 DIAGNOSTIC: Save and print raw href before processing
                    log_debug(f"🧪 Raw embedded href (as extracted): `{raw_href}`")
                    with open("diagnostics_last_raw_href.txt", "w", encoding="utf-8") as f:
                        f.write(raw_href)

                    # Now clean and normalize
                    raw_link = raw_href.strip()
                    if raw_link.startswith("/ix?doc="):
                        raw_link = raw_link.replace("/ix?doc=", "")
                    if raw_link.startswith("/"):
                        primary_url = f"https://www.sec.gov{raw_link}"
                    else:
                        primary_url = raw_link

                    # Final whitespace cleanup
                    primary_url = re.sub(r"\s+", "", primary_url)
                else:
                    log_warn("Could not find <a> inside third column of row.")
            else:
                log_warn("No rows found in Document Format Files table.")


        except Exception as e:
            log_error(f"Failed to parse embedded URL from index.html: {e}")
            primary_url = None

        return {
            "accession_number": accession_number,
            "primary_document_url": primary_url,
        }
