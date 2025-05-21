-- Migration script for Form 4 position-only rows and total_shares_owned
-- This script adds support for the following features:
-- 1. Position-only rows in Form 4 filings (Bug 10 fix)
-- 2. Total shares owned calculation for Form 4 relationships (Bug 11 fix)

-- Make transaction_date nullable to support position-only rows
ALTER TABLE form4_transactions
ALTER COLUMN transaction_date DROP NOT NULL;

-- Add is_position_only flag to form4_transactions
ALTER TABLE form4_transactions
ADD COLUMN is_position_only BOOLEAN DEFAULT FALSE;

-- Add underlying_security_shares to form4_transactions (for derivative holdings)
ALTER TABLE form4_transactions
ADD COLUMN underlying_security_shares NUMERIC;

-- Add total_shares_owned to form4_relationships
ALTER TABLE form4_relationships
ADD COLUMN total_shares_owned NUMERIC;

-- Add index for improved query performance
CREATE INDEX idx_form4_relationships_total_shares 
ON form4_relationships(total_shares_owned);

-- Add comments describing the new fields
COMMENT ON COLUMN form4_transactions.is_position_only IS 'Indicates whether this is a position-only row with no transaction (nonDerivativeHolding or derivativeHolding)';
COMMENT ON COLUMN form4_transactions.underlying_security_shares IS 'Number of underlying security shares for derivative holdings';
COMMENT ON COLUMN form4_relationships.total_shares_owned IS 'Calculated total shares owned based on all related transactions';

-- Note: If this script was already executed manually (total_shares_owned was added),
-- the script will produce an error on that statement only, but still apply the other changes.