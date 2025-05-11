CREATE TABLE form4_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filing_id UUID REFERENCES form4_filings(id) ON DELETE CASCADE,
    transaction_type TEXT,  -- 'non-derivative' or 'derivative'
    transaction_date DATE,
    transaction_code TEXT,
    security_title TEXT,
    shares NUMERIC,
    price_per_share NUMERIC,
    ownership TEXT,
    raw JSONB  -- full source row as fallback
);
