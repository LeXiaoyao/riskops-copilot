# 数据字典

> 由 `metadata/tables.yaml` 和 `metadata/columns.yaml` 自动渲染。

## DIM 层

### dim_customer
- 中文名：客户维表
- 主题域：master_data
- 粒度：customer_id
- 主键：customer_id
- 说明：客户基础信息
- 字段：
  - `customer_id`：客户号，VARCHAR，非空，主键，隐私 P1
  - `customer_id_hash`：客户号哈希，VARCHAR，非空，隐私 P3
  - `mobile_masked`：脱敏手机号，VARCHAR，非空，隐私 P2
  - `gender`：性别，VARCHAR，非空，隐私 P0
  - `age_group`：年龄段，VARCHAR，非空，隐私 P0
  - `province`：省份，VARCHAR，非空，隐私 P0
  - `city`：城市，VARCHAR，非空，隐私 P0
  - `occupation_type`：职业类型，VARCHAR，非空，隐私 P0
  - `customer_segment`：客户分层，VARCHAR，非空，隐私 P0
  - `risk_level_current`：当前风险等级，VARCHAR，非空，隐私 P0
  - `sensitive_flag`：敏感客群标识，BOOLEAN，非空，隐私 P0
  - `blacklist_flag`：黑名单标识，BOOLEAN，非空，隐私 P0

### dim_loan
- 中文名：借据维表
- 主题域：master_data
- 粒度：loan_id
- 主键：loan_id
- 说明：借据基础属性
- 字段：
  - `loan_id`：借据号，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `product_code`：产品编码，VARCHAR，非空，隐私 P0
  - `channel_code`：渠道编码，VARCHAR，非空，隐私 P0
  - `loan_amount`：放款金额，DOUBLE，非空，隐私 P0
  - `loan_term`：借款期数，INTEGER，非空，隐私 P0
  - `interest_rate`：年化利率，DOUBLE，非空，隐私 P0
  - `loan_status`：借据状态，VARCHAR，非空，隐私 P0
  - `disburse_time`：放款时间，TIMESTAMP，非空，隐私 P0
  - `first_due_date`：首期应还日，DATE，非空，隐私 P0
  - `mob`：账龄月，INTEGER，非空，隐私 P0
  - `vintage_month`：Vintage 月，VARCHAR，非空，隐私 P0

### dim_case
- 中文名：案件维表
- 主题域：master_data
- 粒度：case_id
- 主键：case_id
- 说明：催收案件主数据
- 字段：
  - `case_id`：案件编号，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `case_create_time`：案件创建时间，TIMESTAMP，非空，隐私 P0
  - `case_type`：案件类型，VARCHAR，非空，隐私 P0
  - `initial_dpd_bucket`：入案账龄桶，VARCHAR，非空，隐私 P0
  - `initial_outstanding_amount`：入案待还金额，DOUBLE，非空，隐私 P0
  - `balance_segment`：余额分层，VARCHAR，非空，隐私 P0
  - `current_vendor_id`：当前供应商，VARCHAR，非空，隐私 P1
  - `current_line_id`：当前线路，VARCHAR，非空，隐私 P1
  - `protect_flag`：保护标识，BOOLEAN，非空，隐私 P0
  - `sensitive_flag`：敏感客群标识，BOOLEAN，非空，隐私 P0
  - `complaint_flag`：投诉标识，BOOLEAN，非空，隐私 P0

### dim_case_loan_mapping
- 中文名：案件借据映射维表
- 主题域：master_data
- 粒度：mapping_id
- 主键：mapping_id
- 说明：案件与借据多对多映射
- 字段：
  - `mapping_id`：映射编号，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `loan_id`：借据号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `mapping_start_date`：映射开始日，DATE，非空，隐私 P0
  - `mapping_end_date`：映射结束日，DATE，可空，隐私 P0
  - `main_loan_flag`：主借据标识，BOOLEAN，非空，隐私 P0

