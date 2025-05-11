# extractors

Extract specific metrics or annotations from parsed filings:

- **base_extractor.py**  
  Abstract extractor interface (`extract()` method).
- **metrics_extractor.py**  
  General financial ratios (e.g., YoY growth, margins).
- **non_gaap_extractor.py**  
  Non-GAAP reconciliation metrics.
- **risk_factor_extractor.py**  
  Identifies and scores risk-factor sections.
- **capital_allocation_extractor.py**  
  Analyzes dividends, buybacks, and reinvestment yields.