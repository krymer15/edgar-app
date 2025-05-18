# Edgar App TODOs

This document lists high-priority architectural and feature improvements for the Edgar App project.

## Architectural Improvements

### 1. Refactor Form 4 SGML/XML Processing

**Issue**: Currently, XML parsing responsibilities are mixed into SGML indexing code, specifically in `parsers/sgml/indexers/forms/form4_sgml_indexer.py`. This creates architectural confusion and makes the code harder to maintain.

**Solution**: Separate SGML indexing and XML parsing responsibilities:

- [ ] Create a dedicated `parsers/xml/forms/form4_xml_parser.py` component
- [ ] Extract XML parsing logic from `Form4SgmlIndexer` into this new component
- [ ] Update `Form4SgmlIndexer` to focus solely on SGML indexing and XML extraction
- [ ] Modify the processing pipeline to connect these components appropriately
- [ ] Update tests to reflect the new architecture

**Benefits**:
- Clearer separation of concerns
- Better alignment with directory structure
- Improved maintainability and testability
- Easier extension to other form types

### 2. Implement Consistent Filing Processing Architecture

**Issue**: Different form types are processed in inconsistent ways, making the system harder to understand and extend.

**Solution**: Standardize the filing processing architecture:

- [ ] Define clear interfaces for each stage of processing (indexing, parsing, writing)
- [ ] Ensure consistent dataflow between components
- [ ] Implement consistent error handling and validation across all form types
- [ ] Document the standard processing flow for future form type implementations

**Benefits**:
- More predictable codebase
- Easier onboarding for new developers
- Faster implementation of new form types

## Feature Improvements

### 1. Expand Form Type Support

- [ ] Implement support for Form 3 (Initial Statement of Beneficial Ownership)
- [ ] Implement support for Form 5 (Annual Statement of Beneficial Ownership)
- [ ] Implement support for Form 8-K (Current Reports) with exhibit extraction
- [ ] Implement support for Form 10-K/Q (Annual and Quarterly Reports)

### 2. Enhance Entity Relationship Tracking

- [ ] Improve entity deduplication logic
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