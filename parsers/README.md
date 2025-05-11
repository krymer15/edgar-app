# parsers

Parsers transform raw or cleaned text into structured objects:

## Organizational Principle
Parsers are grouped into subfolders by document type, such as:

- IDX
- SGML
- HTML
- XML (XBRL, Form 4, etc.)

This reflects how documents are actually processed in the ingestion flow.

Why?
- Reusable format-specific logic across pipelines
- Avoids duplication of SGML, HTML, or XML logic
- Matches the behavior of FilingParserManager.route() and orchestrators

### Parser Usage Convention
- Parsers do not know about pipelines (e.g., crawler_idx, forms)
- They operate on input from orchestrators and return structured dataclass outputs such as ParsedDocument and ParsedChunk.

🚫 Do Not
- Do not add pipeline-specific folders here (crawler_idx/, forms/)
- Do not couple parsing logic to Postgres writers or orchestrators

## Modules

- **base_parser.py**  
  Abstract parser interface (`parse()` method).

- **sgml_parser.py**  
    - Extracts headers, company info, and initial chunks from `.txt`.
    - `SGMLParser` → produces `ParsedDocument` + `ParsedChunk` list

- **html_parser.py**  
    - Splits HTML pages into meaningful sections.
    - `HTMLParser` → splits into chunks by <SECTION>

- **xbrl_parser.py**  
    - Pulls financial statement line items from XBRL tags.
    - `XBRLParser` → structured financials via tag names

- **form4_parser.py**  
    - Specialized parser for Form 4 XML filings.
    - form-specific (e.g. `Form4Parser`)

All inherit `BaseParser`:

```python
class BaseParser:
    def parse(self, raw: DownloadedDocument) -> Union[ParsedDocument, List[ParsedChunk]]:
        raise NotImplementedError
```

## Parsing Architecture Goals
- Separation of Concerns: Each parser focuses on a specific type of document or transformation.
- Pluggability: New parsers can be registered or invoked dynamically.
- Maintainability: Each parser is testable and loosely coupled.
- Compatibility: Works well with both raw SGML and post-processed HTML/XML.

This folder contains logic for parsing SGML and HTML content from EDGAR filings.

---

## 🔧 Fixture Loading for Parser Development

To support testing and development with real sample XML or HTML inputs, fixture files are stored outside the repo under: `/data/raw/fixtures/` (may have changed)
This folder may be symlinked to an external SSD and is ignored by Git.

Use this utility to load fixtures:
```python
from utils.devtools.fixture_loader import load_fixture
xml_text = load_fixture("form4_sample.xml")
```

### OLD INFO BELOW TO INTEGRATE! ###


## 🛠️ Usage

```python
from parsers.router.filing_router import FilingRouter

router = FilingRouter()
parsed = router.route("4", xml_content)
```

### 💡 About Parser Registry
The registry is just a dictionary behind the scenes. The optional `@register_parser` decorator approach is more dynamic and avoids hardcoding, but for now, **your current router pattern is fine** and avoids bloat.


## Notes
- Uses strict extension filters and known noise terms.
- Diagnostics are gated behind `log_debug()` only.

| Layer | Parser Type                          | Responsibility                                                                                                           |
| ----- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ |
| L1    | `SgmlFilingParser`                   | Parse `<DOCUMENT>` blocks from SGML `.txt` filings. Extract exhibit metadata, flag accessibility, guess primary document |
| L2    | `IndexPageParser`                    | Parse `index.html` to get embedded doc URLs or check anchor structure                                                    |
| L2    | `ExhibitParser`                      | Clean and annotate exhibit HTML                                                                                          |
| L3    | `Form4Parser`, `Form10KParser`, etc. | Custom logic for specific form types (XML Form 4, XBRL 10-K, etc.)                                                       |
| L4    | `FilingRouter` (new)                 | Route to appropriate parser(s) based on form type and extension (e.g., XML → Form 4 XML parser)                          |

## Sample Form 4 Pipeline
L1 – SGML Layer
| Stage | Component               | Role                                                  |
| ----- | ----------------------- | ----------------------------------------------------- |
| 1.1   | `SgmlFilingParser`      | Parses raw `.txt` SGML to extract `<DOCUMENT>` blocks |
| 1.2   | `parsed_sgml_writer.py` | Persists parsed metadata and exhibit structure        |
| 1.3   | `ExhibitMetadata`       | Flags `.xml` exhibit of interest (e.g. Form 4 XML)    |

L2 – Exhibit Resolution Layer
| Stage | Component                      | Role                                           |
| ----- | ------------------------------ | ---------------------------------------------- |
| 2.1   | `IndexPageParser` *(optional)* | Parses `index.html` for anchor link resolution |
| 2.2   | `ExhibitParser` *(optional)*   | Cleans HTML tables, flags accessibility issues |
| 2.3   | Exhibit Handler (logic)        | Downloads `.xml` Form 4 document to disk       |

L3 – Form-Specific Parser
| Stage | Component         | Role                                                             |
| ----- | ----------------- | ---------------------------------------------------------------- |
| 3.1   | `Form4Parser`     | Parses key issuer, owner, and transaction fields from Form 4 XML |
| 3.2   | `form4_writer.py` | Persists parsed results to Postgres (via ORM)                    |

L4 – Filing Router + Orchestrator
| Stage | Component              | Role                                                                |
| ----- | ---------------------- | ------------------------------------------------------------------- |
| 4.1   | `FilingParserManager`  | Routes content to correct parser (`Form4Parser`) based on form type |
| 4.2   | `Form4XmlOrchestrator` | Coordinates: ingest XML → route → write → log                       |

### Thoughts on two-layer Parser interface:

```python
class FilingParser:
    def parse(self, filing_text: str) -> ParsedFiling:
        pass

class HTMLFilingParser(FilingParser):
    def parse(self, filing_text: str) -> ParsedFiling:
        # HTML parsing logic
        pass

class SGMLFilingParser(FilingParser):
    def parse(self, filing_text: str) -> ParsedFiling:
        # SGML parsing logic (later or stub for now)
        pass
```

#### pipeline integration
```rust
Raw Filing -> ParserSelector (HTML or SGML) -> FilingParser -> ParsedFiling (text blocks, exhibits, metadata) -> Storage
```
