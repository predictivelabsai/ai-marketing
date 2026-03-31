-- POLLY Schema — Financial Product Marketing Database
-- Database: finespresso_db
-- Schema: polly
-- Usage: psql -h 72.62.114.124 -U finespresso -d finespresso_db -f sql/create_schema.sql

-- =============================================================================
-- Schema creation
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS polly;

-- =============================================================================
-- Trigger function: auto-update updated_at columns
-- =============================================================================

CREATE OR REPLACE FUNCTION polly.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- 1. polly.users — The users of the system
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.users (
    id              SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    persona         VARCHAR(50) NOT NULL DEFAULT 'campaign',  -- 'management', 'sales', 'campaign'
    company         VARCHAR(255),
    phone           VARCHAR(50),
    whatsapp_authorized  BOOLEAN DEFAULT FALSE,
    telegram_authorized  BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.users IS 'System users — financial advisors and marketing staff who create campaigns and manage products.';

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON polly.users
    FOR EACH ROW
    EXECUTE FUNCTION polly.update_updated_at_column();

-- =============================================================================
-- 2. polly.products — Financial products being marketed
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.products (
    id                    SERIAL PRIMARY KEY,
    name                  VARCHAR(255) NOT NULL,
    product_type          VARCHAR(100) NOT NULL,       -- 'structured-product', 'fund', 'bond', 'etf', 'derivative'
    description           TEXT,
    issuer                VARCHAR(255),
    underlying            VARCHAR(255),                -- underlying asset/index
    currency              VARCHAR(10) DEFAULT 'USD',
    maturity_date         DATE,
    launch_date           DATE,
    jurisdiction          VARCHAR(50) DEFAULT 'UK',
    risk_level            VARCHAR(50),
    target_market         TEXT,                         -- MiFID target market description
    negative_target       TEXT,                         -- negative target market
    distribution_strategy TEXT,
    status                VARCHAR(50) DEFAULT 'draft',  -- 'draft', 'active', 'closed', 'matured'
    created_by            INTEGER REFERENCES polly.users(id),
    created_at            TIMESTAMPTZ DEFAULT NOW(),
    updated_at            TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.products IS 'Financial products being marketed — structured products, funds, bonds, ETFs, and derivatives.';

CREATE INDEX idx_products_product_type ON polly.products(product_type);
CREATE INDEX idx_products_status ON polly.products(status);
CREATE INDEX idx_products_created_by ON polly.products(created_by);

CREATE TRIGGER trg_products_updated_at
    BEFORE UPDATE ON polly.products
    FOR EACH ROW
    EXECUTE FUNCTION polly.update_updated_at_column();

-- =============================================================================
-- 3. polly.user_products — Maps users to products they manage/sell
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.user_products (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES polly.users(id) ON DELETE CASCADE,
    product_id  INTEGER NOT NULL REFERENCES polly.products(id) ON DELETE CASCADE,
    role        VARCHAR(50) NOT NULL DEFAULT 'sales',  -- 'owner', 'sales', 'compliance', 'marketing'
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, product_id)
);

COMMENT ON TABLE polly.user_products IS 'Junction table mapping users to the products they manage, sell, or oversee compliance for.';

CREATE INDEX idx_user_products_user_id ON polly.user_products(user_id);
CREATE INDEX idx_user_products_product_id ON polly.user_products(product_id);

-- =============================================================================
-- 4. polly.compliance_documents — Compliance-approved documents
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.compliance_documents (
    id            SERIAL PRIMARY KEY,
    product_id    INTEGER NOT NULL REFERENCES polly.products(id) ON DELETE CASCADE,
    doc_type      VARCHAR(50) NOT NULL,          -- 'product_description', 'prospectus', 'term_sheet', 'terms_conditions', 'priips', 'mifid_disclosures', 'faq', 'teaser', 'pitch_deck', 'market_research'
    title         VARCHAR(255) NOT NULL,
    content       TEXT NOT NULL,
    version       INTEGER DEFAULT 1,
    status        VARCHAR(50) DEFAULT 'pending', -- 'pending', 'in_review', 'approved', 'rejected'
    submitted_by  INTEGER REFERENCES polly.users(id),
    reviewed_by   INTEGER REFERENCES polly.users(id),
    approved_by   INTEGER REFERENCES polly.users(id),
    review_notes  TEXT,
    submitted_at  TIMESTAMPTZ DEFAULT NOW(),
    reviewed_at   TIMESTAMPTZ,
    approved_at   TIMESTAMPTZ,
    UNIQUE(product_id, doc_type, version)
);

COMMENT ON TABLE polly.compliance_documents IS 'Compliance-approved documents attached to products — prospectuses, term sheets, PRIIPs KIDs, and marketing materials requiring approval.';

CREATE INDEX idx_compliance_documents_product_id ON polly.compliance_documents(product_id);
CREATE INDEX idx_compliance_documents_status ON polly.compliance_documents(status);
CREATE INDEX idx_compliance_documents_submitted_by ON polly.compliance_documents(submitted_by);
CREATE INDEX idx_compliance_documents_reviewed_by ON polly.compliance_documents(reviewed_by);
CREATE INDEX idx_compliance_documents_approved_by ON polly.compliance_documents(approved_by);

-- =============================================================================
-- 5. polly.campaigns — Marketing campaigns
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.campaigns (
    id               SERIAL PRIMARY KEY,
    product_id       INTEGER REFERENCES polly.products(id),
    name             VARCHAR(255) NOT NULL,
    campaign_type    VARCHAR(50) DEFAULT 'product',  -- 'product', 'warmup', 'poll', 'follow-up', 'reactivation'
    channels         TEXT[],                          -- '{email,whatsapp,telegram,linkedin}'
    target_audience  TEXT,
    status           VARCHAR(50) DEFAULT 'draft',    -- 'draft', 'active', 'paused', 'completed', 'archived'
    follow_up_days   INTEGER DEFAULT 3,
    auto_respond     BOOLEAN DEFAULT TRUE,
    calendly_link    VARCHAR(500),
    max_touches      INTEGER DEFAULT 3,
    started_at       TIMESTAMPTZ,
    completed_at     TIMESTAMPTZ,
    created_by       INTEGER REFERENCES polly.users(id),
    created_at       TIMESTAMPTZ DEFAULT NOW(),
    updated_at       TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.campaigns IS 'Marketing campaigns — product launches, warmup sequences, polls, follow-ups, and reactivation outreach.';

CREATE INDEX idx_campaigns_product_id ON polly.campaigns(product_id);
CREATE INDEX idx_campaigns_status ON polly.campaigns(status);
CREATE INDEX idx_campaigns_campaign_type ON polly.campaigns(campaign_type);
CREATE INDEX idx_campaigns_created_by ON polly.campaigns(created_by);

CREATE TRIGGER trg_campaigns_updated_at
    BEFORE UPDATE ON polly.campaigns
    FOR EACH ROW
    EXECUTE FUNCTION polly.update_updated_at_column();

-- =============================================================================
-- 6. polly.campaign_content — Content variants for A/B testing
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.campaign_content (
    id                  SERIAL PRIMARY KEY,
    campaign_id         INTEGER NOT NULL REFERENCES polly.campaigns(id) ON DELETE CASCADE,
    variant_label       VARCHAR(50) NOT NULL DEFAULT 'A',  -- 'A', 'B', 'C'
    channel             VARCHAR(50) NOT NULL,               -- 'email', 'whatsapp', 'telegram', etc.
    subject_line        VARCHAR(500),
    body_text           TEXT NOT NULL,
    cta_text            VARCHAR(255),
    cta_url             VARCHAR(500),
    compliance_approved BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.campaign_content IS 'Content variants per campaign for A/B testing across channels — each variant has its own subject, body, and CTA.';

CREATE INDEX idx_campaign_content_campaign_id ON polly.campaign_content(campaign_id);

-- =============================================================================
-- 7. polly.contacts — Campaign contacts/leads
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.contacts (
    id                SERIAL PRIMARY KEY,
    email             VARCHAR(255),
    full_name         VARCHAR(255),
    phone             VARCHAR(50),
    company           VARCHAR(255),
    investor_type     VARCHAR(50),           -- 'retail', 'professional', 'eligible_counterparty'
    source            VARCHAR(100),          -- where this contact came from
    gdpr_consent      BOOLEAN DEFAULT FALSE,
    gdpr_consent_date TIMESTAMPTZ,
    opted_out         BOOLEAN DEFAULT FALSE,
    opted_out_date    TIMESTAMPTZ,
    created_at        TIMESTAMPTZ DEFAULT NOW(),
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.contacts IS 'Campaign contacts and leads — investors, advisors, and prospects with GDPR consent tracking.';

CREATE INDEX idx_contacts_email ON polly.contacts(email);
CREATE INDEX idx_contacts_investor_type ON polly.contacts(investor_type);
CREATE INDEX idx_contacts_opted_out ON polly.contacts(opted_out);

CREATE TRIGGER trg_contacts_updated_at
    BEFORE UPDATE ON polly.contacts
    FOR EACH ROW
    EXECUTE FUNCTION polly.update_updated_at_column();

-- =============================================================================
-- 8. polly.campaign_responses — Track responses per contact per campaign
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.campaign_responses (
    id            SERIAL PRIMARY KEY,
    campaign_id   INTEGER NOT NULL REFERENCES polly.campaigns(id) ON DELETE CASCADE,
    contact_id    INTEGER NOT NULL REFERENCES polly.contacts(id) ON DELETE CASCADE,
    variant_id    INTEGER REFERENCES polly.campaign_content(id),
    channel       VARCHAR(50) NOT NULL,
    status        VARCHAR(50) NOT NULL DEFAULT 'sent',  -- 'sent', 'delivered', 'opened', 'clicked', 'replied', 'interested', 'not_interested', 'removal_requested'
    response_text TEXT,
    sentiment     VARCHAR(50),              -- 'positive', 'neutral', 'negative', 'question'
    lead_score    INTEGER DEFAULT 0,        -- 0-100
    assigned_to   INTEGER REFERENCES polly.users(id),  -- sales person assigned
    touch_number  INTEGER DEFAULT 1,
    sent_at       TIMESTAMPTZ DEFAULT NOW(),
    delivered_at  TIMESTAMPTZ,
    opened_at     TIMESTAMPTZ,
    responded_at  TIMESTAMPTZ
);

COMMENT ON TABLE polly.campaign_responses IS 'Per-contact response tracking for each campaign — delivery status, engagement, sentiment analysis, and lead scoring.';

CREATE INDEX idx_campaign_responses_campaign_id ON polly.campaign_responses(campaign_id);
CREATE INDEX idx_campaign_responses_contact_id ON polly.campaign_responses(contact_id);
CREATE INDEX idx_campaign_responses_variant_id ON polly.campaign_responses(variant_id);
CREATE INDEX idx_campaign_responses_status ON polly.campaign_responses(status);
CREATE INDEX idx_campaign_responses_assigned_to ON polly.campaign_responses(assigned_to);
CREATE INDEX idx_campaign_responses_sentiment ON polly.campaign_responses(sentiment);

-- =============================================================================
-- 9. polly.channel_analytics — Aggregated channel metrics per campaign
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.channel_analytics (
    id            SERIAL PRIMARY KEY,
    campaign_id   INTEGER NOT NULL REFERENCES polly.campaigns(id) ON DELETE CASCADE,
    channel       VARCHAR(50) NOT NULL,
    period_start  DATE NOT NULL,
    period_end    DATE NOT NULL,
    sent          INTEGER DEFAULT 0,
    delivered     INTEGER DEFAULT 0,
    opened        INTEGER DEFAULT 0,
    clicked       INTEGER DEFAULT 0,
    replied       INTEGER DEFAULT 0,
    unsubscribed  INTEGER DEFAULT 0,
    bounce_rate   DECIMAL(5,2) DEFAULT 0,
    open_rate     DECIMAL(5,2) DEFAULT 0,
    click_rate    DECIMAL(5,2) DEFAULT 0,
    reply_rate    DECIMAL(5,2) DEFAULT 0,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(campaign_id, channel, period_start)
);

COMMENT ON TABLE polly.channel_analytics IS 'Aggregated channel-level metrics per campaign and time period — delivery rates, engagement rates, and unsubscribe tracking.';

CREATE INDEX idx_channel_analytics_campaign_id ON polly.channel_analytics(campaign_id);
CREATE INDEX idx_channel_analytics_channel ON polly.channel_analytics(channel);

-- =============================================================================
-- 10. polly.audit_log — Track all actions for compliance audit trail
-- =============================================================================

CREATE TABLE IF NOT EXISTS polly.audit_log (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES polly.users(id),
    action      VARCHAR(100) NOT NULL,       -- 'document_submitted', 'document_approved', 'campaign_created', 'campaign_sent'
    entity_type VARCHAR(50) NOT NULL,        -- 'product', 'document', 'campaign', 'contact'
    entity_id   INTEGER,
    details     JSONB,
    ip_address  INET,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.audit_log IS 'Immutable compliance audit trail — logs every significant action for regulatory reporting and accountability.';

CREATE INDEX idx_audit_log_user_id ON polly.audit_log(user_id);
CREATE INDEX idx_audit_log_action ON polly.audit_log(action);
CREATE INDEX idx_audit_log_entity_type ON polly.audit_log(entity_type);
CREATE INDEX idx_audit_log_entity_id ON polly.audit_log(entity_id);
CREATE INDEX idx_audit_log_created_at ON polly.audit_log(created_at);
