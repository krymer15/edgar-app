-- Relationship positions table for tracking current positions
CREATE TABLE public.relationship_positions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    position_date date NOT NULL,
    shares_amount numeric NOT NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    filing_id uuid NOT NULL,
    transaction_id uuid NULL,
    is_position_only boolean DEFAULT false NOT NULL,
    position_type text NOT NULL, -- 'equity' or 'derivative'
    derivative_security_id uuid NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT relationship_positions_pkey PRIMARY KEY (id),
    CONSTRAINT relationship_positions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_filing_fkey FOREIGN KEY (filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_derivative_fkey FOREIGN KEY (derivative_security_id) 
        REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT position_type_check CHECK (position_type IN ('equity', 'derivative'))
);

CREATE INDEX idx_relationship_positions_relationship ON public.relationship_positions USING btree (relationship_id);
CREATE INDEX idx_relationship_positions_security ON public.relationship_positions USING btree (security_id);
CREATE INDEX idx_relationship_positions_date ON public.relationship_positions USING btree (position_date);
CREATE INDEX idx_relationship_positions_derivative ON public.relationship_positions USING btree (derivative_security_id);
CREATE INDEX idx_relationship_positions_filing ON public.relationship_positions USING btree (filing_id);
CREATE UNIQUE INDEX idx_relationship_position_unique ON public.relationship_positions USING btree (relationship_id, security_id, position_date, derivative_security_id, direct_ownership) WHERE (is_position_only = true);