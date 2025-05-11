CREATE TABLE public.xml_metadata (
	id text NOT NULL,
	accession_number text NOT NULL,
	filename text NOT NULL,
	downloaded bool DEFAULT false NULL,
	parsed_successfully bool DEFAULT false NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT uq_accession_filename UNIQUE (accession_number, filename),
	CONSTRAINT xml_metadata_pkey PRIMARY KEY (id)
);