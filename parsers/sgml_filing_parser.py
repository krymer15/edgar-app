# sgml_filing_parser.py (place under parsers/)
import re
from parsers.base_parser import BaseParser

class SgmlFilingParser(BaseParser):
    def __init__(self, cik: str, accession: str, form_type: str):
        self.cik = cik
        self.accession = accession
        self.form_type = form_type

    def parse(self, txt_contents: str):
        exhibits = []
        entries = txt_contents.split("<SEQUENCE>")
        IGNORE_EXTENSIONS = (".js", ".css", ".xlsx", ".zip", ".json")
        KNOWN_NOISE = ("IDEA: XBRL DOCUMENT",)

        for entry in entries:
            filename_match = re.search(r"<FILENAME>\s*(.+)", entry)
            desc_match = re.search(r"<DESCRIPTION>\s*(.+)", entry)
            type_match = re.search(r"<TYPE>\s*(.+)", entry)

            if filename_match:
                filename = filename_match.group(1).strip()
                description = desc_match.group(1).strip() if desc_match else ""
                ex_type = type_match.group(1).strip() if type_match else ""

                accessible = not (
                    filename.lower().endswith(IGNORE_EXTENSIONS)
                    or description.upper().strip() in KNOWN_NOISE
                    or ex_type.upper().strip() in KNOWN_NOISE
                )

                exhibits.append({
                    "filename": filename,
                    "description": description,
                    "type": ex_type,
                    "accessible": accessible
                })

        primary_doc = None
        for exhibit in exhibits:
            if exhibit["accessible"] and (
                self.form_type.lower() in exhibit["type"].lower()
                or self.form_type.lower() in exhibit["description"].lower()
            ):
                primary_doc = exhibit["filename"]
                break

        if not primary_doc:
            for exhibit in exhibits:
                if exhibit["accessible"] and exhibit["filename"].lower().endswith(".htm"):
                    primary_doc = exhibit["filename"]
                    break

        base_url = f"https://www.sec.gov/Archives/edgar/data/{int(self.cik)}/{self.accession.replace('-', '')}"
        primary_doc_url = f"{base_url}/{primary_doc}" if primary_doc else None

        return {
            "exhibits": exhibits,
            "primary_document_url": primary_doc_url
        }
