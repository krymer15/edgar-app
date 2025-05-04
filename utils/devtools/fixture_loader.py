# /utils/devtools/fixture_loader.py

"""
Utility to load test or sample fixtures from the external `/data/raw/fixtures/` folder.

Fixtures should be stored in:
- /data/raw/fixtures/   ← Symlinked or mounted to external SSD

Example usage:
    from utils.devtools.fixture_loader import load_fixture
    xml = load_fixture("form4_sample.xml")
"""

import os

FIXTURE_BASE_PATH = os.path.join("data", "raw", "fixtures")

def load_fixture(filename: str, as_text: bool = True, encoding: str = "utf-8"):
    """
    Loads a fixture file from /data/raw/fixtures/.

    Args:
        filename (str): The name of the file (e.g., "form4_sample.xml").
        as_text (bool): Whether to return contents as string (default: True).
        encoding (str): Text encoding to use if as_text=True.

    Returns:
        str | bytes: Contents of the fixture.
    """
    path = os.path.join(FIXTURE_BASE_PATH, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fixture not found: {path}")

    with open(path, "r" if as_text else "rb", encoding=encoding if as_text else None) as f:
        return f.read()
