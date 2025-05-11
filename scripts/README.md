# Conceptual pipelines

Skeleton Specialized Pipeline
Below is a conceptual “run_*” pipeline illustrating the flow for Form 4, 8-K and 10-K. You’d wire these up in your orchestrators or CLI scripts.

## Form 4 Pipeline

```python
# scripts/run_form4_pipeline.py

from collectors.filing_metadata_collector import FilingMetadataCollector
from downloaders.xml_downloader import XMLDownloader
from cleaners.form4.form4_cleaner import Form4Cleaner
from parsers.form4.form4_parser import Form4Parser
from writers.form4.form4_writer import Form4Writer

def run_form4_pipeline(date_str: str):
    # 1. Phase 1: fetch metadata
    metas = FilingMetadataCollector(form_type="4").collect(date_str)
    
    # 2. Phase 2: download raw XML
    raw_docs = [ XMLDownloader().download(m) for m in metas ]
    
    # 3. Phase 3: clean XML
    cleaned = [ Form4Cleaner().clean(doc) for doc in raw_docs ]
    
    # 4. Phase 4: parse into dataclass
    parsed = [ Form4Parser().parse(doc) for doc in cleaned ]
    
    # 5. Phase 5: write to DB
    Form4Writer().write_all(parsed)
```

## Form 8-K Pipeline

```python
# scripts/run_eightk_pipeline.py

from collectors.filing_metadata_collector import FilingMetadataCollector
from downloaders.sgml_downloader import SGMLDownloader
from cleaners.sgml.sgml_cleaner import SGMLCleaner
from parsers.eightk.eightk_parser import EightKParser
from writers.eightk.eightk_writer import EightKWriter

def run_eightk_pipeline(date_str: str):
    metas = FilingMetadataCollector(form_type="8-K").collect(date_str)
    raw    = [ SGMLDownloader().download(m) for m in metas ]
    clean  = [ SGMLCleaner().clean(d)     for d in raw ]
    parsed = [ EightKParser().parse(d)    for d in clean ]
    EightKWriter().write_all(parsed)
```

## Form 10-K Pipeline

```python
# scripts/run_tenk_pipeline.py

from collectors.filing_metadata_collector import FilingMetadataCollector
from downloaders.xbrl_downloader import XBRLDownloader
from cleaners.xbrl.xbrl_cleaner import XBRLCleaner
from parsers.tenk.tenk_parser import TenKParser
from writers.tenk.tenk_writer import TenKWriter

def run_tenk_pipeline(date_str: str):
    metas  = FilingMetadataCollector(form_type="10-K").collect(date_str)
    raw    = [ XBRLDownloader().download(m) for m in metas ]
    clean  = [ XBRLCleaner().clean(d)       for d in raw ]
    parsed = [ TenKParser().parse(d)       for d in clean ]
    TenKWriter().write_all(parsed)
```

## 🔑 Key Takeaways
- Shared base classes live at the root of each module (`base_parser.py`, `base_cleaner.py`, `base_writer.py`).
- Form-specific logic is tucked into its own subfolder when parsing/cleaning/writing diverges.
- Router (`parsers/router.py`) can dispatch form types to one of these specialized pipelines.
- “Raw → Clean → Parse → Write” is the consistent flow for every form.

This layout keeps your code highly modular, easy to navigate, and ready to scale as you add more form types or specialized logic.