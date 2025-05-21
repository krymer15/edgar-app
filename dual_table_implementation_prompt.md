# Form 4 Dual-Table Implementation Prompt

## Context for Form 4 Dual-Table Implementation

In our previous sessions we identified several issues with the current Form 4 transaction handling:
- The current implementation uses a single table for both derivative and non-derivative transactions
- Position-only rows and transaction rows are mixed in the same table
- Columns 4 and 5 (transaction amount vs. ending position) use the same field
- Derivative securities need separate calculations from non-derivatives

## Completed Work
- ✓ Fix the is_position_only flag in form4_writer.py to ensure position-only flag is properly set in database
- ✓ Fix shares_amount handling to ensure clarity between Column 4 (transaction) and Column 5 (positions)
- ✓ Update transaction_code handling - should be empty or null for position-only rows, not 'H'
- ✓ Test derivative position handling after fixing non-derivative issues
- ✓ Add documentation explaining the position-only row handling in the README

## Current Session Focus
- ☐ Create database migration for new form4_non_derivative_transactions and form4_derivative_transactions tables
- ☐ Create ORM models for non-derivative and derivative transactions
- ☐ Update Form4Parser to support separate transaction types
- ☐ Update Form4Writer to write to separate transaction tables
- ☐ Implement data migration script to populate new tables from existing data
- ☐ Add derivative_total_shares_owned to form4_relationships table
- ☐ Create unit tests for new table structure
- ☐ Implement transaction code enum for standardized code handling

## Implementation Plan

1. **First Step - Database Schema Migration**:
   - Create a migration script to add the new tables while keeping existing ones
   - Add appropriate indexes and constraints
   - This allows for a smooth transition with dual writing

2. **Second Step - Create ORM Models**:
   - Define Form4NonDerivativeTransaction and Form4DerivativeTransaction models
   - Include all the specialized fields for each type
   - Keep existing models for backward compatibility

3. **Third Step - Update Parser**:
   - Modify Form4Parser to clearly separate derivative and non-derivative extraction
   - Create distinct data structures for each type
   - Maintain backward compatibility by still populating the old unified structure

4. **Fourth Step - Update Writer**:
   - Implement dual-writing to both old and new tables
   - Create specialized methods for each transaction type
   - Update the total shares calculation to handle both types properly

## Form4_transactions Table Approach

1. **Initial Phase (Dual-Write)**:
   - Keep the form4_transactions table and continue writing to it
   - Simultaneously write to the new specialized tables
   - This ensures we don't break existing functionality while implementing the new structure

2. **Transition Phase**:
   - Update queries to read from the new tables instead of form4_transactions
   - Maintain the data in form4_transactions but start marking it as "legacy"
   - Add deprecation warnings in code that directly accesses this table

3. **Final Phase**:
   - Create a view on top of the new tables that mimics the structure of form4_transactions for any legacy code
   - Eventually stop writing to form4_transactions and only use the view for backward compatibility
   - In a future release, we could mark the table for removal

## Reference Files
- Database schema draft: `sql/create/forms/form4_transaction_tables.sql`
- Documentation: `docs/form4_implementation_notes.md`
- Test fixtures: `tests/fixtures/000032012123000040_form4.xml` (non-derivative), `tests/fixtures/000106299323011116_form4.xml` (derivative)
- ORM model: `models/orm_models/forms/form4_transaction_orm.py`
- Parser: `parsers/forms/form4_parser.py`
- Writer: `writers/forms/form4_writer.py`
- Dataclass models: `models/dataclasses/forms/form4_transaction.py`