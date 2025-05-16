# parsers/sgml/indexers/sgml_document_indexer.py

'''  
Pure logic for parsing SGML content already in memory. (Utility class) 
- Raw parser for SGML content
'''

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
        Rule-based primary document selection that doesn't rely on regex patterns.
        Uses explicit filename checks and prioritization rules.
        """
        # Filter to only accessible files
        accessible_exhibits = [ex for ex in exhibits if ex["accessible"]]
        if not accessible_exhibits:
            return None
        
        # Track matched files for each priority level
        priority_matches = {
            "priority1": [],  # HTML with sequence 1
            "priority2": [],  # Form-named HTML files
            "priority3": [],  # Any HTML file
            "priority4": []   # XML files
        }
        
        # Process each exhibit
        for ex in accessible_exhibits:
            filename = ex["filename"].lower()
            sequence = seq_map.get(ex["filename"], 999)
            
            # HTML file with sequence 1
            if filename.endswith((".htm", ".html")) and sequence == 1:
                priority_matches["priority1"].append(ex["filename"])
                
            # Form-named HTML files - explicit check for common form names
            elif filename.endswith((".htm", ".html")) and (
                "form" in filename or
                "10-k" in filename or "10k" in filename or
                "10-q" in filename or "10q" in filename or
                "8-k" in filename or "8k" in filename or
                "20-f" in filename or "6-k" in filename or
                "s-1" in filename or "s-3" in filename or "s-4" in filename
            ):
                priority_matches["priority2"].append(ex["filename"])
                
            # Any other HTML file
            elif filename.endswith((".htm", ".html")):
                priority_matches["priority3"].append(ex["filename"])
                
            # XML files
            elif filename.endswith(".xml"):
                priority_matches["priority4"].append(ex["filename"])
        
        # Check priorities in order
        for priority in ["priority1", "priority2", "priority3", "priority4"]:
            if priority_matches[priority]:
                # Sort by sequence number if multiple matches at same priority
                sorted_matches = sorted(priority_matches[priority], 
                                       key=lambda f: seq_map.get(f, 999))
                return sorted_matches[0]
        
        # Fallback: just return the first accessible file
        return accessible_exhibits[0]["filename"] if accessible_exhibits else None

    def _extract_tag(self, tag: str, block: str) -> str:
        """
        Extract content between <TAG> and </TAG> or until newline if no closing tag,
        using string operations instead of regex for better reliability.
        """
        # Define the opening and closing tags
        open_tag = f"<{tag}>"
        close_tag = f"</{tag}>"
        
        # Find the start position
        start_pos = block.find(open_tag)
        if start_pos == -1:
            return ""  # Tag not found
        
        # Move past the opening tag
        start_pos += len(open_tag)
        
        # Look for closing tag
        close_pos = block.find(close_tag, start_pos)
        
        # If closing tag found, extract content between tags
        if close_pos != -1:
            return block[start_pos:close_pos].strip()
        
        # If no closing tag, look for next newline
        newline_pos = block.find("\n", start_pos)
        if newline_pos != -1:
            return block[start_pos:newline_pos].strip()
        
        # If no newline either, return the rest of the content
        return block[start_pos:].strip()

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
    
    def extract_issuer_info(self, txt_contents: str) -> dict:
        """
        Extract issuer information from SGML content.
        Returns a dictionary with issuer details.
        """
        issuer_info = {}
        
        # Find the ISSUER section
        issuer_section_start = txt_contents.find("<ISSUER>")
        if issuer_section_start == -1:
            return issuer_info
            
        issuer_section_end = txt_contents.find("</ISSUER>", issuer_section_start)
        if issuer_section_end == -1:
            issuer_section_end = txt_contents.find("<REPORTING-OWNER>", issuer_section_start)
        
        if issuer_section_end == -1:
            return issuer_info
        
        issuer_section = txt_contents[issuer_section_start:issuer_section_end]
        
        # Extract key information
        cik_start = issuer_section.find("CENTRAL INDEX KEY:")
        if cik_start != -1:
            cik_line_end = issuer_section.find("\n", cik_start)
            if cik_line_end != -1:
                cik_line = issuer_section[cik_start:cik_line_end]
                cik = ''.join(c for c in cik_line if c.isdigit())
                if cik:
                    issuer_info["issuer_cik"] = cik
                    
        # Extract company name
        name_start = issuer_section.find("COMPANY CONFORMED NAME:")
        if name_start != -1:
            name_line_end = issuer_section.find("\n", name_start)
            if name_line_end != -1:
                name_line = issuer_section[name_start:name_line_end]
                parts = name_line.split(":")
                if len(parts) > 1:
                    issuer_info["issuer_name"] = parts[1].strip()
        
        return issuer_info