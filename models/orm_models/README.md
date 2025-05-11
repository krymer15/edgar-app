# models/orm_models

SQLAlchemy ORM classes defining the database schema:

- **FilingMetadata**  
  Stores accession numbers, CIK, form type, filing dates, and URLs.
- **FilingDocument**  
  Tracks each downloaded document or exhibit, with flags and URLs.
- **ParsedChunkModel**  
  Persists parsed text chunks (with embedding storage column).
- **FilingVector**  
  Holds vector embeddings for each chunk using pgvector.