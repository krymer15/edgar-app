-- Set this to your test filing date (e.g., 2025-04-28)
-- OR your ingestion run_id (e.g., 2025-04-28T12-00-00Z)
\set target_date '2025-04-28'
\set target_run_id ''

-- Step 1: Delete exhibits tied to filings on this date
DELETE FROM exhibit_metadata
WHERE accession_number IN (
    SELECT accession_number
    FROM parsed_sgml_metadata
    WHERE filing_date = :'target_date'
    OR (:'target_run_id' <> '' AND run_id = :'target_run_id')
);

-- Step 2: Delete parsed metadata
DELETE FROM parsed_sgml_metadata
WHERE filing_date = :'target_date'
OR (:'target_run_id' <> '' AND run_id = :'target_run_id');
