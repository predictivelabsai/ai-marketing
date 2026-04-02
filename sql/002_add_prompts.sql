-- POLLY Prompt Management — stores editable system prompts per user per agent
-- Run: psql $DB_URL -f sql/002_add_prompts.sql

CREATE TABLE IF NOT EXISTS polly.prompts (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER REFERENCES polly.users(id) ON DELETE CASCADE,  -- NULL = global default
    agent_name  VARCHAR(50) NOT NULL,  -- 'content','strategy',...,'_global' for global instructions
    prompt_text TEXT NOT NULL,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

COMMENT ON TABLE polly.prompts IS 'Editable system prompts per user per agent. NULL user_id = global default.';

-- Global prompts: one per agent_name where user_id IS NULL
CREATE UNIQUE INDEX IF NOT EXISTS idx_prompts_global_agent
    ON polly.prompts(agent_name) WHERE user_id IS NULL;

-- User prompts: one per user per agent_name
CREATE UNIQUE INDEX IF NOT EXISTS idx_prompts_user_agent
    ON polly.prompts(user_id, agent_name) WHERE user_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_prompts_user_id ON polly.prompts(user_id);
CREATE INDEX IF NOT EXISTS idx_prompts_agent_name ON polly.prompts(agent_name);

CREATE TRIGGER trg_prompts_updated_at
    BEFORE UPDATE ON polly.prompts
    FOR EACH ROW
    EXECUTE FUNCTION polly.update_updated_at_column();
