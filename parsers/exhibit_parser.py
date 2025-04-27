# exhibit_parser.py

from lxml import html
from lxml.html import HtmlElement

class ExhibitParser:
    """
    Parser for SEC 99.1 Exhibit HTML documents.
    Cleans text by removing tables and optionally tagging major headers.
    """

    def __init__(self, html_content: str, add_header_labels: bool = True):
        """
        Initialize the parser with raw HTML content.
        
        :param html_content: Raw HTML string of the exhibit.
        :param add_header_labels: Whether to insert [HEADER] tags before major sections.
        """
        self.html_content = html_content
        self.add_header_labels = add_header_labels

        if isinstance(html_content, str):
            html_content = html_content.encode("utf-8")  # 🔥 Encode string to bytes if needed

        self.tree: HtmlElement = html.fromstring(html_content)  # 🔥 Now safely parse
        self.cleaned_text: str = ""

    def parse(self):
        """
        Main method to parse, clean, and optionally tag headers.
        """
        self._remove_tables()
        text = self._extract_cleaned_text()
        
        if self.add_header_labels:
            text = self._tag_headers(text)
        
        self.cleaned_text = text

    def get_cleaned_text(self) -> str:
        """
        Retrieve the cleaned exhibit text after parsing.
        """
        return self.cleaned_text

    def _remove_tables(self):
        """
        Remove all <table> elements from the HTML tree.
        """
        tables = self.tree.xpath('//table')
        for table in tables:
            parent = table.getparent()
            if parent is not None:
                parent.remove(table)

    def _extract_cleaned_text(self) -> str:
        """
        Extract visible text from the HTML tree, normalize spaces and newlines.
        """
        raw_text = self.tree.text_content()
        # Normalize whitespace
        lines = [line.strip() for line in raw_text.splitlines()]
        lines = [line for line in lines if line]  # Remove empty lines
        cleaned = "\n".join(lines)
        return cleaned

    def _tag_headers(self, text: str) -> str:
        """
        Find bold or strong text and tag them as headers.
        Simple heuristic based on capitalized lines and formatting tags.
        """
        headers = self.tree.xpath('//b | //strong')

        header_texts = set()
        for header in headers:
            header_text = header.text_content().strip()
            if header_text:
                header_texts.add(header_text)

        # Insert [HEADER] tags in the extracted text
        for header_text in sorted(header_texts, key=len, reverse=True):
            # Only tag headers that are standalone lines
            pattern = f"\n{header_text}\n"
            replacement = f"\n[HEADER] {header_text}\n"
            text = text.replace(pattern, replacement)

        return text
