# tests/forms/test_position_only_rows.py

from dev_tools.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

import os
from parsers.forms.form4_parser import Form4Parser
from decimal import Decimal

def load_fixture(fixture_name):
    """Loads a sample Form 4 XML file from the fixtures directory."""
    # Look in project-level fixtures directory
    test_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fixtures", fixture_name)
    with open(test_path, "r", encoding="utf-8") as f:
        return f.read()

def test_non_derivative_position_only_rows():
    """
    Test that the parser correctly extracts position-only rows from nonDerivativeHolding elements.
    Using the test case from 000032012123000040_form4.xml.
    """
    xml_content = load_fixture("000032012123000040_form4.xml")
    
    # Parse with dummy metadata
    parser = Form4Parser(
        accession_number="000032012123000040",
        cik="0000320121",
        filing_date="2023-05-15"
    )
    result = parser.parse(xml_content)
    
    # Verify we have the expected parsed data
    assert "parsed_data" in result, "Missing parsed_data in result"
    parsed = result["parsed_data"]
    
    # Verify we have non-derivative transactions that include position-only rows
    assert "non_derivative_transactions" in parsed, "Missing non_derivative_transactions"
    transactions = parsed["non_derivative_transactions"]
    
    # This fixture should have position-only entries (nonDerivativeHolding elements)
    position_only_rows = [t for t in transactions if t.get("is_position_only", False)]
    
    # We expect at least one position-only row
    assert len(position_only_rows) > 0, "No position-only rows found"
    
    # Check that all position-only rows have expected fields
    for row in position_only_rows:
        # Should have security title
        assert "securityTitle" in row and row["securityTitle"], "Missing securityTitle in position-only row"
        
        # Should have shares amount
        assert "shares" in row and row["shares"], "Missing shares amount in position-only row"
        
        # Should have no transaction code (null/None)
        assert row.get("transactionCode") is None, f"Unexpected transaction code: {row.get('transactionCode')}"
        
        # Should have no transaction date
        assert "transactionDate" not in row or row["transactionDate"] is None, "Position-only row should not have transaction date"
        
        # Should have no price
        assert "pricePerShare" not in row or row["pricePerShare"] is None, "Position-only row should not have price"
        
        # Should have ownership information
        assert "ownership" in row, "Missing ownership information in position-only row"


def test_derivative_position_only_rows():
    """
    Test that the parser correctly extracts position-only rows from derivativeHolding elements.
    Using the test case from 000106299323011116_form4.xml.
    """
    xml_content = load_fixture("000106299323011116_form4.xml")
    
    # Parse with dummy metadata
    parser = Form4Parser(
        accession_number="000106299323011116",
        cik="0001205922",
        filing_date="2023-05-15"
    )
    result = parser.parse(xml_content)
    
    # Verify we have the expected parsed data
    assert "parsed_data" in result, "Missing parsed_data in result"
    parsed = result["parsed_data"]
    
    # Verify we have derivative transactions that include position-only rows
    assert "derivative_transactions" in parsed, "Missing derivative_transactions"
    transactions = parsed["derivative_transactions"]
    
    # This fixture should have position-only entries (derivativeHolding elements)
    position_only_rows = [t for t in transactions if t.get("is_position_only", False)]
    
    # We expect at least one position-only row
    assert len(position_only_rows) > 0, "No derivative position-only rows found"
    
    # Check that all position-only rows have expected fields
    for row in position_only_rows:
        # Should have security title
        assert "securityTitle" in row and row["securityTitle"], "Missing securityTitle in position-only row"
        
        # Should have shares amount
        assert "shares" in row and row["shares"], "Missing shares amount in position-only row"
        
        # Should have underlying security shares
        assert "underlyingSecurityShares" in row and row["underlyingSecurityShares"], "Missing underlyingSecurityShares"
        
        # Should have no transaction code (null/None)
        assert row.get("transactionCode") is None, f"Unexpected transaction code: {row.get('transactionCode')}"
        
        # Should have no transaction date
        assert "transactionDate" not in row or row["transactionDate"] is None, "Position-only row should not have transaction date"
        
        # Should have conversion/exercise price
        assert "conversionOrExercisePrice" in row, "Missing conversionOrExercisePrice in derivative position-only row"


def test_total_shares_calculation():
    """
    Test the position_value calculation in Form4TransactionData
    which is used for the total_shares_owned calculation.
    """
    from models.dataclasses.forms.form4_transaction import Form4TransactionData
    from datetime import date
    
    # Create a position-only transaction
    position = Form4TransactionData(
        security_title="Common Stock",
        transaction_code=None,  # No transaction code for position-only rows
        shares_amount=Decimal("100"),
        is_position_only=True
    )
    
    # Create an acquisition transaction
    acquisition = Form4TransactionData(
        security_title="Common Stock",
        transaction_code="P",
        transaction_date=date.today(),
        shares_amount=Decimal("50"),
        acquisition_disposition_flag="A"
    )
    
    # Create a disposition transaction
    disposition = Form4TransactionData(
        security_title="Common Stock",
        transaction_code="S",
        transaction_date=date.today(),
        shares_amount=Decimal("25"),
        acquisition_disposition_flag="D"
    )
    
    # Test position values
    assert position.position_value == Decimal("100"), "Position-only row should return full shares amount"
    assert acquisition.position_value == Decimal("50"), "Acquisition should return positive shares amount"
    assert disposition.position_value == Decimal("-25"), "Disposition should return negative shares amount"
    
    # Test calculation
    total = position.position_value + acquisition.position_value + disposition.position_value
    assert total == Decimal("125"), "Total should be 100 + 50 - 25 = 125"


if __name__ == "__main__":
    test_non_derivative_position_only_rows()
    print("✅ Position-only rows in non-derivative section test passed.")
    
    test_derivative_position_only_rows()
    print("✅ Position-only rows in derivative section test passed.")
    
    test_total_shares_calculation()
    print("✅ Total shares calculation test passed.")