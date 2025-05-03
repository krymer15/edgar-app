CREATE TABLE public.parsed_sgml_metadata (
	accession_number text NOT NULL,
	cik text NOT NULL,
	form_type text NULL,
	filing_date date NULL,
	primary_doc_url text NULL,
	exhibits jsonb NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT parsed_sgml_metadata_pkey PRIMARY KEY (accession_number)
);
CREATE INDEX idx_parsed_sgml_cik_date ON public.parsed_sgml_metadata USING btree (cik, filing_date);