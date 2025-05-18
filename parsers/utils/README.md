# Parser Utilities

This directory contains shared utility functions used across the parsing system.

## Overview

Parser utilities provide common functionality needed by multiple parsers, ensuring consistent output formats and reducing code duplication. These utilities help maintain standardization across the various parser implementations.

## Available Utilities

### `parser_utils.py`

Contains utilities for standardizing parser outputs and other common parsing operations.

#### `build_standard_output()`

The `build_standard_output()` function creates a standardized dictionary structure for all parser outputs, ensuring consistent return formats across the codebase:

```python
def build_standard_output(
    parsed_type: str,
    source: str,
    content_type: str,
    accession_number: str,
    form_type: str,
    cik: str,
    filing_date: Optional[str],
    parsed_data: dict,
    metadata: Optional[dict] = None
) -> dict:
    """
    Creates a standardized output structure for parser results.
    
    Parameters:
        parsed_type: The type of parsed content (e.g., "form_4", "form_8k", etc.)
        source: The source of the content (e.g., "embedded", "primary", etc.)
        content_type: The format of the content (e.g., "xml", "html", "text")
        accession_number: The SEC accession number
        form_type: The SEC form type (e.g., "4", "8-K", "10-K")
        cik: The CIK of the filing entity
        filing_date: The date of the filing (ISO format)
        parsed_data: The structured data extracted by the parser
        metadata: Optional additional metadata
        
    Returns:
        A standardized dictionary with all parser result fields
    """
    return {
        "parsed_type": parsed_type,
        "source": source,
        "content_type": content_type,
        "accession_number": accession_number,
        "form_type": form_type,
        "cik": cik,
        "filing_date": filing_date,
        "metadata": metadata or {},
        "parsed_data": parsed_data,
    }
```

### Usage Example

This utility is used by various parsers to ensure consistent output structures:

```python
# In form4_parser.py
from parsers.utils.parser_utils import build_standard_output

class Form4Parser(BaseParser):
    def parse(self, xml_content: str) -> dict:
        # ... parsing logic ...
        
        return build_standard_output(
            parsed_type="form_4",
            source="embedded",
            content_type="xml",
            accession_number=self.accession_number,
            form_type="4",
            cik=self.cik,
            filing_date=self.filing_date,
            parsed_data=parsed_data
        )
```

## Benefits

1. **Consistency**: Ensures all parsers return data in the same structure
2. **Validation**: Enforces required fields through function parameters
3. **Maintainability**: Centralizes output format logic in one place
4. **Adaptability**: Makes it easier to modify the output structure across all parsers

## Future Expansion

As the parser system grows, additional utilities may be added to this directory:

- Text normalization functions
- Common regex patterns
- Error handling utilities
- Field extraction helpers

## Related Components

- [Form Parsers](../forms/): Use these utilities to create standardized outputs
- [SGML Indexers](../sgml/indexers/): May use these utilities for metadata extraction
- [Filing Parser Manager](../filing_parser_manager.py): Expects standardized output formats