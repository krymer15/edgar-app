# models/dataclasses

Pure Python `@dataclass` definitions for in-memory pipeline objects:

- **RawDocument**  
  Metadata + raw text before cleaning.
- **CleanedDocument** *(optional)*  
  Tag-stripped text ready for parsing.
- **ParsedDocument**  
  Structured representation of each document.
- **ParsedChunk**  
  Granular text segments for embedding/vectorization.
- **FilingHeader**  
  Core metadata (accession, dates, form type).
- **CompanyInfo**  
  Company identifier data (CIK, ticker, SIC).
- **ParsedFiling**  
  Aggregate dataclass tying header, company, all docs, chunks, and extracted metrics.