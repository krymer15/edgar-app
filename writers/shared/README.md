# Shared Writers

This directory contains shared writer components that are used across multiple pipelines in the EDGAR App.

## Components

### EntityWriter

`EntityWriter` is a specialized component for creating and managing entity records (companies and people) in the database. It implements caching for improved performance during batch operations.

#### Key Responsibilities

- Creates or updates entity records for issuers and reporting owners
- Implements an in-memory cache to reduce redundant database queries
- Normalizes CIKs for consistent lookup
- Provides lookup by both CIK and UUID
- Handles entity type validation (company, person, trust, group)

#### Role in Form 4 Pipeline

`EntityWriter` plays a critical role in the Form 4 processing pipeline:

1. **Entity Creation**: Manages both issuer (company) and owner (person) entities
2. **Deduplication**: Prevents duplicate entity records based on CIK
3. **Relationship Support**: Provides entity record lookup for relationship creation
4. **Performance Optimization**: Reduces database queries during batch processing

The `Form4Writer` heavily relies on `EntityWriter` for its entity management needs, using the `get_or_create_entity` method to ensure entities exist before creating relationships and transactions.

#### Usage

```python
from writers.shared.entity_writer import EntityWriter
from models.dataclasses.entity import EntityData
from models.database import SessionLocal

# Create a database session
session = SessionLocal()

# Initialize the entity writer
entity_writer = EntityWriter(db_session=session)

# Create or update an entity
entity_data = EntityData(
    cik="0001234567",
    name="ACME Corporation",
    entity_type="company"
)
entity = entity_writer.get_or_create_entity(entity_data)

# Lookup entities with caching
entity_by_cik = entity_writer.get_entity_by_cik("1234567")
entity_by_id = entity_writer.get_entity_by_id(entity_id)
```

#### Implementation Details

The `EntityWriter` includes several optimization techniques:

1. **In-memory Caching**
   - Stores retrieved entities by normalized CIK
   - Avoids redundant database lookups during batch operations
   - Cache is maintained for the lifecycle of the writer instance

2. **Conditional Updates**
   - Only updates entity fields if they have changed
   - Avoids unnecessary database operations
   - Logs when entity details are updated

3. **Duplicate Prevention**
   - Uses CIK as a natural key for deduplication
   - Preserves entity IDs for proper foreign key relationships
   - Ensures consistency across related records

### RawFileWriter

`RawFileWriter` handles persisting raw file content to the filesystem with proper organization and error handling. It serves as the core component of **Pipeline 3: SGML Disk Storage**.

#### Key Responsibilities

- Writes raw file content to disk with organized directory structure
- Supports multiple file types (sgml, html_index, exhibits, xml)
- Creates directories as needed
- Ensures consistent UTF-8 encoding
- Provides detailed logging of file operations

#### Role in Pipelines

1. **Pipeline 3 (SGML Disk Storage)**
   - The `SgmlDiskOrchestrator` uses `RawFileWriter` through the `SgmlDiskCollector`
   - Responsible for writing complete SGML filings to the filesystem
   - Creates the directory structure by year/CIK/form type
   - This is the primary file persistence mechanism for raw EDGAR filings

2. **Form 4 Pipeline**
   - The `Form4Orchestrator` optionally uses `RawFileWriter` to store XML content
   - Controlled by the `write_raw_xml` parameter in the orchestrator
   - Saves extracted Form 4 XML content to the filesystem for debugging or archival
   - Example from `form4_orchestrator.py`:

```python
# Initialize RawFileWriter specifically for XML
raw_writer = RawFileWriter(file_type="xml") if write_raw_xml else None

# Create a RawDocument with the XML content
xml_doc = RawDocument(
    cik=filing.cik,
    accession_number=filing.accession_number,
    form_type=filing.form_type,
    filing_date=filing.filing_date,
    content=xml_content,
    filename=xml_filename,
    document_type="xml",
    source_url=source_url,
    source_type="form4_xml",
    description=f"Form 4 XML for {filing.accession_number}"
)

# Write to filesystem
xml_path = raw_writer.write(xml_doc)
```

#### Storage Structure

The `RawFileWriter` uses `path_manager.build_raw_filepath_by_type()` to create a consistent directory structure:

```
data/
├── sgml/             # SGML filings (.txt)
│   ├── 2025/         # Year
│   │   ├── 0001234567/  # CIK
│   │   │   └── 0001234567-25-000123.txt
│   │   └── ...
│
├── xml/              # XML files
│   ├── 2025/
│   │   ├── 0001234567/
│   │   │   └── 0001234567-25-000123_form4.xml
│   │   └── ...
│
├── html_index/       # Index.html files
└── exhibits/         # Filing exhibits
```

#### Usage

```python
from writers.shared.raw_file_writer import RawFileWriter
from models.dataclasses.raw_document import RawDocument
from datetime import date

# Initialize a writer for a specific file type
writer = RawFileWriter(file_type="sgml")  # Options: sgml, html_index, exhibits, xml

# Create a raw document
raw_doc = RawDocument(
    content="<DOCUMENT>...</DOCUMENT>",
    accession_number="0001234567-25-000123",
    cik="0001234567",
    form_type="8-K",
    filing_date=date(2025, 1, 15),
    filename="primary-document.txt"
)

# Write to disk
output_path = writer.write(raw_doc)
```

#### Implementation Details

The `RawFileWriter` uses the following workflow:

1. **Validation**
   - Verifies the file type is supported (`sgml`, `html_index`, `exhibits`, `xml`)
   - Ensures content is provided and valid

2. **Path Construction**
   - Uses `build_raw_filepath_by_type()` from `path_manager`
   - Creates a consistent directory structure based on year/CIK/form type

3. **Directory Creation**
   - Creates parent directories if they don't exist
   - Uses `os.makedirs()` with `exist_ok=True` for idempotence

4. **Content Writing**
   - Writes content with UTF-8 encoding
   - Handles file I/O with proper error handling

5. **Logging**
   - Logs successful writes with the full path
   - Logs detailed error information on failure

## Related Components

- [SgmlDiskOrchestrator](../../orchestrators/crawler_idx/sgml_disk_orchestrator.py): Pipeline 3 orchestrator that coordinates saving SGML to disk
- [Form4Orchestrator](../../orchestrators/forms/form4_orchestrator.py): Coordinates Form 4 processing including entity writing and optional XML storage
- [Form4Writer](../forms/form4_writer.py): Uses EntityWriter for entity management in Form 4 processing
- [PathManager](../../utils/path_manager.py): Provides path construction utilities used by RawFileWriter