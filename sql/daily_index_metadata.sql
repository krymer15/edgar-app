CREATE TABLE public.daily_index_metadata (
	accession_number text NOT NULL,
	cik text NOT NULL,
	form_type text NULL,
	filing_date date NULL,
	filing_url text NOT NULL,
	downloaded text DEFAULT 'false'::text NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT daily_index_metadata_pkey PRIMARY KEY (accession_number)
);