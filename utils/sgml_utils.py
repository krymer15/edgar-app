# utils/sgml_utils.py

"""
Planned utility module for shared SGML parsing logic.

This will eventually handle:
- Parsing <DOCUMENT> blocks into structured dicts
- Extracting <FILENAME>, <TYPE>, <DESCRIPTION>, <SEQ>, etc.
- Possibly joining with the Document Format Files HTML section if needed

The goal is to allow all exhibit parsers (e.g., XBRL, ownership, 10-K) to reuse a normalized format.
"""

# TODO: Implement
def extract_documents(sgml_text: str) -> list:
    raise NotImplementedError("SGML document extractor not yet implemented.")
