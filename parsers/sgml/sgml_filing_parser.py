# sgml_filing_parser.py

'''  
Pure logic for parsing SGML content already in memory. (Utility class) 
- Raw parser for SGML content
'''

import re
from typing import List, Optional
from utils.url_builder import construct_primary_document_url, normalize_cik
from parsers.base_parser import BaseParser
from models.dataclasses.parsed_document import ParsedDocument
from utils.report_logger import log_debug

IGNORE_EXTENSIONS = (
    ".js", ".css", ".xlsx", ".zip", ".json",
    ".pdf", ".doc", ".docx", ".xls", ".ppt", ".pptx", ".exe"
)

KNOWN_NOISE = ("SIGNATURE", "SIGNATURES", "EX-24", "IDEA: XBRL DOCUMENT")


class SgmlFilingParser(BaseParser):
    def __init__(self, cik: str, accession_number: str, form_type: str):
        self.cik = cik
        self.accession_number = accession_number
        self.form_type = form_type

    def parse(self, txt_contents: str) -> dict:
        """
        Legacy-style parser that returns primary_doc URL + raw exhibit dicts.
        Prefer `parse_to_documents()` for production use.
        """
        entries = txt_contents.split("<DOCUMENT>")
        exhibits = []

        for entry in entries[1:]:
            filename = self._extract_tag("FILENAME", entry)
            description = self._extract_tag("DESCRIPTION", entry)
            ex_type = self._extract_tag("TYPE", entry)

            accessible = not (
                filename.lower().endswith(IGNORE_EXTENSIONS)
                or description.upper().strip() in KNOWN_NOISE
                or ex_type.upper().strip() in KNOWN_NOISE
            )

            if not accessible:
                log_debug(f"[SKIPPED] Binary or noise exhibit: {filename}")

            exhibits.append({
                "filename": filename,
                "description": description,
                "type": ex_type,
                "accessible": accessible
            })

        # ✅ Improved primary_doc logic
        primary_doc = None
        html_like = [
            ex for ex in exhibits
            if ex["accessible"] and ex["filename"].lower().endswith((".xml", ".htm", ".html"))
        ]

        if html_like:
            html_like.sort(key=lambda x: x["filename"].lower())
            primary_doc = html_like[0]["filename"]
        else:
            for ex in exhibits:
                if ex["accessible"] and (
                    self.form_type.lower() in ex.get("type", "").lower()
                    or self.form_type.lower() in ex.get("description", "").lower()
                ):
                    primary_doc = ex["filename"]
                    break

        return {
            "primary_document_url": construct_primary_document_url(
                self.cik, self.accession_number, primary_doc
            ) if primary_doc else None,
            "exhibits": exhibits
        }

    def _extract_tag(self, tag: str, block: str) -> str:
        match = re.search(rf"<{tag}>(.*?)\n", block)
        return match.group(1).strip() if match else ""

    def parse_to_documents(self, txt_contents: str) -> List[ParsedDocument]:
        result = self.parse(txt_contents)
        primary_doc_url = result.get("primary_document_url")
        exhibits = result.get("exhibits", [])

        documents = []
        for ex in exhibits:
            filename = ex.get("filename", "").strip()
            source_url = f"https://www.sec.gov/Archives/edgar/data/{normalize_cik(self.cik)}/{self.accession_number.replace('-', '')}/{filename}"

            documents.append(ParsedDocument(
                cik=self.cik,
                accession_number=self.accession_number,
                form_type=self.form_type,
                filename=filename,
                description=ex.get("description"),
                type=ex.get("type"),
                source_url=source_url,
                is_primary=(primary_doc_url and filename in primary_doc_url),
                is_exhibit=not filename.lower().endswith(".xml"),
                is_data_support=filename.lower().endswith(".xml"),
                accessible=ex.get("accessible", True)
            ))

        return documents