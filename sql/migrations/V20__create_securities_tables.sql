-- V20__create_securities_tables.sql
-- Phase 1 of Form 4 schema redesign: Security Normalization
-- Creates the securities and derivative_securities tables and populates them from existing data

-- Securities table for normalized security information
CREATE TABLE IF NOT EXISTS public.securities (
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

-- Create indexes for efficient querying
CREATE INDEX idx_securities_issuer ON public.securities USING btree (issuer_entity_id);
CREATE INDEX idx_securities_title ON public.securities USING btree (title);
CREATE INDEX idx_securities_title_issuer ON public.securities USING btree (title, issuer_entity_id);

-- Add comments for documentation
COMMENT ON TABLE public.securities IS 'Normalized security information related to Form 4 transactions';
COMMENT ON COLUMN public.securities.security_type IS 'Type of security: equity, option, convertible, or other_derivative';
COMMENT ON COLUMN public.securities.standard_cusip IS 'Standard CUSIP identifier when available';

-- Derivative securities table for derivative-specific details
CREATE TABLE IF NOT EXISTS public.derivative_securities (
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

-- Create indexes for derivative securities
CREATE INDEX idx_derivative_underlying ON public.derivative_securities USING btree (underlying_security_id);
CREATE INDEX idx_derivative_security_id ON public.derivative_securities USING btree (security_id);

-- Add comments for documentation
COMMENT ON TABLE public.derivative_securities IS 'Additional details for derivative securities such as options and convertibles';
COMMENT ON COLUMN public.derivative_securities.underlying_security_id IS 'ID of the underlying equity security when it can be determined';
COMMENT ON COLUMN public.derivative_securities.conversion_price IS 'Price at which derivative can be converted to underlying security';

-- Migration logic: First create a function to handle the data migration safely
DO $$
DECLARE
    migration_success BOOLEAN := TRUE;
    error_message TEXT;
    equity_count INTEGER := 0;
    derivative_count INTEGER := 0;
BEGIN
    -- Use a transaction to ensure atomicity of the migration
    BEGIN
        -- Step 1: Migrate non-derivative securities (equity)
        INSERT INTO securities (title, issuer_entity_id, security_type, created_at, updated_at)
        SELECT DISTINCT 
            t.security_title as title,
            r.issuer_entity_id,
            'equity' as security_type,
            t.created_at,
            t.updated_at
        FROM form4_transactions t
        JOIN form4_relationships r ON t.relationship_id = r.id
        WHERE t.is_derivative = false
        AND r.issuer_entity_id IS NOT NULL
        ON CONFLICT DO NOTHING;
        
        GET DIAGNOSTICS equity_count = ROW_COUNT;
        
        -- Step 2: Migrate derivative securities
        INSERT INTO securities (title, issuer_entity_id, security_type, created_at, updated_at)
        SELECT DISTINCT 
            t.security_title as title,
            r.issuer_entity_id,
            CASE 
                WHEN t.security_title ILIKE '%option%' THEN 'option'
                WHEN t.security_title ILIKE '%convert%' THEN 'convertible'
                ELSE 'other_derivative'
            END as security_type,
            t.created_at,
            t.updated_at
        FROM form4_transactions t
        JOIN form4_relationships r ON t.relationship_id = r.id
        WHERE t.is_derivative = true
        AND r.issuer_entity_id IS NOT NULL
        ON CONFLICT DO NOTHING;
        
        GET DIAGNOSTICS derivative_count = ROW_COUNT;
        
        -- Step 3: Create a temporary mapping table for derivative security details
        CREATE TEMPORARY TABLE temp_derivative_mapping AS
        SELECT DISTINCT
            s.id as security_id,
            t.underlying_security_title,
            t.conversion_price,
            t.exercise_date,
            t.expiration_date
        FROM form4_transactions t
        JOIN form4_relationships r ON t.relationship_id = r.id
        JOIN securities s ON s.title = t.security_title AND s.issuer_entity_id = r.issuer_entity_id
        WHERE t.is_derivative = true;
        
        -- Step 4: Identify underlying securities when possible and create mapping
        WITH underlying_security_map AS (
            SELECT 
                dm.security_id,
                s.id as underlying_id
            FROM temp_derivative_mapping dm
            JOIN securities s ON s.title = dm.underlying_security_title
            JOIN securities ds ON ds.id = dm.security_id
            WHERE s.issuer_entity_id = ds.issuer_entity_id  -- Same issuer
        )
        UPDATE temp_derivative_mapping dm
        SET underlying_security_id = usm.underlying_id
        FROM underlying_security_map usm
        WHERE dm.security_id = usm.security_id;
        
        -- Step 5: Populate derivative_securities table
        INSERT INTO derivative_securities 
            (security_id, underlying_security_id, underlying_security_title, 
             conversion_price, exercise_date, expiration_date)
        SELECT 
            security_id,
            underlying_security_id,
            underlying_security_title,
            conversion_price,
            exercise_date,
            expiration_date
        FROM temp_derivative_mapping
        ON CONFLICT DO NOTHING;
        
        -- Clean up temporary table
        DROP TABLE temp_derivative_mapping;
        
        -- Log migration summary
        RAISE NOTICE 'Securities migration completed: % equity securities and % derivative securities created', 
                     equity_count, derivative_count;
        
    EXCEPTION WHEN OTHERS THEN
        -- Log error and set flag
        GET STACKED DIAGNOSTICS error_message = MESSAGE_TEXT;
        RAISE WARNING 'Error during securities migration: %', error_message;
        migration_success := FALSE;
        RAISE EXCEPTION '%', error_message;  -- Re-throw to rollback transaction
    END;
    
    -- Final verification step - make sure all form4_transactions have corresponding securities
    IF migration_success THEN
        -- If any transaction has no security record, raise a warning
        PERFORM t.id, t.security_title, r.issuer_entity_id
        FROM form4_transactions t
        JOIN form4_relationships r ON t.relationship_id = r.id
        LEFT JOIN securities s ON s.title = t.security_title AND s.issuer_entity_id = r.issuer_entity_id
        WHERE s.id IS NULL AND r.issuer_entity_id IS NOT NULL
        LIMIT 5;
        
        IF FOUND THEN
            RAISE WARNING 'Warning: Some transactions could not be linked to securities. This may require investigation.';
        END IF;
    END IF;
END $$;