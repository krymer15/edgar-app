# Form 4 Parser V2 Implementation Prompt

## Objective

Implement a new **Form4ParserV2** that processes pure XML content (not SGML) with full integration into the Phase 1-3 service layer. This parser will replace the legacy Form4Parser while preserving all sophisticated business logic and edge case handling.

## Context & Background

**Project Status:**
- ✅ **Phase 1 Complete**: Security normalization with SecurityService, SecurityData, DerivativeSecurityData
- ✅ **Phase 2 Complete**: Transaction separation with TransactionService, NonDerivativeTransactionData, DerivativeTransactionData  
- ✅ **Phase 3 Complete**: Position tracking with PositionService, RelationshipPositionData
- 🔄 **Phase 4 Current**: Parser integration with new services (CRITICAL MISSING COMPONENT)

**Critical Issue:** The new service layer (Phases 1-3) is isolated from the actual Form 4 processing pipeline. The current parsers still use legacy models, making the new implementation non-functional in production.

## Architecture Documentation

**PRIMARY REFERENCE:** `tests/tmp/form4_parser_architecture.md`

This comprehensive document contains:
- Complete class definitions and method signatures
- Detailed implementation strategies for each component  
- Preserved business logic patterns from legacy parsers
- Service integration approaches
- Testing strategies and usage examples

## Key Requirements

### Input/Output Specification
- **Input**: Pure XML content from `.xml` files (e.g., `tests/fixtures/0001610717-23-000035.xml`)
- **Metadata Container**: `Form4FilingContext` dataclass with accession_number, cik, filing_date
- **No SGML**: Parser does NOT handle `.txt` files with SGML wrappers
- **Service Integration**: Full integration with SecurityService, TransactionService, PositionService

### Core Implementation Tasks

#### 1. Create Form4FilingContext Dataclass
```python
# Location: models/dataclasses/forms/form4_filing_context.py
@dataclass
class Form4FilingContext:
    accession_number: str
    cik: str
    filing_date: Optional[date] = None
    form_type: str = "4"
    source_url: Optional[str] = None
```

#### 2. Implement Form4ParserV2 Class
```python
# Location: parsers/forms/form4_parser_v2.py
class Form4ParserV2(BaseParser):
    def __init__(self, security_service, transaction_service, position_service, entity_service=None):
    def parse(self, xml_content: str, filing_context: Form4FilingContext) -> Dict[str, Any]:
```

#### 3. Service Integration Points
- **SecurityService**: `services/forms/security_service.py` - for security normalization
- **TransactionService**: `services/forms/transaction_service.py` - for transaction processing  
- **PositionService**: `services/forms/position_service.py` - for position tracking
- **New Dataclasses**: Use Phase 1-3 dataclasses (SecurityData, NonDerivativeTransactionData, etc.)

### Business Logic Preservation Requirements

**CRITICAL**: All business logic from legacy parsers must be preserved. Key patterns documented in architecture:

1. **Fallback Chain Strategy** - Multi-strategy extraction with graceful degradation
2. **Entity Type Detection** - Business entity classification heuristics  
3. **CIK-based Deduplication** - Prevent duplicate owners in complex filings
4. **Error-Resilient Type Conversion** - Safe conversion with data integrity
5. **4-Strategy Footnote Extraction** - Comprehensive footnote detection
6. **Boolean Flag Normalization** - Handle both "1"/"0" and "true"/"false"
7. **Position-Only Holdings** - Support holdings without transactions
8. **Group Filing Detection** - Identify filings with multiple owners

### Test Files for Validation

Use these sample XML files to validate different scenarios:
- `tests/fixtures/0001610717-23-000035.xml` - Basic single owner case
- `tests/fixtures/000032012123000040_form4.xml` - Multiple transaction types
- `tests/fixtures/000120919123029527_form4.xml` - Multiple owners (group filing)
- `tests/fixtures/000092963823001482_form4.xml` - Derivative transactions

## Implementation Steps

### Step 1: Create Form4FilingContext (30 minutes)
Create the metadata container dataclass in `models/dataclasses/forms/form4_filing_context.py`

### Step 2: Implement Form4ParserV2 Core (2-3 hours)
1. Create `parsers/forms/form4_parser_v2.py`
2. Implement constructor with service injection
3. Implement main `parse()` method with single-pass XML extraction
4. Add XML safety parsing and error handling

### Step 3: Implement Entity Extraction (1-2 hours)
1. `_extract_and_process_entities()` method
2. Preserve deduplication logic and entity type heuristics
3. Extract relationship information with boolean flag handling
4. Integrate with EntityService if available

