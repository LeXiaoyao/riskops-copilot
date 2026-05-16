CREATE TABLE IF NOT EXISTS ads_postloan_dashboard_di (
    stat_date DATE,
    m1_due_amount DOUBLE,
    m1_repaid_amount_d7 DOUBLE,
    m1_recovery_rate_d7 DOUBLE,
    connect_rate DOUBLE,
    ai_coverage_rate DOUBLE,
    ptp_fulfillment_rate DOUBLE,
    high_balance_case_share DOUBLE,
    PRIMARY KEY (stat_date)
);

CREATE TABLE IF NOT EXISTS ads_recovery_attribution_di (
    stat_date DATE,
    factor_code VARCHAR,
    factor_name VARCHAR,
    factor_value DOUBLE,
    contribution_pct DOUBLE,
    PRIMARY KEY (stat_date, factor_code)
);

CREATE TABLE IF NOT EXISTS ads_vendor_performance_di (
    stat_date DATE,
    vendor_id VARCHAR,
    action_count INTEGER,
    connect_rate DOUBLE,
    ptp_rate DOUBLE,
    complaint_rate DOUBLE,
    PRIMARY KEY (stat_date, vendor_id)
);

CREATE TABLE IF NOT EXISTS ads_collector_performance_di (
    stat_date DATE,
    collector_id VARCHAR,
    vendor_id VARCHAR,
    action_count INTEGER,
    connect_rate DOUBLE,
    ptp_fulfillment_rate DOUBLE,
    complaint_count INTEGER,
    PRIMARY KEY (stat_date, collector_id)
);

CREATE TABLE IF NOT EXISTS ads_reduction_roi_di (
    stat_date DATE,
    reduction_case_count INTEGER,
    approved_reduction_amount DOUBLE,
    repaid_amount DOUBLE,
    reduction_usage_rate DOUBLE,
    reduction_roi DOUBLE,
    PRIMARY KEY (stat_date)
);

CREATE TABLE IF NOT EXISTS ads_compliance_qc_di (
    stat_date DATE,
    template_id VARCHAR,
    send_count INTEGER,
    complaint_count INTEGER,
    complaint_rate DOUBLE,
    PRIMARY KEY (stat_date, template_id)
);
