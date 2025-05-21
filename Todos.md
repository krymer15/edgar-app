# Edgar App TODOs

This document lists high-priority architectural and feature improvements for the Edgar App project.

## Feature Improvements

### 1. Form 4 Processing Improvements

- [x] Fix Bug 1: Deduplication of reporting owners in Form4SgmlIndexer
- [x] Fix Bug 2: Relationship flag handling to support both "1" and "true" values
- [x] Fix Bug 4: Update has_multiple_owners flag based on actual relationship count
- [x] Fix Bug 3: Enhance footnote extraction from Form 4 XML
- [x] Fix Bug 5: Fix footnote ID transfer to Form4TransactionData objects
- [x] Fix Bug 6: Populate relationship_details field in form4_relationships table
- [x] Add comprehensive tests for all Form 4 processing fixes
- [x] Fix Bug 7: Set is_group_filing flag properly for multi-owner Form 4 filings
- [x] Fix Bug 8: Standardize URL construction to always use issuer CIK, ensuring consistent file paths and proper storage of XML files
- [x] Add column to form4_transactions table for acquisition/disposition flag ("(A) or (D)" value in XML)
- [ ] Add support for position-only rows in Form 4 filings (rows with ownership data but no transaction details) using test cases from fixtures/000032012123000040_form4.xml (non-derivative section) and fixtures/000106299323011116_form4.xml (derivative section)
- [ ] Add calculated total_shares_owned field to form4_relationships table aggregating all related transaction amounts
- [ ] Reprocess problematic Form 4 filings after all fixes are implemented

### 2. Expand Form Type Support

- [ ] Implement support for Form 3 (Initial Statement of Beneficial Ownership)
- [ ] Implement support for Form 5 (Annual Statement of Beneficial Ownership)
- [ ] Implement support for Form 8-K (Current Reports) with exhibit extraction
- [ ] Implement support for Form 10-K/Q (Annual and Quarterly Reports)

### 3. Enhance Entity Relationship Tracking

- [x] Improve entity deduplication logic in Form 4 processing
- [ ] Implement relationship tracking across different filing types
- [ ] Create APIs for relationship graph queries
- [ ] Add historical relationship change tracking

## Documentation Improvements

- [ ] Create architecture diagrams for key subsystems
- [ ] Document standard patterns for extending the system
- [ ] Add more code comments explaining complex parsing logic
- [ ] Update READMEs in all major directories

## Testing Improvements

- [ ] Increase unit test coverage for core components
- [ ] Add integration tests for end-to-end processing flows
- [ ] Create more comprehensive test fixtures for different form types
- [ ] Implement performance testing for large batch processing

## Performance Optimizations

- [ ] Optimize database queries in writers
- [ ] Implement batch processing for high-volume form types
- [ ] Add caching for frequently accessed entities
- [ ] Profile and optimize memory usage in large document processing

## Implementation Plan

I recommend this implementation order:

  1. Database Schema Updates (First Priority)
    - Create migration script to add transaction_shares and position_shares columns to form4_transactions
    - Add derivative_total_shares_owned column to form4_relationships
    - This forms the foundation for all other changes
  2. ORM Model Updates
    - Update the Form4Transaction and Form4Relationship ORM models
    - Keep backward compatibility with existing shares_amount field
  3. Parser Updates
    - Modify Form4Parser to extract and separate transaction amounts from position amounts
    - Update position extraction for both derivatives and non-derivatives
  4. Writer Updates
    - Update Form4Writer to store values in the new columns
    - Implement separate derivative/non-derivative total calculations
  5. Testing
    - Update test cases to verify correct column usage
    - Test with both example files to ensure both types work

  Each step should be implemented and tested thoroughly before moving to the next. This approach minimizes risk and ensures we can verify
  each component works correctly.