CREATE TABLE IF NOT EXISTS mca_audit_log (
    id UUID PRIMARY KEY,
    occurred_at TIMESTAMPTZ NOT NULL,
    tenant_id VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    resource_type VARCHAR(128) NOT NULL,
    resource_id VARCHAR(128) NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    payload JSONB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_tenant_type ON mca_audit_log (tenant_id, resource_type, occurred_at DESC);
REVOKE UPDATE, DELETE ON mca_audit_log FROM PUBLIC;
