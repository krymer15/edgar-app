-- public.filing_metadata definition

-- Drop table

-- DROP TABLE public.filing_metadata;

CREATE TABLE public.filing_metadata (
	accession_number text NOT NULL,
	cik text NOT NULL,
	form_type text NOT NULL,
	filing_date date NOT NULL,
	filing_url text NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	processing_status public."processing_status_enum" NULL,
	processing_started_at timestamptz NULL,
	processing_completed_at timestamptz NULL,
	processing_error text NULL,
	job_id varchar(36) NULL,
	last_updated_by varchar(100) NULL,
	CONSTRAINT check_processing_timestamps CHECK (((processing_completed_at IS NULL) OR (processing_started_at IS NULL) OR (processing_completed_at >= processing_started_at))),
	CONSTRAINT filing_metadata_pkey PRIMARY KEY (accession_number)
);
CREATE INDEX idx_filing_metadata_job_id ON public.filing_metadata USING btree (job_id);