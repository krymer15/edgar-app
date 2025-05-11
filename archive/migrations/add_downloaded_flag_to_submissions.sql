-- migrations/add_downloaded_flag_to_submissions.sql

-- Adds a 'downloaded' boolean flag to submissions_metadata table
ALTER TABLE submissions_metadata
ADD COLUMN IF NOT EXISTS downloaded BOOLEAN DEFAULT FALSE;
