# Here's how I'd recommend breaking down the Form 4 pipeline improvements into manageable Claude Code sessions:

Session 1: Schema Design Planning

- Review current schema vs actual implementation
- Design new schema with separate transaction/position tables
- Develop migration strategy
- Deliverable: Schema design document with migration plan

Session 2: Core Data Models

- Implement base entity and security models
- Create separate non-derivative/derivative transaction models
- Develop position history model
- Deliverable: Updated data models with tests

Session 3: Parser Refactoring

- Refactor XML parsing for cleaner extraction
- Improve entity extraction and matching
- Enhance footnote handling
- Deliverable: Refactored parser with consistent error handling

Session 4: Position Calculation Engine

- Implement specialized calculator for positions
- Add support for derivatives impact calculation
- Create position history tracking
- Deliverable: Position calculation module with tests

Session 5: Writer Refactoring

- Implement repository pattern for database operations
- Add transaction validation
- Optimize batch operations
- Deliverable: Refactored writer component with validation

Session 6: Orchestrator Improvements

- Enhance job coordination
- Add incremental processing
- Improve error handling and recovery
- Deliverable: Updated orchestrator with better progress tracking

Each session maintains focus on related components while producing a concrete deliverable, helping manage context and maintain progress.

  -------------

# SESSION PROMPTS

## Form 4 Pipeline Improvement Session Prompts

### Session 1: Schema Design Planning

I'm working on improving the Form 4 processing pipeline, starting with a schema redesign. Please help me:

1. Review the current schema structure in:
    - models/orm_models/forms/form4_transaction_orm.py
    - models/orm_models/forms/form4_relationship_orm.py
    - sql/create/forms/form4_transaction_tables.sql

2. Design an improved schema that:
    - Separates transaction and position tables
    - Properly models derivative vs non-derivative securities
    - Normalizes security information
    - Supports position history tracking

3. Create a migration strategy that:
    - Preserves existing data
    - Minimizes downtime
    - Includes validation steps

Please provide the schema design as SQL DDL statements and a detailed migration plan document.

### Session 2: Core Data Models

I need to implement the new data models for our Form 4 pipeline based on the schema design from our previous session. Please help me:

1. Create or update these dataclasses:
    - Base security model (common fields)
    - Non-derivative transaction
    - Derivative transaction
    - Position history
    - Enhanced entity data

2. Update the ORM models to match our new schema:
    - Implement proper relationships between models
    - Add appropriate validation
    - Ensure compatibility with SQLAlchemy patterns

3. Add unit tests for:
    - Model instantiation
    - Validation logic
    - Relationship integrity

Please focus on clean separation of concerns and type safety.

### Session 3: Parser Refactoring

I need to refactor the Form 4 XML parser to support our new data models. Please help me:

1. Review the existing parsing logic in:
    - parsers/forms/form4_parser.py
    - parsers/sgml/indexers/forms/form4_sgml_indexer.py

2. Refactor the parser to:
    - Use a single-pass XML extraction approach
    - Properly distinguish between transactions and positions
    - Extract normalized security information
    - Improve footnote handling
    - Implement consistent error handling

3. Add proper validation for:
    - Date fields
    - A/D flags and transaction codes
    - Security identifiers
    - Numeric values

Please ensure backward compatibility with existing pipeline components while preparing for our new models.

### Session 4: Position Calculation Engine

I need to develop a specialized position calculation engine for Form 4 data. Please help me:

1. Create a new module that:
    - Calculates position changes from transactions
    - Handles position-only rows properly
    - Accounts for derivative securities' impact
    - Tracks position history over time

2. Implement calculation strategies for:
    - Different security types (common stock, options, etc.)
    - Direct vs. indirect ownership
    - A/D flag interpretation
    - Total beneficial ownership

3. Add robust testing for:
    - Simple transactions (buys/sells)
    - Complex scenarios (options exercises, conversions)
    - Edge cases (missing data, contradictory flags)
    - Historical position reconstruction

Focus on accuracy, performance, and clean separation from persistence logic.

### Session 5: Writer Refactoring

I need to refactor the Form 4 writer component to work with our new data models and calculation engine. Please help me:

1. Review the existing writer logic in writers/forms/form4_writer.py

2. Implement a repository pattern with:
    - Separate repositories for each entity type
    - Atomic transaction handling
    - Optimized batch operations
    - Connection pooling improvements

3. Add a validation layer that:
    - Checks data consistency before writing
    - Validates foreign key references
    - Ensures business rules are followed
    - Provides clear error messages

4. Optimize database operations for:
    - Reduced round trips
    - Efficient bulk inserts
    - Proper indexing usage
    - Transaction management

Please focus on maintainability and performance while ensuring data integrity.

### Session 6: Orchestrator Improvements

I need to enhance the Form 4 orchestrator to coordinate our improved pipeline components. Please help me:

1. Review the existing orchestration in orchestrators/forms/form4_orchestrator.py

2. Refactor the orchestrator to:
    - Use the new data models and repositories
    - Implement incremental processing
    - Add better progress tracking
    - Improve error handling and recovery

3. Implement enhancements for:
    - Parallel processing where possible
    - Configurable batch sizes
    - Memory usage optimization
    - Detailed logging and metrics

4. Create a simple CLI interface for:
    - Processing specific filings
    - Reprocessing failed items
    - Generating status reports
    - Basic pipeline monitoring

Please ensure the orchestrator remains compatible with the existing daily ingestion pipeline while leveraging our new components.