CREATE TABLE filing_parties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL REFERENCES filing_metadata(accession_number) ON DELETE CASCADE,
    party_cik TEXT NOT NULL,
    party_name TEXT,
    party_type TEXT NOT NULL, -- 'company', 'individual', 'fund', etc.
    party_role TEXT NOT NULL, -- 'issuer', 'reporting_owner', 'subject_company', 'filed_by', etc.
    is_primary BOOLEAN DEFAULT false,
    relationship_data JSONB, -- Additional relationship-specific data
    filing_date DATE,  -- Denormalized for easier querying
    
    -- Additional informative fields
    ownership_percentage NUMERIC, -- For beneficial ownership filings
    officer_title TEXT,  -- For executive role filings
    is_director BOOLEAN,
    is_officer BOOLEAN,
    is_ten_percent_owner BOOLEAN,
    
    -- Constraints
    UNIQUE (accession_number, party_cik, party_role)
);

-- Appropriate indexes
CREATE INDEX idx_filing_parties_party_cik ON filing_parties(party_cik);
CREATE INDEX idx_filing_parties_party_role ON filing_parties(party_role);
CREATE INDEX idx_filing_parties_filing_date ON filing_parties(filing_date);