CREATE TABLE submissions_metadata (
    accession_number TEXT PRIMARY KEY,
    cik TEXT NOT NULL REFERENCES companies_metadata(cik),
    filing_date DATE,
    report_date DATE,
    form_type TEXT,
    items TEXT[],
    primary_document TEXT,
    document_description TEXT,
    is_xbrl BOOLEAN,
    is_inline_xbrl BOOLEAN,
    acceptance_datetime TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
