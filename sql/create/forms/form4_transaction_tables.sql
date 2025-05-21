-- Table: form4_non_derivative_transactions

CREATE TABLE form4_non_derivative_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL,
    reporting_owner_cik TEXT NOT NULL,
    issuer_cik TEXT NOT NULL,
    security_title TEXT NOT NULL,
    transaction_date DATE,
    transaction_code TEXT,
    transaction_acquired_disposed_code TEXT CHECK (transaction_acquired_disposed_code IN ('A', 'D')),
    transaction_shares NUMERIC(20, 4),
    transaction_price_per_share NUMERIC(20, 4),
    shares_owned_following_transaction NUMERIC(20, 4),
    direct_or_indirect_ownership TEXT CHECK (direct_or_indirect_ownership IN ('D', 'I')),
    nature_of_ownership TEXT,
    is_holding BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Table: form4_derivative_transactions

CREATE TABLE form4_derivative_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL,
    reporting_owner_cik TEXT NOT NULL,
    issuer_cik TEXT NOT NULL,
    derivative_security_title TEXT NOT NULL,
    transaction_date DATE,
    transaction_code TEXT,
    transaction_acquired_disposed_code TEXT CHECK (transaction_acquired_disposed_code IN ('A', 'D')),
    derivative_units NUMERIC(20, 4),
    price_per_derivative_unit NUMERIC(20, 4),
    date_exercisable DATE,
    expiration_date DATE,
    underlying_security_title TEXT,
    underlying_shares NUMERIC(20, 4),
    derivative_units_owned_following_transaction NUMERIC(20, 4),
    direct_or_indirect_ownership TEXT CHECK (direct_or_indirect_ownership IN ('D', 'I')),
    nature_of_ownership TEXT,
    is_holding BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now()
);