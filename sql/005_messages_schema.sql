-- POLLY Messages -- stores all inbound/outbound messages across channels
-- Run: psql $DB_URL -f sql/005_messages_schema.sql

CREATE TABLE IF NOT EXISTS polly.messages (
    id          SERIAL PRIMARY KEY,
    source      VARCHAR(20) NOT NULL,       -- 'web', 'whatsapp', 'telegram'
    sender_id   VARCHAR(100) NOT NULL,      -- user_id, phone, telegram chat_id
    direction   VARCHAR(10) NOT NULL,       -- 'inbound', 'outbound'
    content     TEXT NOT NULL,
    product_id  INTEGER REFERENCES polly.products(id) ON DELETE SET NULL,
    session_id  VARCHAR(100),               -- conversation tracking
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_source     ON polly.messages(source);
CREATE INDEX IF NOT EXISTS idx_messages_sender     ON polly.messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_messages_session    ON polly.messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON polly.messages(created_at);
