CREATE TABLE IF NOT EXISTS dwd_due_plan_detail_di (
    stat_date DATE,
    plan_id VARCHAR,
    loan_id VARCHAR,
    customer_id VARCHAR,
    product_code VARCHAR,
    channel_code VARCHAR,
    due_date DATE,
    due_amount DOUBLE,
    outstanding_amount DOUBLE,
    dpd_bucket VARCHAR,
    PRIMARY KEY (stat_date, plan_id)
);

CREATE TABLE IF NOT EXISTS dwd_repayment_detail_di (
    repay_id VARCHAR,
    plan_id VARCHAR,
    loan_id VARCHAR,
    customer_id VARCHAR,
    repay_time TIMESTAMP,
    repay_date DATE,
    repay_amount DOUBLE,
    repay_status VARCHAR,
    PRIMARY KEY (repay_id)
);

CREATE TABLE IF NOT EXISTS dwd_collection_action_detail_di (
    action_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    line_id VARCHAR,
    collector_id VARCHAR,
    action_time TIMESTAMP,
    action_date DATE,
    action_type VARCHAR,
    template_id VARCHAR,
    connected_flag BOOLEAN,
    ptp_flag BOOLEAN,
    ptp_fulfilled_flag BOOLEAN,
    ai_outbound_flag BOOLEAN,
    PRIMARY KEY (action_id)
);

CREATE TABLE IF NOT EXISTS dwd_case_flow_detail_di (
    flow_id VARCHAR,
    case_id VARCHAR,
    from_status VARCHAR,
    to_status VARCHAR,
    flow_time TIMESTAMP,
    flow_date DATE,
    strategy_id VARCHAR,
    PRIMARY KEY (flow_id)
);

CREATE TABLE IF NOT EXISTS dwd_complaint_detail_di (
    complaint_id VARCHAR,
    case_id VARCHAR,
    customer_id VARCHAR,
    vendor_id VARCHAR,
    collector_id VARCHAR,
    template_id VARCHAR,
    complaint_time TIMESTAMP,
    complaint_date DATE,
    complaint_type VARCHAR,
    complaint_level VARCHAR,
    PRIMARY KEY (complaint_id)
);
