
-- 1. Create securities table to normalize security information
CREATE TABLE public.securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title text NOT NULL,
    issuer_entity_id uuid NOT NULL,
    security_type text NOT NULL, -- 'equity', 'option', 'convertible', etc.
    standard_cusip text NULL,    -- Optional CUSIP identifier if available
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT securities_pkey PRIMARY KEY (id),
    CONSTRAINT securities_issuer_entity_fkey FOREIGN KEY (issuer_entity_id) REFERENCES public.entities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT security_type_check CHECK (security_type IN ('equity', 'option', 'convertible', 'other_derivative'))
);
CREATE INDEX idx_securities_issuer ON public.securities USING btree (issuer_entity_id);
CREATE INDEX idx_securities_title ON public.securities USING btree (title);

-- 2. Create derivative securities table for additional derivative-specific information
CREATE TABLE public.derivative_securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    underlying_security_id uuid NULL, -- Can be null if underlying security not in system
    underlying_security_title text NOT NULL,
    conversion_price numeric NULL,
    exercise_date date NULL,
    expiration_date date NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_securities_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_securities_security_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_securities_underlying_fkey FOREIGN KEY (underlying_security_id) REFERENCES public.securities(id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE INDEX idx_derivative_underlying ON public.derivative_securities USING btree (underlying_security_id);

-- 3. Create relationship positions table to track positions at point in time
CREATE TABLE public.relationship_positions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    position_date date NOT NULL,
    shares_amount numeric NOT NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    filing_id uuid NOT NULL, -- Which filing established this position
    transaction_id uuid NULL, -- Can be null for initial positions
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT relationship_positions_pkey PRIMARY KEY (id),
    CONSTRAINT relationship_positions_relationship_fkey FOREIGN KEY (relationship_id) REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_security_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT relationship_positions_filing_fkey FOREIGN KEY (filing_id) REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE INDEX idx_relationship_positions_relationship ON public.relationship_positions USING btree (relationship_id);
CREATE INDEX idx_relationship_positions_security ON public.relationship_positions USING btree (security_id);
CREATE INDEX idx_relationship_positions_date ON public.relationship_positions USING btree (position_date);

-- 4. Create non-derivative transactions table
CREATE TABLE public.non_derivative_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    form4_filing_id uuid NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    transaction_code text NOT NULL,
    transaction_date date NOT NULL,
    transaction_form_type text NULL,
    shares_amount numeric NOT NULL,
    price_per_share numeric NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    transaction_timeliness text NULL, -- 'P' for on time, 'L' for late
    footnote_ids text[] NULL,
    acquisition_disposition_flag text NOT NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT non_derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT non_derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE
CASCADE,
    CONSTRAINT non_derivative_transactions_security_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT non_derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);
CREATE INDEX idx_non_derivative_transactions_filing ON public.non_derivative_transactions USING btree (form4_filing_id);
CREATE INDEX idx_non_derivative_transactions_relationship ON public.non_derivative_transactions USING btree (relationship_id);
CREATE INDEX idx_non_derivative_transactions_security ON public.non_derivative_transactions USING btree (security_id);
CREATE INDEX idx_non_derivative_transactions_date ON public.non_derivative_transactions USING btree (transaction_date);

-- 5. Create derivative transactions table
CREATE TABLE public.derivative_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    form4_filing_id uuid NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL, -- References securities.id
    derivative_security_id uuid NOT NULL, -- References derivative_securities.id
    transaction_code text NOT NULL,
    transaction_date date NOT NULL,
    transaction_form_type text NULL,
    derivative_shares_amount numeric NOT NULL, -- Amount of derivative securities
    price_per_derivative numeric NULL,
    underlying_shares_amount numeric NULL,  -- Equivalent number of underlying shares
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    transaction_timeliness text NULL,
    footnote_ids text[] NULL,
    acquisition_disposition_flag text NOT NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_security_fkey FOREIGN KEY (security_id) REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_derivative_fkey FOREIGN KEY (derivative_security_id) REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE
CASCADE,
    CONSTRAINT derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);
CREATE INDEX idx_derivative_transactions_filing ON public.derivative_transactions USING btree (form4_filing_id);
CREATE INDEX idx_derivative_transactions_relationship ON public.derivative_transactions USING btree (relationship_id);
CREATE INDEX idx_derivative_transactions_security ON public.derivative_transactions USING btree (security_id);
CREATE INDEX idx_derivative_transactions_derivative ON public.derivative_transactions USING btree (derivative_security_id);
CREATE INDEX idx_derivative_transactions_date ON public.derivative_transactions USING btree (transaction_date);