CREATE TABLE IF NOT EXISTS ods_repayment_plan (
    plan_id VARCHAR,
    loan_id VARCHAR,
    customer_id VARCHAR,
    period_no INTEGER,
    due_date DATE,
    due_principal DOUBLE,
    due_interest DOUBLE,
    due_fee DOUBLE,
    due_amount DOUBLE,
    plan_status VARCHAR,
    PRIMARY KEY (plan_id)
);

CREATE TABLE IF NOT EXISTS ods_repayment_detail (
    repay_id VARCHAR,
    plan_id VARCHAR,
    loan_id VARCHAR,
    customer_id VARCHAR,
    repay_time TIMESTAMP,
    repay_amount DOUBLE,
    repay_channel VARCHAR,
    repay_status VARCHAR,
    PRIMARY KEY (repay_id)
);

CREATE TABLE IF NOT EXISTS ods_loan_daily_snapshot (
    stat_date DATE,
    loan_id VARCHAR,
    customer_id VARCHAR,
    dpd INTEGER,
    dpd_bucket VARCHAR,
    outstanding_amount DOUBLE,
    loan_status VARCHAR,
    PRIMARY KEY (stat_date, loan_id)
);

CREATE TABLE IF NOT EXISTS ods_case_daily_snapshot (
    stat_date DATE,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    collector_id VARCHAR,
    case_status VARCHAR,
    dpd_bucket VARCHAR,
    outstanding_amount DOUBLE,
    PRIMARY KEY (stat_date, case_id)
);

CREATE TABLE IF NOT EXISTS ods_customer_daily_snapshot (
    stat_date DATE,
    customer_id VARCHAR,
    active_loan_count INTEGER,
    active_case_count INTEGER,
    total_outstanding_amount DOUBLE,
    max_dpd INTEGER,
    risk_level VARCHAR,
    PRIMARY KEY (stat_date, customer_id)
);

CREATE TABLE IF NOT EXISTS ods_case_flow (
    flow_id VARCHAR,
    case_id VARCHAR,
    from_status VARCHAR,
    to_status VARCHAR,
    flow_time TIMESTAMP,
    strategy_id VARCHAR,
    PRIMARY KEY (flow_id)
);

CREATE TABLE IF NOT EXISTS ods_assignment_decision_log (
    decision_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    collector_id VARCHAR,
    strategy_id VARCHAR,
    decision_time TIMESTAMP,
    decision_reason VARCHAR,
    PRIMARY KEY (decision_id)
);

CREATE TABLE IF NOT EXISTS ods_postloan_c_score (
    score_id VARCHAR,
    customer_id VARCHAR,
    score_date DATE,
    postloan_c_score DOUBLE,
    score_level VARCHAR,
    PRIMARY KEY (score_id)
);

CREATE TABLE IF NOT EXISTS ods_collection_note (
    note_id VARCHAR,
    case_id VARCHAR,
    collector_id VARCHAR,
    note_time TIMESTAMP,
    note_type VARCHAR,
    note_text_masked VARCHAR,
    PRIMARY KEY (note_id)
);

CREATE TABLE IF NOT EXISTS ods_collection_action (
    action_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    collector_id VARCHAR,
    action_time TIMESTAMP,
    action_type VARCHAR,
    template_id VARCHAR,
    connected_flag BOOLEAN,
    ptp_flag BOOLEAN,
    ptp_fulfilled_flag BOOLEAN,
    ai_outbound_flag BOOLEAN,
    PRIMARY KEY (action_id)
);

CREATE TABLE IF NOT EXISTS ods_call_record (
    call_id VARCHAR,
    action_id VARCHAR,
    case_id VARCHAR,
    call_start_time TIMESTAMP,
    duration_seconds INTEGER,
    recording_uri VARCHAR,
    transcript_masked VARCHAR,
    PRIMARY KEY (call_id)
);

CREATE TABLE IF NOT EXISTS ods_sms_send_log (
    message_id VARCHAR,
    action_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    template_id VARCHAR,
    send_time TIMESTAMP,
    send_status VARCHAR,
    PRIMARY KEY (message_id)
);

CREATE TABLE IF NOT EXISTS ods_reduction_application (
    reduction_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    apply_time TIMESTAMP,
    apply_amount DOUBLE,
    approved_amount DOUBLE,
    approval_status VARCHAR,
    PRIMARY KEY (reduction_id)
);

CREATE TABLE IF NOT EXISTS ods_complaint (
    complaint_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    collector_id VARCHAR,
    template_id VARCHAR,
    complaint_time TIMESTAMP,
    complaint_type VARCHAR,
    complaint_level VARCHAR,
    PRIMARY KEY (complaint_id)
);
