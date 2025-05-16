-- sql/migrations/add_issuer_cik_to_filing_documents.sql

BEGIN;

-- Add issuer_cik column to filing_documents table
ALTER TABLE filing_documents
ADD COLUMN issuer_cik TEXT;

-- Create index for efficient queries
CREATE INDEX idx_filing_documents_issuer_cik ON filing_documents (issuer_cik);

-- Add a comment to the table for documentation
COMMENT ON COLUMN filing_documents.issuer_cik IS 
'The CIK of the actual issuer of the filing, which may differ from the cik column for Form 4/3/5, 13D/G filings where a reporting owner may be in the cik column';

COMMIT;

-- Optional: Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration complete: Added issuer_cik column to filing_documents table';
END $$;