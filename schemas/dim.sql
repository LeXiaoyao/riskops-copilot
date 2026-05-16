CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id VARCHAR,
    customer_id_hash VARCHAR,
    mobile_masked VARCHAR,
    gender VARCHAR,
    age_group VARCHAR,
    province VARCHAR,
    city VARCHAR,
    occupation_type VARCHAR,
    customer_segment VARCHAR,
    risk_level_current VARCHAR,
    sensitive_flag BOOLEAN,
    blacklist_flag BOOLEAN,
    PRIMARY KEY (customer_id)
);

CREATE TABLE IF NOT EXISTS dim_loan (
    loan_id VARCHAR,
    customer_id VARCHAR,
    product_code VARCHAR,
    channel_code VARCHAR,
    loan_amount DOUBLE,
    loan_term INTEGER,
    interest_rate DOUBLE,
    loan_status VARCHAR,
    disburse_time TIMESTAMP,
    first_due_date DATE,
    mob INTEGER,
    vintage_month VARCHAR,
    PRIMARY KEY (loan_id)
);

CREATE TABLE IF NOT EXISTS dim_case (
    case_id VARCHAR,
    customer_id VARCHAR,
    case_create_time TIMESTAMP,
    case_type VARCHAR,
    initial_dpd_bucket VARCHAR,
    initial_outstanding_amount DOUBLE,
    balance_segment VARCHAR,
    current_vendor_id VARCHAR,
    current_line_id VARCHAR,
    protect_flag BOOLEAN,
    sensitive_flag BOOLEAN,
    complaint_flag BOOLEAN,
    PRIMARY KEY (case_id)
);

CREATE TABLE IF NOT EXISTS dim_case_loan_mapping (
    mapping_id VARCHAR,
    case_id VARCHAR,
    loan_id VARCHAR,
    customer_id VARCHAR,
    mapping_start_date DATE,
    mapping_end_date DATE,
    main_loan_flag BOOLEAN,
    PRIMARY KEY (mapping_id)
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_code VARCHAR,
    product_name VARCHAR,
    product_type VARCHAR,
    funder_type VARCHAR,
    interest_rate_min DOUBLE,
    interest_rate_max DOUBLE,
    term_min INTEGER,
    term_max INTEGER,
    online_flag BOOLEAN,
    PRIMARY KEY (product_code)
);

CREATE TABLE IF NOT EXISTS dim_channel (
    channel_code VARCHAR,
    channel_name VARCHAR,
    channel_type VARCHAR,
    partner_name VARCHAR,
    online_flag BOOLEAN,
    PRIMARY KEY (channel_code)
);

CREATE TABLE IF NOT EXISTS dim_vendor (
    vendor_id VARCHAR,
    vendor_name VARCHAR,
    vendor_type VARCHAR,
    region VARCHAR,
    max_capacity INTEGER,
    settlement_method VARCHAR,
    compliance_level VARCHAR,
    PRIMARY KEY (vendor_id)
);

CREATE TABLE IF NOT EXISTS dim_collection_line (
    line_id VARCHAR,
    vendor_id VARCHAR,
    line_name VARCHAR,
    region VARCHAR,
    line_type VARCHAR,
    dpd_bucket_scope VARCHAR,
    capacity_limit INTEGER,
    PRIMARY KEY (line_id)
);

CREATE TABLE IF NOT EXISTS dim_collector (
    collector_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    role_type VARCHAR,
    entry_date DATE,
    skill_level VARCHAR,
    max_daily_case_capacity INTEGER,
    compliance_level VARCHAR,
    PRIMARY KEY (collector_id)
);

CREATE TABLE IF NOT EXISTS dim_strategy (
    strategy_id VARCHAR,
    strategy_type VARCHAR,
    strategy_version VARCHAR,
    effective_start_date DATE,
    effective_end_date DATE,
    owner_team VARCHAR,
    PRIMARY KEY (strategy_id)
);
