-- public.filing_documents definition

-- Drop table

-- DROP TABLE public.filing_documents;

CREATE TABLE public.filing_documents (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	accession_number text NOT NULL,
	cik text NOT NULL,
	document_type text NULL,
	filename text NULL,
	description text NULL,
	source_url text NULL,
	source_type text NULL,
	is_primary bool DEFAULT false NULL,
	is_exhibit bool DEFAULT false NULL,
	is_data_support bool DEFAULT false NULL,
	accessible bool DEFAULT true NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	issuer_cik text NULL,
	CONSTRAINT filing_documents_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_filing_documents_issuer_cik ON public.filing_documents USING btree (issuer_cik);


-- public.filing_documents foreign keys

ALTER TABLE public.filing_documents ADD CONSTRAINT filing_documents_accession_number_fkey FOREIGN KEY (accession_number) REFERENCES public.filing_metadata(accession_number);