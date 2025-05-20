# Fix for Bug 1: Owner Count in Form4SgmlIndexer
# 
# This code fixes the issue where Form4SgmlIndexer is incorrectly counting
# reporting owners by adding deduplication by CIK.

from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from models.dataclasses.entity import EntityData
from typing import List, Dict, Optional, Tuple, Any
import re
from utils.report_logger import log_info, log_warn, log_error

# Original method for reference
original_extract_reporting_owners = Form4SgmlIndexer._extract_reporting_owners

def fixed_extract_reporting_owners(self, txt_contents: str) -> List[Dict]:
    """
    Extract all reporting owners from SGML content with deduplication.
    
    This fixes the bug where owners might be counted twice (from SGML and XML).
    """
    owners = []
    owner_ciks = set()  # Track unique CIKs to avoid duplication
    
    # First try with explicit REPORTING-OWNER tags
    start_pos = 0
    while True:
        owner_start = txt_contents.find("REPORTING-OWNER:", start_pos)
        if owner_start == -1:
            owner_start = txt_contents.find("<REPORTING-OWNER>", start_pos)
            if owner_start == -1:
                break
        
        # Find the next section or the end of the file
        next_section_start = txt_contents.find("\n\n", owner_start + 1)
        if next_section_start == -1:
            owner_end = len(txt_contents)
        else:
            # Look for actual end tag
            owner_end_tag = txt_contents.find("</REPORTING-OWNER>", owner_start)
            if owner_end_tag != -1 and owner_end_tag < next_section_start:
                owner_end = owner_end_tag
            else:
                owner_end = next_section_start
        
        # Extract the owner section
        owner_section = txt_contents[owner_start:owner_end]
        
        # Extract owner data section
        owner_data_start = owner_section.find("OWNER DATA:")
        if owner_data_start != -1:
            # Extract the subsection for owner data
            owner_data_section = owner_section[owner_data_start:]
            
            # Extract CIK
            cik = self._extract_value(owner_data_section, "CENTRAL INDEX KEY:")
            
            # Extract name
            name = self._extract_value(owner_data_section, "COMPANY CONFORMED NAME:")
            
            # If we found valid owner data, create an entity
            if cik:
                # Check if this CIK already exists - DEDUPLICATION HERE
                if cik in owner_ciks:
                    log_info(f"Skipping duplicate owner CIK: {cik}")
                else:
                    owner_ciks.add(cik)
                    
                    # Determine if individual or company
                    entity_type = "person"
                    if name and any(business_term in name.lower() for business_term in ["corp", "inc", "llc", "lp", "trust", "partners", "fund"]):
                        entity_type = "company"
                    
                    # Create owner data dictionary
                    owner_data = {
                        "entity": EntityData(
                            cik=cik,
                            name=name or f"Unknown Owner ({cik})",
                            entity_type=entity_type
                        )
                    }
                    
                    # Initialize relationship fields (will be populated from XML later)
                    owner_data["is_director"] = False
                    owner_data["is_officer"] = False
                    owner_data["is_ten_percent_owner"] = False
                    owner_data["is_other"] = False
                    owner_data["officer_title"] = None
                    
                    owners.append(owner_data)
        
        # Move to the next section
        start_pos = owner_end + 1
    
    # If no owners found with primary method, try a fallback approach
    if not owners:
        # Find all CIKs in the SGML header section
        header_end = txt_contents.find("</SEC-HEADER>")
        if header_end == -1:
            header_end = txt_contents.find("<DOCUMENT>")
        
        if header_end != -1:
            header_section = txt_contents[:header_end]
            cik_matches = re.finditer(r"CENTRAL INDEX KEY:\s+(\d+)", header_section)
            
            # Create an owner for each unique CIK found
            unique_ciks = set()
            for match in cik_matches:
                cik = match.group(1)
                if cik != self.cik and cik not in unique_ciks:  # Skip issuer CIK
                    unique_ciks.add(cik)
                    
                    # Try to find name near this CIK mention
                    surrounding_text = header_section[max(0, match.start() - 100):min(len(header_section), match.start() + 100)]
                    name_match = re.search(r"COMPANY CONFORMED NAME:\s+([^\n]+)", surrounding_text)
                    name = name_match.group(1) if name_match else f"Unknown Owner ({cik})"
                    
                    entity_type = "company"  # Default assumption
                    owner_data = {
                        "entity": EntityData(
                            cik=cik,
                            name=name,
                            entity_type=entity_type
                        )
                    }
                    
                    # Initialize relationship fields
                    owner_data["is_director"] = False
                    owner_data["is_officer"] = False
                    owner_data["is_ten_percent_owner"] = False
                    owner_data["is_other"] = False
                    owner_data["officer_title"] = None
                    
                    # Only add if the CIK is not already in owner_ciks - DEDUPLICATION HERE
                    if cik not in owner_ciks:
                        owner_ciks.add(cik)
                        owners.append(owner_data)
    
    # Log the results
    if owners:
        log_info(f"Extracted {len(owners)} unique reporting owners")
    else:
        log_warn(f"No reporting owners found in filing {self.accession_number}")
    
    return owners

# Function to apply this fix
def apply_fix():
    """Apply the fix to Form4SgmlIndexer._extract_reporting_owners"""
    # Keep a reference to the original method for testing/rollback
    Form4SgmlIndexer._original_extract_reporting_owners = Form4SgmlIndexer._extract_reporting_owners
    
    # Replace with fixed method
    Form4SgmlIndexer._extract_reporting_owners = fixed_extract_reporting_owners
    
    return "Fixed Form4SgmlIndexer._extract_reporting_owners with deduplication"

# Function to rollback the fix
def rollback_fix():
    """Rollback the fix if needed"""
    if hasattr(Form4SgmlIndexer, '_original_extract_reporting_owners'):
        Form4SgmlIndexer._extract_reporting_owners = Form4SgmlIndexer._original_extract_reporting_owners
        delattr(Form4SgmlIndexer, '_original_extract_reporting_owners')
        return "Rolled back Form4SgmlIndexer._extract_reporting_owners fix"
    return "No original method found to rollback"

if __name__ == "__main__":
    print("Applying fix for Form4SgmlIndexer._extract_reporting_owners...")
    result = apply_fix()
    print(result)