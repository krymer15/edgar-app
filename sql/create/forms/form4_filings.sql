-- public.form4_filings definition

-- Drop table

-- DROP TABLE public.form4_filings;

CREATE TABLE public.form4_filings (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	accession_number text NOT NULL,
	period_of_report date NULL,
	has_multiple_owners bool DEFAULT false NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT form4_filings_pkey PRIMARY KEY (id),
	CONSTRAINT unique_form4_accession UNIQUE (accession_number)
);
CREATE INDEX idx_form4_filings_accession ON public.form4_filings USING btree (accession_number);


-- public.form4_filings foreign keys

ALTER TABLE public.form4_filings ADD CONSTRAINT form4_filings_accession_number_fkey FOREIGN KEY (accession_number) REFERENCES public.filing_metadata(accession_number) ON DELETE CASCADE ON UPDATE CASCADE;