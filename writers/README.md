# Writers

Writers are responsible for persisting structured data to storage (database or filesystem). They form the final stage of data processing pipelines in the EDGAR App.

## Architecture

Writers follow a clear separation of concerns pattern:
- They receive structured dataclass objects from orchestrators
- They convert these objects to ORM models or filesystem formats
- They handle storage concerns like transactions, error handling, and logging
- They do not contain business logic (which belongs in orchestrators)

## Directory Structure

```
writers/
├── README.md                  # This document
├── base_writer.py             # Abstract base class for writers
│
├── crawler_idx/               # Writers for the crawler.idx pipeline
│   ├── README.md              # Documentation for crawler_idx writers
│   ├── filing_documents_writer.py # Writes document metadata to database
│   └── filing_metadata_writer.py  # Writes filing metadata to database
│
├── forms/                     # Writers for SEC form-specific data
│   ├── README.md              # Documentation for form writers
│   └── form4_writer.py        # Writes Form 4 data (entities, relationships, transactions)
│
├── shared/                    # Shared utilities used by multiple writers
│   ├── README.md              # Documentation for shared writers
│   ├── entity_writer.py       # Creates and retrieves entity records
│   └── raw_file_writer.py     # Writes raw content to filesystem
│
└── submissions_api/           # Writers for the SEC Submissions API pipeline (placeholder)
```

## Core Components

### BaseWriter

Abstract base class that defines the interface for writers:

```python
class BaseWriter(ABC):
    def __init__(self, db_session):
        self.db_session = db_session

    @abstractmethod
    def write_metadata(self, *args, **kwargs):
        """Write collected filing metadata to storage."""
        pass

    @abstractmethod
    def write_content(self, *args, **kwargs):
        """Write parsed and structured filing content to storage."""
        pass
```

### Crawler IDX Writers

Writers for the EDGAR crawler.idx pipelines. These handle the metadata and document records from daily index files.

- **FilingMetadataWriter**: Writes filing metadata records to the `filing_metadata` table
- **FilingDocumentsWriter**: Writes document metadata records to the `filing_documents` table

[Documentation for crawler_idx writers](./crawler_idx/README.md)

### Form Writers

Writers for form-specific data extracted from SEC filings. Currently focused on Form 4 processing.

- **Form4Writer**: Writes Form 4 data, including:
  - Entity records (issuers and owners)
  - Relationship records between entities
  - Transaction records with details about securities traded

[Documentation for form writers](./forms/README.md)

### Shared Writers

Utilities that handle common writing tasks across different pipelines:

- **EntityWriter**: Creates and retrieves entity records with caching for performance
- **RawFileWriter**: Writes raw file content to the filesystem with organized directory structure

[Documentation for shared writers](./shared/README.md)

## Database Tables

Writers persist data to the following key database tables:

### Crawler IDX Pipeline
- **filing_metadata**: Core table for SEC filing records
- **filing_documents**: Metadata for all documents within filings

### Form 4 Pipeline
- **entities**: Database representation of companies and people
- **form4_filings**: Form 4 filing metadata
- **form4_relationships**: Relationships between issuers and reporting owners
- **form4_transactions**: Security transaction details

## Writer Behaviors

Writers implement several important behaviors:

1. **Transaction Management**
   - Writers handle database transactions with proper commit/rollback
   - Some writers use per-record transactions for better isolation
   - Others use batched transactions for better performance

2. **Upsert Operations**
   - Writers check for existing records to avoid duplicates
   - They update fields when records already exist (e.g., processing status)
   - They implement efficient update detection to minimize database operations

3. **Error Handling**
   - Writers catch and log database exceptions
   - They properly roll back transactions on error
   - They report success/failure counts to orchestrators

4. **Optimization Techniques**
   - Entity caching to reduce database queries
   - Batched operations for improved performance
   - Sequential dependencies for complex relationships

## Usage Patterns

### Database Writers

```python
# Example: Using a database writer
from writers.crawler_idx.filing_metadata_writer import FilingMetadataWriter

# Initialize writer
writer = FilingMetadataWriter()

# Write metadata records
writer.upsert_many(filing_metadata_records)
```

### File Writers

```python
# Example: Using a file writer
from writers.shared.raw_file_writer import RawFileWriter

# Initialize writer for a specific file type
writer = RawFileWriter(file_type="sgml")

# Write file content
output_path = writer.write(raw_document)
```

### Complex Writers (Form 4)

```python
# Example: Using the Form 4 writer with relationships
from writers.forms.form4_writer import Form4Writer
from models.database import SessionLocal

# Create database session
session = SessionLocal()

# Initialize writer with session
writer = Form4Writer(db_session=session)

# Write Form 4 data (entities, relationships, transactions)
writer.write_form4_data(form4_data)
```

## Design Patterns

Writers implement several design patterns:

1. **Adapter Pattern**
   - Dataclass objects are converted to ORM models via adapter functions
   - Adapters are centralized in `models/adapters/dataclass_to_orm.py`

2. **Repository Pattern**
   - Writers encapsulate all database interactions
   - They provide high-level methods for creating/updating/retrieving data

3. **Transaction Script Pattern**
   - Complex writers use transaction scripts for multi-step persistence
   - Example: Form4Writer handles entities → relationships → transactions

4. **Caching Pattern**
   - EntityWriter implements an in-memory cache to reduce database queries
   - Cache is maintained at the writer level for the lifecycle of an operation

## Related Components

- [Orchestrators](../orchestrators/): Coordinate the processing flow and invoke writers
- [Models/Dataclasses](../models/dataclasses/): Define the input structures for writers
- [Models/ORM](../models/orm_models/): Define the database models written by writers
- [Models/Adapters](../models/adapters/): Convert between dataclasses and ORM models