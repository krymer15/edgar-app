# Fix for Bug 3: Missing Footnotes
# 
# This code fixes the issue where footnotes referenced in the XML 
# are not being saved to the footnote_ids field in the database.

from parsers.forms.form4_parser import Form4Parser
from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from typing import List, Dict, Any, Optional
import xml.etree.ElementTree as ET
from models.dataclasses.forms.form4_transaction import Form4TransactionData

# Fix for Form4Parser.extract_non_derivative_transactions
original_extract_non_derivative_transactions = Form4Parser.extract_non_derivative_transactions

def fixed_extract_non_derivative_transactions(self, root) -> List[Dict[str, Any]]:
    """
    Extract non-derivative transaction information from Form 4 XML,
    including footnote references.
    
    Args:
        root: XML root element
        
    Returns:
        List of non-derivative transaction dictionaries.
    """
    def get_text(el, path):
        node = el.find(path)
        return node.text.strip() if node is not None and node.text else None
        
    transactions = []
    for txn in root.findall(".//nonDerivativeTransaction"):
        # Extract footnote IDs - THIS IS THE FIX
        footnote_ids = []
        
        # Add debug logging for non-derivative transactions
        security_title = get_text(txn, './/securityTitle/value')
        print(f"Looking for footnotes in non-derivative transaction: {security_title}")
        
        # Method 1: Direct footnoteId elements
        footnote_elements = txn.findall(".//footnoteId")
        print(f"Method 1: Found {len(footnote_elements)} footnoteId elements")
        for el in footnote_elements:
            footnote_id = el.get("id")
            print(f"  Found footnoteId element with id={footnote_id}")
            if footnote_id and footnote_id not in footnote_ids:
                footnote_ids.append(footnote_id)
                print(f"  Added footnote ID: {footnote_id}")
        
        # Method 2: Elements with footnoteId children
        elements_with_footnote = txn.findall(".//*[footnoteId]")
        print(f"Method 2: Found {len(elements_with_footnote)} elements with footnoteId children")
        for element_with_footnote in elements_with_footnote:
            footnote_els = element_with_footnote.findall("./footnoteId")
            print(f"  Element {element_with_footnote.tag} has {len(footnote_els)} footnoteId children")
            for footnote_el in footnote_els:
                footnote_id = footnote_el.get("id")
                print(f"    Found footnote with id={footnote_id}")
                if footnote_id and footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
                    print(f"    Added footnote ID: {footnote_id}")
                
        transactions.append({
            "securityTitle": get_text(txn, ".//securityTitle/value"),
            "transactionDate": get_text(txn, ".//transactionDate/value"),
            "transactionCode": get_text(txn, ".//transactionCoding/transactionCode"),
            "formType": get_text(txn, ".//transactionCoding/formType"),
            "shares": get_text(txn, ".//transactionAmounts/transactionShares/value"),
            "pricePerShare": get_text(txn, ".//transactionAmounts/transactionPricePerShare/value"),
            "ownership": get_text(txn, ".//ownershipNature/directOrIndirectOwnership/value"),
            "indirectOwnershipNature": get_text(txn, ".//ownershipNature/natureOfOwnership/value"),
            "footnoteIds": footnote_ids if footnote_ids else None  # Include footnote IDs
        })
    return transactions

# Fix for Form4Parser.extract_derivative_transactions
original_extract_derivative_transactions = Form4Parser.extract_derivative_transactions

def fixed_extract_derivative_transactions(self, root) -> List[Dict[str, Any]]:
    """
    Extract derivative transaction information from Form 4 XML,
    including footnote references.
    
    Args:
        root: XML root element
        
    Returns:
        List of derivative transaction dictionaries.
    """
    def get_text(el, path):
        node = el.find(path)
        return node.text.strip() if node is not None and node.text else None
        
    transactions = []
    for txn in root.findall(".//derivativeTransaction"):
        # Extract footnote IDs - THIS IS THE FIX
        footnote_ids = []
        
        # Add debug logging for derivative transactions
        security_title = get_text(txn, './/securityTitle/value')
        print(f"Looking for footnotes in derivative transaction: {security_title}")
        
        # Method 1: Direct footnoteId elements
        footnote_elements = txn.findall(".//footnoteId")
        print(f"Method 1: Found {len(footnote_elements)} footnoteId elements")
        for el in footnote_elements:
            footnote_id = el.get("id")
            print(f"  Found footnoteId element with id={footnote_id}")
            if footnote_id and footnote_id not in footnote_ids:
                footnote_ids.append(footnote_id)
                print(f"  Added footnote ID: {footnote_id}")
        
        # Method 2: Elements with footnoteId children
        elements_with_footnote = txn.findall(".//*[footnoteId]")
        print(f"Method 2: Found {len(elements_with_footnote)} elements with footnoteId children")
        for element_with_footnote in elements_with_footnote:
            footnote_els = element_with_footnote.findall("./footnoteId")
            print(f"  Element {element_with_footnote.tag} has {len(footnote_els)} footnoteId children")
            for footnote_el in footnote_els:
                footnote_id = footnote_el.get("id")
                print(f"    Found footnote with id={footnote_id}")
                if footnote_id and footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
                    print(f"    Added footnote ID: {footnote_id}")
                
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
            "footnoteIds": footnote_ids if footnote_ids else None  # Include footnote IDs
        })
    return transactions

