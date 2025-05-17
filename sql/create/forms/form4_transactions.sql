CREATE TABLE form4_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form4_filing_id UUID NOT NULL,
    relationship_id UUID NOT NULL,
    transaction_code TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    security_title TEXT NOT NULL,
    transaction_form_type TEXT,
    shares_amount NUMERIC,
    price_per_share NUMERIC,
    ownership_nature TEXT, -- 'D' for Direct or 'I' for Indirect
    is_derivative BOOLEAN NOT NULL DEFAULT FALSE,
    equity_swap_involved BOOLEAN DEFAULT FALSE,
    transaction_timeliness TEXT, -- 'P' for on time, 'L' for late
    footnote_ids TEXT[],
    indirect_ownership_explanation TEXT,
    conversion_price NUMERIC,
    exercise_date DATE,
    expiration_date DATE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT form4_transactions_form4_filing_id_fkey
        FOREIGN KEY (form4_filing_id)
        REFERENCES form4_filings(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT form4_transactions_relationship_id_fkey
        FOREIGN KEY (relationship_id)
        REFERENCES form4_relationships(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Indexes to support joins by filing and relationship
CREATE INDEX idx_form4_transactions_filing_id ON form4_transactions(form4_filing_id);
CREATE INDEX idx_form4_transactions_relationship_id ON form4_transactions(relationship_id);
