CREATE TABLE IF NOT EXISTS commerce_order (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    order_number VARCHAR(32) NOT NULL UNIQUE,
    cart_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64),
    pincode VARCHAR(6) NOT NULL,
    payment_mode VARCHAR(16) NOT NULL,
    status VARCHAR(32) NOT NULL,
    grand_total_inr NUMERIC(12,2) NOT NULL,
    origin_state VARCHAR(2) NOT NULL DEFAULT 'HR',
    dest_state VARCHAR(2) NOT NULL DEFAULT 'DL',
    payment_id UUID,
    invoice_id UUID,
    wave_id VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS order_line (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    order_id UUID NOT NULL REFERENCES commerce_order(id),
    sku VARCHAR(64) NOT NULL,
    qty INT NOT NULL,
    unit_price_inr NUMERIC(12,2) NOT NULL,
    hsn_code VARCHAR(8)
);

CREATE INDEX IF NOT EXISTS idx_order_line_order ON order_line(order_id);

CREATE TABLE IF NOT EXISTS checkout_saga (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    order_id UUID NOT NULL REFERENCES commerce_order(id),
    state VARCHAR(32) NOT NULL,
    last_step VARCHAR(64),
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS affinity_rule (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    anchor_sku VARCHAR(64) NOT NULL,
    suggested_sku VARCHAR(64) NOT NULL,
    suggestion_type VARCHAR(16) NOT NULL,
    score NUMERIC(8,4) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    UNIQUE (anchor_sku, suggested_sku, suggestion_type)
);

INSERT INTO affinity_rule (id, created_at, updated_at, tenant_id, version, anchor_sku, suggested_sku, suggestion_type, score, reason)
VALUES
(gen_random_uuid(), now(), now(), 'default', 0, 'SKU-PHONE-8-128-BLACK', 'SKU-BUDS-PRO', 'CROSS_SELL', 0.82, 'Frequently bought together: TWS buds with smartphone'),
(gen_random_uuid(), now(), now(), 'default', 0, 'SKU-PHONE-8-128-BLACK', 'SKU-CHARGER-65W', 'CROSS_SELL', 0.74, 'Complementary 65W GaN charger'),
(gen_random_uuid(), now(), now(), 'default', 0, 'SKU-PHONE-8-128-BLACK', 'SKU-PHONE-12-256-GOLD', 'UP_SELL', 0.91, 'Higher RAM/storage in the same Nova X family'),
(gen_random_uuid(), now(), now(), 'default', 0, 'SKU-PHONE-12-256-GOLD', 'SKU-BUDS-PRO', 'CROSS_SELL', 0.79, 'Premium audio attach for flagship phone'),
(gen_random_uuid(), now(), now(), 'default', 0, 'SKU-BUDS-PRO', 'SKU-BUDS-CASE', 'CROSS_SELL', 0.61, 'Protective case attach')
ON CONFLICT DO NOTHING;
