CREATE TABLE form4_filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL,
    cik TEXT NOT NULL,
    form_type TEXT NOT NULL DEFAULT '4',
    filing_date DATE NOT NULL,
    issuer JSON,
    reporting_owner JSON,
    non_derivative_transactions JSON,
    derivative_transactions JSON
);
CREATE INDEX idx_form4_accession ON form4_filings (accession_number);
CREATE INDEX idx_form4_cik ON form4_filings (cik);
