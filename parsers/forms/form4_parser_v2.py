# parsers/forms/form4_parser_v2.py
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from xml.etree import ElementTree as ET
import logging

from parsers.base_parser import BaseParser
from models.dataclasses.forms.form4_filing_context import Form4FilingContext
from models.dataclasses.entity import EntityData
from models.dataclasses.forms.form4_relationship import Form4RelationshipData
from models.dataclasses.forms.security_data import SecurityData
from models.dataclasses.forms.derivative_security_data import DerivativeSecurityData
from models.dataclasses.forms.transaction_data import NonDerivativeTransactionData, DerivativeTransactionData
from models.dataclasses.forms.position_data import RelationshipPositionData

logger = logging.getLogger(__name__)


class Form4ParserV2(BaseParser):
    """
    Pure XML parser for Form 4 ownership documents with full service integration.
    
    Responsibilities:
    - Parse clean XML content using single-pass extraction
    - Integrate with SecurityService, TransactionService, PositionService
    - Handle all business logic for entities, transactions, positions
    - Preserve all nuanced edge case handling from original parser
    """
    
    def __init__(self, 
                 security_service,
                 transaction_service,
                 position_service,
                 entity_service=None):
        """
        Initialize parser with injected service dependencies.
        
        Args:
            security_service: Service for security normalization and management
            transaction_service: Service for transaction processing and storage
            position_service: Service for position tracking and calculation
            entity_service: Optional service for entity management
        """
        self.security_service = security_service
        self.transaction_service = transaction_service
        self.position_service = position_service
        self.entity_service = entity_service
    
    def parse(self, 
              xml_content: str, 
              filing_context: Form4FilingContext) -> Dict[str, Any]:
        """
        Parse Form 4 XML content with full service integration.
        
        Args:
            xml_content: Clean XML content from .xml file
            filing_context: Metadata container with accession_number, cik, etc.
            
        Returns:
            Structured result with entity, security, transaction, and position IDs
        """
        try:
            logger.info(f"Parsing Form 4 XML for accession {filing_context.accession_number}")
            
            # Single XML parse
            root = self._parse_xml_safely(xml_content)
            
            # Extract all data in coordinated single pass
            entities = self._extract_and_process_entities(root, filing_context)
            securities = self._extract_and_normalize_securities(root, entities)
            transactions = self._process_transactions(root, entities, securities, filing_context)
            positions = self._process_positions(root, entities, securities, filing_context)
            
            # Return service operation results
            return {
                "success": True,
                "filing_id": self._create_filing_record(root, filing_context, entities),
                "entities": entities,
                "securities": securities,
                "transactions": transactions,
                "positions": positions,
                "metadata": self._extract_filing_metadata(root)
            }
            
        except Exception as e:
            logger.error(f"Error parsing Form 4 XML for {filing_context.accession_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "filing_context": filing_context
            }
    
    def _parse_xml_safely(self, xml_content: str) -> ET.Element:
        """Safe XML parsing with error handling."""
        try:
            return ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"Invalid XML syntax: {e}")
            raise ValueError(f"Invalid XML syntax: {e}")
        except Exception as e:
            logger.error(f"Error parsing XML: {e}")
            raise ValueError(f"Error parsing XML: {e}")
    
    def _get_text(self, element: Optional[ET.Element], xpath: str) -> Optional[str]:
        """Safe text extraction with None handling."""
        if element is None:
            return None
        node = element.find(xpath)
        return node.text.strip() if node is not None and node.text else None
    
    def _get_decimal(self, element: Optional[ET.Element], xpath: str) -> Optional[Decimal]:
        """Safe decimal extraction with validation."""
        text = self._get_text(element, xpath)
        if not text:
            return None
        try:
            return Decimal(text)
        except (ValueError, InvalidOperation):
            logger.warning(f"Failed to convert '{text}' to Decimal")
            return None
    
    def _parse_date_safely(self, date_text: str, context: str = "") -> Optional[date]:
        """Preserve robust date parsing with multiple format support."""
        if not date_text:
            return None
        
        date_text = date_text.strip()
        
        # Try XML format (YYYY-MM-DD) - most common in pure XML
        try:
            return datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError:
            pass
        
        # Try SGML format (YYYYMMDD) - backup
        try:
            return datetime.strptime(date_text, "%Y%m%d").date()
        except ValueError:
            pass
        
        # Try other common formats
        for fmt in ["%m/%d/%Y", "%m-%d-%Y", "%Y/%m/%d"]:
            try:
                return datetime.strptime(date_text, fmt).date()
            except ValueError:
                continue
        
        # Log warning and return None for invalid dates
        logger.warning(f"Invalid date format in {context}: {date_text}")
        return None
    
    def _parse_boolean_flag(self, element: Optional[ET.Element], flag_name: str) -> bool:
        """Preserve robust boolean handling from original parser."""
        if element is None:
            return False
            
        flag_el = element.find(flag_name)
        if flag_el is None or not flag_el.text:
            return False
        
        flag_text = flag_el.text.strip().lower()
        return flag_text in ("1", "true")
    
    def _classify_entity_type(self, name: str) -> str:
        """Preserve entity type classification heuristics from original indexer."""
        if not name:
            return "company"  # Default assumption
            
        # Preserved business terms from original implementation
        business_terms = ["corp", "inc", "llc", "lp", "trust", "partners", "fund"]
        return "company" if any(term in name.lower() for term in business_terms) else "person"
    
    def _extract_footnote_ids(self, element: ET.Element) -> List[str]:
        """
        Preserve all 4 footnote extraction strategies from original parser.
        """
        footnote_ids = []
        
        # Method 1: Direct footnoteId elements
        for el in element.findall(".//footnoteId"):
            footnote_id = el.get("id")
            if footnote_id and footnote_id not in footnote_ids:
                footnote_ids.append(footnote_id)
        
        # Method 2: Elements with footnoteId attributes
        for el in element.findall(".//*[@footnoteId]"):
            footnote_id = el.get("footnoteId")
            if footnote_id and footnote_id not in footnote_ids:
                footnote_ids.append(footnote_id)
        
        # Method 3: Elements with footnoteId children
        for element_with_footnote in element.findall(".//*[footnoteId]"):
            for footnote_el in element_with_footnote.findall("./footnoteId"):
                footnote_id = footnote_el.get("id")
                if footnote_id and footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
        
        # Method 4: Check specific common locations
        for specific_path in [".//exerciseDate", ".//transactionPricePerShare", ".//securityTitle"]:
            specific_el = element.find(specific_path)
            if specific_el is not None:
                for child in specific_el:
                    if child.tag == 'footnoteId' and 'id' in child.attrib:
                        footnote_id = child.attrib['id']
                        if footnote_id not in footnote_ids:
                            footnote_ids.append(footnote_id)
        
        return footnote_ids
    
    def _determine_relationship_type(self, is_director: bool, is_officer: bool, 
                                   is_ten_percent_owner: bool, is_other: bool) -> str:
        """
        Preserve hierarchical relationship classification from original indexer.
        """
        if is_director:
            return "director"
        elif is_officer:
            return "officer"
        elif is_ten_percent_owner:
            return "10_percent_owner"
        else:
            return "other"
    
    def _extract_and_process_entities(self, root: ET.Element, filing_context: Form4FilingContext) -> Dict[str, Any]:
        """
        Extract entities with all original edge case handling preserved.
        Integrates with EntityService if available, otherwise creates dataclass objects.
        """
        entities = {
            "issuer": None,
            "owners": [],
            "relationships": []
        }
        
        # Extract issuer (always required)
        issuer_element = root.find(".//issuer")
        if issuer_element is not None:
            issuer_cik = self._get_text(issuer_element, "issuerCik")
            issuer_name = self._get_text(issuer_element, "issuerName")
            trading_symbol = self._get_text(issuer_element, "issuerTradingSymbol")
            
            if issuer_cik and issuer_name:
                issuer_data = EntityData(
                    cik=issuer_cik.lstrip('0'),  # Remove leading zeros per EntityData __post_init__
                    name=issuer_name,
                    entity_type="company",
                    source_accession=filing_context.accession_number
                )
                
                # Use EntityService if available, otherwise store dataclass
                if self.entity_service:
                    issuer_id = self.entity_service.find_or_create_entity(issuer_data)
                    entities["issuer"] = {"id": issuer_id, "data": issuer_data}
                else:
                    entities["issuer"] = {"data": issuer_data}
            else:
                logger.warning(f"Missing issuer CIK or name in {filing_context.accession_number}")
        
        # Extract reporting owners (preserve multiple owner handling)
        owner_ciks = set()  # Deduplication
        for owner_element in root.findall(".//reportingOwner"):
            owner_id_el = owner_element.find("./reportingOwnerId")
            if owner_id_el is None:
                continue
                
            owner_cik = self._get_text(owner_id_el, "rptOwnerCik")
            owner_name = self._get_text(owner_id_el, "rptOwnerName")
            
            # Preserve deduplication logic
            if owner_cik and owner_cik not in owner_ciks:
                owner_ciks.add(owner_cik)
                
                # Preserve entity type detection heuristics
                entity_type = self._classify_entity_type(owner_name)
                
                owner_data = EntityData(
                    cik=owner_cik.lstrip('0'),  # Remove leading zeros per EntityData __post_init__
                    name=owner_name or f"Unknown Owner ({owner_cik})",
                    entity_type=entity_type,
                    source_accession=filing_context.accession_number
                )
                
                # Extract relationship info with preserved boolean handling
                relationship_data = self._extract_relationship_info(
                    owner_element, entities["issuer"], owner_data, filing_context
                )
                
                if self.entity_service:
                    owner_id = self.entity_service.find_or_create_entity(owner_data)
                    entities["owners"].append({"id": owner_id, "data": owner_data})
                else:
                    entities["owners"].append({"data": owner_data})
                    
                entities["relationships"].append(relationship_data)
            else:
                logger.info(f"Skipping duplicate owner CIK: {owner_cik}")
        
        return entities
    
    def _extract_relationship_info(self, owner_element: ET.Element, issuer_info: Dict[str, Any], 
                                 owner_data: EntityData, filing_context: Form4FilingContext) -> Form4RelationshipData:
        """Extract relationship with preserved boolean flag handling."""
        rel_element = owner_element.find("./reportingOwnerRelationship")
        
        # Preserve robust boolean handling for both "1"/"0" and "true"/"false"
        is_director = self._parse_boolean_flag(rel_element, "isDirector")
        is_officer = self._parse_boolean_flag(rel_element, "isOfficer") 
        is_ten_percent_owner = self._parse_boolean_flag(rel_element, "isTenPercentOwner")
        is_other = self._parse_boolean_flag(rel_element, "isOther")
        
        # Preserve fallback logic
        if not any([is_director, is_officer, is_ten_percent_owner, is_other]):
            is_other = True
            other_text = "Form 4 Filer"
        else:
            other_text = self._get_text(rel_element, "otherText") if is_other else None
        
        officer_title = self._get_text(rel_element, "officerTitle") if is_officer else None
        
        # Handle case where issuer info might be None
        issuer_entity_id = None
        if issuer_info and "data" in issuer_info:
            issuer_entity_id = issuer_info["data"].id
        
        return Form4RelationshipData(
            issuer_entity_id=issuer_entity_id,
            owner_entity_id=owner_data.id,
            filing_date=filing_context.filing_date,
            is_director=is_director,
            is_officer=is_officer,
            is_ten_percent_owner=is_ten_percent_owner,
            is_other=is_other,
            officer_title=officer_title,
            other_text=other_text,
            relationship_type=self._determine_relationship_type(is_director, is_officer, is_ten_percent_owner, is_other)
        )
    
    def _extract_and_normalize_securities(self, root: ET.Element, entities: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract and normalize securities through SecurityService.
        Returns mapping of security titles to security IDs.
        """
        security_id_map = {}  # title -> security_id
        processed_titles = set()  # Avoid duplicates
        
        # Get issuer entity ID for security creation
        issuer_entity_id = None
        if entities.get("issuer") and "data" in entities["issuer"]:
            issuer_entity_id = str(entities["issuer"]["data"].id)
        
        # Extract non-derivative securities
        for security_element in root.findall(".//nonDerivativeTable//*[securityTitle]"):
            title = self._get_text(security_element, "securityTitle/value")
            if title and title not in processed_titles:
                processed_titles.add(title)
                
                security_data = SecurityData(
                    title=title,
                    security_type="equity",
                    issuer_entity_id=issuer_entity_id
                )
                
                try:
                    security_id = self.security_service.get_or_create_security(security_data)
                    security_id_map[title] = security_id
                except Exception as e:
                    logger.error(f"Failed to create security '{title}': {e}")
        
        # Extract derivative securities with underlying relationships
        for derivative_element in root.findall(".//derivativeTable//*[securityTitle]"):
            title = self._get_text(derivative_element, "securityTitle/value")
            if title and title not in processed_titles:
                processed_titles.add(title)
                
                # First create the base security for the derivative
                base_security_data = SecurityData(
                    title=title,
                    security_type="other_derivative",  # Could be option, convertible, etc.
                    issuer_entity_id=issuer_entity_id
                )
                
                try:
                    security_id = self.security_service.get_or_create_security(base_security_data)
                    security_id_map[title] = security_id
                    
                    # Extract derivative-specific fields
                    conversion_price = self._get_decimal(derivative_element, "conversionOrExercisePrice/value")
                    exercise_date = self._parse_date_safely(
                        self._get_text(derivative_element, "exerciseDate/value") or ""
                    )
                    expiration_date = self._parse_date_safely(
                        self._get_text(derivative_element, "expirationDate/value") or ""
                    )
                    
                    # Extract underlying security info
                    underlying_element = derivative_element.find(".//underlyingSecurity")
                    underlying_title = None
                    if underlying_element is not None:
                        underlying_title = self._get_text(underlying_element, "underlyingSecurityTitle/value")
                    
                    # Create derivative security details if we have meaningful data
                    if underlying_title or conversion_price or exercise_date or expiration_date:
                        derivative_security_data = DerivativeSecurityData(
                            security_id=security_id,
                            underlying_security_title=underlying_title or "Unknown",
                            conversion_price=conversion_price,
                            exercise_date=exercise_date,
                            expiration_date=expiration_date
                        )
                        
                        try:
                            derivative_id = self.security_service.get_or_create_derivative_security(derivative_security_data)
                            # Store derivative mapping with special key
                            security_id_map[f"{title}_derivative"] = derivative_id
                        except Exception as e:
                            logger.error(f"Failed to create derivative security for '{title}': {e}")
                            
                except Exception as e:
                    logger.error(f"Failed to create base security for derivative '{title}': {e}")
        
        return security_id_map
    
    def _find_security_id(self, security_title: str, security_id_map: Dict[str, str]) -> Optional[str]:
        """Find security ID from the processed securities map."""
        return security_id_map.get(security_title)
    
    def _process_transactions(self, root: ET.Element, entities: Dict[str, Any], 
                            security_id_map: Dict[str, str], filing_context: Form4FilingContext) -> List[str]:
        """
        Process transactions using new transaction dataclasses and services.
        Automatically updates positions through PositionService.
        """
        transaction_ids = []
        
        # Get the default relationship ID for linking transactions
        default_relationship_id = None
        if entities.get("relationships") and len(entities["relationships"]) > 0:
            default_relationship_id = str(entities["relationships"][0].id)
        
        # Process non-derivative transactions
        for txn_element in root.findall(".//nonDerivativeTransaction"):
            transaction_data = self._parse_non_derivative_transaction(
                txn_element, entities, security_id_map, filing_context, default_relationship_id
            )
            
            if transaction_data:
                try:
                    # Create transaction through service
                    transaction_id = self.transaction_service.create_transaction(transaction_data)
                    transaction_ids.append(transaction_id)
                    
                    # Auto-update positions
                    self.position_service.update_position_from_transaction(transaction_data)
                except Exception as e:
                    logger.error(f"Failed to create non-derivative transaction: {e}")
        
        # Process derivative transactions  
        for txn_element in root.findall(".//derivativeTransaction"):
            transaction_data = self._parse_derivative_transaction(
                txn_element, entities, security_id_map, filing_context, default_relationship_id
            )
            
            if transaction_data:
                try:
                    transaction_id = self.transaction_service.create_transaction(transaction_data)
                    transaction_ids.append(transaction_id)
                    
                    # Auto-update positions for derivatives
                    self.position_service.update_position_from_transaction(transaction_data)
                except Exception as e:
                    logger.error(f"Failed to create derivative transaction: {e}")
        
        return transaction_ids
    
    def _parse_non_derivative_transaction(self, txn_element: ET.Element, entities: Dict[str, Any],
                                        security_id_map: Dict[str, str], filing_context: Form4FilingContext,
                                        default_relationship_id: Optional[str]) -> Optional[NonDerivativeTransactionData]:
        """
        Parse non-derivative transaction with preserved edge case handling.
        """
        # Extract core fields with preserved validation
        security_title = self._get_text(txn_element, "securityTitle/value")
        if not security_title:
            logger.warning("Missing security title in non-derivative transaction")
            return None
        
        transaction_date = self._parse_date_safely(
            self._get_text(txn_element, "transactionDate/value") or ""
        )
        if not transaction_date:
            logger.warning("Missing transaction date in non-derivative transaction")
            return None
        
        transaction_code = self._get_text(txn_element, "transactionCoding/transactionCode")
        if not transaction_code:
            logger.warning("Missing transaction code in non-derivative transaction")
            return None
        
        # Extract amounts with type conversion
        shares_amount = self._get_decimal(txn_element, "transactionAmounts/transactionShares/value")
        if shares_amount is None:
            logger.warning("Missing shares amount in non-derivative transaction")
            return None
            
        price_per_share = self._get_decimal(txn_element, "transactionAmounts/transactionPricePerShare/value")
        
        # Extract A/D flag with preserved logic
        acq_disp_flag = self._get_text(txn_element, "transactionAmounts/transactionAcquiredDisposedCode/value")
        if not acq_disp_flag:
            # Try fallback location
            acq_disp_flag = self._get_text(txn_element, "transactionCoding/transactionAcquiredDisposedCode")
        
        if acq_disp_flag not in ['A', 'D']:
            logger.warning(f"Invalid or missing acquisition/disposition flag: {acq_disp_flag}")
            return None
        
        # Extract ownership info
        ownership_nature = self._get_text(txn_element, "ownershipNature/directOrIndirectOwnership/value")
        direct_ownership = ownership_nature != "I"
        
        ownership_explanation = None
        if not direct_ownership:
            ownership_explanation = self._get_text(txn_element, "ownershipNature/natureOfOwnership/value")
        
        # Preserve comprehensive footnote extraction
        footnote_ids = self._extract_footnote_ids(txn_element)
        
        # Find security ID from processed securities
        security_id = self._find_security_id(security_title, security_id_map)
        if not security_id:
            logger.warning(f"Could not find security ID for title: {security_title}")
            return None
        
        return NonDerivativeTransactionData(
            relationship_id=default_relationship_id,
            security_id=security_id,
            transaction_date=transaction_date,
            transaction_code=transaction_code,
            shares_amount=shares_amount,
            price_per_share=price_per_share,
            acquisition_disposition_flag=acq_disp_flag,
            direct_ownership=direct_ownership,
            ownership_nature_explanation=ownership_explanation,
            footnote_ids=footnote_ids,
            form4_filing_id=filing_context.accession_number  # Reference to filing
        )
    
    def _parse_derivative_transaction(self, txn_element: ET.Element, entities: Dict[str, Any],
                                    security_id_map: Dict[str, str], filing_context: Form4FilingContext,
                                    default_relationship_id: Optional[str]) -> Optional[DerivativeTransactionData]:
        """
        Parse derivative transaction with preserved edge case handling.
        """
        # Extract core fields
        security_title = self._get_text(txn_element, "securityTitle/value")
        if not security_title:
            logger.warning("Missing security title in derivative transaction")
            return None
        
        transaction_date = self._parse_date_safely(
            self._get_text(txn_element, "transactionDate/value") or ""
        )
        if not transaction_date:
            logger.warning("Missing transaction date in derivative transaction")
            return None
        
        transaction_code = self._get_text(txn_element, "transactionCoding/transactionCode")
        if not transaction_code:
            logger.warning("Missing transaction code in derivative transaction")
            return None
        
        # Extract amounts
        shares_amount = self._get_decimal(txn_element, "transactionAmounts/transactionShares/value")
        if shares_amount is None:
            logger.warning("Missing shares amount in derivative transaction")
            return None
            
        price_per_derivative = self._get_decimal(txn_element, "transactionAmounts/transactionPricePerShare/value")
        
        # Extract A/D flag
        acq_disp_flag = self._get_text(txn_element, "transactionAmounts/transactionAcquiredDisposedCode/value")
        if not acq_disp_flag:
            acq_disp_flag = self._get_text(txn_element, "transactionCoding/transactionAcquiredDisposedCode")
        
        if acq_disp_flag not in ['A', 'D']:
            logger.warning(f"Invalid or missing acquisition/disposition flag in derivative: {acq_disp_flag}")
            return None
        
        # Extract ownership info
        ownership_nature = self._get_text(txn_element, "ownershipNature/directOrIndirectOwnership/value")
        direct_ownership = ownership_nature != "I"
        
        ownership_explanation = None
        if not direct_ownership:
            ownership_explanation = self._get_text(txn_element, "ownershipNature/natureOfOwnership/value")
        
        # Extract underlying shares amount
        underlying_shares = self._get_decimal(txn_element, "underlyingSecurity/underlyingSecurityShares/value")
        
        # Extract footnotes
        footnote_ids = self._extract_footnote_ids(txn_element)
        
        # Find security IDs
        security_id = self._find_security_id(security_title, security_id_map)
        derivative_security_id = self._find_security_id(f"{security_title}_derivative", security_id_map)
        
        if not security_id:
            logger.warning(f"Could not find security ID for derivative title: {security_title}")
            return None
        
        return DerivativeTransactionData(
            relationship_id=default_relationship_id,
            security_id=security_id,
            derivative_security_id=derivative_security_id,
            transaction_date=transaction_date,
            transaction_code=transaction_code,
            shares_amount=shares_amount,
            price_per_derivative=price_per_derivative,
            underlying_shares_amount=underlying_shares,
            acquisition_disposition_flag=acq_disp_flag,
            direct_ownership=direct_ownership,
            ownership_nature_explanation=ownership_explanation,
            footnote_ids=footnote_ids,
            form4_filing_id=filing_context.accession_number
        )
    
    def _process_positions(self, root: ET.Element, entities: Dict[str, Any], 
                         security_id_map: Dict[str, str], filing_context: Form4FilingContext) -> List[str]:
        """
        Handle position-only holdings with preserved business logic.
        """
        position_ids = []
        
        # Get the default relationship ID for linking positions
        default_relationship_id = None
        if entities.get("relationships") and len(entities["relationships"]) > 0:
            default_relationship_id = str(entities["relationships"][0].id)
        
        # Process non-derivative holdings
        for holding_element in root.findall(".//nonDerivativeHolding"):
            position_data = self._parse_position_holding(
                holding_element, entities, security_id_map, filing_context, 
                default_relationship_id, is_derivative=False
            )
            
            if position_data:
                try:
                    position_id = self.position_service.create_position_only_entry(position_data)
                    position_ids.append(position_id)
                except Exception as e:
                    logger.error(f"Failed to create non-derivative position: {e}")
        
        # Process derivative holdings
        for holding_element in root.findall(".//derivativeHolding"):
            position_data = self._parse_position_holding(
                holding_element, entities, security_id_map, filing_context, 
                default_relationship_id, is_derivative=True
            )
            
            if position_data:
                try:
                    position_id = self.position_service.create_position_only_entry(position_data)
                    position_ids.append(position_id)
                except Exception as e:
                    logger.error(f"Failed to create derivative position: {e}")
        
        return position_ids
    
    def _parse_position_holding(self, holding_element: ET.Element, entities: Dict[str, Any],
                              security_id_map: Dict[str, str], filing_context: Form4FilingContext,
                              default_relationship_id: Optional[str], is_derivative: bool = False) -> Optional[RelationshipPositionData]:
        """
        Parse position-only holding with preserved logic.
        """
        security_title = self._get_text(holding_element, "securityTitle/value")
        if not security_title:
            logger.warning("Missing security title in position holding")
            return None
        
        # For holdings, use shares owned amount
        shares_amount = self._get_decimal(holding_element, "postTransactionAmounts/sharesOwnedFollowingTransaction/value")
        if shares_amount is None:
            logger.warning("Missing shares amount in position holding")
            return None
        
        # Extract ownership info
        ownership_nature = self._get_text(holding_element, "ownershipNature/directOrIndirectOwnership/value")
        direct_ownership = ownership_nature != "I"
        
        ownership_explanation = None
        if not direct_ownership:
            ownership_explanation = self._get_text(holding_element, "ownershipNature/natureOfOwnership/value")
        
        # Extract footnotes with preserved strategies
        footnote_ids = self._extract_footnote_ids(holding_element)
        
        # Find security and derivative security IDs
        security_id = self._find_security_id(security_title, security_id_map)
        if not security_id:
            logger.warning(f"Could not find security ID for holding title: {security_title}")
            return None
        
        derivative_security_id = None
        if is_derivative:
            derivative_security_id = self._find_security_id(f"{security_title}_derivative", security_id_map)
        
        return RelationshipPositionData(
            relationship_id=default_relationship_id,
            security_id=security_id,
            position_date=filing_context.filing_date,
            shares_amount=shares_amount,
            filing_id=filing_context.accession_number,
            position_type="derivative" if is_derivative else "equity",
            direct_ownership=direct_ownership,
            ownership_nature_explanation=ownership_explanation,
            is_position_only=True,
            derivative_security_id=derivative_security_id
        )
    
    def _create_filing_record(self, root: ET.Element, filing_context: Form4FilingContext, 
                            entities: Dict[str, Any]) -> Optional[str]:
        """
        Create filing record if needed. For now, return the accession number as filing ID.
        In a full implementation, this would create a Form4Filing record.
        """
        return filing_context.accession_number
    
    def _extract_filing_metadata(self, root: ET.Element) -> Dict[str, Any]:
        """
        Extract filing metadata from XML.
        """
        metadata = {}
        
        # Extract basic filing info
        metadata["document_type"] = self._get_text(root, "documentType")
        metadata["schema_version"] = self._get_text(root, "schemaVersion")
        metadata["period_of_report"] = self._get_text(root, "periodOfReport")
        
        # Extract additional flags
        metadata["aff10b5One"] = self._parse_boolean_flag(root, "aff10b5One")
        
        # Count transactions and holdings
        metadata["non_derivative_transactions"] = len(root.findall(".//nonDerivativeTransaction"))
        metadata["derivative_transactions"] = len(root.findall(".//derivativeTransaction"))
        metadata["non_derivative_holdings"] = len(root.findall(".//nonDerivativeHolding"))
        metadata["derivative_holdings"] = len(root.findall(".//derivativeHolding"))
        
        return metadata