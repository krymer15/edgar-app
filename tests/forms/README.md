# Form Parser Tests

This directory contains tests for form-specific parsers, with a focus on the Form 4 parser and related components.

## Form 4 Test Suite

The Form 4 test suite verifies correct parsing and processing of Form 4 filings, including proper handling of various edge cases. These tests ensure that the Form 4 processing pipeline works correctly from SGML/XML extraction through final database object creation.

### Bug Fix Test Files

Several Form 4-specific issues have been addressed, with dedicated test files to verify each fix:

1. **test_form4_relationship_flags.py**
   - Tests boolean flag handling in Form4Parser.extract_entity_information
   - Verifies support for both "1" and "true" values in XML relationship flags
   - Ensures proper setting of is_director, is_officer, etc. flags

2. **test_form4_footnote_extraction.py**
   - Tests footnote extraction in Form4Parser
   - Verifies footnote ID transfer to Form4TransactionData objects
   - Checks extraction from both derivative and non-derivative transactions

3. **test_form4_relationship_details.py**
   - Tests population of the relationship_details field
   - Verifies structured JSON metadata in Form4RelationshipData objects
   - Checks proper role information formatting and entity identification

4. **test_form4_entity_extraction.py**
   - Tests entity extraction from Form 4 XML
   - Verifies proper CIK normalization and name extraction
   - Checks entity classification (person vs. company)

### Test Fixtures

The tests use fixtures from the `../fixtures/` directory, including:

- **0001610717-23-000035.xml**: Test file with "true" value for is_director
- **0001610717-23-000035_rel_num.xml**: Test file with "1" value for is_director
- **form4_sample.xml**: General sample for basic Form 4 testing

### Known Issues (Resolved)

The following issues have been identified and fixed in the Form 4 processing pipeline:

1. **Owner Count Issue**
   - Bug: The system incorrectly reported multiple owners when there was only one
   - Fix: Added deduplication by CIK in Form4SgmlIndexer._extract_reporting_owners

2. **Relationship Flags Issue**
   - Bug: The is_director flag was set to False when XML had "true" instead of "1"
   - Fix: Updated boolean flag parsing to handle both "1" and "true" values

3. **Missing Footnotes Issue**
   - Bug: Footnotes weren't properly extracted from the XML
   - Fix: Enhanced extraction in Form4Parser and Form4SgmlIndexer._parse_transaction

4. **Multiple Owners Flag Issue**
   - Bug: The has_multiple_owners flag was incorrectly set to True
   - Fix: Added explicit update based on actual relationship count

5. **Footnote Transfer Issue**
   - Bug: Footnotes were detected but not transferred to transaction objects
   - Fix: Updated _add_transactions_from_parsed_xml to pass footnote IDs

6. **Relationship Details Issue**
   - Bug: The relationship_details field in form4_relationships table was NULL
   - Fix: Added population of the field with structured JSON metadata

### Running Tests

To run all Form 4 tests:
```bash
python -m pytest tests/forms/test_form4_*.py -v
```

To run a specific test file:
```bash
python -m pytest tests/forms/test_form4_footnote_extraction.py -v
```

## Schema Redesign Test Suites

### Position Tracking Tests (`position/`)

The position test suite verifies the Form 4 position tracking functionality implemented as part of the schema redesign (Phase 3). These tests ensure proper tracking of security positions over time.

#### Position Test Files

1. **test_mocked_service.py**
   - Tests position service functionality using mock implementations
   - Verifies position creation, retrieval, and calculation methods
   - Tests position updates from transactions
   - Validates position-only entry handling
   - Checks position history tracking and total share calculations

2. **conftest.py**
   - Provides test fixtures for position testing
   - Mock database sessions and sample position data
   - Sample transaction data for position update testing

#### Position Service Functionality

The position service provides the following key capabilities:

- **Position Creation**: Create new position entries from transactions or holdings
- **Position Retrieval**: Get positions by ID, relationship, or security
- **Position Updates**: Update positions based on transaction impacts
- **Position History**: Track position changes over time
- **Total Calculations**: Calculate total shares owned per security
- **Position Recalculation**: Recalculate positions from transaction history

### Transaction Tests (`transaction/`)

The transaction test suite verifies the normalized transaction handling for both derivative and non-derivative securities.

#### Transaction Test Files

1. **test_mocked_service.py**
   - Tests transaction service functionality using mock implementations
   - Verifies transaction creation for both derivative and non-derivative types
   - Tests transaction retrieval by various criteria
   - Validates transaction impact calculations

### Security Tests (`security/`)

The security test suite verifies the normalized security handling and derivative security relationships.

#### Security Test Files

1. **test_mocked_service.py**
   - Tests security service functionality using mock implementations
   - Verifies security normalization and creation
   - Tests derivative security relationships
   - Validates security search and retrieval

## Testing Approach

### Mock-Based Testing Strategy

The schema redesign tests use a mock-based testing approach to avoid circular dependencies and database requirements:

1. **Isolated Testing**: Each service is tested independently without requiring database connections
2. **Mock Services**: Mock implementations provide the same interface as real services
3. **Dataclass Focus**: Tests focus on dataclass validation and business logic
4. **Performance**: Mock tests run quickly without database overhead

### Test Organization

- Each major component (position, transaction, security) has its own test directory
- Mock service implementations are provided for isolated testing
- Shared fixtures are defined in `conftest.py` files
- Test files follow the naming convention `test_mocked_service.py`

## Running Schema Redesign Tests

To run all schema redesign tests:
```bash
python -m pytest tests/forms/position/ tests/forms/transaction/ tests/forms/security/ -v
```

To run position-specific tests:
```bash
python -m pytest tests/forms/position/ -v
```

To run a specific position test:
```bash
python -m pytest tests/forms/position/test_mocked_service.py::TestPositionFunctionality::test_position_creation -v
```

## Other Form Tests

As support for other form types is implemented, relevant test files should be added to this directory following similar patterns and naming conventions.