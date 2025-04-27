CREATE TABLE companies_metadata (
    cik TEXT PRIMARY KEY,
    entity_type TEXT,
    sic TEXT,
    sic_description TEXT,
    name TEXT NOT NULL,
    tickers TEXT[], -- array
    exchanges TEXT[], -- array
    ein TEXT,
    description TEXT,
    website TEXT,
    investor_website TEXT,
    category TEXT,
    fiscal_year_end TEXT,
    state_of_incorporation TEXT,
    state_of_incorporation_description TEXT,
    mailing_address JSONB,
    business_address JSONB,
    phone TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