### dim_product
- 中文名：产品维表
- 主题域：master_data
- 粒度：product_code
- 主键：product_code
- 说明：产品主数据
- 字段：
  - `product_code`：产品编码，VARCHAR，非空，主键，隐私 P0
  - `product_name`：产品名称，VARCHAR，非空，隐私 P0
  - `product_type`：产品类型，VARCHAR，非空，隐私 P0
  - `funder_type`：资金方类型，VARCHAR，非空，隐私 P0
  - `interest_rate_min`：最低年化利率，DOUBLE，非空，隐私 P0
  - `interest_rate_max`：最高年化利率，DOUBLE，非空，隐私 P0
  - `term_min`：最短期数，INTEGER，非空，隐私 P0
  - `term_max`：最长期数，INTEGER，非空，隐私 P0
  - `online_flag`：线上标识，BOOLEAN，非空，隐私 P0

### dim_channel
- 中文名：渠道维表
- 主题域：master_data
- 粒度：channel_code
- 主键：channel_code
- 说明：渠道主数据
- 字段：
  - `channel_code`：渠道编码，VARCHAR，非空，主键，隐私 P0
  - `channel_name`：渠道名称，VARCHAR，非空，隐私 P0
  - `channel_type`：渠道类型，VARCHAR，非空，隐私 P0
  - `partner_name`：合作方名称，VARCHAR，非空，隐私 P0
  - `online_flag`：线上标识，BOOLEAN，非空，隐私 P0

### dim_vendor
- 中文名：供应商维表
- 主题域：master_data
- 粒度：vendor_id
- 主键：vendor_id
- 说明：供应商主数据
- 字段：
  - `vendor_id`：供应商编号，VARCHAR，非空，主键，隐私 P1
  - `vendor_name`：供应商名称，VARCHAR，非空，隐私 P0
  - `vendor_type`：供应商类型，VARCHAR，非空，隐私 P0
  - `region`：区域，VARCHAR，非空，隐私 P0
  - `max_capacity`：最大产能，INTEGER，非空，隐私 P0
  - `settlement_method`：结算方式，VARCHAR，非空，隐私 P0
  - `compliance_level`：合规等级，VARCHAR，非空，隐私 P0