### Step 4: Implement Security Normalization (1-2 hours)
1. `_extract_and_normalize_securities()` method
2. Process non-derivative and derivative securities
3. Use SecurityService for normalization and deduplication
4. Handle underlying security relationships for derivatives

### Step 5: Implement Transaction Processing (2-3 hours)
1. `_process_transactions()` method
2. Parse non-derivative and derivative transactions
3. Use TransactionService for transaction creation
4. Auto-update positions through PositionService
5. Preserve comprehensive footnote extraction

### Step 6: Implement Position Handling (1-2 hours)
1. `_process_positions()` method  
2. Handle position-only holdings (nonDerivativeHolding/derivativeHolding)
3. Use PositionService for position-only entries
4. Extract ownership information and footnotes

### Step 7: Add Helper Methods (1 hour)
1. `_get_text()`, `_get_decimal()`, `_parse_date_safely()`
2. `_parse_boolean_flag()`, `_extract_footnote_ids()`
3. `_classify_entity_type()`, `_parse_xml_safely()`

### Step 8: Create Comprehensive Tests (2-3 hours)
1. Create `tests/forms/test_form4_parser_v2.py`
2. Mock-based unit tests for service integration
3. Test with sample XML files for different scenarios
4. Validate edge cases and error handling

### Step 9: Integration Testing (1-2 hours)
1. Test with actual service instances
2. Validate database operations
3. Performance testing vs legacy parser
4. End-to-end validation with orchestrator

## Key Integration Points

### Service Dependencies
```python
# Initialize services (example usage)
db_session = get_db_session()
security_service = SecurityService(db_session)
transaction_service = TransactionService(db_session)  
position_service = PositionService(db_session)

# Initialize parser
parser = Form4ParserV2(security_service, transaction_service, position_service)
```

### Database Session Management
- Services expect database session injection
- Parser should not manage transactions directly
- Caller (orchestrator) handles commit/rollback

### Error Handling Strategy
- Parse errors should return structured error responses
- Service errors should be logged but not crash parser
- Maintain data integrity through validation

## Success Criteria

### Functional Requirements
- [ ] Parse all sample XML files successfully
- [ ] Full service integration working (SecurityService, TransactionService, PositionService)
- [ ] All legacy business logic preserved
- [ ] Comprehensive footnote extraction functional
- [ ] Position-only holdings supported
- [ ] Multiple owner scenarios handled
- [ ] Boolean flag variations processed correctly

### Performance Requirements
- [ ] Single-pass XML extraction implemented
- [ ] Processing time equal to or better than legacy parser
- [ ] Memory usage optimized
- [ ] Service layer operations efficient

### Quality Requirements
- [ ] Comprehensive test coverage (>90%)
- [ ] Clean service injection with dependency injection
- [ ] Type hints throughout
- [ ] Error handling robust
- [ ] Documentation complete

## File Structure

```
parsers/forms/
├── form4_parser_v2.py           # New parser implementation
├── form4_parser.py              # Legacy parser (keep for now)
└── README.md                    # Update with V2 info

models/dataclasses/forms/
├── form4_filing_context.py      # New metadata container
├── security_data.py             # Existing (Phase 1)
├── transaction_data.py          # Existing (Phase 2)  
└── position_data.py             # Existing (Phase 3)

tests/forms/
├── test_form4_parser_v2.py      # New comprehensive tests
└── fixtures/                    # Existing sample XML files

services/forms/
├── security_service.py          # Existing (Phase 1)
├── transaction_service.py       # Existing (Phase 2)
└── position_service.py          # Existing (Phase 3)
```

## Important Notes

1. **Reference Legacy Code**: Study `parsers/forms/form4_parser.py` and `parsers/sgml/indexers/forms/form4_sgml_indexer.py` for business logic patterns (but don't copy the architecture)

2. **Preserve Bug Fixes**: The legacy code contains numerous bug fixes for edge cases that must be preserved in the new implementation

3. **Service Integration**: This is the critical missing piece - the new services exist but aren't connected to the parsing pipeline

4. **Testing Strategy**: Use mock-based testing for service integration, plus real XML file testing for business logic validation

5. **Backward Compatibility**: Keep legacy parsers until V2 is fully validated in production

## Next Steps After Implementation

1. **Orchestrator Integration**: Update `orchestrators/forms/form4_orchestrator.py` to use Form4ParserV2
2. **Performance Validation**: Compare performance with legacy implementation
3. **Production Testing**: Run with feature flag alongside legacy parser
4. **Documentation Updates**: Update relevant README files and architecture docs

This implementation will complete Phase 4 of the Form 4 schema redesign and make the new service layer functional in the production pipeline.