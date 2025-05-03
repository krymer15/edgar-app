CREATE TABLE exhibit_metadata (
    id SERIAL PRIMARY KEY,
    accession_number TEXT NOT NULL REFERENCES parsed_sgml_metadata(accession_number),
    filename TEXT,
    type TEXT,
    description TEXT,
    accessible BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