### dim_collection_line
- 中文名：催收线路维表
- 主题域：master_data
- 粒度：line_id
- 主键：line_id
- 说明：催收线路主数据
- 字段：
  - `line_id`：线路编号，VARCHAR，非空，主键，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_name`：线路名称，VARCHAR，非空，隐私 P0
  - `region`：区域，VARCHAR，非空，隐私 P0
  - `line_type`：线路类型，VARCHAR，非空，隐私 P0
  - `dpd_bucket_scope`：账龄覆盖，VARCHAR，非空，隐私 P0
  - `capacity_limit`：产能上限，INTEGER，非空，隐私 P0

### dim_collector
- 中文名：催员维表
- 主题域：master_data
- 粒度：collector_id
- 主键：collector_id
- 说明：催员主数据
- 字段：
  - `collector_id`：催员编号，VARCHAR，非空，主键，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `role_type`：角色类型，VARCHAR，非空，隐私 P0
  - `entry_date`：入职日期，DATE，非空，隐私 P0
  - `skill_level`：技能等级，VARCHAR，非空，隐私 P0
  - `max_daily_case_capacity`：日最大案量，INTEGER，非空，隐私 P0
  - `compliance_level`：合规等级，VARCHAR，非空，隐私 P0

### dim_strategy
- 中文名：策略维表
- 主题域：master_data
- 粒度：strategy_id
- 主键：strategy_id
- 说明：策略主数据
- 字段：
  - `strategy_id`：策略编号，VARCHAR，非空，主键，隐私 P1
  - `strategy_type`：策略类型，VARCHAR，非空，隐私 P0
  - `strategy_version`：策略版本，VARCHAR，非空，隐私 P0
  - `effective_start_date`：生效开始日，DATE，非空，隐私 P0
  - `effective_end_date`：生效结束日，DATE，可空，隐私 P0
  - `owner_team`：负责团队，VARCHAR，非空，隐私 P0

## ODS 层

### ods_repayment_plan
- 中文名：还款计划
- 主题域：source_events
- 粒度：plan_id
- 主键：plan_id
- 说明：每笔借据每期应还计划
- 字段：
  - `plan_id`：还款计划 ID，VARCHAR，非空，主键，隐私 P1
  - `loan_id`：借据号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `period_no`：期数，INTEGER，非空，隐私 P0
  - `due_date`：应还日，DATE，非空，隐私 P0
  - `due_principal`：应还本金，DOUBLE，非空，隐私 P0
  - `due_interest`：应还利息，DOUBLE，非空，隐私 P0
  - `due_fee`：应还费用，DOUBLE，非空，隐私 P0
  - `due_amount`：应还总额，DOUBLE，非空，隐私 P0
  - `plan_status`：计划状态，VARCHAR，非空，隐私 P0

### ods_repayment_detail
- 中文名：还款流水
- 主题域：source_events
- 粒度：repay_id
- 主键：repay_id
- 说明：真实还款流水
- 字段：
  - `repay_id`：还款流水 ID，VARCHAR，非空，主键，隐私 P1
  - `plan_id`：还款计划 ID，VARCHAR，非空，隐私 P1
  - `loan_id`：借据号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `repay_time`：还款时间，TIMESTAMP，非空，隐私 P0
  - `repay_amount`：还款金额，DOUBLE，非空，隐私 P0
  - `repay_channel`：还款渠道，VARCHAR，非空，隐私 P0
  - `repay_status`：还款状态，VARCHAR，非空，隐私 P0

### ods_loan_daily_snapshot
- 中文名：借据日切
- 主题域：source_events
- 粒度：stat_date+loan_id
- 主键：['stat_date', 'loan_id']
- 说明：借据状态日切片
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `loan_id`：借据号，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `dpd`：逾期天数，INTEGER，非空，隐私 P0
  - `dpd_bucket`：账龄桶，VARCHAR，非空，隐私 P0
  - `outstanding_amount`：待还金额，DOUBLE，非空，隐私 P0
  - `loan_status`：借据状态，VARCHAR，非空，隐私 P0

### ods_case_daily_snapshot
- 中文名：案件日切
- 主题域：source_events
- 粒度：stat_date+case_id
- 主键：['stat_date', 'case_id']
- 说明：案件状态日切片
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `case_id`：案件编号，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `case_status`：案件状态，VARCHAR，非空，隐私 P0
  - `dpd_bucket`：账龄桶，VARCHAR，非空，隐私 P0
  - `outstanding_amount`：待还金额，DOUBLE，非空，隐私 P0

### ods_customer_daily_snapshot
- 中文名：客户日切
- 主题域：source_events
- 粒度：stat_date+customer_id
- 主键：['stat_date', 'customer_id']
- 说明：客户状态日切片
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `customer_id`：客户号，VARCHAR，非空，主键，隐私 P1
  - `active_loan_count`：有效借据数，INTEGER，非空，隐私 P0
  - `active_case_count`：有效案件数，INTEGER，非空，隐私 P0
  - `total_outstanding_amount`：总待还金额，DOUBLE，非空，隐私 P0
  - `max_dpd`：最大逾期天数，INTEGER，非空，隐私 P0
  - `risk_level`：风险等级，VARCHAR，非空，隐私 P0

### ods_case_flow
- 中文名：案件流转
- 主题域：source_events
- 粒度：flow_id
- 主键：flow_id
- 说明：案件状态流转流水
- 字段：
  - `flow_id`：流转 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `from_status`：原状态，VARCHAR，非空，隐私 P0
  - `to_status`：新状态，VARCHAR，非空，隐私 P0
  - `flow_time`：流转时间，TIMESTAMP，非空，隐私 P0
  - `strategy_id`：策略编号，VARCHAR，非空，隐私 P1

### ods_assignment_decision_log
- 中文名：分案决策流水
- 主题域：source_events
- 粒度：decision_id
- 主键：decision_id
- 说明：分案决策日志
- 字段：
  - `decision_id`：决策 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `strategy_id`：策略编号，VARCHAR，非空，隐私 P1
  - `decision_time`：决策时间，TIMESTAMP，非空，隐私 P0
  - `decision_reason`：决策原因，VARCHAR，非空，隐私 P0

### ods_postloan_c_score
- 中文名：贷后 C 卡分
- 主题域：source_events
- 粒度：score_id
- 主键：score_id
- 说明：贷后评分历史快照
- 字段：
  - `score_id`：评分 ID，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `score_date`：评分日期，DATE，非空，隐私 P0
  - `postloan_c_score`：贷后 C 卡分，DOUBLE，非空，隐私 P0
  - `score_level`：评分等级，VARCHAR，非空，隐私 P0

### ods_collection_note
- 中文名：催记
- 主题域：source_events
- 粒度：note_id
- 主键：note_id
- 说明：催员作业文本记录
- 字段：
  - `note_id`：催记 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `note_time`：催记时间，TIMESTAMP，非空，隐私 P0
  - `note_type`：催记类型，VARCHAR，非空，隐私 P0
  - `note_text_masked`：脱敏催记文本，VARCHAR，非空，隐私 P2

### ods_collection_action
- 中文名：催收动作
- 主题域：source_events
- 粒度：action_id
- 主键：action_id
- 说明：拨打、短信、AI 外呼等触达动作
- 字段：
  - `action_id`：动作 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `action_time`：动作时间，TIMESTAMP，非空，隐私 P0
  - `action_type`：动作类型，VARCHAR，非空，隐私 P0
  - `template_id`：模板 ID，VARCHAR，可空，隐私 P1
  - `connected_flag`：接通标识，BOOLEAN，非空，隐私 P0
  - `ptp_flag`：PTP 标识，BOOLEAN，非空，隐私 P0
  - `ptp_fulfilled_flag`：PTP 履约标识，BOOLEAN，非空，隐私 P0
  - `ai_outbound_flag`：AI 外呼标识，BOOLEAN，非空，隐私 P0

### ods_call_record
- 中文名：外呼记录
- 主题域：source_events
- 粒度：call_id
- 主键：call_id
- 说明：外呼结果与录音转写引用
- 字段：
  - `call_id`：通话 ID，VARCHAR，非空，主键，隐私 P1
  - `action_id`：动作 ID，VARCHAR，非空，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `call_start_time`：通话开始时间，TIMESTAMP，非空，隐私 P0
  - `duration_seconds`：通话时长秒，INTEGER，非空，隐私 P0
  - `recording_uri`：录音引用，VARCHAR，非空，隐私 P1
  - `transcript_masked`：脱敏转写，VARCHAR，非空，隐私 P2

### ods_sms_send_log
- 中文名：短信发送日志
- 主题域：source_events
- 粒度：message_id
- 主键：message_id
- 说明：短信和语音发送流水
- 字段：
  - `message_id`：消息 ID，VARCHAR，非空，主键，隐私 P1
  - `action_id`：动作 ID，VARCHAR，非空，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `template_id`：模板 ID，VARCHAR，非空，隐私 P1
  - `send_time`：发送时间，TIMESTAMP，非空，隐私 P0
  - `send_status`：发送状态，VARCHAR，非空，隐私 P0

### ods_reduction_application
- 中文名：减免申请
- 主题域：source_events
- 粒度：reduction_id
- 主键：reduction_id
- 说明：减免申请与审批记录
- 字段：
  - `reduction_id`：减免 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `apply_time`：申请时间，TIMESTAMP，非空，隐私 P0
  - `apply_amount`：申请减免金额，DOUBLE，非空，隐私 P0
  - `approved_amount`：审批减免金额，DOUBLE，非空，隐私 P0
  - `approval_status`：审批状态，VARCHAR，非空，隐私 P0

### ods_complaint
- 中文名：投诉记录
- 主题域：source_events
- 粒度：complaint_id
- 主键：complaint_id
- 说明：投诉与合规事件记录
- 字段：
  - `complaint_id`：投诉 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，可空，隐私 P1
  - `template_id`：模板 ID，VARCHAR，可空，隐私 P1
  - `complaint_time`：投诉时间，TIMESTAMP，非空，隐私 P0
  - `complaint_type`：投诉类型，VARCHAR，非空，隐私 P0
  - `complaint_level`：投诉等级，VARCHAR，非空，隐私 P0

## DWD 层

### dwd_due_plan_detail_di
- 中文名：到期计划明细
- 主题域：detail_fact
- 粒度：stat_date+plan_id
- 主键：['stat_date', 'plan_id']
- 说明：清洗后的到期计划明细
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `plan_id`：还款计划 ID，VARCHAR，非空，主键，隐私 P1
  - `loan_id`：借据号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `product_code`：产品编码，VARCHAR，非空，隐私 P0
  - `channel_code`：渠道编码，VARCHAR，非空，隐私 P0
  - `due_date`：应还日，DATE，非空，隐私 P0
  - `due_amount`：应还总额，DOUBLE，非空，隐私 P0
  - `outstanding_amount`：待还金额，DOUBLE，非空，隐私 P0
  - `dpd_bucket`：账龄桶，VARCHAR，非空，隐私 P0

### dwd_repayment_detail_di
- 中文名：回款明细事实
- 主题域：detail_fact
- 粒度：repay_id
- 主键：repay_id
- 说明：清洗后的回款事实
- 字段：
  - `repay_id`：还款流水 ID，VARCHAR，非空，主键，隐私 P1
  - `plan_id`：还款计划 ID，VARCHAR，非空，隐私 P1
  - `loan_id`：借据号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `repay_time`：还款时间，TIMESTAMP，非空，隐私 P0
  - `repay_date`：还款日期，DATE，非空，隐私 P0
  - `repay_amount`：还款金额，DOUBLE，非空，隐私 P0
  - `repay_status`：还款状态，VARCHAR，非空，隐私 P0

### dwd_collection_action_detail_di
- 中文名：催收动作明细
- 主题域：detail_fact
- 粒度：action_id
- 主键：action_id
- 说明：清洗后的催收动作事实
- 字段：
  - `action_id`：动作 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `action_time`：动作时间，TIMESTAMP，非空，隐私 P0
  - `action_date`：动作日期，DATE，非空，隐私 P0
  - `action_type`：动作类型，VARCHAR，非空，隐私 P0
  - `template_id`：模板 ID，VARCHAR，可空，隐私 P1
  - `connected_flag`：接通标识，BOOLEAN，非空，隐私 P0
  - `ptp_flag`：PTP 标识，BOOLEAN，非空，隐私 P0
  - `ptp_fulfilled_flag`：PTP 履约标识，BOOLEAN，非空，隐私 P0
  - `ai_outbound_flag`：AI 外呼标识，BOOLEAN，非空，隐私 P0

### dwd_case_flow_detail_di
- 中文名：案件流转明细
- 主题域：detail_fact
- 粒度：flow_id
- 主键：flow_id
- 说明：清洗后的案件流转事实
- 字段：
  - `flow_id`：流转 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `from_status`：原状态，VARCHAR，非空，隐私 P0
  - `to_status`：新状态，VARCHAR，非空，隐私 P0
  - `flow_time`：流转时间，TIMESTAMP，非空，隐私 P0
  - `flow_date`：流转日期，DATE，非空，隐私 P0
  - `strategy_id`：策略编号，VARCHAR，非空，隐私 P1

### dwd_complaint_detail_di
- 中文名：投诉明细
- 主题域：detail_fact
- 粒度：complaint_id
- 主键：complaint_id
- 说明：清洗后的投诉事实
- 字段：
  - `complaint_id`：投诉 ID，VARCHAR，非空，主键，隐私 P1
  - `case_id`：案件编号，VARCHAR，非空，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，可空，隐私 P1
  - `template_id`：模板 ID，VARCHAR，可空，隐私 P1
  - `complaint_time`：投诉时间，TIMESTAMP，非空，隐私 P0
  - `complaint_date`：投诉日期，DATE，非空，隐私 P0
  - `complaint_type`：投诉类型，VARCHAR，非空，隐私 P0
  - `complaint_level`：投诉等级，VARCHAR，非空，隐私 P0

## DWS 层

### dws_loan_status_snapshot_di
- 中文名：借据状态日切宽表
- 主题域：subject_wide
- 粒度：stat_date+loan_id
- 主键：['stat_date', 'loan_id']
- 说明：借据状态与回款窗口宽表
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `loan_id`：借据号，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `product_code`：产品编码，VARCHAR，非空，隐私 P0
  - `dpd_bucket`：账龄桶，VARCHAR，非空，隐私 P0
  - `due_amount`：应还金额，DOUBLE，非空，隐私 P0
  - `repaid_amount_d7`：D7 回款金额，DOUBLE，非空，隐私 P0
  - `recovery_rate_d7`：D7 回收率，DOUBLE，非空，隐私 P0

### dws_case_status_snapshot_di
- 中文名：案件状态日切宽表
- 主题域：subject_wide
- 粒度：stat_date+case_id
- 主键：['stat_date', 'case_id']
- 说明：案件状态与作业结果宽表
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `case_id`：案件编号，VARCHAR，非空，主键，隐私 P1
  - `customer_id`：客户号，VARCHAR，非空，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `dpd_bucket`：账龄桶，VARCHAR，非空，隐私 P0
  - `outstanding_amount`：待还金额，DOUBLE，非空，隐私 P0
  - `action_count`：动作数，INTEGER，非空，隐私 P0
  - `connected_count`：接通数，INTEGER，非空，隐私 P0
  - `ptp_count`：PTP 数，INTEGER，非空，隐私 P0
  - `repaid_amount`：回款金额，DOUBLE，非空，隐私 P0

### dws_customer_status_snapshot_di
- 中文名：客户状态日切宽表
- 主题域：subject_wide
- 粒度：stat_date+customer_id
- 主键：['stat_date', 'customer_id']
- 说明：归户视角日切宽表
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `customer_id`：客户号，VARCHAR，非空，主键，隐私 P1
  - `active_loan_count`：有效借据数，INTEGER，非空，隐私 P0
  - `active_case_count`：有效案件数，INTEGER，非空，隐私 P0
  - `total_outstanding_amount`：总待还金额，DOUBLE，非空，隐私 P0
  - `max_dpd`：最大逾期天数，INTEGER，非空，隐私 P0
  - `risk_level`：风险等级，VARCHAR，非空，隐私 P0

### dws_collection_process_wide_di
- 中文名：催收过程宽表
- 主题域：subject_wide
- 粒度：stat_date+case_id
- 主键：['stat_date', 'case_id']
- 说明：触达、PTP、履约、投诉过程宽表
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `case_id`：案件编号，VARCHAR，非空，主键，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `collector_id`：催员编号，VARCHAR，非空，隐私 P1
  - `action_count`：动作数，INTEGER，非空，隐私 P0
  - `ai_action_count`：AI 外呼动作数，INTEGER，非空，隐私 P0
  - `connected_count`：接通数，INTEGER，非空，隐私 P0
  - `ptp_count`：PTP 数，INTEGER，非空，隐私 P0
  - `ptp_fulfilled_count`：PTP 履约数，INTEGER，非空，隐私 P0
  - `complaint_count`：投诉数，INTEGER，非空，隐私 P0
  - `connect_rate`：接通率，DOUBLE，非空，隐私 P0
  - `ptp_fulfillment_rate`：PTP 履约率，DOUBLE，非空，隐私 P0
  - `ai_coverage_rate`：AI 外呼覆盖率，DOUBLE，非空，隐私 P0

### dws_vendor_line_capacity_di
- 中文名：供应商线路产能宽表
- 主题域：subject_wide
- 粒度：stat_date+vendor_id+line_id
- 主键：['stat_date', 'vendor_id', 'line_id']
- 说明：供应商线路产能日切宽表
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `vendor_id`：供应商编号，VARCHAR，非空，主键，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，主键，隐私 P1
  - `region`：区域，VARCHAR，非空，隐私 P0
  - `active_case_count`：在催案件数，INTEGER，非空，隐私 P0
  - `active_collector_count`：在岗催员数，INTEGER，非空，隐私 P0
  - `case_per_collector`：人均案量，DOUBLE，非空，隐私 P0

### dws_customer_profile_di
- 中文名：客户画像日切
- 主题域：subject_wide
- 粒度：stat_date+customer_id
- 主键：['stat_date', 'customer_id']
- 说明：客户基础、借款、还款、贷后画像
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `customer_id`：客户号，VARCHAR，非空，主键，隐私 P1
  - `customer_id_hash`：客户号哈希，VARCHAR，非空，隐私 P3
  - `mobile_masked`：脱敏手机号，VARCHAR，非空，隐私 P2
  - `province`：省份，VARCHAR，非空，隐私 P0
  - `customer_segment`：客户分层，VARCHAR，非空，隐私 P0
  - `risk_level_current`：当前风险等级，VARCHAR，非空，隐私 P0
  - `total_outstanding_amount`：总待还金额，DOUBLE，非空，隐私 P0

### dws_collector_profile_di
- 中文名：催员画像日切
- 主题域：subject_wide
- 粒度：stat_date+collector_id
- 主键：['stat_date', 'collector_id']
- 说明：催员作业、结果、合规画像
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `collector_id`：催员编号，VARCHAR，非空，主键，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `line_id`：线路编号，VARCHAR，非空，隐私 P1
  - `skill_level`：技能等级，VARCHAR，非空，隐私 P0
  - `action_count`：动作数，INTEGER，非空，隐私 P0
  - `connect_rate`：接通率，DOUBLE，非空，隐私 P0
  - `complaint_count`：投诉数，INTEGER，非空，隐私 P0

### dws_customer_postloan_tag_di
- 中文名：客户贷后标签日切
- 主题域：subject_wide
- 粒度：stat_date+customer_id
- 主键：['stat_date', 'customer_id']
- 说明：客户贷后标签日切
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `customer_id`：客户号，VARCHAR，非空，主键，隐私 P1
  - `dpd_tag`：账龄标签，VARCHAR，非空，隐私 P0
  - `balance_tag`：金额标签，VARCHAR，非空，隐私 P0
  - `behavior_tag`：行为标签，VARCHAR，非空，隐私 P0
  - `touch_tag`：触达标签，VARCHAR，非空，隐私 P0
  - `compliance_tag`：合规投诉标签，VARCHAR，非空，隐私 P0
  - `strategy_tag`：策略标签，VARCHAR，非空，隐私 P0

## ADS 层

### ads_postloan_dashboard_di
- 中文名：贷后经营驾驶舱日切
- 主题域：application_summary
- 粒度：stat_date
- 主键：stat_date
- 说明：贷后核心经营汇总
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `m1_due_amount`：M1 应还金额，DOUBLE，非空，隐私 P0
  - `m1_repaid_amount_d7`：M1 D7 回款金额，DOUBLE，非空，隐私 P0
  - `m1_recovery_rate_d7`：M1 D7 回收率，DOUBLE，非空，隐私 P0
  - `connect_rate`：接通率，DOUBLE，非空，隐私 P0
  - `ai_coverage_rate`：AI 外呼覆盖率，DOUBLE，非空，隐私 P0
  - `ptp_fulfillment_rate`：PTP 履约率，DOUBLE，非空，隐私 P0
  - `high_balance_case_share`：高余额案件占比，DOUBLE，非空，隐私 P0

### ads_recovery_attribution_di
- 中文名：回收率归因日切
- 主题域：application_summary
- 粒度：stat_date+factor_code
- 主键：['stat_date', 'factor_code']
- 说明：回收率归因占位汇总
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `factor_code`：因子编码，VARCHAR，非空，主键，隐私 P0
  - `factor_name`：因子名称，VARCHAR，非空，隐私 P0
  - `factor_value`：因子值，DOUBLE，非空，隐私 P0
  - `contribution_pct`：贡献占比，DOUBLE，非空，隐私 P0

### ads_vendor_performance_di
- 中文名：供应商绩效日切
- 主题域：application_summary
- 粒度：stat_date+vendor_id
- 主键：['stat_date', 'vendor_id']
- 说明：供应商绩效日切
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `vendor_id`：供应商编号，VARCHAR，非空，主键，隐私 P1
  - `action_count`：动作数，INTEGER，非空，隐私 P0
  - `connect_rate`：接通率，DOUBLE，非空，隐私 P0
  - `ptp_rate`：PTP 率，DOUBLE，非空，隐私 P0
  - `complaint_rate`：投诉率，DOUBLE，非空，隐私 P0

### ads_collector_performance_di
- 中文名：催员绩效日切
- 主题域：application_summary
- 粒度：stat_date+collector_id
- 主键：['stat_date', 'collector_id']
- 说明：催员绩效日切
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `collector_id`：催员编号，VARCHAR，非空，主键，隐私 P1
  - `vendor_id`：供应商编号，VARCHAR，非空，隐私 P1
  - `action_count`：动作数，INTEGER，非空，隐私 P0
  - `connect_rate`：接通率，DOUBLE，非空，隐私 P0
  - `ptp_fulfillment_rate`：PTP 履约率，DOUBLE，非空，隐私 P0
  - `complaint_count`：投诉数，INTEGER，非空，隐私 P0

### ads_reduction_roi_di
- 中文名：减免 ROI 日切
- 主题域：application_summary
- 粒度：stat_date
- 主键：stat_date
- 说明：减免使用与回款 ROI 汇总
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `reduction_case_count`：减免案件数，INTEGER，非空，隐私 P0
  - `approved_reduction_amount`：审批减免金额，DOUBLE，非空，隐私 P0
  - `repaid_amount`：回款金额，DOUBLE，非空，隐私 P0
  - `reduction_usage_rate`：减免使用率，DOUBLE，非空，隐私 P0
  - `reduction_roi`：减免 ROI，DOUBLE，非空，隐私 P0

### ads_compliance_qc_di
- 中文名：合规质检日切
- 主题域：application_summary
- 粒度：stat_date+template_id
- 主键：['stat_date', 'template_id']
- 说明：投诉与合规质检汇总
- 字段：
  - `stat_date`：统计日期，DATE，非空，主键，隐私 P0
  - `template_id`：模板 ID，VARCHAR，非空，主键，隐私 P1
  - `send_count`：发送数，INTEGER，非空，隐私 P0
  - `complaint_count`：投诉数，INTEGER，非空，隐私 P0
  - `complaint_rate`：投诉率，DOUBLE，非空，隐私 P0
