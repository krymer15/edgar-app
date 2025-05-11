# downloaders

## Classes responsible for downloading raw EDGAR documents:

- **base_downloader.py**  
  Abstract base class defining the `download()` interface.

- **sgml_downloader.py**  
  - Downloads SGML/text `.txt` filings.
  - `SGMLDownloader` → .txt

- **html_downloader.py**  
  - Downloads HTML index pages and exhibit HTML.
  - `HtmlDownloader` → HTML filings/exhibits

- **xbrl_downloader.py**  
  - Downloads XML/XBRL files.
  - `XBRLDownloader` → `XML`/`XBRL` content

```python
class BaseDownloader:
    def download(self, doc: FilingDocument) -> DownloadedDocument:
        raise NotImplementedError
```