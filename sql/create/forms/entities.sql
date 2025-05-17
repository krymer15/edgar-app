CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cik TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,  -- 'company', 'person', 'trust', 'group'
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT entity_type_check CHECK (entity_type IN ('company', 'person', 'trust', 'group'))
);

-- Index on CIK (unique but also explicitly queried)
CREATE INDEX idx_entities_cik ON entities(cik);