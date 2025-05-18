# XBRL Parsers

This directory is intended to house XBRL-specific parsers for processing financial data in SEC filings. XBRL (eXtensible Business Reporting Language) is an XML-based markup language used for electronic communication of business and financial data.

## Parsers vs. Indexers

In this codebase, there is a critical distinction between **Parsers** and **Indexers**:

- **Parsers**: Process specific document types and extract structured data. They transform raw content into rich structured objects with meaningful fields.
- **Indexers**: Extract document blocks, metadata, and pointers from container files. They **locate and identify** content without processing its full semantics.

The XBRL components in this directory will be parsers that interpret the content of XBRL documents after they have been identified and extracted by indexers.

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

## Document Processing Flow

The XBRL parsing components will fit into the document processing flow after SGML indexing:

```
SgmlTextDocument (.txt file from EDGAR)
       │
       ▼
┌──────────────────┐     
│SgmlDocumentIndexer│     
└──────┬───────────┘     
       │ (extracts XBRL documents)              
       │                               
       ▼                              
┌──────────────────┐    
│XBRL Parser       │ <- Future components in this directory
│                  │    
└──────┬───────────┘    
       │
       ▼
┌──────────────────┐
│Financial Data    │
│                  │
└──────────────────┘
```

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

## Related Components

- [Form-Specific Parsers](../forms/) - Similar implementation pattern
- [SGML Indexers](../sgml/indexers/) - Extract documents before parsing
- [Form 10-K Parser](../forms/form10k_parser.py) - Will use XBRL parser for financial data