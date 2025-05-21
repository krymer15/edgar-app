-- Add acquisition_disposition_flag column to form4_transactions table
-- This column stores the (A) or (D) value from the transactionAcquiredDisposedCode element in Form 4 XML
-- A = Acquisition, D = Disposition

-- First check if the column already exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.columns 
        WHERE table_name = 'form4_transactions' 
        AND column_name = 'acquisition_disposition_flag'
    ) THEN
        -- Add the column if it doesn't exist
        ALTER TABLE public.form4_transactions 
        ADD COLUMN acquisition_disposition_flag text;
        
        -- Add a constraint to ensure only valid values are accepted
        ALTER TABLE public.form4_transactions 
        ADD CONSTRAINT acquisition_disposition_flag_check 
        CHECK (acquisition_disposition_flag IN ('A', 'D') OR acquisition_disposition_flag IS NULL);
    END IF;
END $$;

COMMENT ON COLUMN public.form4_transactions.acquisition_disposition_flag IS 'Indicates whether the transaction was an acquisition (A) or disposition (D) of securities';