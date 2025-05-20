# Fix for Bug 4: Form4 Multiple Owners Flag
# 
# This code fixes the issue where the has_multiple_owners flag is incorrectly
# set to True when there's only one owner.

from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from datetime import datetime
from typing import Dict, Any
from utils.report_logger import log_info, log_warn, log_error

# Original method for reference
original_update_form4_data_from_xml = Form4SgmlIndexer._update_form4_data_from_xml

def fixed_update_form4_data_from_xml(self, form4_data: Form4FilingData, entity_data: Dict[str, Any], parsed_xml: Dict = None) -> None:
    """
    Update Form4FilingData with more accurate entity information from XML.
    
    This fixes the bug where has_multiple_owners is not being correctly updated
    after relationships are changed.
    
    Args:
        form4_data: The Form4FilingData object to update
        entity_data: Dictionary containing entity information from XML
        parsed_xml: Full parsed XML data if available (contains transactions)
    """
    try:
        # Clear existing relationships that were created from SGML
        form4_data.relationships = []
        
        # Also clear transactions to avoid duplicates
        form4_data.transactions = []
        
        # Get the issuer entity from XML
        issuer_entity = entity_data.get("issuer_entity")
        if not issuer_entity:
            log_warn(f"No issuer entity found in XML for {self.accession_number}")
            return
            
        # Get owner entities from XML
        owner_entities = entity_data.get("owner_entities", [])
        if not owner_entities:
            log_warn(f"No owner entities found in XML for {self.accession_number}")
            return
            
        # Get relationship information from XML
        relationships = entity_data.get("relationships", [])
        if not relationships:
            log_warn(f"No relationships found in XML for {self.accession_number}")
            return
        
        # Attach entities directly to form4_data for use by Form4Writer
        form4_data.issuer_entity = issuer_entity
        form4_data.owner_entities = owner_entities
            
        # Create relationships using the accurate entity information
        filing_date = form4_data.period_of_report or datetime.now().date()
        
        for owner_entity, rel_data in zip(owner_entities, relationships):
            # Create relationship with proper entity IDs
            relationship = Form4RelationshipData(
                issuer_entity_id=issuer_entity.id,
                owner_entity_id=owner_entity.id,
                filing_date=filing_date,
                is_director=rel_data.get("is_director", False),
                is_officer=rel_data.get("is_officer", False),
                is_ten_percent_owner=rel_data.get("is_ten_percent_owner", False),
                is_other=rel_data.get("is_other", False),
                officer_title=rel_data.get("officer_title"),
                other_text=rel_data.get("other_text"),
            )
            
            # Add to form4_data
            form4_data.add_relationship(relationship)
            
        log_info(f"Updated Form4FilingData with {len(form4_data.relationships)} relationships from XML")
        log_info(f"Attached issuer_entity and {len(owner_entities)} owner_entities directly to Form4FilingData")
        
        # THIS IS THE FIX - Explicitly update the has_multiple_owners flag
        form4_data.has_multiple_owners = len(form4_data.relationships) > 1
        log_info(f"Set has_multiple_owners to {form4_data.has_multiple_owners} based on {len(form4_data.relationships)} relationships")
        
    except Exception as e:
        log_error(f"Error updating Form4FilingData from XML: {e}")
        # If an error occurs, we'll keep the original SGML-based entities

# Function to apply this fix
def apply_fix():
    """Apply the fix to Form4SgmlIndexer._update_form4_data_from_xml"""
    # Keep a reference to the original method for testing/rollback
    Form4SgmlIndexer._original_update_form4_data_from_xml = Form4SgmlIndexer._update_form4_data_from_xml
    
    # Replace with fixed method
    Form4SgmlIndexer._update_form4_data_from_xml = fixed_update_form4_data_from_xml
    
    return "Fixed Form4SgmlIndexer._update_form4_data_from_xml with explicit has_multiple_owners update"

# Function to rollback the fix
def rollback_fix():
    """Rollback the fix if needed"""
    if hasattr(Form4SgmlIndexer, '_original_update_form4_data_from_xml'):
        Form4SgmlIndexer._update_form4_data_from_xml = Form4SgmlIndexer._original_update_form4_data_from_xml
        delattr(Form4SgmlIndexer, '_original_update_form4_data_from_xml')
        return "Rolled back Form4SgmlIndexer._update_form4_data_from_xml fix"
    return "No original method found to rollback"

if __name__ == "__main__":
    print("Applying fix for Form4SgmlIndexer._update_form4_data_from_xml...")
    result = apply_fix()
    print(result)