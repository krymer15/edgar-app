-- V19__allow_null_transaction_code.sql
-- Makes transaction_code nullable to support position-only rows which have no transaction code

-- Alter the transaction_code column to allow nulls
ALTER TABLE form4_transactions ALTER COLUMN transaction_code DROP NOT NULL;

-- Add an index on is_position_only for faster lookup of position-only rows
CREATE INDEX idx_form4_transactions_is_position_only ON form4_transactions(is_position_only);

-- Update constraint to accept NULL transaction_code
ALTER TABLE form4_transactions DROP CONSTRAINT IF EXISTS transaction_code_check;
ALTER TABLE form4_transactions ADD CONSTRAINT transaction_code_check
    CHECK (
        (is_position_only = true AND transaction_code IS NULL) OR
        (is_position_only = false AND transaction_code IS NOT NULL)
    );