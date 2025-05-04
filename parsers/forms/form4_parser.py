# parsers/forms/form4_parser.py

from parsers.base_parser import BaseParser
from lxml import etree
import io
from parsers.utils.parser_utils import build_standard_output


class Form4Parser(BaseParser):
    def __init__(self, accession_number: str, cik: str, filing_date: str):
        self.accession_number = accession_number
        self.cik = cik
        self.filing_date = filing_date

    from parsers.base_parser import BaseParser
from lxml import etree
import io
from parsers.utils.parser_utils import build_standard_output

class Form4Parser(BaseParser):
    def __init__(self, accession_number: str, cik: str, filing_date: str):
        self.accession_number = accession_number
        self.cik = cik
        self.filing_date = filing_date

    def parse(self, xml_content: str) -> dict:
        try:
            tree = etree.parse(io.StringIO(xml_content))
            root = tree.getroot()

            def get_text(el, path):
                node = el.find(path)
                return node.text.strip() if node is not None and node.text else None

            issuer_el = root.find(".//issuer")
            reporting_owners = []
            for owner_el in root.findall(".//reportingOwner"):
                reporting_owners.append({
                    "name": get_text(owner_el, ".//rptOwnerName"),
                    "cik": get_text(owner_el, ".//rptOwnerCik"),
                    "is_director": get_text(owner_el, ".//isDirector"),
                    "is_officer": get_text(owner_el, ".//isOfficer"),
                    "is_ten_percent_owner": get_text(owner_el, ".//isTenPercentOwner"),
                })

            parsed_data = {
                "issuer": {
                    "name": get_text(issuer_el, "issuerName"),
                    "cik": get_text(issuer_el, "issuerCik"),
                },
                "reporting_owners": reporting_owners,
                "period_of_report": get_text(root, ".//periodOfReport"),
                "non_derivative_transactions": [],
                "derivative_transactions": [],
            }

            for txn in root.findall(".//nonDerivativeTransaction"):
                parsed_data["non_derivative_transactions"].append({
                    "securityTitle": get_text(txn, ".//securityTitle/value"),
                    "transactionDate": get_text(txn, ".//transactionDate/value"),
                    "transactionCode": get_text(txn, ".//transactionCoding/transactionCode"),
                    "formType": get_text(txn, ".//transactionCoding/formType"),
                    "shares": get_text(txn, ".//transactionAmounts/transactionShares/value"),
                    "pricePerShare": get_text(txn, ".//transactionAmounts/transactionPricePerShare/value"),
                    "ownership": get_text(txn, ".//ownershipNature/directOrIndirectOwnership"),
                })

            for txn in root.findall(".//derivativeTransaction"):
                parsed_data["derivative_transactions"].append({
                    "securityTitle": get_text(txn, ".//securityTitle/value"),
                    "transactionDate": get_text(txn, ".//transactionDate/value"),
                    "transactionCode": get_text(txn, ".//transactionCoding/transactionCode"),
                    "formType": get_text(txn, ".//transactionCoding/formType"),
                    "shares": get_text(txn, ".//transactionAmounts/transactionShares/value"),
                    "pricePerShare": get_text(txn, ".//transactionAmounts/transactionPricePerShare/value"),
                    "conversionOrExercisePrice": get_text(txn, ".//conversionOrExercisePrice/value"),
                    "exerciseDate": get_text(txn, ".//exerciseDate/value"),
                    "expirationDate": get_text(txn, ".//expirationDate/value"),
                    "ownership": get_text(txn, ".//ownershipNature/directOrIndirectOwnership"),
                })

            return build_standard_output(
                parsed_type="form_4",
                source="embedded",  # or "exhibit" if applicable
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
