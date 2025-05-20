# Edgar App TODOs

This document lists high-priority architectural and feature improvements for the Edgar App project.

## Architectural Improvements

### 1. ~~Refactor Form 4 SGML/XML Processing~~ (Resolved through documentation)

- [x] Updated README.md files in parsers directories to document the intentional hybrid approach to SGML/XML processing

### 2. ~~Implement Consistent Filing Processing Architecture~~ (Resolved through documentation)

- [x] Updated README.md files to document the inherent diversity of SEC filing formats
- [x] Documented the necessary flexibility in processing different form types
- [x] Provided clear patterns for implementing new form processors while acknowledging natural variations
- [x] Focused on documentation consistency rather than enforcing rigid architecture

## Feature Improvements

### 1. Form 4 Processing Improvements

- [x] Fix Bug 1: Deduplication of reporting owners in Form4SgmlIndexer
- [x] Fix Bug 2: Relationship flag handling to support both "1" and "true" values
- [x] Fix Bug 4: Update has_multiple_owners flag based on actual relationship count
- [x] Fix Bug 3: Enhance footnote extraction from Form 4 XML
- [x] Fix Bug 5: Fix footnote ID transfer to Form4TransactionData objects
- [x] Fix Bug 6: Populate relationship_details field in form4_relationships table
- [x] Add comprehensive tests for all Form 4 processing fixes
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