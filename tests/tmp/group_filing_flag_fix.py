# Proposed Fix for Group Filing Flag Issue

# In parsers/sgml/indexers/forms/form4_sgml_indexer.py
# Update the _update_form4_data_from_xml method around line 1059-1071

# Import the necessary modules
from datetime import datetime
from typing import Dict, Any
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from utils.report_logger import log_info, log_warn, log_error

def _update_form4_data_from_xml(self, form4_data: Form4FilingData, entity_data: Dict[str, Any], parsed_xml: Dict = None) -> None:
    """
    Update Form4FilingData with more accurate entity information from XML.
    
    Bug 6 Fix: Populates the relationship_details field with structured JSON metadata.
    Bug 7 Fix: Sets is_group_filing flag when multiple reporting owners exist
    
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
        
        # Bug 7 Fix: Determine if this is a group filing based on multiple reporting owners
        is_group_filing = len(owner_entities) > 1
        
        for owner_entity, rel_data in zip(owner_entities, relationships):
            # Bug 6 Fix: Create relationship_details dictionary with structured metadata
            relationship_details = {
                "filing_date": filing_date.isoformat(),
                "accession_number": self.accession_number,
                "form_type": "4",
                "issuer": {
                    "name": issuer_entity.name,
                    "cik": issuer_entity.cik
                },
                "owner": {
                    "name": owner_entity.name,
                    "cik": owner_entity.cik,
                    "type": owner_entity.entity_type
                },
                "roles": []
            }
            
            # Bug 7 Fix: Add is_group_filing to relationship_details
            if is_group_filing:
                relationship_details["is_group_filing"] = True
            
            # Add role information
            if rel_data.get("is_director", False):
                relationship_details["roles"].append("director")
            if rel_data.get("is_officer", False):
                officer_role = {
                    "type": "officer"
                }
                if rel_data.get("officer_title"):
                    officer_role["title"] = rel_data.get("officer_title")
                relationship_details["roles"].append(officer_role)
            if rel_data.get("is_ten_percent_owner", False):
                relationship_details["roles"].append("10_percent_owner")
            if rel_data.get("is_other", False):
                other_role = {
                    "type": "other"
                }
                if rel_data.get("other_text"):
                    other_role["description"] = rel_data.get("other_text")
                relationship_details["roles"].append(other_role)
            
            # Create relationship with proper entity IDs and details
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
                is_group_filing=is_group_filing,  # Bug 7 Fix: Set is_group_filing flag
                relationship_details=relationship_details  # Bug 6 Fix: Add relationship_details
            )
            
            # Add to form4_data
            form4_data.add_relationship(relationship)
            
        log_info(f"Updated Form4FilingData with {len(form4_data.relationships)} relationships from XML")
        log_info(f"Attached issuer_entity and {len(owner_entities)} owner_entities directly to Form4FilingData")
        
        # Fix for Bug 4: Explicitly update the has_multiple_owners flag based on the 
        # actual number of relationships rather than the initial owner count
        form4_data.has_multiple_owners = len(form4_data.relationships) > 1
        log_info(f"Set has_multiple_owners to {form4_data.has_multiple_owners} based on {len(form4_data.relationships)} relationships")
        
        # Bug 7 Fix: Log group filing status
        if is_group_filing:
            log_info(f"Set is_group_filing to True based on {len(owner_entities)} reporting owners")
        
    except Exception as e:
        log_error(f"Error updating Form4FilingData from XML: {e}")
        # If an error occurs, we'll keep the original SGML-based entities