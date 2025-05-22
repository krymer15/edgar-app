-- Derivative transactions table
CREATE TABLE IF NOT EXISTS public.derivative_transactions (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    form4_filing_id uuid NOT NULL,
    relationship_id uuid NOT NULL,
    security_id uuid NOT NULL,
    derivative_security_id uuid NOT NULL,
    transaction_code text NOT NULL,
    transaction_date date NOT NULL,
    transaction_form_type text NULL,
    derivative_shares_amount numeric NOT NULL,
    price_per_derivative numeric NULL,
    underlying_shares_amount numeric NULL,
    direct_ownership boolean NOT NULL DEFAULT true,
    ownership_nature_explanation text NULL,
    transaction_timeliness text NULL,
    footnote_ids text[] NULL,
    acquisition_disposition_flag text NOT NULL,
    is_part_of_group_filing boolean DEFAULT false NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_transactions_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_transactions_filing_fkey FOREIGN KEY (form4_filing_id) 
        REFERENCES public.form4_filings(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_relationship_fkey FOREIGN KEY (relationship_id) 
        REFERENCES public.form4_relationships(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_transactions_derivative_fkey FOREIGN KEY (derivative_security_id) 
        REFERENCES public.derivative_securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_ad_flag_check CHECK (acquisition_disposition_flag IN ('A', 'D'))
);

-- Create indexes for derivative transactions
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_filing ON public.derivative_transactions USING btree (form4_filing_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_relationship ON public.derivative_transactions USING btree (relationship_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_security ON public.derivative_transactions USING btree (security_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_derivative ON public.derivative_transactions USING btree (derivative_security_id);
CREATE INDEX IF NOT EXISTS idx_derivative_transactions_date ON public.derivative_transactions USING btree (transaction_date);