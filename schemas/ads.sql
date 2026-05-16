CREATE TABLE IF NOT EXISTS ads_postloan_dashboard_di (
    stat_date DATE,
    due_account_count INTEGER,
    due_loan_count INTEGER,
    due_total_amount DOUBLE,
    collection_entry_rate DOUBLE,
    recovery_rate_d7 DOUBLE,
    recovery_rate_d15 DOUBLE,
    recovery_rate_d30 DOUBLE,
    m1_recovery_rate DOUBLE,
    call_coverage_rate DOUBLE,
    valid_coverage_rate DOUBLE,
    connect_rate DOUBLE,
    valid_contact_rate DOUBLE,
    first_contact_hours DOUBLE,
    ptp_rate DOUBLE,
    ptp_keep_rate DOUBLE,
    avg_call_duration_per_call DOUBLE,
    avg_call_duration_per_collector DOUBLE,
    collector_productivity DOUBLE,
    complaint_rate DOUBLE,
    complaint_per_10k_cases DOUBLE,
    risk_phrase_hit_rate DOUBLE,
    qa_fail_rate DOUBLE,
    over_frequency_contact_rate DOUBLE,
    reduction_usage_rate DOUBLE,
    reduction_recovery_rate DOUBLE,
    reduction_roi DOUBLE,
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
    call_coverage_rate DOUBLE,
    connect_rate DOUBLE,
    ptp_rate DOUBLE,
    ptp_keep_rate DOUBLE,
    complaint_rate DOUBLE,
    PRIMARY KEY (stat_date, vendor_id)
);

CREATE TABLE IF NOT EXISTS ads_collector_performance_di (
    stat_date DATE,
    collector_id VARCHAR,
    vendor_id VARCHAR,
    action_count INTEGER,
    connect_rate DOUBLE,
    ptp_keep_rate DOUBLE,
    first_contact_hours DOUBLE,
    avg_call_duration_per_call DOUBLE,
    avg_call_duration_per_collector DOUBLE,
    collector_productivity DOUBLE,
    complaint_count INTEGER,
    PRIMARY KEY (stat_date, collector_id)
);

CREATE TABLE IF NOT EXISTS ads_reduction_roi_di (
    stat_date DATE,
    reduction_case_count INTEGER,
    approved_reduction_amount DOUBLE,
    reduction_usage_rate DOUBLE,
    reduction_recovery_rate DOUBLE,
    reduction_roi DOUBLE,
    PRIMARY KEY (stat_date)
);

CREATE TABLE IF NOT EXISTS ads_compliance_qc_di (
    stat_date DATE,
    template_id VARCHAR,
    active_case_count INTEGER,
    complaint_count INTEGER,
    complaint_rate DOUBLE,
    complaint_per_10k_cases DOUBLE,
    risk_phrase_hit_rate DOUBLE,
    qa_fail_rate DOUBLE,
    over_frequency_contact_rate DOUBLE,
    PRIMARY KEY (stat_date, template_id)
);
