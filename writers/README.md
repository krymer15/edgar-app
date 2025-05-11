# writers

Persistence layer for writing pipeline outputs to the database:

## Modules

- **base_writer.py**  
  - Defines the `write()` interface.

- **metadata_writer.py**  
  - Persists `FilingMetadata` records.
  - `MetadataWriter` → writes `FilingMetadata`

- **document_writer.py**  
  - Persists `FilingDocument` entries.
  - `DocumentWriter` → writes `FilingDocument`

- **parsed_writer.py**  
  - Persists `ParsedChunkModel` rows.
  - `ParsedWriter` → writes `ParsedChunkModel`

- **vector_writer.py**  
  - Persists `FilingVector` embeddings.
  - `VectorWriter` → writes `FilingVector`
## Key Classes

Abstract `BaseWriter`:

```python
Copy
Edit
class BaseWriter:
    def write(self, obj) -> None:
        raise NotImplementedError
```


### Notes
- All writers use SQLAlchemy ORM.
- Canonical field for primary doc URL is `primary_doc_url`.

