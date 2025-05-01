CREATE TABLE filing_metadata (
    id SERIAL PRIMARY KEY,
    cik TEXT NOT NULL,
    accession_number TEXT NOT NULL,
    form_type TEXT NOT NULL,
    filing_date DATE,
    filing_url TEXT,
    source_format TEXT DEFAULT 'sgml',
    parse_status TEXT, -- e.g. 'success', 'partial', 'error'
    error_message TEXT, -- optional for logging parse failures
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
