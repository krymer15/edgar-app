CREATE TABLE filing_documents (
  id UUID PRIMARY KEY,
  cik TEXT NOT NULL,
  accession_number TEXT NOT NULL,
  form_type TEXT NOT NULL,
  filing_date DATE,
  document_type TEXT,             -- e.g., 'EX-99.1'
  filename TEXT,
  description TEXT,
  source_url TEXT,
  is_primary BOOLEAN DEFAULT FALSE,
  is_exhibit BOOLEAN DEFAULT FALSE,
  is_data_support BOOLEAN DEFAULT FALSE,
  source_type TEXT,                -- 'sgml', 'index_html', 'inferred'
  created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);