-- Securities table for normalized security information
CREATE TABLE public.securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    issuer_entity_id uuid NOT NULL,
    security_type text NOT NULL, -- 'equity', 'option', 'convertible', 'other_derivative'
    standard_cusip text NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT securities_pkey PRIMARY KEY (id),
    CONSTRAINT securities_issuer_entity_fkey FOREIGN KEY (issuer_entity_id) 
        REFERENCES public.entities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT security_type_check CHECK (security_type IN 
        ('equity', 'option', 'convertible', 'other_derivative'))
);
CREATE INDEX idx_securities_issuer ON public.securities USING btree (issuer_entity_id);
CREATE INDEX idx_securities_title ON public.securities USING btree (title);
CREATE INDEX idx_securities_title_issuer ON public.securities USING btree (title, issuer_entity_id);

-- Add comments for documentation
COMMENT ON TABLE public.securities IS 'Normalized security information related to Form 4 transactions';
COMMENT ON COLUMN public.securities.security_type IS 'Type of security: equity, option, convertible, or other_derivative';
COMMENT ON COLUMN public.securities.standard_cusip IS 'Standard CUSIP identifier when available';