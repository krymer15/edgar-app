CREATE TABLE filing_metadata (
  accession_number TEXT PRIMARY KEY,
  cik TEXT NOT NULL,
  form_type TEXT NOT NULL,
  filing_date DATE,
  filing_url TEXT, 

  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);