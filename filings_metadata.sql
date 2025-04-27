CREATE TABLE filings_metadata (
    accession_number TEXT PRIMARY KEY,
    cik TEXT NOT NULL,  -- raw, not padded
    company_name TEXT NOT NULL,
    ticker TEXT,
    form_type TEXT NOT NULL,
    filed_date DATE NOT NULL,
    items TEXT[], -- New: array of item codes like ['1.01', '2.03']
    filing_url TEXT NOT NULL,
    local_file_path TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_accession_number UNIQUE (accession_number)
);

-- Useful indexes
CREATE INDEX idx_filings_metadata_cik ON filings_metadata (cik);
CREATE INDEX idx_filings_metadata_form_type ON filings_metadata (form_type);
CREATE INDEX idx_filings_metadata_filed_date ON filings_metadata (filed_date);
