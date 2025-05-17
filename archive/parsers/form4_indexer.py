"""
  DEPRECATED: This module is being replaced by form4_sgml_indexer.py.
  Use Form4SgmlIndexer instead for more comprehensive Form 4 processing.
  """

# parsers/sgml/indexers/forms/form4_indexer.py

#TODO plug into rest of app and Form 4 pipeline(s).

"""
This is an indexer that:
    - Extracts metadata from the SGML header section of Form 4 filings
    - Focuses on identifying issuers and reporting owners
    - Handles the 1:N relationship between issuer and owners
    - Doesn't parse transaction details
    - Works directly with raw SGML text files
"""

def extract_issuer_and_reporting_owners(sgml_content: str) -> dict:
    """
    Extract issuer and all reporting owners from a Form 4 SGML filing.
    Handles the case of multiple reporting owners.
    """
    result = {
        "issuer_cik": None,
        "issuer_name": None,
        "reporting_owners": []
    }
    
    # Extract issuer info
    issuer_section_start = sgml_content.find("<ISSUER>")
    if issuer_section_start != -1:
        issuer_section_end = sgml_content.find("</ISSUER>", issuer_section_start)
        issuer_section = sgml_content[issuer_section_start:issuer_section_end]
        
        # Find CIK line
        cik_start = issuer_section.find("CENTRAL INDEX KEY:")
        if cik_start != -1:
            cik_line_end = issuer_section.find("\n", cik_start)
            cik_line = issuer_section[cik_start:cik_line_end]
            cik = ''.join(c for c in cik_line if c.isdigit())
            result["issuer_cik"] = cik
        
        # Find name line
        name_start = issuer_section.find("COMPANY CONFORMED NAME:")
        if name_start != -1:
            name_line_end = issuer_section.find("\n", name_start)
            name_line = issuer_section[name_start:name_line_end]
            name = name_line.split(":", 1)[1].strip() if ":" in name_line else ""
            result["issuer_name"] = name
    
    # Extract all reporting owners (there may be multiple)
    start_pos = 0
    while True:
        owner_start = sgml_content.find("<REPORTING-OWNER>", start_pos)
        if owner_start == -1:
            break
            
        owner_end = sgml_content.find("</REPORTING-OWNER>", owner_start)
        if owner_end == -1:
            break
            
        owner_section = sgml_content[owner_start:owner_end]
        
        # Extract owner CIK
        cik_start = owner_section.find("CENTRAL INDEX KEY:")
        owner_cik = None
        if cik_start != -1:
            cik_line_end = owner_section.find("\n", cik_start)
            cik_line = owner_section[cik_start:cik_line_end]
            owner_cik = ''.join(c for c in cik_line if c.isdigit())
        
        # Extract owner name
        name_start = owner_section.find("COMPANY CONFORMED NAME:")
        owner_name = None
        if name_start != -1:
            name_line_end = owner_section.find("\n", name_start)
            name_line = owner_section[name_start:name_line_end]
            owner_name = name_line.split(":", 1)[1].strip() if ":" in name_line else ""
        
        if owner_cik:
            result["reporting_owners"].append({
                "cik": owner_cik,
                "name": owner_name
            })
        
        start_pos = owner_end + 1
    
    return result