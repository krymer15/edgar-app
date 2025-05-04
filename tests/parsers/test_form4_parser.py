# tests/parsers/test_form4_parser.py

from utils.bootstrap import add_project_root_to_sys_path
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

if __name__ == "__main__":
    test_parse_form4_fields()
    print("✅ test_parse_form4_fields passed.")
