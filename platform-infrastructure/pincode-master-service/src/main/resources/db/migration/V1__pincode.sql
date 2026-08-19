CREATE TABLE IF NOT EXISTS pincode_master (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    created_by VARCHAR(128),
    updated_by VARCHAR(128),
    tenant_id VARCHAR(64) NOT NULL DEFAULT 'default',
    version BIGINT NOT NULL DEFAULT 0,
    pincode VARCHAR(6) NOT NULL UNIQUE,
    city VARCHAR(80) NOT NULL,
    district VARCHAR(80) NOT NULL,
    state_name VARCHAR(80) NOT NULL,
    state_code VARCHAR(2) NOT NULL,
    oda BOOLEAN NOT NULL DEFAULT FALSE,
    serviceable BOOLEAN NOT NULL DEFAULT TRUE,
    standard_transit_days INT NOT NULL DEFAULT 4
);

INSERT INTO pincode_master (id, created_at, updated_at, tenant_id, version, pincode, city, district, state_name, state_code, oda, serviceable, standard_transit_days)
VALUES
(gen_random_uuid(), now(), now(), 'default', 0, '110001', 'New Delhi', 'New Delhi', 'Delhi', 'DL', false, true, 2),
(gen_random_uuid(), now(), now(), 'default', 0, '400001', 'Mumbai', 'Mumbai', 'Maharashtra', 'MH', false, true, 3),
(gen_random_uuid(), now(), now(), 'default', 0, '560001', 'Bengaluru', 'Bengaluru', 'Karnataka', 'KA', false, true, 3),
(gen_random_uuid(), now(), now(), 'default', 0, '600001', 'Chennai', 'Chennai', 'Tamil Nadu', 'TN', false, true, 4),
(gen_random_uuid(), now(), now(), 'default', 0, '700001', 'Kolkata', 'Kolkata', 'West Bengal', 'WB', false, true, 4),
(gen_random_uuid(), now(), now(), 'default', 0, '500001', 'Hyderabad', 'Hyderabad', 'Telangana', 'TS', false, true, 3),
(gen_random_uuid(), now(), now(), 'default', 0, '380001', 'Ahmedabad', 'Ahmedabad', 'Gujarat', 'GJ', false, true, 4),
(gen_random_uuid(), now(), now(), 'default', 0, '302001', 'Jaipur', 'Jaipur', 'Rajasthan', 'RJ', false, true, 5),
(gen_random_uuid(), now(), now(), 'default', 0, '226001', 'Lucknow', 'Lucknow', 'Uttar Pradesh', 'UP', false, true, 5),
(gen_random_uuid(), now(), now(), 'default', 0, '141001', 'Ludhiana', 'Ludhiana', 'Punjab', 'PB', true, true, 6)
ON CONFLICT DO NOTHING;
