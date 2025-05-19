# XBRL Parsers

This directory is intended to house XBRL-specific parsers for processing financial data in SEC filings. XBRL (eXtensible Business Reporting Language) is an XML-based markup language used for electronic communication of business and financial data.

## Inherent Ambiguities: XML, XBRL, and Parser Roles

In this codebase, we maintain a conceptual distinction between **Parsers** and **Indexers**:

- **Parsers**: Process specific document types and extract structured data. They transform raw content into rich structured objects with meaningful fields.
- **Indexers**: Extract document blocks, metadata, and pointers from container files. They **locate and identify** content without processing its full semantics.

However, XBRL processing naturally crosses several boundaries:

1. **Format Boundary**: XBRL is simultaneously:
   - An XML format (technically XBRL is XML with specialized tags/structure)
   - A financial reporting standard (semantically distinct from general XML) 

2. **Processing Boundary**: XBRL processing involves:
   - Basic XML parsing (shared with other XML formats)
   - Specialized financial taxonomy understanding (unique to XBRL)
   - Integration with other filing components (footnotes, exhibits, etc.)

3. **Organizational Boundary**: This creates a challenge in code organization:
   - Should XBRL parsers be treated as specialized XML parsers? (technical perspective)
   - Should they be treated as a completely separate format? (semantic perspective)
   - Should they be organized by form type? (filing-oriented perspective)

The XBRL components in this directory acknowledge these inherent ambiguities while focusing on the financial reporting aspects that make XBRL distinct from general XML processing.

## Future Implementation

This directory will house parsers for XBRL content in financial filings, particularly for:

- Form 10-K (Annual reports)
- Form 10-Q (Quarterly reports)
- Form 8-K with financial exhibits

### Expected Functionality

Future XBRL parsers will:

1. Parse XBRL taxonomy elements and extract financial data
2. Map XBRL tags to standardized financial concepts
3. Extract time periods and contexts
4. Process calculation relationships
5. Handle company-specific extensions

## Planned Components

```
xbrl/
├── xbrl_base_parser.py           # Base parser for XBRL files
├── financial_statement_parser.py # Extract income statement, balance sheet, etc.
├── taxonomy_mapper.py            # Map tags to standard financial concepts
└── forms/                        # Form-specific XBRL parsers
    ├── xbrl_10k_parser.py        # 10-K specific parsing
    └── xbrl_10q_parser.py        # 10-Q specific parsing
```

## Document Processing Flow with Format Crossovers

The actual XBRL processing flow will likely involve multiple components with overlapping responsibilities:

```
SgmlTextDocument (.txt file from EDGAR containing XBRL)
       │
       ▼
┌──────────────────────┐     
│ Form-Specific SGML   │     
│ Indexer (e.g. 10-K)  │     
└──────────┬───────────┘     
           │              
           ├─── Extract Document Metadata              
           │                               
           ├─── Extract Embedded XBRL Content
           │     │              
           │     └───────────────────►
           │                  │
           │            ┌─────────────────┐
           │            │ XBRL Parser     │
           │            └────────┬────────┘
           │                    │
           │                    │ returns parsed financial data
           │                    │
           │◄───────────────────┘ 
           │
           ├─── Extract Non-XBRL Content
           │     (e.g., textual disclosures)
           │
           ├─── Integrate Financial & Textual Data
           │
           ▼
┌──────────────────────┐
│ Complete Financial   │
│ Report with Context  │
└──────────────────────┘
```

This flow acknowledges that processing financial reports requires:
1. XBRL data extraction for structured financial tables
2. HTML/text extraction for footnotes and management discussion
3. Integration of both for a complete representation

## Implementation Example

Future XBRL parsers will follow this pattern:

```python
from parsers.base_parser import BaseParser
import xml.etree.ElementTree as ET
from typing import Dict, List, Any

class XbrlFinancialStatementParser(BaseParser):
    def __init__(self, accession_number: str, cik: str, filing_date: str):
        self.accession_number = accession_number
        self.cik = cik
        self.filing_date = filing_date
        self.ns = {
            'xbrli': 'http://www.xbrl.org/2003/instance',
            'us-gaap': 'http://fasb.org/us-gaap/2021-01-31'
        }
        
    def parse(self, xbrl_content: str) -> dict:
        try:
            root = ET.fromstring(xbrl_content)
            
            # Extract context periods
            contexts = self._extract_contexts(root)
            
            # Extract financial data points
            income_statement = self._extract_income_statement(root, contexts)
            balance_sheet = self._extract_balance_sheet(root, contexts)
            cash_flow = self._extract_cash_flow(root, contexts)
            
            return {
                "parsed_type": "xbrl_financial_statements",
                "parsed_data": {
                    "income_statement": income_statement,
                    "balance_sheet": balance_sheet,
                    "cash_flow": cash_flow
                },
                "content_type": "xbrl",
                "accession_number": self.accession_number,
                "cik": self.cik,
                "filing_date": self.filing_date
            }
        except Exception as e:
            return {
                "parsed_type": "xbrl_financial_statements",
                "error": str(e)
            }
            
    def _extract_contexts(self, root: ET.Element) -> Dict[str, Dict[str, str]]:
        # Extract context periods from XBRL
        contexts = {}
        for context in root.findall('.//xbrli:context', self.ns):
            # Implementation details...
        return contexts
        
    def _extract_income_statement(self, root: ET.Element, contexts: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        # Extract income statement items
        # Implementation details...
        return income_statement
```

## XML/XBRL Overlap Considerations

When implementing XBRL parsers, carefully consider the overlap with XML processing:

1. **Reuse XML Utilities**: For basic XML parsing functions (Node selection, attribute access)
2. **Create XBRL-Specific Logic**: For financial taxonomy interpretation 
3. **Document Boundary Decisions**: Clarify in comments where XML parsing ends and XBRL-specific logic begins

This documented clarity will help maintain the codebase, even as the technical distinction between XML and XBRL may be blurry.

## Related Components

- [Form-Specific Parsers](../forms/) - Similar implementation pattern
- [SGML Indexers](../sgml/indexers/) - Extract documents before parsing
- [XML Parsers](../xml/) - Handle general XML processing
- [Form 10-K Parser](../forms/form10k_parser.py) - Will use XBRL parser for financial data