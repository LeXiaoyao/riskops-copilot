CREATE TABLE IF NOT EXISTS dws_loan_status_snapshot_di (
    stat_date DATE,
    loan_id VARCHAR,
    customer_id VARCHAR,
    product_code VARCHAR,
    dpd_bucket VARCHAR,
    due_amount DOUBLE,
    repaid_amount_d7 DOUBLE,
    recovery_rate_d7 DOUBLE,
    PRIMARY KEY (stat_date, loan_id)
);

CREATE TABLE IF NOT EXISTS dws_case_status_snapshot_di (
    stat_date DATE,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    collector_id VARCHAR,
    dpd_bucket VARCHAR,
    outstanding_amount DOUBLE,
    action_count INTEGER,
    connected_count INTEGER,
    ptp_count INTEGER,
    repaid_amount DOUBLE,
    PRIMARY KEY (stat_date, case_id)
);

CREATE TABLE IF NOT EXISTS dws_customer_status_snapshot_di (
    stat_date DATE,
    customer_id VARCHAR,
    active_loan_count INTEGER,
    active_case_count INTEGER,
    total_outstanding_amount DOUBLE,
    max_dpd INTEGER,
    risk_level VARCHAR,
    PRIMARY KEY (stat_date, customer_id)
);

CREATE TABLE IF NOT EXISTS dws_collection_process_wide_di (
    stat_date DATE,
    case_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    collector_id VARCHAR,
    action_count INTEGER,
    ai_action_count INTEGER,
    connected_count INTEGER,
    ptp_count INTEGER,
    ptp_fulfilled_count INTEGER,
    complaint_count INTEGER,
    connect_rate DOUBLE,
    ptp_fulfillment_rate DOUBLE,
    ai_coverage_rate DOUBLE,
    PRIMARY KEY (stat_date, case_id)
);

CREATE TABLE IF NOT EXISTS dws_vendor_line_capacity_di (
    stat_date DATE,
    vendor_id VARCHAR,
    line_id VARCHAR,
    region VARCHAR,
    active_case_count INTEGER,
    active_collector_count INTEGER,
    case_per_collector DOUBLE,
    PRIMARY KEY (stat_date, vendor_id, line_id)
);

CREATE TABLE IF NOT EXISTS dws_customer_profile_di (
    stat_date DATE,
    customer_id VARCHAR,
    customer_id_hash VARCHAR,
    mobile_masked VARCHAR,
    province VARCHAR,
    customer_segment VARCHAR,
    risk_level_current VARCHAR,
    total_outstanding_amount DOUBLE,
    PRIMARY KEY (stat_date, customer_id)
);

CREATE TABLE IF NOT EXISTS dws_collector_profile_di (
    stat_date DATE,
    collector_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    skill_level VARCHAR,
    action_count INTEGER,
    connect_rate DOUBLE,
    complaint_count INTEGER,
    PRIMARY KEY (stat_date, collector_id)
);

CREATE TABLE IF NOT EXISTS dws_customer_postloan_tag_di (
    stat_date DATE,
    customer_id VARCHAR,
    dpd_tag VARCHAR,
    balance_tag VARCHAR,
    behavior_tag VARCHAR,
    touch_tag VARCHAR,
    compliance_tag VARCHAR,
    strategy_tag VARCHAR,
    PRIMARY KEY (stat_date, customer_id)
);
