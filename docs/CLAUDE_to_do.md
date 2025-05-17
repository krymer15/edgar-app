# TODO List

1. EDGAR Document Discovery: Directory Browsing vs. SGML Parsing

    ## Overview

    The SEC EDGAR system provides two primary methods for discovering filing documents:

    1. SGML Parsing: Extracting document references from the submission text file
    2. Directory Browsing: Directly listing files in the CIK/accession number directories

    Each approach has distinct tradeoffs that impact our document collection strategy.

    ## Comparison Matrix

    Recommended Hybrid Implementation

    1. Primary Strategy: Continue using SGML parsing for rich metadata extraction and relationship mapping
    2. Validation Layer: Implement a directory browsing validation step that:
    - Compares SGML-extracted documents with directory contents
    - Identifies and adds any missing documents
    - Flags discrepancies for potential investigation
    - Runs at lower frequency to avoid rate limiting
    3. Database Enhancement: Add validation fields to filing_documents:
    - discovery_method: enum ('sgml_parsed', 'directory_discovered', 'both')
    - validation_status: enum ('validated', 'missing_in_sgml', 'missing_in_directory')
    - last_validated: timestamp

    Implementation TODO

    - Create directory browsing client with rate limiting safeguards
    - Implement validation logic to compare SGML-parsed and directory-listed documents
    - Update database schema with validation tracking fields
    - Design background job for periodic document validation
    - Add reporting for document discovery discrepancies

    Expected Benefits

    - More complete document collection
    - Higher confidence in document discovery
    - Better metadata for all documents
    - Improved error detection for document indexing issues

    Reference: https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data

2. Next