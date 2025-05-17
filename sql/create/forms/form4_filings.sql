CREATE TABLE form4_filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL,
    period_of_report DATE,
    has_multiple_owners BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_form4_accession UNIQUE(accession_number),
    CONSTRAINT form4_filings_accession_number_fkey
        FOREIGN KEY (accession_number)
        REFERENCES filing_metadata(accession_number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Index on accession_number for lookup joins
CREATE INDEX idx_form4_filings_accession ON form4_filings(accession_number);