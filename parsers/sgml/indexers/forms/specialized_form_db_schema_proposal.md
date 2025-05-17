here's a recommended architecture for handling SEC filings with complex relationships:

# Database Schema Design

  Core Tables

  1. filing_metadata (unchanged)
    - Primary table for all filings regardless of form type
    - Add issuer_cik field to identify the main company
  2. filing_documents (enhanced)
    - Add issuer_cik field (already present)
    - Add document_role enum ('primary', 'exhibit', 'xml_data')
    - Keep as a universal document pointer table

  Form-Specific Tables

  3. form4_filings
    - Keep specialized fields for Form 4
    - Remove JSON arrays for relationships
    - Focus on filing-specific data
  4. form4_issuers
    - id (PK)
    - cik
    - name
    - Other issuer metadata
  5. form4_reporting_owners
    - id (PK)
    - cik
    - name
    - type (person/entity)
  6. form4_ownership_relationships
    - filing_id (FK to form4_filings)
    - issuer_id (FK to form4_issuers)
    - owner_id (FK to form4_reporting_owners)
    - relationship_type (director, officer, 10% owner)
    - officer_title (if applicable)
    - filing_date
  7. form4_transactions
    - id (PK)
    - filing_id (FK to form4_filings)
    - owner_id (FK to form4_reporting_owners)
    - Transaction details

  Architecture Components

  1. Indexers: Extract basic metadata
    - Base indexer for common SGML structures
    - Form-specific indexers for unique relationship extraction
  2. Parsers: Process document content
    - Extract semantic meaning and transaction details
    - Form-specific parsers for unique data models
  3. Writers: Handle database operations
    - Maintain proper relationships across tables
    - Form-specific writers for specialized tables

  This structure properly handles the 1:N relationship between issuers and reporting owners, allows efficient querying of ownership
  relationships, and maintains separation between general document handling and form-specific processing.

# Recommended Structure

  1. Central Document Registry: Keep filing_documents as the universal document pointer registry that:
    - Tracks all document locations (URLs)
    - Maintains basic metadata
    - Serves as the canonical source for document existence
  2. Form 4 Specialized Data: Create a clean one-way relationship:
  filing_documents (1) --> (0..1) form4_filings
  3. Key Linking Fields:
    - Use accession_number + form_type as the primary link
    - Add an optional foreign key from form4_filings to filing_documents
  4. Processing Flow:
    a. Generic SGML indexer populates filing_documents
    b. Form 4 processor checks for existence in filing_documents
    c. Form 4 data gets extracted and stored in specialized tables

  This approach:
  - Maintains a clean separation of concerns
  - Avoids duplication of metadata
  - Enables specialized querying for Form 4 data
  - Creates a foundation for other form-specific tables
  - Allows for efficient "progressive enhancement" of general document data

Updated Recommended Structure

  1. Processing Flow Optimization:
    - Since Form 4 files are simple and already being written to disk, process them in a single pass
    - Use the SGML indexer to extract header metadata
    - Extract the XML portion in the same pass
    - Parse the XML content immediately without requiring a separate file read
  2. Database Structure:
  filing_metadata (1) <-- (1) form4_filings
    - filing_metadata remains the source of truth for all filing metadata
    - form4_filings stores only Form 4 specific data without duplicating metadata
    - Use accession_number as the direct foreign key between tables
  3. Schema Adjustments:
    - Modify form4_filings to reference filing_metadata
    - Remove duplicate fields from form4_filings that exist in filing_metadata
    - Keep filing_documents separate, linked via accession_number to both tables

  This approach:
  - Eliminates redundant file reads/writes
  - Maintains clean separation of concerns
  - Leverages the existing pipeline structure
  - Optimizes for Form 4's simpler structure
  - Ensures efficient queries through proper table relationships

  The key insight is treating Form 4 data as an extension of general filing metadata rather than as an extension of document content.