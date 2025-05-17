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

-- Indexes for joins and filtering by filing and entity
CREATE INDEX idx_form4_relationships_filing_id ON form4_relationships(form4_filing_id);
CREATE INDEX idx_form4_relationships_issuer ON form4_relationships(issuer_entity_id);
CREATE INDEX idx_form4_relationships_owner ON form4_relationships(owner_entity_id);