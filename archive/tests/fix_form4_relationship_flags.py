# Fix for Bug 2: Relationship Flags in Form4Parser
# 
# This code fixes the issue where relationship flags (is_director, is_officer, etc.)
# are not being correctly extracted from XML, particularly when "true"/"false" are used
# instead of "1"/"0".

from parsers.forms.form4_parser import Form4Parser
from models.dataclasses.entity import EntityData
from typing import Dict, Any

# Original method for reference (extract_entity_information has the bug)
original_extract_entity_information = Form4Parser.extract_entity_information

def fixed_extract_entity_information(self, root) -> Dict[str, Any]:
    """
    Extract detailed issuer and reporting owner information from Form 4 XML.
    
    This fixes the bug where boolean flags in relationship info weren't correctly
    parsed when "true"/"false" strings were used instead of "1"/"0".
    
    Args:
        root: XML root element
        
    Returns:
        Dictionary containing issuer and reporting owner information, as well as
        entity objects ready to be used by the writer.
    """
    def get_text(el, path):
        node = el.find(path)
        return node.text.strip() if node is not None and node.text else None
    
    result = {
        "issuer": {},
        "reporting_owners": [],
        "issuer_entity": None,
        "owner_entities": [],
        "relationships": []
    }
    
    # Extract issuer information
    issuer_el = root.find(".//issuer")
    if issuer_el is not None:
        issuer_cik = get_text(issuer_el, "issuerCik")
        issuer_name = get_text(issuer_el, "issuerName")
        issuer_trading_symbol = get_text(issuer_el, "issuerTradingSymbol")
        
        # Create dictionary for the standard parsed output
        result["issuer"] = {
            "cik": issuer_cik,
            "name": issuer_name,
            "trading_symbol": issuer_trading_symbol
        }
        
        # Create EntityData object for direct use in the writer
        result["issuer_entity"] = EntityData(
            cik=issuer_cik,
            name=issuer_name,
            entity_type="company",
            # Additional metadata that might be useful
            source_accession=self.accession_number
        )
    
    # Extract reporting owner information
    for owner_el in root.findall(".//reportingOwner"):
        # First get the owner identity information
        owner_id_el = owner_el.find("./reportingOwnerId")
        if owner_id_el is None:
            continue
            
        owner_cik = get_text(owner_id_el, "rptOwnerCik")
        owner_name = get_text(owner_id_el, "rptOwnerName")
        
        # Then get relationship information
        rel_el = owner_el.find("./reportingOwnerRelationship")
        
        # FIX: More robust boolean flag handling
        # Accept both "1" and "true" as True values
        is_director_text = get_text(rel_el, "isDirector") if rel_el is not None else None
        is_officer_text = get_text(rel_el, "isOfficer") if rel_el is not None else None
        is_ten_percent_owner_text = get_text(rel_el, "isTenPercentOwner") if rel_el is not None else None
        is_other_text = get_text(rel_el, "isOther") if rel_el is not None else None
        
        is_director = is_director_text == "1" or is_director_text == "true" if is_director_text else False
        is_officer = is_officer_text == "1" or is_officer_text == "true" if is_officer_text else False
        is_ten_percent_owner = is_ten_percent_owner_text == "1" or is_ten_percent_owner_text == "true" if is_ten_percent_owner_text else False
        is_other = is_other_text == "1" or is_other_text == "true" if is_other_text else False
        
        officer_title = get_text(rel_el, "officerTitle") if is_officer else None
        other_text = get_text(rel_el, "otherText") if is_other else None
        
        # Get address information if available
        address_el = owner_el.find("./reportingOwnerAddress")
        address = {}
        if address_el is not None:
            address = {
                "street1": get_text(address_el, "rptOwnerStreet1"),
                "street2": get_text(address_el, "rptOwnerStreet2"),
                "city": get_text(address_el, "rptOwnerCity"),
                "state": get_text(address_el, "rptOwnerState"),
                "zip": get_text(address_el, "rptOwnerZipCode"),
                "state_description": get_text(address_el, "rptOwnerStateDescription")
            }
        
        # Create dictionary for standard parsed output
        owner_data = {
            "cik": owner_cik,
            "name": owner_name,
            "is_director": is_director,
            "is_officer": is_officer,
            "is_ten_percent_owner": is_ten_percent_owner,
            "is_other": is_other,
            "officer_title": officer_title,
            "other_text": other_text,
            "address": address
        }
        result["reporting_owners"].append(owner_data)
        
        # Determine entity type based on name heuristics
        entity_type = "company"
        if owner_name and not any(business_term in owner_name.lower() 
                                 for business_term in ["corp", "inc", "llc", "lp", "trust", "partners", "fund"]):
            entity_type = "person"
            
        # Create EntityData object for direct use in the writer
        owner_entity = EntityData(
            cik=owner_cik,
            name=owner_name,
            entity_type=entity_type,
            source_accession=self.accession_number
        )
        result["owner_entities"].append(owner_entity)
        
        # Create relationship data for direct use in the Form4Orchestrator
        relationship = {
            "issuer_cik": result["issuer"]["cik"],
            "owner_cik": owner_cik,
            "is_director": is_director,
            "is_officer": is_officer,
            "is_ten_percent_owner": is_ten_percent_owner,
            "is_other": is_other,
            "officer_title": officer_title,
            "other_text": other_text
        }
        result["relationships"].append(relationship)
    
    return result

# Function to apply this fix
def apply_fix():
    """Apply the fix to Form4Parser.extract_entity_information"""
    # Keep a reference to the original method for testing/rollback
    Form4Parser._original_extract_entity_information = Form4Parser.extract_entity_information
    
    # Replace with fixed method
    Form4Parser.extract_entity_information = fixed_extract_entity_information
    
    return "Fixed Form4Parser.extract_entity_information with better boolean handling"

# Function to rollback the fix
def rollback_fix():
    """Rollback the fix if needed"""
    if hasattr(Form4Parser, '_original_extract_entity_information'):
        Form4Parser.extract_entity_information = Form4Parser._original_extract_entity_information
        delattr(Form4Parser, '_original_extract_entity_information')
        return "Rolled back Form4Parser.extract_entity_information fix"
    return "No original method found to rollback"

if __name__ == "__main__":
    print("Applying fix for Form4Parser.extract_entity_information...")
    result = apply_fix()
    print(result)
    
    # Also apply fix to Form4SgmlIndexer - we need to create similar fix for that class
    # This would be implemented separately in a production fix