# Fix for Form4SgmlIndexer._parse_transaction
original_parse_transaction = Form4SgmlIndexer._parse_transaction

def fixed_parse_transaction(self, txn_element: ET.Element, is_derivative: bool) -> Optional[Form4TransactionData]:
    """
    Parse a transaction element from Form 4 XML with better footnote handling.
    """
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
        
        # Improved footnote extraction - THIS IS THE FIX
        footnote_ids = []
        
        # Direct debug of the XML structure
        log_info(f"Processing transaction: {security_title}")
        
        # Look for footnotes in the exerciseDate element (where we know one exists in our test file)
        exercise_date_el = txn_element.find(".//exerciseDate")
        if exercise_date_el is not None:
            log_info(f"Found exerciseDate element, children: {[child.tag for child in exercise_date_el]}") 
            for child in exercise_date_el:
                log_info(f"exerciseDate child: {child.tag}, attribs: {child.attrib}")
                if child.tag == 'footnoteId' and 'id' in child.attrib:
                    footnote_id = child.attrib['id']
                    log_info(f"Found footnote ID: {footnote_id}")
                    footnote_ids.append(footnote_id)
        
        # Look for footnotes in the transactionPricePerShare element (where we know one exists in our test file)
        price_el = txn_element.find(".//transactionPricePerShare")
        if price_el is not None:
            log_info(f"Found transactionPricePerShare element, children: {[child.tag for child in price_el]}")
            for child in price_el:
                log_info(f"transactionPricePerShare child: {child.tag}, attribs: {child.attrib}")
                if child.tag == 'footnoteId' and 'id' in child.attrib:
                    footnote_id = child.attrib['id']
                    log_info(f"Found footnote ID: {footnote_id}")
                    footnote_ids.append(footnote_id)
        
        # General search for footnoteId elements
        for el in txn_element.iter():
            if el.tag == 'footnoteId' and 'id' in el.attrib:
                footnote_id = el.attrib['id']
                log_info(f"General search: Found footnote ID: {footnote_id}")
                if footnote_id not in footnote_ids:
                    footnote_ids.append(footnote_id)
                    log_info(f"Added footnote ID: {footnote_id}")
        
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
            footnote_ids=footnote_ids,  # Use the improved footnote IDs
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

# Function to apply the fixes
def apply_fixes():
    """Apply the fixes to Form4Parser and Form4SgmlIndexer for footnote handling"""
    # Keep references to original methods
    Form4Parser._original_extract_non_derivative_transactions = Form4Parser.extract_non_derivative_transactions
    Form4Parser._original_extract_derivative_transactions = Form4Parser.extract_derivative_transactions
    Form4SgmlIndexer._original_parse_transaction = Form4SgmlIndexer._parse_transaction
    
    # Replace with fixed methods
    Form4Parser.extract_non_derivative_transactions = fixed_extract_non_derivative_transactions
    Form4Parser.extract_derivative_transactions = fixed_extract_derivative_transactions
    Form4SgmlIndexer._parse_transaction = fixed_parse_transaction
    
    return "Fixed footnote extraction in Form4Parser and Form4SgmlIndexer"

# Function to rollback the fixes
def rollback_fixes():
    """Rollback the fixes if needed"""
    results = []
    
    if hasattr(Form4Parser, '_original_extract_non_derivative_transactions'):
        Form4Parser.extract_non_derivative_transactions = Form4Parser._original_extract_non_derivative_transactions
        delattr(Form4Parser, '_original_extract_non_derivative_transactions')
        results.append("Rolled back Form4Parser.extract_non_derivative_transactions fix")
    
    if hasattr(Form4Parser, '_original_extract_derivative_transactions'):
        Form4Parser.extract_derivative_transactions = Form4Parser._original_extract_derivative_transactions
        delattr(Form4Parser, '_original_extract_derivative_transactions')
        results.append("Rolled back Form4Parser.extract_derivative_transactions fix")
    
    if hasattr(Form4SgmlIndexer, '_original_parse_transaction'):
        Form4SgmlIndexer._parse_transaction = Form4SgmlIndexer._original_parse_transaction
        delattr(Form4SgmlIndexer, '_original_parse_transaction')
        results.append("Rolled back Form4SgmlIndexer._parse_transaction fix")
    
    return "\n".join(results) if results else "No original methods found to rollback"

if __name__ == "__main__":
    # These imports are needed for the fixed methods
    from datetime import datetime
    from utils.report_logger import log_info, log_warn, log_error
    
    print("Applying fixes for footnote extraction...")
    result = apply_fixes()
    print(result)