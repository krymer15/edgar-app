-- public.entities definition

-- Drop table

-- DROP TABLE public.entities;

CREATE TABLE public.entities (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	cik text NOT NULL,
	"name" text NOT NULL,
	entity_type text NOT NULL,
	created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
	CONSTRAINT entities_cik_key UNIQUE (cik),
	CONSTRAINT entities_pkey PRIMARY KEY (id),
	CONSTRAINT entity_type_check CHECK ((entity_type = ANY (ARRAY['company'::text, 'person'::text, 'trust'::text, 'group'::text])))
);
CREATE INDEX idx_entities_cik ON public.entities USING btree (cik);