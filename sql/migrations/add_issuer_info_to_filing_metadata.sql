-- Add issuer identification fields to filing_metadata table
ALTER TABLE filing_metadata 
ADD COLUMN issuer_cik TEXT,
ADD COLUMN is_issuer BOOLEAN DEFAULT TRUE;

-- Create index on issuer_cik for efficient queries
CREATE INDEX idx_filing_metadata_issuer_cik ON filing_metadata (issuer_cik);

-- Update existing records to assume current CIK is the issuer
UPDATE filing_metadata
SET is_issuer = TRUE, 
    issuer_cik = cik;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration complete: Added issuer_cik and is_issuer columns to filing_metadata';
END $$;