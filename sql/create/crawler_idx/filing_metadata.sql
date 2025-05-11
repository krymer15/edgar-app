CREATE TABLE filing_metadata (
	accession_number text NOT NULL,
	cik text NOT NULL,
	form_type text NOT NULL,
	filing_date date NOT NULL,
	filing_url text NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT filing_metadata_pkey PRIMARY KEY (accession_number)
);