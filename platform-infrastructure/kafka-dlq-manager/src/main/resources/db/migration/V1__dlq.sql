CREATE TABLE IF NOT EXISTS dead_letter (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    original_topic VARCHAR(255) NOT NULL,
    consumer_group VARCHAR(255) NOT NULL,
    payload TEXT NOT NULL,
    error_message TEXT NOT NULL,
    replay_attempts INT NOT NULL DEFAULT 0,
    status VARCHAR(24) NOT NULL
);
