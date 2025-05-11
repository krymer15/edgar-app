# Parser subclass (e.g., `html`) specialization and folder layout

Beyond the core html_parser.py, a healthy parsers/html/ folder often needs supporting modules to keep concerns separated, reusable, and testable. Here are the kinds of files you might add—and what each does:

```bash
parsers/
└── html/
    ├── __init__.py
    ├── html_parser.py          # your main parsing entrypoint/class
    ├── html_utils.py           # DOM-traversal helpers, text normalization, safe extraction
    ├── html_selectors.py       # centralized CSS/XPath selector definitions for common elements (titles, tables, headers)
    ├── html_models.py          # dataclasses for HTML-specific constructs (e.g. Section, Table, Link)
    ├── html_exceptions.py      # custom exceptions (e.g. MissingElementError, ValidationError)
    ├── html_chunker.py         # logic to split large HTML blobs into semantic chunks (e.g. by header tags)
    └── html_schema.py          # mapping rules/schema for converting raw DOM → your dataclasses
```

## Brief overview
- `html_utils.py`
    - Contains low-level routines like “get all text under this node,” “strip inline styles,” or “normalize whitespace.”

- `html_selectors.py`
    - Keeps all your CSS/XPath strings in one place (e.g. SECTION_TITLE = "//h2"), so when the SEC tweaks its template, you update one file.

- `html_models.py`
    - Defines small dataclasses—e.g.

```python
@dataclass
class HtmlSection:
    title: str
    body: str
@dataclass
class HtmlTable:
    headers: Sequence[str]
    rows: Sequence[Sequence[str]]
```

- `html_exceptions.py`
    - Lets you raise meaningful errors (instead of `KeyError` or `AttributeError`) and catch them up the chain.

- `html_chunker.py`
    - Your embedding pipeline often wants to break a huge filing into paragraphs or sections. Isolate that logic here.

- `html_schema.py`
    - If you treat parsing as a transformation from DOM → dataclass, this file can hold “rules” or mappings—e.g. “map <h1> → `DocumentTitle.title`,” “map <table class='financials'> → `FinancialTable`.”

With these helpers in place, `html_parser.py` can stay lean:

```python
from .html_utils import extract_node_text
from .html_selectors import SECTION_TITLE, SECTION_BODY
from .html_models import HtmlSection
from .html_exceptions import MissingElementError

class HtmlParser(BaseParser):
    def parse(self, cleaned_doc: CleanedDocument) -> ParsedDocument:
        dom = self._to_dom(cleaned_doc.content)
        title = extract_node_text(dom, SECTION_TITLE) or raise MissingElementError(...)
        body  = extract_node_text(dom, SECTION_BODY)
        sections = chunk_sections(dom)              # from html_chunker
        return ParsedDocument(sections=[...], title=title, ...)
```

You’d follow the same pattern in `parsers/sgml/`, `parsers/xbrl/`, or any other form-specific subfolder—keeping the core parser class focused on orchestration, and delegating helpers to their own modules.