-- sql/migrations/add_processing_status_to_filing_metadata.sql

-- Create the ENUM type first
CREATE TYPE processing_status_enum AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'skipped'
);

-- Add new columns
ALTER TABLE filing_metadata 
ADD COLUMN processing_status processing_status_enum,
ADD COLUMN processing_started_at TIMESTAMPTZ,
ADD COLUMN processing_completed_at TIMESTAMPTZ,
ADD COLUMN processing_error TEXT,
ADD COLUMN job_id VARCHAR(36),
ADD COLUMN last_updated_by VARCHAR(100);

-- Add constraint for timestamps
ALTER TABLE filing_metadata 
    ADD CONSTRAINT check_processing_timestamps 
    CHECK (
        processing_completed_at IS NULL OR 
        processing_started_at IS NULL OR
        processing_completed_at >= processing_started_at
    );

-- Add indexes for faster queries
CREATE INDEX idx_filing_metadata_processing_status ON filing_metadata(processing_status);
CREATE INDEX idx_filing_metadata_job_id ON filing_metadata(job_id);

-- Backfill status based on existing data
-- Mark records that have been processed (exist in filing_documents) as completed
UPDATE filing_metadata fm
SET processing_status = 'completed'::processing_status_enum,
    processing_completed_at = NOW(),
    last_updated_by = 'migration'
WHERE EXISTS (
    SELECT 1 
    FROM filing_documents fd 
    WHERE fd.accession_number = fm.accession_number
);

-- Mark remaining records as pending
UPDATE filing_metadata
SET processing_status = 'pending'::processing_status_enum,
    last_updated_by = 'migration'
WHERE processing_status IS NULL;

-- Create function for status updates with validation
CREATE OR REPLACE FUNCTION update_filing_status(
    p_accession_number TEXT,
    p_status TEXT,
    p_error TEXT DEFAULT NULL,
    p_user TEXT DEFAULT 'system'
) RETURNS BOOLEAN AS $$
DECLARE
    v_timestamp TIMESTAMPTZ := NOW();
    v_valid_statuses TEXT[] := ARRAY['pending', 'processing', 'completed', 'failed', 'skipped'];
BEGIN
    -- Validate status
    IF NOT p_status = ANY(v_valid_statuses) THEN
        RAISE EXCEPTION 'Invalid status: %. Valid statuses are: %', p_status, v_valid_statuses;
    END IF;

    -- Update the record based on status
    IF p_status = 'processing' THEN
        UPDATE filing_metadata SET
            processing_status = p_status::processing_status_enum,
            processing_started_at = v_timestamp,
            last_updated_by = p_user
        WHERE accession_number = p_accession_number;
    ELSIF p_status = 'completed' THEN
        UPDATE filing_metadata SET
            processing_status = p_status::processing_status_enum,
            processing_completed_at = v_timestamp,
            last_updated_by = p_user
        WHERE accession_number = p_accession_number;
    ELSIF p_status = 'failed' THEN
        UPDATE filing_metadata SET
            processing_status = p_status::processing_status_enum,
            processing_error = p_error,
            last_updated_by = p_user
        WHERE accession_number = p_accession_number;
    ELSE
        UPDATE filing_metadata SET
            processing_status = p_status::processing_status_enum,
            last_updated_by = p_user
        WHERE accession_number = p_accession_number;
    END IF;
    
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

-- Log completion message
DO $$
DECLARE
    completed_count INT;
    pending_count INT;
BEGIN
    SELECT COUNT(*) INTO completed_count FROM filing_metadata WHERE processing_status = 'completed';
    SELECT COUNT(*) INTO pending_count FROM filing_metadata WHERE processing_status = 'pending';
    RAISE NOTICE 'Migration complete: % records marked completed, % records marked pending', 
                 completed_count, pending_count;
END $$;