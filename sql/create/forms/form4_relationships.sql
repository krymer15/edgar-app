-- public.form4_relationships definition

-- Drop table

-- DROP TABLE public.form4_relationships;

CREATE TABLE public.form4_relationships (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	form4_filing_id uuid NOT NULL,
	issuer_entity_id uuid NOT NULL,
	owner_entity_id uuid NOT NULL,
	relationship_type text NOT NULL,
	is_director bool DEFAULT false NULL,
	is_officer bool DEFAULT false NULL,
	is_ten_percent_owner bool DEFAULT false NULL,
	is_other bool DEFAULT false NULL,
	officer_title text NULL,
	other_text text NULL,
	relationship_details jsonb NULL,
	is_group_filing bool DEFAULT false NULL,
	filing_date date NOT NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT form4_relationships_pkey PRIMARY KEY (id),
	CONSTRAINT relationship_type_check CHECK ((relationship_type = ANY (ARRAY['director'::text, 'officer'::text, '10_percent_owner'::text, 'other'::text])))
);
CREATE INDEX idx_form4_relationships_filing_id ON public.form4_relationships USING btree (form4_filing_id);
CREATE INDEX idx_form4_relationships_issuer ON public.form4_relationships USING btree (issuer_entity_id);
CREATE INDEX idx_form4_relationships_owner ON public.form4_relationships USING btree (owner_entity_id);


-- public.form4_relationships foreign keys

ALTER TABLE public.form4_relationships ADD CONSTRAINT form4_relationships_form4_filing_id_fkey FOREIGN KEY (form4_filing_id) REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE public.form4_relationships ADD CONSTRAINT form4_relationships_issuer_entity_id_fkey FOREIGN KEY (issuer_entity_id) REFERENCES public.entities(id) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE public.form4_relationships ADD CONSTRAINT form4_relationships_owner_entity_id_fkey FOREIGN KEY (owner_entity_id) REFERENCES public.entities(id) ON DELETE CASCADE ON UPDATE CASCADE;