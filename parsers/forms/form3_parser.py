# parsers/forms/form3_parser.py (or form5_parser.py)

from parsers.base_parser import BaseParser

class Form3Parser(BaseParser):
    def parse(self, xml_content: str) -> dict:
        # Similar logic to Form4Parser
        return {"parsed_type": "form_3", "parsed_data": {}, "content_type": "xml"}
