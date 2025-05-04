# parsers/router/filing_parser_manager.py
# Dispatches correct parser based on form_type

from parsers.forms.form4_parser import Form4Parser
from parsers.forms.form10k_parser import Form10KParser

class FilingParserManager:
    def __init__(self):
        self.registry = {
            "4": Form4Parser(),
            "FORM 4": Form4Parser(),  # Redundant fallback
            "10K": Form10KParser(),
            "FORM 10-K": Form10KParser(),
        }

    def route(self, form_type: str, content: str, metadata: dict, content_type: str = "xml") -> dict:
        normalized_form = form_type.strip().upper().replace("-", "")
        parser_class = self.registry.get(normalized_form)
        if parser_class:
            parser = parser_class(
                accession_number=metadata.get("accession_number", "unknown"),
                cik=metadata.get("cik", "unknown"),
                filing_date=metadata.get("filing_date", None)
            )
            return parser.parse(content)
        else:
            return {
                "parsed_type": normalized_form,
                "error": f"No registered parser for {form_type}"
            }