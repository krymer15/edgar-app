# Form 4 Extraction Issues and Future Improvements

This document captures issues identified during testing of the Form 4 extraction pipeline and outlines areas for future improvement.

## Current Issues Identified

### Entity Creation and Relationship Handling

1. **Multiple reporting owners created:**
   - The system extracted 2 reporting owners when only one was expected
   - Log showed: `[INFO] Extracted 2 reporting owners`
   - The database shows three entities (one issuer company and two owner individuals)

2. **Incorrect relationship type determination:**
   - Relationships are marked with `is_other: true` when they should have `is_director: true`
   - The validation logic for relationship types may need adjustment

3. **CIK Extraction Issues:**
   - Issuer CIK is derived from the accession number rather than the actual CIK in the filing
   - For owner entities, using generated IDs like `owner_e0cc9b` and `owner_4226ec` rather than real CIKs

4. **Footnote Handling:**
   - Footnote IDs exist in the XML but are not properly populated in the `footnote_ids` field
   - Need to verify if footnote contents are stored anywhere

## Technical Issues Resolved

During initial testing, several technical issues were resolved:

1. **Accession number format mismatch:**
   - Accession numbers must use the same format (with dashes) in all tables
   - Created `accession_formatter.py` utility to standardize formatting

2. **Entity creation and referential integrity:**
   - Entity IDs must be preserved from original dataclasses when creating database records
   - An explicit commit is needed after entity creation before creating relationships

3. **Form4Relationship validation:**
   - Default to "other" relationship instead of raising an error when no relationship type is specified

## Future Improvements

1. **XML Extraction Refinement:**
   - Improve XML parsing to correctly identify all reporting owners
   - Properly extract CIK values instead of generating them
   - Ensure proper relationship type identification

2. **Footnote Management:**
   - Implement proper parsing and storage of footnote contents
   - Correctly associate footnotes with transactions

3. **Entity Deduplication:**
   - Implement proper entity merging/deduplication logic
   - Match entities across filings by CIK to avoid duplicates

4. **Testing Enhancements:**
   - Create test fixtures specific to Form 4 testing
   - Implement integration tests for multi-owner and special case scenarios

5. **Pipeline Integration:**
   - Test end-to-end pipeline integration
   - Ensure proper workflow with other components

## Next Steps

1. Complete the existing extraction pipeline test with the current functionality
2. Document further issues discovered during end-to-end testing
3. Implement more robust Form 4 XML parsing in future iterations

## Test Results Summary

Testing a Form 4 filing (accession: 0001610717-23-000035) produced these results:

- One Form 4 filing record created in `form4_filings` table
- Three transactions written to `form4_transactions` table
- Two relationship records created in `form4_relationships` table (expected only one)
- Three entities written to `entities` table (one issuer, two owners)

The system successfully extracted and stored the core data, but relationship and entity handling needs refinement.