import os
from lxml import html, etree

class EmbeddedDocParser:
    def __init__(self, raw_text: str, url: str):
        self.raw_text = raw_text
        self.url = url

    def detect_type(self):
        if self.url.endswith(".xml"):
            return "xml"
        elif self.url.endswith(".htm") or self.url.endswith(".html"):
            return "html"
        return "unknown"

    def parse(self) -> str:
        doc_type = self.detect_type()
        if doc_type == "html":
            return self._parse_html()
        elif doc_type == "xml":
            return self._handle_xml()
        return "[UNSUPPORTED DOCUMENT TYPE]"

    def _parse_html(self) -> str:
        try:
            tree = html.fromstring(self.raw_text)
            body = tree.xpath("//body")[0]
            return body.text_content().strip()
        except Exception as e:
            return f"[HTML PARSE ERROR]: {e}"

    def _handle_xml(self) -> str:
        # Skipping XML forms for now
        return "[SKIPPED: XML document not parsed]"
