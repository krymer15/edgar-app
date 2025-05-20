# Fix for Bug 5: Footnote IDs Transfer
# 
# This code fixes the issue where footnote IDs are correctly detected in Form4Parser 
# but not being transferred to Form4TransactionData objects in Form4SgmlIndexer.

from parsers.sgml.indexers.forms.form4_sgml_indexer import Form4SgmlIndexer
from models.dataclasses.forms.form4_filing import Form4FilingData
from models.dataclasses.forms.form4_transaction import Form4TransactionData
from typing import List, Dict, Any
from utils.report_logger import log_info, log_warn, log_error

# Original method for reference
original_add_transactions_from_parsed_xml = Form4SgmlIndexer._add_transactions_from_parsed_xml

def fixed_add_transactions_from_parsed_xml(self, form4_data: Form4FilingData, 
                                non_derivative_transactions: List[Dict], 
                                derivative_transactions: List[Dict]) -> None:
    """
    Convert transaction dictionaries from Form4Parser to Form4TransactionData objects
    and add them to Form4FilingData.
    
    This fixes the issue where footnote IDs aren't being transferred from the parser output
    to the Form4TransactionData objects.
    
    Args:
        form4_data: The Form4FilingData to update
        non_derivative_transactions: List of non-derivative transaction dictionaries
        derivative_transactions: List of derivative transaction dictionaries
    """
    from datetime import datetime
    
    # Process non-derivative transactions
    for txn_dict in non_derivative_transactions:
        try:
            # Convert date string to date object
            transaction_date = None
            if txn_dict.get('transactionDate'):
                try:
                    transaction_date = datetime.strptime(txn_dict['transactionDate'], '%Y-%m-%d').date()
                except ValueError:
                    log_warn(f"Invalid transaction date format: {txn_dict['transactionDate']}")
                    continue
            
            # Convert numeric values
            shares_amount = None
            if txn_dict.get('shares'):
                try:
                    shares_amount = float(txn_dict['shares'])
                except ValueError:
                    pass
            
            price_per_share = None
            if txn_dict.get('pricePerShare'):
                try:
                    price_per_share = float(txn_dict['pricePerShare'])
                except ValueError:
                    pass
            
            # FIX: Extract footnote_ids from the transaction dictionary
            footnote_ids = txn_dict.get('footnoteIds')
            log_info(f"Non-derivative transaction has footnoteIds: {footnote_ids}")
            
            # Create transaction object
            transaction = Form4TransactionData(
                security_title=txn_dict.get('securityTitle', 'Unknown Security'),
                transaction_date=transaction_date or form4_data.period_of_report,
                transaction_code=txn_dict.get('transactionCode', 'P'),  # Default to Purchase
                transaction_form_type=txn_dict.get('formType'),
                shares_amount=shares_amount,
                price_per_share=price_per_share,
                ownership_nature=txn_dict.get('ownership'),
                indirect_ownership_explanation=txn_dict.get('indirectOwnershipNature'),
                is_derivative=False,
                footnote_ids=footnote_ids  # FIX: Add footnote_ids to the transaction
            )
            
            # Add to form4_data
            form4_data.transactions.append(transaction)
            log_info(f"Added non-derivative transaction: {transaction.security_title} on {transaction.transaction_date}")
            
        except Exception as e:
            log_error(f"Error creating non-derivative transaction: {e}")
            continue
    
    # Process derivative transactions
    for txn_dict in derivative_transactions:
        try:
            # Convert date string to date object
            transaction_date = None
            if txn_dict.get('transactionDate'):
                try:
                    transaction_date = datetime.strptime(txn_dict['transactionDate'], '%Y-%m-%d').date()
                except ValueError:
                    log_warn(f"Invalid transaction date format: {txn_dict['transactionDate']}")
                    continue
            
            # Convert numeric values
            shares_amount = None
            if txn_dict.get('shares'):
                try:
                    shares_amount = float(txn_dict['shares'])
                except ValueError:
                    pass
            
            price_per_share = None
            if txn_dict.get('pricePerShare'):
                try:
                    price_per_share = float(txn_dict['pricePerShare'])
                except ValueError:
                    pass
            
            conversion_price = None
            if txn_dict.get('conversionOrExercisePrice'):
                try:
                    conversion_price = float(txn_dict['conversionOrExercisePrice'])
                except ValueError:
                    pass
            
            # Handle dates
            exercise_date = None
            if txn_dict.get('exerciseDate'):
                try:
                    exercise_date = datetime.strptime(txn_dict['exerciseDate'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            expiration_date = None
            if txn_dict.get('expirationDate'):
                try:
                    expiration_date = datetime.strptime(txn_dict['expirationDate'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            
            # FIX: Extract footnote_ids from the transaction dictionary
            footnote_ids = txn_dict.get('footnoteIds')
            log_info(f"Derivative transaction has footnoteIds: {footnote_ids}")
            
            # Create transaction object
            transaction = Form4TransactionData(
                security_title=txn_dict.get('securityTitle', 'Unknown Security'),
                transaction_date=transaction_date or form4_data.period_of_report,
                transaction_code=txn_dict.get('transactionCode', 'P'),  # Default to Purchase
                transaction_form_type=txn_dict.get('formType'),
                shares_amount=shares_amount,
                price_per_share=price_per_share,
                ownership_nature=txn_dict.get('ownership'),
                indirect_ownership_explanation=txn_dict.get('indirectOwnershipNature'),
                is_derivative=True,
                conversion_price=conversion_price,
                exercise_date=exercise_date,
                expiration_date=expiration_date,
                footnote_ids=footnote_ids  # FIX: Add footnote_ids to the transaction
            )
            
            # Add to form4_data
            form4_data.transactions.append(transaction)
            log_info(f"Added derivative transaction: {transaction.security_title} on {transaction.transaction_date}")
            
        except Exception as e:
            log_error(f"Error creating derivative transaction: {e}")
            continue
    
    log_info(f"Added {len(non_derivative_transactions) + len(derivative_transactions)} transactions from parsed XML")

# Function to apply this fix
def apply_fix():
    """Apply the fix to Form4SgmlIndexer._add_transactions_from_parsed_xml"""
    # Keep a reference to the original method for testing/rollback
    Form4SgmlIndexer._original_add_transactions_from_parsed_xml = Form4SgmlIndexer._add_transactions_from_parsed_xml
    
    # Replace with fixed method
    Form4SgmlIndexer._add_transactions_from_parsed_xml = fixed_add_transactions_from_parsed_xml
    
    return "Fixed Form4SgmlIndexer._add_transactions_from_parsed_xml to transfer footnote IDs"

# Function to rollback the fix
def rollback_fix():
    """Rollback the fix if needed"""
    if hasattr(Form4SgmlIndexer, '_original_add_transactions_from_parsed_xml'):
        Form4SgmlIndexer._add_transactions_from_parsed_xml = Form4SgmlIndexer._original_add_transactions_from_parsed_xml
        delattr(Form4SgmlIndexer, '_original_add_transactions_from_parsed_xml')
        return "Rolled back Form4SgmlIndexer._add_transactions_from_parsed_xml fix"
    return "No original method found to rollback"

if __name__ == "__main__":
    print("Applying fix for Form4SgmlIndexer._add_transactions_from_parsed_xml...")
    result = apply_fix()
    print(result)