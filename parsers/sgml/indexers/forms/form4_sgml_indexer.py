# parsers/sgml/indexers/forms/form4_sgml_indexer.py

from parsers.sgml.indexers.sgml_document_indexer import SgmlDocumentIndexer
from models.dataclasses.filing_document_metadata import FilingDocumentMetadata
from models.dataclasses.forms.form4_transaction import Form4TransactionData
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.entity import EntityData
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import xml.etree.ElementTree as ET
import re
from utils.report_logger import log_info, log_warn, log_error

class Form4SgmlIndexer(SgmlDocumentIndexer):
    """
    Specialized indexer for Form 4 filings that extracts both document metadata
    and Form 4-specific entity and transaction data.
    """
    def __init__(self, cik: str, accession_number: str):
        super().__init__(cik, accession_number, "4")
        
    def index_documents(self, txt_contents: str) -> Dict[str, Any]:
        """
        Parses SGML content to extract document metadata and form4-specific data.
        
        Returns:
            Dict containing:
            - "documents": List of FilingDocumentMetadata
            - "form4_data": Form4FilingData object
            - "xml_content": Raw XML content for further processing
        """
        # Extract standard document metadata
        documents = super().index_documents(txt_contents)
        
        # Extract Form 4 specific data
        form4_data = self.extract_form4_data(txt_contents)
        
        # Extract XML content for transaction details
        xml_content = self.extract_xml_content(txt_contents)
        
        if xml_content:
            # Parse transaction details from XML
            self.parse_xml_transactions(xml_content, form4_data)
        
        return {
            "documents": documents,
            "form4_data": form4_data,
            "xml_content": xml_content
        }
    
    def extract_form4_data(self, txt_contents: str) -> Form4FilingData:
        """
        Extract Form 4 specific data from SGML content including issuer, 
        reporting owners, and relationships.
        """
        # Extract period of report
        period_of_report_str = self._extract_header_value(txt_contents, "CONFORMED PERIOD OF REPORT:")
        period_of_report = None
        if period_of_report_str:
            try:
                period_of_report = datetime.strptime(period_of_report_str.strip(), "%Y%m%d").date()
            except ValueError:
                log_warn(f"Invalid period of report format: {period_of_report_str}")
        
        # Extract issuer
        issuer_data = self._extract_issuer_data(txt_contents)
        
        # Extract all reporting owners
        owner_data_list = self._extract_reporting_owners(txt_contents)
        
        # Create relationships
        relationships = []
        filing_date_str = self._extract_header_value(txt_contents, "FILED AS OF DATE:")
        filing_date = None
        if filing_date_str:
            try:
                filing_date = datetime.strptime(filing_date_str.strip(), "%Y%m%d").date()
            except ValueError:
                log_warn(f"Invalid filing date format: {filing_date_str}")
                filing_date = datetime.now().date()  # Fallback
        
        for owner_data in owner_data_list:
            try:
                # We need to use entity IDs instead of entity objects directly
                relationship = Form4RelationshipData(
                    issuer_entity_id=issuer_data.id,
                    owner_entity_id=owner_data["entity"].id,
                    filing_date=filing_date or datetime.now().date(),
                    is_director=owner_data.get("is_director", False),
                    is_officer=owner_data.get("is_officer", False),
                    is_ten_percent_owner=owner_data.get("is_ten_percent_owner", False),
                    is_other=owner_data.get("is_other", False),
                    officer_title=owner_data.get("officer_title"),
                    other_text=owner_data.get("other_text"),
                    relationship_type=self._determine_relationship_type(owner_data)
                )
                relationships.append(relationship)
            except ValueError as e:
                # Skip invalid relationships but log the error
                log_warn(f"Skipping invalid relationship: {e}")
        
        # Create Form4FilingData
        form4_data = Form4FilingData(
            accession_number=self.accession_number,
            period_of_report=period_of_report or (filing_date if filing_date else datetime.now().date()),
            has_multiple_owners=len(owner_data_list) > 1,
            relationships=relationships
        )

        # And set footnotes separately if needed:
        form4_data.footnotes = {}
        
        return form4_data
    
    def _extract_issuer_data(self, txt_contents: str) -> EntityData:
        """
        Extract issuer information from SGML content.
        
        This method handles different SGML formats for issuer data:
        1. <ISSUER> tag with COMPANY DATA subsection
        2. ISSUER: marker with COMPANY DATA subsection
        3. Fallback to parsing the full SEC-HEADER for issuer info
        """
        # Try with <ISSUER> tag first
        issuer_section = None
        issuer_section_start = txt_contents.find("<ISSUER>")
        if issuer_section_start != -1:
            issuer_section_end = txt_contents.find("</ISSUER>", issuer_section_start)
            if issuer_section_end != -1:
                issuer_section = txt_contents[issuer_section_start:issuer_section_end]
        
        # Try with ISSUER: marker if tag not found
        if not issuer_section:
            issuer_section_start = txt_contents.find("ISSUER:")
            if issuer_section_start != -1:
                # Find the next section or the end of the file
                next_section_start = txt_contents.find("\n\n", issuer_section_start + 1)
                if next_section_start == -1:
                    issuer_section_end = len(txt_contents)
                else:
                    issuer_section_end = next_section_start
                issuer_section = txt_contents[issuer_section_start:issuer_section_end]
        
        # Try parsing COMPANY DATA section if issuer section found
        if issuer_section:
            company_data_start = issuer_section.find("COMPANY DATA:")
            if company_data_start != -1:
                company_data_section = issuer_section[company_data_start:]
                
                # Extract CIK and name
                cik = self._extract_value(company_data_section, "CENTRAL INDEX KEY:")
                name = self._extract_value(company_data_section, "COMPANY CONFORMED NAME:")
                
                if cik and name:
                    return EntityData(
                        cik=cik,
                        name=name,
                        entity_type="company"
                    )
        
        # Fallback: Try to find issuer info in the XML section
        xml_content = self.extract_xml_content(txt_contents)
        if xml_content:
            try:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(xml_content)
                
                issuer_element = root.find(".//issuer")
                if issuer_element is not None:
                    cik_el = issuer_element.find("issuerCik")
                    name_el = issuer_element.find("issuerName")
                    
                    if cik_el is not None and cik_el.text and name_el is not None and name_el.text:
                        return EntityData(
                            cik=cik_el.text.strip(),
                            name=name_el.text.strip(),
                            entity_type="company"
                        )
            except Exception as e:
                log_warn(f"Error parsing issuer from XML: {e}")
        
        # Final fallback to SEC-HEADER
        header_end = txt_contents.find("</SEC-HEADER>")
        if header_end == -1:
            header_end = txt_contents.find("<DOCUMENT>")
        
        if header_end != -1:
            header_section = txt_contents[:header_end]
            
            # Search for company info in header
            cik_match = re.search(r"CENTRAL INDEX KEY:\s+(\d+)", header_section)
            name_match = re.search(r"COMPANY CONFORMED NAME:\s+([^\n]+)", header_section)
            
            if cik_match:
                cik = cik_match.group(1)
                name = name_match.group(1) if name_match else f"Unknown Issuer ({cik})"
                
                return EntityData(
                    cik=cik,
                    name=name,
                    entity_type="company"
                )
        
        # Absolute last resort: use the CIK passed to the indexer
        return EntityData(
            cik=self.cik,
            name=f"Unknown Issuer ({self.cik})",
            entity_type="company"
        )
    
    def _extract_reporting_owners(self, txt_contents: str) -> List[Dict]:
        """
        Extract all reporting owners from SGML content.
        
        This method handles Form 4 SGML which has a specific structure for REPORTING-OWNER.
        The method searches for REPORTING-OWNER sections in the SGML content and extracts
        the CIK and name information for each owner.
        """
        owners = []
        
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
                        
                        owners.append(owner_data)
        
        # Log the results
        if owners:
            log_info(f"Extracted {len(owners)} reporting owners")
        else:
            log_warn(f"No reporting owners found in filing {self.accession_number}")
        
        return owners
    
    def _determine_relationship_type(self, owner_data: Dict) -> str:
        """Determine the primary relationship type based on roles."""
        if owner_data.get("is_director", False):
            return "director"
        elif owner_data.get("is_officer", False):
            return "officer"
        elif owner_data.get("is_ten_percent_owner", False):
            return "10_percent_owner"
        else:
            return "other"
    
    def extract_xml_content(self, txt_contents: str) -> Optional[str]:
        """Extract Form 4 XML content from SGML."""
        try:
            xml_start = txt_contents.find("<XML>")
            if xml_start == -1:
                log_warn(f"No <XML> tag found in Form 4 filing {self.accession_number}")
                return None

            xml_end = txt_contents.find("</XML>", xml_start)
            if xml_end == -1:
                log_warn(f"Unclosed <XML> tag in Form 4 filing {self.accession_number}")
                return None

            xml_content = txt_contents[xml_start+5:xml_end].strip()

            # Quick validation check
            if not xml_content or "<ownershipDocument" not in xml_content:
                log_warn(f"XML content appears invalid in Form 4 filing {self.accession_number}")
                return None

            return xml_content
        except Exception as e:
            log_error(f"Error extracting XML content from Form 4 filing {self.accession_number}: {e}")
            return None
    
    def parse_xml_transactions(self, xml_content: str, form4_data: Form4FilingData) -> None:
        """Parse transaction details from XML content and update form4_data."""
        try:
            root = ET.fromstring(xml_content)
            
            # Extract footnotes
            footnotes = {}
            footnotes_element = root.find(".//footnotes")
            if footnotes_element is not None:
                for footnote in footnotes_element.findall("./footnote"):
                    footnote_id = footnote.get("id")
                    if footnote_id and footnote.text:
                        footnotes[footnote_id] = footnote.text
            
            form4_data.footnotes = footnotes
            
            # Extract relationship information from XML to update our relationship objects
            reporting_owner_elements = root.findall(".//reportingOwner")
            
            # We might need to create new relationships if they weren't found in the SGML headers
            if not form4_data.relationships and reporting_owner_elements:
                # Find the issuer info
                issuer_element = root.find(".//issuer")
                issuer_cik = None
                issuer_name = None
                
                if issuer_element is not None:
                    cik_el = issuer_element.find("issuerCik")
                    name_el = issuer_element.find("issuerName")
                    issuer_cik = cik_el.text.strip() if cik_el is not None and cik_el.text else self.cik
                    issuer_name = name_el.text.strip() if name_el is not None and name_el.text else f"Unknown Issuer ({issuer_cik})"
                else:
                    issuer_cik = self.cik
                    issuer_name = f"Unknown Issuer ({self.cik})"
                
                # Create an issuer entity if needed
                issuer_entity = EntityData(
                    cik=issuer_cik,
                    name=issuer_name,
                    entity_type="company"
                )
                
                # Now process each reporting owner and create relationships
                for owner_el in reporting_owner_elements:
                    try:
                        # Extract owner info
                        owner_id_el = owner_el.find("./reportingOwnerId")
                        owner_cik = None
                        owner_name = None
                        
                        if owner_id_el is not None:
                            cik_el = owner_id_el.find("rptOwnerCik")
                            name_el = owner_id_el.find("rptOwnerName")
                            owner_cik = cik_el.text.strip() if cik_el is not None and cik_el.text else None
                            owner_name = name_el.text.strip() if name_el is not None and name_el.text else f"Unknown Owner ({owner_cik})"
                        
                        if not owner_cik:
                            continue
                        
                        # Determine owner type
                        entity_type = "company"
                        if not any(business_term in owner_name.lower() for business_term in ["corp", "inc", "llc", "lp", "trust", "partners", "fund"]):
                            entity_type = "person"
                        
                        # Create owner entity
                        owner_entity = EntityData(
                            cik=owner_cik,
                            name=owner_name,
                            entity_type=entity_type
                        )
                        
                        # Extract relationship attributes
                        rel_element = owner_el.find("./reportingOwnerRelationship")
                        if rel_element is not None:
                            is_director_el = rel_element.find("isDirector") 
                            is_officer_el = rel_element.find("isOfficer")
                            is_ten_percent_el = rel_element.find("isTenPercentOwner") 
                            is_other_el = rel_element.find("isOther")
                            
                            is_director = is_director_el is not None and is_director_el.text == "1"
                            is_officer = is_officer_el is not None and is_officer_el.text == "1"
                            is_ten_percent_owner = is_ten_percent_el is not None and is_ten_percent_el.text == "1"
                            is_other = is_other_el is not None and is_other_el.text == "1"
                            
                            officer_title = None
                            if is_officer:
                                officer_title_el = rel_element.find("officerTitle")
                                if officer_title_el is not None and officer_title_el.text:
                                    officer_title = officer_title_el.text
                            
                            other_text = None
                            if is_other:
                                other_text_el = rel_element.find("otherText")
                                if other_text_el is not None and other_text_el.text:
                                    other_text = other_text_el.text
                            
                            # Ensure we have at least one relationship type
                            if not any([is_director, is_officer, is_ten_percent_owner, is_other]):
                                # Default to "other" if none specified
                                is_other = True
                                other_text = "Form 4 Filer"
                            
                            # Create relationship
                            relationship = Form4RelationshipData(
                                issuer_entity_id=issuer_entity.id,
                                owner_entity_id=owner_entity.id,
                                filing_date=form4_data.period_of_report,
                                is_director=is_director,
                                is_officer=is_officer,
                                is_ten_percent_owner=is_ten_percent_owner,
                                is_other=is_other,
                                officer_title=officer_title,
                                other_text=other_text,
                                relationship_type=self._determine_relationship_type({
                                    "is_director": is_director,
                                    "is_officer": is_officer,
                                    "is_ten_percent_owner": is_ten_percent_owner,
                                    "is_other": is_other
                                })
                            )
                            form4_data.relationships.append(relationship)
                    except Exception as e:
                        log_error(f"Error creating relationship from XML: {e}")
            elif form4_data.relationships:
                # We have existing relationships - just update them with XML data
                # This part will be skipped since we create relationships in a new way
                # but it's kept for backward compatibility
                for idx, relationship in enumerate(form4_data.relationships):
                    if idx < len(reporting_owner_elements):
                        owner_el = reporting_owner_elements[idx]
                        rel_element = owner_el.find("./reportingOwnerRelationship")
                        if rel_element is not None:
                            # No direct attribute updates since we're working with IDs now
                            pass
            
            # Extract non-derivative transactions
            non_derivative_table = root.find(".//nonDerivativeTable")
            if non_derivative_table is not None:
                for txn_element in non_derivative_table.findall(".//nonDerivativeTransaction"):
                    transaction = self._parse_transaction(txn_element, is_derivative=False)
                    if transaction:
                        form4_data.transactions.append(transaction)
            
            # Extract derivative transactions
            derivative_table = root.find(".//derivativeTable")
            if derivative_table is not None:
                for txn_element in derivative_table.findall(".//derivativeTransaction"):
                    transaction = self._parse_transaction(txn_element, is_derivative=True)
                    if transaction:
                        form4_data.transactions.append(transaction)
        
        except Exception as e:
            log_error(f"Error parsing Form 4 XML: {e}")
    
    def _parse_transaction(self, txn_element: ET.Element, is_derivative: bool) -> Optional[Form4TransactionData]:
        """Parse a transaction element from Form 4 XML."""
        try:
            # Extract security title
            security_title_el = txn_element.find(".//securityTitle/value")
            if security_title_el is None or not security_title_el.text:
                return None
            
            security_title = security_title_el.text.strip()
            
            # Extract transaction date
            date_el = txn_element.find(".//transactionDate/value")
            if date_el is None or not date_el.text:
                return None
            
            try:
                transaction_date = datetime.strptime(date_el.text.strip(), "%Y-%m-%d").date()
            except ValueError:
                log_warn(f"Invalid transaction date format: {date_el.text}")
                return None
            
            # Extract transaction code
            code_el = txn_element.find(".//transactionCoding/transactionCode")
            if code_el is None or not code_el.text:
                return None
            
            transaction_code = code_el.text.strip()
            
            # Extract form type
            form_type_el = txn_element.find(".//transactionCoding/transactionFormType")
            transaction_form_type = form_type_el.text.strip() if form_type_el is not None and form_type_el.text else None
            
            # Extract equity swap involved
            swap_el = txn_element.find(".//transactionCoding/equitySwapInvolved")
            equity_swap_involved = swap_el is not None and swap_el.text == "1"
            
            # Extract shares and price
            shares_el = txn_element.find(".//transactionAmounts/transactionShares/value")
            shares = float(shares_el.text) if shares_el is not None and shares_el.text else None
            
            price_el = txn_element.find(".//transactionAmounts/transactionPricePerShare/value")
            price = float(price_el.text) if price_el is not None and price_el.text else None
            
            # Extract ownership nature
            ownership_el = txn_element.find(".//ownershipNature/directOrIndirectOwnership/value")
            ownership_nature = ownership_el.text.strip() if ownership_el is not None and ownership_el.text else None

            # Extract derivative-specific fields if applicable
            if is_derivative:
                # Conversion/exercise price
                conv_price_el = txn_element.find(".//conversionOrExercisePrice/value")
                conversion_price = float(conv_price_el.text) if conv_price_el is not None and conv_price_el.text else None

                # Exercise date
                exercise_date_el = txn_element.find(".//exerciseDate/value")
                exercise_date = None
                if exercise_date_el is not None and exercise_date_el.text:
                    try:
                        exercise_date = datetime.strptime(exercise_date_el.text.strip(), "%Y-%m-%d").date()
                    except ValueError:
                        pass

                # Expiration date
                expiration_date_el = txn_element.find(".//expirationDate/value")
                expiration_date = None
                if expiration_date_el is not None and expiration_date_el.text:
                    try:
                        expiration_date = datetime.strptime(expiration_date_el.text.strip(), "%Y-%m-%d").date()
                    except ValueError:
                        pass
            else:
                conversion_price = None
                exercise_date = None
                expiration_date = None            
            
            # Extract footnote references
            footnote_ids = []
            for el in txn_element.findall(".//*[@footnoteId]"):
                footnote_id = el.get("footnoteId")
                if footnote_id and footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
            
            return Form4TransactionData(
                security_title=security_title,
                transaction_date=transaction_date,
                transaction_code=transaction_code,
                transaction_form_type=transaction_form_type,
                shares_amount=shares,
                price_per_share=price,
                ownership_nature=ownership_nature,
                is_derivative=is_derivative,
                equity_swap_involved=equity_swap_involved,
                footnote_ids=footnote_ids,
                # Add the new fields:
                conversion_price=conversion_price,
                exercise_date=exercise_date,
                expiration_date=expiration_date,
                # Add indirect ownership extraction:
                indirect_ownership_explanation=self._extract_indirect_ownership_explanation(txn_element) if ownership_nature == 'I' else None
            )
        
        except Exception as e:
            log_error(f"Error parsing transaction: {e}")
            return None
    
    def _extract_header_value(self, txt_contents: str, tag: str) -> Optional[str]:
        """
        Extract value from SEC-HEADER section.
        
        This method uses the same enhanced parsing logic as _extract_value
        but specifically targets the SEC-HEADER section for common header fields.
        """
        # First find the SEC-HEADER section
        header_start = txt_contents.find("<SEC-HEADER>")
        header_end = txt_contents.find("</SEC-HEADER>")
        
        if header_start == -1 or header_end == -1:
            # If no explicit header tags, use the beginning of the file up to the first document
            header_end = txt_contents.find("<DOCUMENT>")
            if header_end == -1:
                # Use the whole file as a fallback
                header_text = txt_contents
            else:
                header_text = txt_contents[:header_end]
        else:
            header_text = txt_contents[header_start:header_end]
        
        # Use the enhanced extraction logic
        return self._extract_value(header_text, tag)
    
    def _extract_value(self, section: str, tag: str) -> Optional[str]:
        """
        Extract value from a section using tag.
        
        This method handles various SGML formatting patterns:
        - Direct key-value pairs: "TAG: value"
        - Indented values: "TAG:       value"
        - Values after whitespace: "TAG:                   value"
        - Newline-separated values
        """
        # Try several patterns from most specific to most general
        
        # Pattern 1: TAG: value (with any amount of spacing)
        pattern = f"{re.escape(tag)}\\s+(.+?)(?:\\n|$)"
        match = re.search(pattern, section)
        if match:
            return match.group(1).strip()
            
        # Pattern 2: TAG:value (no space after colon)
        pattern = f"{re.escape(tag)}(.+?)(?:\\n|$)"
        match = re.search(pattern, section)
        if match:
            return match.group(1).strip()
            
        # Pattern 3: Match after the tag on any line (more generic)
        pattern = f"{re.escape(tag)}.*?([^\\n:]+)(?:\\n|$)"
        match = re.search(pattern, section)
        if match:
            return match.group(1).strip()
        
        # Debug log if no match found
        log_info(f"Failed to extract value for tag '{tag}' from section: {section[:100]}...")
        
        return None
    
    def _extract_indirect_ownership_explanation(self, txn_element: ET.Element) -> Optional[str]:
        """Extract the explanation for indirect ownership"""
        explanation_el = txn_element.find(".//ownershipNature/natureOfOwnership/value")
        if explanation_el is not None and explanation_el.text:
            return explanation_el.text.strip()
        return None    