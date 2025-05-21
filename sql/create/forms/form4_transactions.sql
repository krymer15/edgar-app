-- public.form4_transactions definition

-- Drop table

-- DROP TABLE public.form4_transactions;

CREATE TABLE public.form4_transactions (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	form4_filing_id uuid NOT NULL,
	relationship_id uuid NOT NULL,
	transaction_code text NOT NULL,
	transaction_date date NULL,
	security_title text NOT NULL,
	transaction_form_type text NULL,
	shares_amount numeric NULL,
	price_per_share numeric NULL,
	ownership_nature text NULL,
	is_derivative bool DEFAULT false NOT NULL,
	equity_swap_involved bool DEFAULT false NULL,
	transaction_timeliness text NULL,
	footnote_ids _text NULL,
	indirect_ownership_explanation text NULL,
	conversion_price numeric NULL,
	exercise_date date NULL,
	expiration_date date NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	acquisition_disposition_flag text NULL,
	is_position_only bool DEFAULT false NULL,
	underlying_security_shares numeric NULL,
	CONSTRAINT acquisition_disposition_flag_check CHECK (((acquisition_disposition_flag = ANY (ARRAY['A'::text, 'D'::text])) OR (acquisition_disposition_flag IS NULL))),
	CONSTRAINT form4_transactions_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_form4_transactions_filing_id ON public.form4_transactions USING btree (form4_filing_id);
CREATE INDEX idx_form4_transactions_relationship_id ON public.form4_transactions USING btree (relationship_id);


-- public.form4_transactions foreign keys

ALTER TABLE public.form4_transactions ADD CONSTRAINT form4_transactions_form4_filing_id_fkey FOREIGN KEY (form4_filing_id) REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE public.form4_transactions ADD CONSTRAINT form4_transactions_relationship_id_fkey FOREIGN KEY (relationship_id) REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE;