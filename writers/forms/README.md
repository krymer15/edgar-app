# Form Writers

This directory contains writer components responsible for persisting form-specific data extracted from SEC filings to the database.

## Components

### Form4Writer

The `Form4Writer` class is a sophisticated writer that handles the complex data model for Form 4 (Statement of Changes in Beneficial Ownership) filings. It manages a multi-step process to store entities, relationships, and transactions from insider trading reports.

#### Key Responsibilities

- Creates and maintains entity records (issuers and reporting owners)
- Establishes relationships between issuers and owners
- Records individual securities transactions
- Handles both non-derivative (stock) and derivative (options, warrants) transactions
- Supports position-only rows without transaction details (Bug 10 fix)
  - Maintains null transaction_code, transaction_date fields for position rows
  - Sets is_position_only flag to distinguish from regular transactions
  - Uses shares_amount to store Column 5 position data (not transaction amount)
  - Handles underlying_security_shares for derivative position records
- Calculates and stores total shares owned by relationship (Bug 11 fix)
  - Aggregates impact of all transactions for a given relationship
  - Groups calculations by security_title for accurate position tracking
  - Considers acquisition/disposition flags to add/subtract from total position
  - Includes position-only rows in the calculation
- Ensures proper database transaction management and error handling

#### Database Schema

The Form 4 data is stored across several related tables:

1. **entities**: Represents companies (issuers) and people (reporting owners)
   - Primary key: `id` (UUID)
   - Unique constraint: `cik`
   - Key fields: `name`, `entity_type` (company, person, trust, group)

2. **form4_filings**: Core Form 4 filing information
   - Primary key: `id` (UUID)
   - Key fields: `accession_number`, `period_of_report`, `has_multiple_owners`

3. **form4_relationships**: Relationships between issuers and reporting owners
   - Primary key: `id` (UUID)
   - Foreign keys: `form4_filing_id`, `issuer_entity_id`, `owner_entity_id`
   - Key fields: `is_director`, `is_officer`, `is_ten_percent_owner`, `officer_title`, `total_shares_owned`

4. **form4_transactions**: Individual security transactions and positions
   - Primary key: `id` (UUID)
   - Foreign keys: `form4_filing_id`, `relationship_id`
   - Key fields: `transaction_code`, `transaction_date`, `security_title`, `shares_amount`, `price_per_share`
   - Additional fields: `is_position_only`, `underlying_security_shares`

#### Usage

```python
from writers.forms.form4_writer import Form4Writer
from models.database import SessionLocal

# Create a database session
session = SessionLocal()

# Initialize the writer with the session
writer = Form4Writer(db_session=session)

# Write Form 4 data (handles entity creation/update and all relationships)
writer.write_form4_data(form4_data)
```

#### Implementation Details

The `Form4Writer` implements a multi-step transaction process:

1. **Initial Setup**
   - Formats the accession number for database storage
   - Checks for existing filing to determine update vs. insert
   - Deletes existing relationships and transactions for clean updates

2. **Entity Creation/Management**
   - Creates or updates issuer and owner entities
   - Uses `EntityWriter` for entity management
   - Handles both direct entity objects and relationship-based entity references

3. **Relationship Management**
   - Links issuers and owners with specific relationship details
   - Records director/officer/ten-percent owner status
   - Stores officer titles and other relationship metadata

4. **Transaction and Position Recording**
   - Associates transactions with the appropriate relationship
   - Stores transaction codes, dates, amounts, and prices
   - Handles both direct ownership and indirect ownership details
   - Supports position-only rows for holdings without transaction details
   - Calculates total share ownership from transactions and positions

5. **Transaction Management**
   - Uses strategic transaction boundaries for data consistency
   - Implements proper error handling and rollback
   - Provides detailed logging throughout the process

## Dependencies

The form writers rely on several shared components:

- **EntityWriter**: Creates and manages entity records with caching for performance
- **Adapter Functions**: Convert between dataclasses and ORM models
- **Database Session Management**: SQLAlchemy session handling
- **Error Handling**: Consistent exception handling and logging

## Related Components

- [Form4Parser](../../parsers/forms/form4_parser.py): Extracts data from Form 4 XML
- [Form4Orchestrator](../../orchestrators/forms/form4_orchestrator.py): Orchestrates the Form 4 processing pipeline
- [EntityData](../../models/dataclasses/entity.py): Dataclass for entity information
- [Form4FilingData](../../models/dataclasses/forms/form4_filing.py): Dataclass for Form 4 data