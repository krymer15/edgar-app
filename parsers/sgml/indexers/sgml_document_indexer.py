# parsers/sgml/indexers/sgml_document_indexer.py

'''  
Pure logic for parsing SGML content already in memory. (Utility class) 
- Raw parser for SGML content
'''

import re
from typing import List, Optional
from utils.url_builder import construct_primary_document_url, normalize_cik
from parsers.base_parser import BaseParser
from models.dataclasses.filing_document_metadata import FilingDocumentMetadata
from utils.report_logger import log_debug

IGNORE_EXTENSIONS = (
    ".js", ".css", ".xlsx", ".zip", ".json",
    ".pdf", ".doc", ".docx", ".xls", ".ppt", ".pptx", ".exe"
)

KNOWN_NOISE = ("SIGNATURE", "SIGNATURES", "EX-24", "IDEA: XBRL DOCUMENT")

# Priority patterns for primary documents
PRIMARY_DOC_PATTERNS = [
    # Common filing main documents (case insensitive)
    r"form.*8-k", r"form.*10-k", r"form.*10-q", r"form.*20-f", 
    r"8-k", r"10-k", r"10-q", r"20-f", r"6-k",
    r"^8k", r"^10k", r"^10q",
    # Registration statements
    r"form.*s-1", r"form.*s-3", r"form.*s-4", r"s-1", r"s-3", r"s-4"
]


class SgmlDocumentIndexer(BaseParser):
    '''
    Indexes SGML .txt content to extract document metadata pointers (FilingDocumentMetadata) for each declared exhibit or primary document.
    '''
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
        
        # Track sequence numbers if available
        seq_map = {}

        for idx, entry in enumerate(entries[1:]):
            filename = self._extract_tag("FILENAME", entry)
            description = self._extract_tag("DESCRIPTION", entry)
            ex_type = self._extract_tag("TYPE", entry)
            
            # Try to extract sequence number
            seq_num = self._extract_tag("SEQUENCE", entry)
            if seq_num and seq_num.isdigit():
                seq_num = int(seq_num)
            else:
                # Fall back to document order if no sequence
                seq_num = idx + 1
                
            # Store the sequence number with the exhibit
            seq_map[filename] = seq_num

            accessible = not (
                filename.lower().endswith(IGNORE_EXTENSIONS)
                or description.upper().strip() in KNOWN_NOISE
                or ex_type.upper().strip() in KNOWN_NOISE
            )

            if not accessible:
                log_debug(f"[MARKED NON-ACCESSIBLE] Binary or noise exhibit: {filename}")

            exhibits.append({
                "filename": filename,
                "description": description,
                "type": ex_type,
                "accessible": accessible,
                "sequence": seq_num
            })

        # Improved primary_doc selection logic
        primary_doc = self._select_primary_document(exhibits, seq_map)
        
        if primary_doc:
            log_debug(f"[SELECTED PRIMARY] {primary_doc}")
        else:
            log_debug("[WARNING] No primary document identified")

        return {
            "primary_document_url": construct_primary_document_url(
                self.cik, self.accession_number, primary_doc
            ) if primary_doc else None,
            "exhibits": exhibits
        }
    
    def _select_primary_document(self, exhibits, seq_map):
        """
        Improved primary document selection with multiple heuristics:
        1. First try to find an HTM/HTML file with sequence=1
        2. Then try to find a file matching common form patterns
        3. Fall back to the first HTM/HTML file if available
        4. Otherwise use the first accessible XML file
        """
        # Filter to only accessible files
        accessible_exhibits = [ex for ex in exhibits if ex["accessible"]]
        if not accessible_exhibits:
            return None
            
        # Priority 1: HTML/HTM files with sequence 1
        seq_1_html = [
            ex["filename"] for ex in accessible_exhibits 
            if (ex["filename"].lower().endswith((".htm", ".html")) and 
                seq_map.get(ex["filename"]) == 1)
        ]
        if seq_1_html:
            return seq_1_html[0]
            
        # Priority 2: Files matching primary document patterns
        for pattern in PRIMARY_DOC_PATTERNS:
            pattern_regex = re.compile(pattern, re.IGNORECASE)
            matching_files = [
                ex["filename"] for ex in accessible_exhibits
                if pattern_regex.search(ex["filename"])
            ]
            
            # Prefer HTML files first, then any match
            html_matches = [f for f in matching_files if f.lower().endswith((".htm", ".html"))]
            if html_matches:
                return html_matches[0]
            elif matching_files:
                return matching_files[0]
                
        # Priority 3: Any HTM/HTML file (sorted by sequence)
        html_files = [
            ex["filename"] for ex in accessible_exhibits
            if ex["filename"].lower().endswith((".htm", ".html"))
        ]
        if html_files:
            # Sort by sequence number
            html_files.sort(key=lambda f: seq_map.get(f, 999))
            return html_files[0]
            
        # Priority 4: XML files as last resort
        xml_files = [
            ex["filename"] for ex in accessible_exhibits
            if ex["filename"].lower().endswith(".xml")
        ]
        if xml_files:
            xml_files.sort(key=lambda f: seq_map.get(f, 999))
            return xml_files[0]
            
        # Fallback: just return the first accessible file
        return accessible_exhibits[0]["filename"]

    def _extract_tag(self, tag: str, block: str) -> str:
        match = re.search(rf"<{tag}>(.*?)\n", block)
        return match.group(1).strip() if match else ""

    def index_documents(self, txt_contents: str) -> list[FilingDocumentMetadata]:
        """
        Parses the SGML `.txt` content and returns a list of FilingDocumentMetadata pointers.
        Each represents an embedded document (exhibit, primary, or supporting file).
        """
        result: dict = self.parse(txt_contents)
        primary_doc_url = result.get("primary_document_url")
        exhibits = result.get("exhibits", [])

        documents = []
        for ex in exhibits:
            filename = ex.get("filename", "").strip()
            source_url = f"https://www.sec.gov/Archives/edgar/data/{normalize_cik(self.cik)}/{self.accession_number.replace('-', '')}/{filename}"

            documents.append(FilingDocumentMetadata(
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