# Claude Code Prompt: Implementation Plan for Multi-CIK Relationship Modeling in EDGAR AI

This document consolidates two architectural proposals:
- Multi-CIK Relationship Schema for Form 4 Filings
- Form-Type-Aware Pipeline and Database Architecture

You have access to the existing `edgar-app` codebase. Your task is to generate an implementation plan that will integrate the models and schemas described below, preserving performance, modularity, and future extensibility for additional form types.

---

## PART 1: Multi-CIK Relationship Schema for Form 4

### Goals

- Model multi-entity relationships found in Form 4 filings.
- Normalize entities (people, companies, groups) to a universal registry.
- Track relationships and transactions per filing while supporting group filings and footnote details.

### Database Tables

```sql
-- Universal Entity Registry
CREATE TABLE entities (
    id UUID PRIMARY KEY,
    cik TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    entity_type ENUM('company', 'person', 'trust', 'group') NOT NULL,
    last_updated TIMESTAMP NOT NULL
);

-- Relationship Model
CREATE TABLE form4_relationships (
    id UUID PRIMARY KEY,
    filing_id UUID REFERENCES form4_filings(id),
    issuer_entity_id UUID REFERENCES entities(id),
    owner_entity_id UUID REFERENCES entities(id),
    relationship_type ENUM('director', 'officer', '10_percent_owner', 'other') NOT NULL,
    relationship_details JSONB,
    is_group_filing BOOLEAN DEFAULT FALSE,
    filing_date DATE NOT NULL
);

-- Transaction Bridge Table
CREATE TABLE form4_transactions (
    id UUID PRIMARY KEY,
    filing_id UUID REFERENCES form4_filings(id),
    relationship_id UUID REFERENCES form4_relationships(id),
    transaction_type TEXT NOT NULL,
    security_title TEXT NOT NULL,
    CONSTRAINT unique_transaction UNIQUE(filing_id, relationship_id, transaction_type)
);
```

---

## PART 2: Pipeline and Form-Specific Architecture

### Filing Flow

1. **crawler.idx ingestion** → `filing_metadata`
2. **Submission parsing (.txt)** → `filing_documents`
3. **Form-specific logic (e.g., Form 4)** → `form4_filings`, `form4_relationships`, `form4_transactions`

### Hybrid Architecture Recommendation

- Retain `filing_documents` as a central document registry
- Extend with cleanly joined form-specific tables
- Use specialized Sgml indexers to populate both general and form-specific tables

### Proposed Tables

```sql
-- Core filing join
CREATE TABLE form4_filings (
    id UUID PRIMARY KEY,
    accession_number TEXT NOT NULL REFERENCES filing_metadata(accession_number),
    period_of_report DATE,
    has_multiple_owners BOOLEAN DEFAULT FALSE,
    CONSTRAINT unique_accession UNIQUE(accession_number)
);

-- Simplified inline version of form4_relationships (to be replaced by full entity join)
CREATE TABLE form4_relationships (
    id UUID PRIMARY KEY,
    form4_filing_id UUID REFERENCES form4_filings(id),
    issuer_cik TEXT NOT NULL,
    issuer_name TEXT,
    owner_cik TEXT NOT NULL,
    owner_name TEXT,
    is_director BOOLEAN,
    is_officer BOOLEAN,
    is_ten_percent_owner BOOLEAN,
    officer_title TEXT
);
```

### Pipeline Enhancements

```python
# Factory logic
class SgmlIndexerFactory:
    @staticmethod
    def create_indexer(form_type, cik, accession_number):
        if form_type.startswith("4"):
            return Form4SgmlIndexer(cik, accession_number)
        else:
            return SgmlDocumentIndexer(cik, accession_number, form_type)

# Specialized Form 4 Indexer
class Form4SgmlIndexer(BaseSgmlIndexer):
    def index_documents(self, sgml_content):
        standard_docs = super().index_documents(sgml_content)
        form4_data = self.extract_relationships(sgml_content)
        xml_content = self.extract_xml_content(sgml_content)
        return {
            "documents": standard_docs,
            "form4_data": form4_data,
            "xml_content": xml_content
        }
```

---

## Request to Claude Code

Please generate a step-by-step **implementation plan** for this architecture with the following expectations:

1. Integrate with existing ingestion and parsing modules in `edgar-app`
2. Use modular, testable architecture aligned with current orchestrator, writer, and parser interfaces
3. Suggest where to insert logic to:
   - Normalize and store entities
   - Populate `form4_filings`, `form4_relationships`, and `form4_transactions`
   - Maintain relationships to `filing_metadata` and `filing_documents`
4. Add support for in-memory SGML passing where necessary
5. Provide placeholder tests or test scaffolds for these additions
6. Specify if any new CLI runners, ORM models, or config file edits are needed
