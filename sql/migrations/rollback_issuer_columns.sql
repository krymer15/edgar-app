-- rollback_issuer_columns.sql
-- Removes the redundant issuer_cik and is_issuer columns from filing_metadata table
-- These columns are unnecessary as each filing in the table is already from the perspective of the primary entity
-- The collector logic will still handle resolving the correct CIK during SGML download

BEGIN;

-- Drop the index first
DROP INDEX IF EXISTS idx_filing_metadata_issuer_cik;

-- Remove the columns
ALTER TABLE filing_metadata 
DROP COLUMN IF EXISTS issuer_cik,
DROP COLUMN IF EXISTS is_issuer;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration complete: Removed issuer_cik and is_issuer columns from filing_metadata';
END $$;

COMMIT;