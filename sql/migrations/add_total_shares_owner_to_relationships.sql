-- Add total_shares_owned field to form4_relationships
  ALTER TABLE form4_relationships
  ADD COLUMN total_shares_owned NUMERIC;

  -- Optional: Add index for query optimization
  CREATE INDEX idx_form4_relationships_total_shares
  ON form4_relationships(total_shares_owned);

  -- Comment explaining the field
  COMMENT ON COLUMN form4_relationships.total_shares_owned
  IS 'Calculated total shares owned based on all related transactions';