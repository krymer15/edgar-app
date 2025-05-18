# SQL Schema Definitions

This directory contains SQL schema definition files (DDL) for the Edgar App database. The files are organized into subfolders based on the related pipeline.

## Directory Structure

### crawler_idx/
SQL definitions for the Crawler IDX pipeline, which processes filing data from SEC EDGAR daily index files:

- **filing_metadata.sql**  
  Defines the primary table for basic filing information.
  
- **filing_documents.sql**  
  Defines the table for individual documents within filings.

### forms/
SQL definitions for form-specific tables, primarily focused on Form 4 processing:

- **entities.sql**  
  Defines the table for companies, people, and other entities.
  
- **form4_filings.sql**  
  Defines the table for Form 4 filing data with a link to filing_metadata.
  
- **form4_relationships.sql**  
  Defines the table for relationships between issuers and reporting owners.
  
- **form4_transactions.sql**  
  Defines the table for individual transactions within Form 4 filings.

**Note:** The `xml_metadata.sql` file has been deprecated and moved to the `archive/` directory as it's not used in current pipelines.

### submissions_api/
SQL definitions for the SEC Submissions API pipeline:

- **companies_metadata.sql**  
  Defines the table for company data from the SEC API.
  
- **submissions_metadata.sql**  
  Defines the table for submission data from the SEC API.

## Table Relationships

The database schema implements a relational design with the following key relationships:

```
                                         ┌─────────────────┐
                                         │     entities    │
                                         └─────────┬───────┘
                                                  ▲│
                                                  ││
                                                  ││
┌─────────────────┐     ┌─────────────────┐      ││
│  filing_metadata │     │  form4_filings  │      ││
└────────┬─────────┘     └────────┬────────┘      ││
         │                        │               ││
         │                        │               ││
         │                        │      ┌────────┴┴───────┐
         │                        └─────►│form4_relationships│
         │                               └────────┬─────────┘
         │                                        │
┌────────▼────────┐                      ┌────────▼────────┐
│filing_documents │                      │form4_transactions│
└─────────────────┘                      └─────────────────┘

┌───────────────────┐    ┌───────────────────┐
│companies_metadata │───►│submissions_metadata│
└───────────────────┘    └───────────────────┘
```

## Table Details

### filing_metadata

Primary filing information table used by the Crawler IDX pipeline.

```sql
CREATE TABLE filing_metadata (
    accession_number text NOT NULL PRIMARY KEY,
    cik text NOT NULL,
    form_type text NOT NULL,
    filing_date date NOT NULL,
    filing_url text NULL,
    processing_status processing_status_enum NULL,  -- Enum: pending, processing, completed, failed, skipped
    ...
);
```

### filing_documents

Individual documents within filings, with foreign key to filing_metadata.

```sql
CREATE TABLE filing_documents (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    accession_number text NOT NULL,
    cik text NOT NULL,
    document_type text NULL,
    filename text NULL,
    ...
    FOREIGN KEY (accession_number) REFERENCES filing_metadata(accession_number)
);
```

### form4_filings

Form 4 specific data with foreign key to filing_metadata.

```sql
CREATE TABLE form4_filings (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    accession_number text NOT NULL UNIQUE,
    period_of_report date NULL,
    has_multiple_owners bool DEFAULT false NULL,
    ...
    FOREIGN KEY (accession_number) REFERENCES filing_metadata(accession_number)
);
```

### entities

Represents companies, people, and other entities in SEC filings.

```sql
CREATE TABLE entities (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    cik text NOT NULL UNIQUE,
    name text NOT NULL,
    entity_type text NOT NULL CHECK (entity_type IN ('company', 'person', 'trust', 'group')),
    ...
);
```

### companies_metadata and submissions_metadata

Tables for the SEC Submissions API pipeline, with relationship between companies and their submissions.

```sql
CREATE TABLE companies_metadata (
    cik TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    ...
);

CREATE TABLE submissions_metadata (
    accession_number TEXT PRIMARY KEY,
    cik TEXT NOT NULL REFERENCES companies_metadata(cik),
    ...
);
```

## Usage

These SQL files can be executed directly on a PostgreSQL database to create the schema. The standard approach is:

```bash
# Using psql command-line client
psql -h localhost -U postgres -d edgar_app -f sql/create/crawler_idx/filing_metadata.sql
psql -h localhost -U postgres -d edgar_app -f sql/create/crawler_idx/filing_documents.sql
# ... and so on for each file
```

For database migrations, see the `sql/migrations/` directory, though those scripts may be outdated relative to these schema definitions.