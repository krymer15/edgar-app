# parsers/forms/form10k_parser.py

from parsers.base_parser import BaseParser
from lxml import etree
import io

class Form10KParser(BaseParser):
    def parse(self, xml_or_html_content: str) -> dict:
        try:
            # TODO: Switch between XML (XBRL) vs HTML parsing based on content_type
            tree = etree.parse(io.StringIO(xml_or_html_content))
            root = tree.getroot()

            # Placeholder: parse XBRL tags or fallback HTML
            results = {
                "companyName": root.findtext(".//dei:EntityRegistrantName", namespaces={"dei": "http://xbrl.sec.gov/dei/2020"}),
                "fiscalYearEnd": root.findtext(".//dei:DocumentFiscalYearFocus", namespaces={"dei": "http://xbrl.sec.gov/dei/2020"}),
                "documentType": root.findtext(".//dei:DocumentType", namespaces={"dei": "http://xbrl.sec.gov/dei/2020"}),
            }

            return {
                "parsed_type": "form_10k",
                "content_type": "xml",
                "parsed_data": results
            }

        except Exception as e:
            return {
                "parsed_type": "form_10k",
                "error": str(e)
            }
