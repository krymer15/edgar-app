-- Derivative securities table for derivative-specific details  
CREATE TABLE public.derivative_securities (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    security_id uuid NOT NULL,
    underlying_security_id uuid NULL,
    underlying_security_title text NOT NULL,
    conversion_price numeric NULL,
    exercise_date date NULL,
    expiration_date date NULL,
    created_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    updated_at timestamptz DEFAULT CURRENT_TIMESTAMP NULL,
    CONSTRAINT derivative_securities_pkey PRIMARY KEY (id),
    CONSTRAINT derivative_securities_security_fkey FOREIGN KEY (security_id) 
        REFERENCES public.securities(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT derivative_securities_underlying_fkey FOREIGN KEY (underlying_security_id) 
        REFERENCES public.securities(id) ON DELETE SET NULL ON UPDATE CASCADE
);
CREATE INDEX idx_derivative_underlying ON public.derivative_securities USING btree (underlying_security_id);
CREATE INDEX idx_derivative_security_id ON public.derivative_securities USING btree (security_id);

COMMENT ON TABLE public.derivative_securities IS 'Additional details for derivative securities such as options and convertibles';
COMMENT ON COLUMN public.derivative_securities.underlying_security_id IS 'ID of the underlying equity security when it can be determined';
COMMENT ON COLUMN public.derivative_securities.conversion_price IS 'Price at which derivative can be converted to underlying security';
