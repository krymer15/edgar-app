# tests/parsers/test_form4_parser.py

from dev_tools.bootstrap import add_project_root_to_sys_path
add_project_root_to_sys_path()

import os
from parsers.forms.form4_parser import Form4Parser

def load_fixture():
    """
    Loads a sample Form 4 XML file from the fixtures directory.
    """
    test_path = os.path.join(os.path.dirname(__file__), "fixtures", "form4_sample.xml")
    with open(test_path, "r", encoding="utf-8") as f:
        return f.read()

def test_parse_form4_fields():
    """
    Validates basic structure of parsed Form 4 data.
    """
    xml_content = load_fixture()

    # These can be mocked as dummy metadata for test purposes
    accession_number = "0000000000-00-000000"
    cik = "0000000000"
    filing_date = "2025-01-01"

    parser = Form4Parser(
        accession_number=accession_number,
        cik=cik,
        filing_date=filing_date
    )
    result = parser.parse(xml_content)

    if "error" in result:
        print("❌ Parser error:", result["error"])
        assert False, "Form4Parser failed to parse XML."

    parsed = result.get("parsed_data", {})
    assert "reporting_owners" in parsed, "Missing reporting_owners key"
    assert isinstance(parsed["reporting_owners"], list), "reporting_owners is not a list"
    assert len(parsed["reporting_owners"]) > 0, "No reporting owners found"
    assert parsed["reporting_owners"][0]["name"], "First reporting owner name is missing"
    assert result["parsed_type"] == "form_4", "Incorrect parsed_type"
    assert parsed["issuer"]["name"], "Issuer name missing"
    assert isinstance(parsed["non_derivative_transactions"], list), "non_derivative_transactions should be a list"
    assert isinstance(parsed["derivative_transactions"], list), "derivative_transactions should be a list"
    assert len(parsed["non_derivative_transactions"]) + len(parsed["derivative_transactions"]) > 0, "No transactions parsed"
    
def test_extract_issuer_cik_from_xml():
    """
    Test the static method to extract issuer CIK from XML (Bug 8 fix).
    
    This test validates the new functionality added to address Bug 8:
    - Standardize on issuer CIK for URL construction
    """
    xml_content = load_fixture()
    
    # Use the static method to extract issuer CIK
    issuer_cik = Form4Parser.extract_issuer_cik_from_xml(xml_content)
    
    # The fixture contains 1800flowers CIK
    assert issuer_cik == "0001084869", f"Incorrect issuer CIK: {issuer_cik}"
    
def test_extract_issuer_cik_from_xml_handles_errors():
    """
    Test that the static method gracefully handles invalid XML.
    
    This ensures the method doesn't raise exceptions when given invalid input.
    """
    # Test with invalid XML
    invalid_xml = "<invalid>This is not valid XML"
    issuer_cik = Form4Parser.extract_issuer_cik_from_xml(invalid_xml)
    assert issuer_cik is None, "Should return None for invalid XML"
    
    # Test with valid XML but no issuer element
    valid_xml_no_issuer = "<ownershipDocument><reportingOwner><reportingOwnerId><rptOwnerCik>1234567</rptOwnerCik></reportingOwnerId></reportingOwner></ownershipDocument>"
    issuer_cik = Form4Parser.extract_issuer_cik_from_xml(valid_xml_no_issuer)
    assert issuer_cik is None, "Should return None when issuer element is missing"
    
    # Test with empty string
    issuer_cik = Form4Parser.extract_issuer_cik_from_xml("")
    assert issuer_cik is None, "Should return None for empty string"

def test_extract_issuer_cik_from_sgml():
    """
    Test extracting issuer CIK from full SGML content with embedded XML.
    
    This simulates how the Form4Orchestrator uses the method.
    """
    # Create mock SGML content with embedded XML
    xml_content = load_fixture()
    sgml_content = f"""<SEC-HEADER>
ACCESSION NUMBER:  0000000000-00-000000
CONFORMED SUBMISSION TYPE: 4
PUBLIC DOCUMENT COUNT: 1
FILED AS OF DATE: 20250101
</SEC-HEADER>

<XML>
{xml_content}
</XML>
"""
    
    # Extract XML from SGML
    xml_start = sgml_content.find("<XML>")
    xml_end = sgml_content.find("</XML>", xml_start)
    extracted_xml = sgml_content[xml_start+5:xml_end].strip() if xml_start != -1 and xml_end != -1 else ""
    
    # Extract issuer CIK using our static method
    issuer_cik = Form4Parser.extract_issuer_cik_from_xml(extracted_xml)
    
    # Verify we got the correct issuer CIK
    assert issuer_cik == "0001084869", f"Failed to extract issuer CIK from SGML content: {issuer_cik}"

if __name__ == "__main__":
    test_parse_form4_fields()
    print("✅ test_parse_form4_fields passed.")
    
    test_extract_issuer_cik_from_xml()
    print("✅ test_extract_issuer_cik_from_xml passed.")
    
    test_extract_issuer_cik_from_xml_handles_errors()
    print("✅ test_extract_issuer_cik_from_xml_handles_errors passed.")
    
    test_extract_issuer_cik_from_sgml()
    print("✅ test_extract_issuer_cik_from_sgml passed.")
