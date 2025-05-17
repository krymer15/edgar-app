-- sql/migrations/create_entities_table.sql

-- Table: entities
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cik TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- 'company', 'person', 'trust', 'group'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT entity_type_check CHECK (entity_type IN ('company', 'person', 'trust', 'group'))
);

-- Table: form4_filings
CREATE TABLE form4_filings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    accession_number TEXT NOT NULL,
    period_of_report DATE,
    has_multiple_owners BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_form4_accession UNIQUE(accession_number),
    CONSTRAINT form4_filings_accession_number_fkey
        FOREIGN KEY (accession_number)
        REFERENCES filing_metadata(accession_number)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: form4_relationships
CREATE TABLE form4_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form4_filing_id UUID NOT NULL,
    issuer_entity_id UUID NOT NULL,
    owner_entity_id UUID NOT NULL,
    relationship_type TEXT NOT NULL,
    is_director BOOLEAN DEFAULT FALSE,
    is_officer BOOLEAN DEFAULT FALSE, 
    is_ten_percent_owner BOOLEAN DEFAULT FALSE,
    is_other BOOLEAN DEFAULT FALSE,
    officer_title TEXT,
    other_text TEXT,
    relationship_details JSONB,
    is_group_filing BOOLEAN DEFAULT FALSE,
    filing_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT relationship_type_check CHECK (relationship_type IN ('director', 'officer', '10_percent_owner', 'other')),
    CONSTRAINT form4_relationships_form4_filing_id_fkey
        FOREIGN KEY (form4_filing_id)
        REFERENCES form4_filings(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT form4_relationships_issuer_entity_id_fkey
        FOREIGN KEY (issuer_entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT form4_relationships_owner_entity_id_fkey
        FOREIGN KEY (owner_entity_id)
        REFERENCES entities(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Table: form4_transactions
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

-- Indexes
CREATE INDEX idx_form4_relationships_filing_id ON form4_relationships(form4_filing_id);
CREATE INDEX idx_form4_relationships_issuer ON form4_relationships(issuer_entity_id);
CREATE INDEX idx_form4_relationships_owner ON form4_relationships(owner_entity_id);
CREATE INDEX idx_form4_transactions_filing_id ON form4_transactions(form4_filing_id);
CREATE INDEX idx_form4_transactions_relationship_id ON form4_transactions(relationship_id);
CREATE INDEX idx_entities_cik ON entities(cik);
CREATE INDEX idx_form4_filings_accession ON form4_filings(accession_number);
