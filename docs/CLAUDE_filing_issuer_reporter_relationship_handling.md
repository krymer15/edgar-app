# SEC Filing Issuer-Reporter Relationship Handling

## Overview

SEC filings like Forms 3, 4, 5, 13D/G, and others involve relationships between multiple entities - typically an issuer company and one or more reporting owners/parties. This document outlines how to properly model and handle these relationships in the EDGAR AI platform.

## Current Implementation Issues

1. The current model stores `issuer_cik` and `is_issuer` flags in the `filing_metadata` table, which is redundant as:
   - Each accession in `filing_metadata` represents one filing from the perspective of its filer
   - For most forms, this is simply the issuer company
   - For ownership forms (3, 4, 5, etc.), crawler.idx typically lists the issuer's CIK, not the reporting owner

2. The real issue occurs during SGML download where we need the correct CIK (usually the issuer's) to construct the URL, regardless of which CIK is in our metadata.

## Form Types with Special CIK Relationships

| Form Type | Relationship Type | Primary Sections | Description |
|-----------|------------------|------------------|-------------|
| Form 3    | Issuer/Reporting Owner | `<ISSUER>`, `<REPORTING-OWNER>` | Initial beneficial ownership |
| Form 4    | Issuer/Reporting Owner | `<ISSUER>`, `<REPORTING-OWNER>` | Changes in beneficial ownership |
| Form 5    | Issuer/Reporting Owner | `<ISSUER>`, `<REPORTING-OWNER>` | Annual beneficial ownership |
| 13D       | Issuer/Reporting Owner | `<SUBJECT-COMPANY>`, `<REPORTING-OWNER>` | Active ownership report |
| 13G       | Issuer/Reporting Owner | `<SUBJECT-COMPANY>`, `<REPORTING-OWNER>` | Passive ownership report |
| 13F-HR    | Institutional Investor/Holdings | `<REPORTING-OWNER>`, `<tableStart>` | Institutional holdings |
| 144       | Issuer/Seller | `<ISSUER>`, `<REPORTING-OWNER>` | Sale of restricted securities |
| SC TO-I   | Bidder/Target | `<SUBJECT-COMPANY>`, `<FILED-BY>` | Issuer tender offer |
| SC TO-T   | Bidder/Target | `<SUBJECT-COMPANY>`, `<FILED-BY>` | Third-party tender offer |
| DEFM14A   | Multiple Companies | Various | Merger proxy statement |
| 425       | Multiple Companies | Various | Business combination communications |
| S-4       | Multiple Companies | Various | Business combination registration |

## Enhanced Architecture Proposal

### Phase 1: Simplify Current Implementation
- Remove redundant `issuer_cik` and `is_issuer` fields from `filing_metadata` table
- Keep SGML utility functions and collector logic for correct file downloads
- Continue using the SGML parsing approach for determining the actual issuer CIK during download

### Phase 2: Enhanced Document Model
- Add `issuer_cik` to the `filing_documents` table to track the actual issuer for each document
- Consider adding a `reporting_ciks` field (array type in PostgreSQL) to store multiple reporting owners

### Phase 3: Relationship Modeling (Future Consideration)
- Create a new `filing_parties` table to model the specific relationships:

```sql
CREATE TABLE filing_parties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL REFERENCES filing_metadata(accession_number) ON DELETE CASCADE,
    party_cik TEXT NOT NULL,
    party_name TEXT,
    party_role TEXT NOT NULL, -- 'issuer', 'reporting_owner', 'subject_company', 'filed_by', etc.
    is_primary BOOLEAN DEFAULT false,
    relationship_data JSONB, -- Additional relationship-specific data
    UNIQUE (accession_number, party_cik, party_role)
);
```