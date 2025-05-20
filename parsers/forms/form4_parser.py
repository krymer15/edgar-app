# parsers/forms/form4_parser.py

"""
This is a parser that:
    - Processes the XML content within Form 4 filings
    - Extracts detailed transaction data
    - Extracts issuer and reporting owner entity information
    - Handles both non-derivative and derivative transactions
    - Builds a standardized output structure
    - Requires the XML portion to be already extracted
"""

from parsers.base_parser import BaseParser
from lxml import etree
import io
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from models.dataclasses.entity import EntityData
from parsers.utils.parser_utils import build_standard_output


class Form4Parser(BaseParser):
    def __init__(self, accession_number: str, cik: str, filing_date: str):
        self.accession_number = accession_number
        self.cik = cik
        self.filing_date = filing_date
        
    @staticmethod
    def extract_issuer_cik_from_xml(xml_content: str) -> Optional[str]:
        """
        Extract the issuer CIK from Form 4 XML content.
        
        This is a utility method for Bug 8 fix that allows other components
        to extract the issuer CIK without duplicating XML parsing logic.
        
        Args:
            xml_content: The XML content to parse
            
        Returns:
            The issuer CIK if found, None otherwise
        """
        try:
            tree = etree.parse(io.StringIO(xml_content))
            root = tree.getroot()
            
            # Use the same logic as extract_entity_information
            issuer_el = root.find(".//issuer")
            if issuer_el is not None:
                cik_el = issuer_el.find("issuerCik")
                if cik_el is not None and cik_el.text:
                    return cik_el.text.strip()
        except Exception:
            # Silent failure - caller should handle None return
            pass
            
        return None

    def parse(self, xml_content: str) -> dict:
        try:
            tree = etree.parse(io.StringIO(xml_content))
            root = tree.getroot()

            def get_text(el, path):
                node = el.find(path)
                return node.text.strip() if node is not None and node.text else None
            
            # Extract entity information
            entity_info = self.extract_entity_information(root)
            
            # Extract transaction information
            non_derivative_transactions = self.extract_non_derivative_transactions(root)
            derivative_transactions = self.extract_derivative_transactions(root)
            
            # Build the complete parsed data structure
            parsed_data = {
                "issuer": entity_info["issuer"],
                "reporting_owners": entity_info["reporting_owners"],
                "period_of_report": get_text(root, ".//periodOfReport"),
                "non_derivative_transactions": non_derivative_transactions,
                "derivative_transactions": derivative_transactions,
                # Add the new entity objects for direct use in the orchestrator
                "entity_data": {
                    "issuer_entity": entity_info["issuer_entity"],
                    "owner_entities": entity_info["owner_entities"],
                    "relationships": entity_info["relationships"]
                }
            }

            return build_standard_output(
                parsed_type="form_4",
                source="embedded",
                content_type="xml",
                accession_number=self.accession_number,
                form_type="4",
                cik=self.cik,
                filing_date=self.filing_date,
                parsed_data=parsed_data
            )

        except Exception as e:
            return {
                "parsed_type": "form_4",
                "error": str(e)
            }
            
    def extract_entity_information(self, root) -> Dict[str, Any]:
        """
        Extract detailed issuer and reporting owner information from Form 4 XML.
        
        Handles relationship flags (is_director, is_officer, etc.) with support
        for both "1" and "true" values to accommodate different XML formats.
        
        Relationship flags are extracted from the XML elements like <isDirector>, <isOfficer>,
        etc. and are expected to be either "1" or "true" for a True value. These flags
        are used to determine the relationship between the issuer and reporting owner.
        
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
            
            # More robust boolean flag handling
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
    
    def extract_non_derivative_transactions(self, root) -> List[Dict[str, Any]]:
        """
        Extract non-derivative transaction information from Form 4 XML,
        including footnote references.
        
        This implementation includes full support for footnote extraction (Bug 3 fix).
        The method uses multiple strategies to find footnote references in various
        locations within the transaction XML structure, including direct footnoteId
        elements and nested footnote references.
        
        Args:
            root: XML root element
            
        Returns:
            List of non-derivative transaction dictionaries with footnote IDs included.
        """
        def get_text(el, path):
            node = el.find(path)
            return node.text.strip() if node is not None and node.text else None
            
        transactions = []
        for txn in root.findall(".//nonDerivativeTransaction"):
            # Extract footnote IDs - Bug 3 fix implementation
            footnote_ids = []
            
            # Method 1: Direct footnoteId elements
            for el in txn.findall(".//footnoteId"):
                footnote_id = el.get("id")
                if footnote_id and footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
            
            # Method 2: Elements with footnoteId children
            for element_with_footnote in txn.findall(".//*[footnoteId]"):
                for footnote_el in element_with_footnote.findall("./footnoteId"):
                    footnote_id = footnote_el.get("id")
                    if footnote_id and footnote_id not in footnote_ids:
                        footnote_ids.append(footnote_id)
            
            transactions.append({
                "securityTitle": get_text(txn, ".//securityTitle/value"),
                "transactionDate": get_text(txn, ".//transactionDate/value"),
                "transactionCode": get_text(txn, ".//transactionCoding/transactionCode"),
                "formType": get_text(txn, ".//transactionCoding/formType"),
                "shares": get_text(txn, ".//transactionAmounts/transactionShares/value"),
                "pricePerShare": get_text(txn, ".//transactionAmounts/transactionPricePerShare/value"),
                "ownership": get_text(txn, ".//ownershipNature/directOrIndirectOwnership/value"),
                "indirectOwnershipNature": get_text(txn, ".//ownershipNature/natureOfOwnership/value"),
                "footnoteIds": footnote_ids if footnote_ids else None  # Bug 3 fix: Include footnote IDs
            })
        return transactions
    
    def extract_derivative_transactions(self, root) -> List[Dict[str, Any]]:
        """
        Extract derivative transaction information from Form 4 XML,
        including footnote references.
        
        This implementation includes full support for footnote extraction (Bug 3 fix).
        Derivative transactions often contain footnotes for exercise dates, expiration dates,
        or conversion prices. This method extracts those footnote references using multiple
        strategies to ensure all footnotes are captured correctly.
        
        Args:
            root: XML root element
            
        Returns:
            List of derivative transaction dictionaries with footnote IDs included.
        """
        def get_text(el, path):
            node = el.find(path)
            return node.text.strip() if node is not None and node.text else None
            
        transactions = []
        for txn in root.findall(".//derivativeTransaction"):
            # Extract footnote IDs - Bug 3 fix implementation
            footnote_ids = []
            
            # Method 1: Direct footnoteId elements
            for el in txn.findall(".//footnoteId"):
                footnote_id = el.get("id")
                if footnote_id and footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
            
            # Method 2: Elements with footnoteId children
            for element_with_footnote in txn.findall(".//*[footnoteId]"):
                for footnote_el in element_with_footnote.findall("./footnoteId"):
                    footnote_id = footnote_el.get("id")
                    if footnote_id and footnote_id not in footnote_ids:
                        footnote_ids.append(footnote_id)
                        
            transactions.append({
                "securityTitle": get_text(txn, ".//securityTitle/value"),
                "transactionDate": get_text(txn, ".//transactionDate/value"),
                "transactionCode": get_text(txn, ".//transactionCoding/transactionCode"),
                "formType": get_text(txn, ".//transactionCoding/formType"),
                "shares": get_text(txn, ".//transactionAmounts/transactionShares/value"),
                "pricePerShare": get_text(txn, ".//transactionAmounts/transactionPricePerShare/value"),
                "conversionOrExercisePrice": get_text(txn, ".//conversionOrExercisePrice/value"),
                "exerciseDate": get_text(txn, ".//exerciseDate/value"),
                "expirationDate": get_text(txn, ".//expirationDate/value"),
                "ownership": get_text(txn, ".//ownershipNature/directOrIndirectOwnership/value"),
                "indirectOwnershipNature": get_text(txn, ".//ownershipNature/natureOfOwnership/value"),
                "footnoteIds": footnote_ids if footnote_ids else None  # Bug 3 fix: Include footnote IDs
            })
        return transactions