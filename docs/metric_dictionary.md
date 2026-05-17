# 指标字典

> 由 `metadata/metric_dictionary.yaml` 自动渲染。

## postloan

### due_account_count
- 中文名：到期账户数
- 类型：count
- 分子：到期窗口内去重客户数
- 分母：无
- 公式：`count(distinct customer_id where due_date in window)`
- 粒度：stat_date, product_code, channel_code, city, risk_level
- 来源表：dwd_due_plan_detail_di, dim_customer
- 过滤条件：`due_date = stat_date`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：账户按 customer_id 去重，服务贷后经营到期规模判断。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### due_loan_count
- 中文名：到期借据数
- 类型：count
- 分子：到期窗口内去重借据数
- 分母：无
- 公式：`count(distinct loan_id where due_date in window)`
- 粒度：stat_date, product_code, channel_code
- 来源表：dwd_due_plan_detail_di
- 过滤条件：`due_date = stat_date`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：借据按 loan_id 去重。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### due_total_amount
- 中文名：到期应还金额
- 类型：amount
- 分子：到期应还金额合计
- 分母：无
- 公式：`sum(due_amount)`
- 粒度：stat_date, product_code, channel_code
- 来源表：dwd_due_plan_detail_di
- 过滤条件：`due_date = stat_date`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：金额含本金、利息和费用，不含减免。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### collection_entry_rate
- 中文名：入催率
- 类型：ratio
- 分子：入催账户数
- 分母：到期账户数
- 公式：`collection_entry_count / due_account_count`
- 粒度：stat_date, product_code, dpd_bucket, risk_level
- 来源表：dim_case, dwd_due_plan_detail_di
- 过滤条件：`case_create_date = stat_date`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 按入案日与到期日同日口径汇总。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### recovery_rate_d7
- 中文名：D7 回收率
- 类型：ratio
- 分子：到期后 7 天内累计回款金额
- 分母：到期应还金额
- 公式：`repay_amount_within_7d / due_amount`
- 粒度：stat_date, vendor_id, line_id, collector_id, dpd_bucket
- 来源表：dwd_due_plan_detail_di, dwd_repayment_detail_di, dim_case_loan_mapping, dim_case
- 过滤条件：`repay_time <= due_date + 7 days`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：金额口径不含减免。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### recovery_rate_d15
- 中文名：D15 回收率
- 类型：ratio
- 分子：到期后 15 天内累计回款金额
- 分母：到期应还金额
- 公式：`repay_amount_within_15d / due_amount`
- 粒度：stat_date, vendor_id, line_id, collector_id, dpd_bucket
- 来源表：dwd_due_plan_detail_di, dwd_repayment_detail_di, dim_case_loan_mapping, dim_case
- 过滤条件：`repay_time <= due_date + 15 days`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：金额口径不含减免。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### recovery_rate_d30
- 中文名：D30 回收率
- 类型：ratio
- 分子：到期后 30 天内累计回款金额
- 分母：到期应还金额
- 公式：`repay_amount_within_30d / due_amount`
- 粒度：stat_date, vendor_id, line_id, collector_id, dpd_bucket
- 来源表：dwd_due_plan_detail_di, dwd_repayment_detail_di, dim_case_loan_mapping, dim_case
- 过滤条件：`repay_time <= due_date + 30 days`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：金额口径不含减免。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### m1_recovery_rate
- 中文名：M1 回收率
- 类型：ratio
- 分子：M1 案件回款金额
- 分母：M1 初始待还金额
- 公式：`m1_repay_amount / m1_initial_outstanding_amount`
- 粒度：stat_date, vendor_id, line_id, product_code, balance_segment, risk_level
- 来源表：dws_loan_status_snapshot_di
- 过滤条件：`dpd_bucket = M1`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 使用 DWS 借据日切 M1 金额口径。
- 变更记录：
  - 2026-05-15：Phase 1 初版

## collection

### call_coverage_rate
- 中文名：拨打覆盖率
- 类型：ratio
- 分子：已拨打案件数
- 分母：已分配案件数
- 公式：`called_case_count / assigned_case_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dws_collection_process_wide_di, dws_case_status_snapshot_di
- 过滤条件：`action_count > 0`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：案件去重口径。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### valid_coverage_rate
- 中文名：有效覆盖率
- 类型：ratio
- 分子：有效沟通案件数
- 分母：已分配案件数
- 公式：`valid_contact_case_count / assigned_case_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dwd_collection_action_detail_di, ods_call_record, dws_case_status_snapshot_di
- 过滤条件：`connected_flag = true and duration_seconds >= 60`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：有效沟通为接通且通话时长不少于 60 秒。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### connect_rate
- 中文名：接通率
- 类型：ratio
- 分子：接通次数
- 分母：拨打次数
- 公式：`connect_count / call_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dws_collection_process_wide_di
- 过滤条件：`action_count > 0`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 以触达动作总数作为拨打次数近似口径。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### valid_contact_rate
- 中文名：有效沟通率
- 类型：ratio
- 分子：有效沟通次数
- 分母：接通次数
- 公式：`valid_contact_count / connect_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dwd_collection_action_detail_di, ods_call_record
- 过滤条件：`connected_flag = true`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：有效沟通为接通且通话时长不少于 60 秒。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### first_contact_hours
- 中文名：首触达时效
- 类型：score
- 分子：首次触达时间与分案时间的小时差均值
- 分母：已触达案件数
- 公式：`avg(first_contact_time - assign_time)`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dwd_collection_action_detail_di, dim_case
- 过滤条件：`action_time >= case_create_time`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：单位小时，Phase 1 以 case_create_time 近似分案时间。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### ptp_rate
- 中文名：PTP 率
- 类型：ratio
- 分子：PTP 次数
- 分母：有效沟通次数
- 公式：`ptp_count / valid_contact_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dwd_collection_action_detail_di, ods_call_record
- 过滤条件：`valid_contact_flag = true`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 dashboard 口径以 calculator 为准，按 ptp_count / valid_contact_count 计算；vendor / collector 维度当前缺少完整 valid_contact_count 分层明细时，允许在 ADS 侧降级为 ptp_count / connected_count，仅用于资源维度横向比较，不与 dashboard 绝对值混读。M3 归因默认读取 dashboard 权威口径，M4 展示 vendor / collector 时需标注降级分母；后续补齐分层有效沟通宽表后再统一口径。
- 变更记录：
  - 2026-05-15：Phase 1 初版
  - 2026-05-17：M3-prep 补充 dashboard 权威口径与 vendor / collector 降级边界

### ptp_keep_rate
- 中文名：PTP 履约率
- 类型：ratio
- 分子：已履约 PTP 次数
- 分母：已到期 PTP 次数
- 公式：`kept_ptp_count / matured_ptp_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dws_collection_process_wide_di
- 过滤条件：`matured_ptp_count > 0`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 合成数据中 PTP 均视为已到承诺观察日。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### avg_call_duration_per_call
- 中文名：单通平均时长
- 类型：score
- 分子：通话总时长秒数
- 分母：通话次数
- 公式：`sum(call_duration_sec where connect=1) / connect_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：ods_call_record, dwd_collection_action_detail_di
- 过滤条件：`duration_seconds > 0`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P1
- 说明：单位秒。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### avg_call_duration_per_collector
- 中文名：人均日通话时长
- 类型：score
- 分子：通话总时长秒数
- 分母：活跃催员数
- 公式：`sum(call_duration_sec) / active_collector_count / work_days`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：ods_call_record, dwd_collection_action_detail_di
- 过滤条件：`duration_seconds > 0`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P1
- 说明：日切数据中 work_days 固定为 1。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### collector_productivity
- 中文名：作业人效
- 类型：amount
- 分子：回款金额
- 分母：活跃催员数
- 公式：`repay_amount / active_collector_count`
- 粒度：stat_date, vendor_id, line_id, collector_id
- 来源表：dws_case_status_snapshot_di
- 过滤条件：`active_collector_count > 0`
- Owner：collection_operation_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P1
- 说明：单位为元每活跃催员。
- 变更记录：
  - 2026-05-15：Phase 1 初版

## compliance

### complaint_rate
- 中文名：投诉率
- 类型：ratio
- 分子：投诉案件数
- 分母：在催案件数
- 公式：`complaint_case_count / active_case_count`
- 粒度：stat_date, vendor_id, collector_id, template_id
- 来源表：dwd_complaint_detail_di, dws_case_status_snapshot_di
- 过滤条件：`active_case_count > 0`
- Owner：compliance_qc_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 dashboard 口径以 calculator 为准，按 complaint_case_count / active_case_count 的案件去重口径计算；vendor / collector 维度如仅有 assigned_case_count 或动作聚合投诉数，允许降级为 complaint_count / assigned_case_count， 仅用于资源维度风险排序，不与 dashboard 绝对值混读。M3 归因默认读取 dashboard 权威口径，M4 展示 vendor / collector 时需标注降级分母；后续补齐投诉案件与在催案件的同粒度桥表后再统一口径。
- 变更记录：
  - 2026-05-15：Phase 1 初版
  - 2026-05-17：M3-prep 补充 dashboard 权威口径与 vendor / collector 降级边界

### complaint_per_10k_cases
- 中文名：万案投诉率
- 类型：score
- 分子：投诉次数
- 分母：在催案件数
- 公式：`complaint_count / active_case_count * 10000`
- 粒度：stat_date, vendor_id, collector_id, template_id
- 来源表：dwd_complaint_detail_di, dws_case_status_snapshot_di
- 过滤条件：`active_case_count > 0`
- Owner：compliance_qc_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：单位为每万案件投诉次数。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### risk_phrase_hit_rate
- 中文名：高风险话术命中率
- 类型：ratio
- 分子：高风险话术命中次数
- 分母：质检检查次数
- 公式：`risk_phrase_hit_count / qa_checked_count`
- 粒度：stat_date, vendor_id, collector_id, template_id
- 来源表：dwd_collection_action_detail_di
- 过滤条件：`template_id = TPL_RISK_NOTICE`
- Owner：compliance_qc_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 以风险短信模板作为高风险话术命中代理。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### qa_fail_rate
- 中文名：质检不合格率
- 类型：ratio
- 分子：质检不合格通话数
- 分母：质检通话数
- 公式：`qa_fail_call_count / qa_checked_call_count`
- 粒度：stat_date, vendor_id, collector_id, template_id
- 来源表：dwd_complaint_detail_di, dwd_collection_action_detail_di
- 过滤条件：`complaint_level in (MEDIUM, HIGH)`
- Owner：compliance_qc_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P1
- 说明：Phase 1 以中高等级投诉作为质检不合格代理。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### over_frequency_contact_rate
- 中文名：超频触达率
- 类型：ratio
- 分子：单日触达超过 3 次的案件数
- 分母：单日已触达案件数
- 公式：`over_frequency_case_count / contacted_case_count`
- 粒度：stat_date, vendor_id, collector_id
- 来源表：dwd_collection_action_detail_di
- 过滤条件：`daily_action_count > 3`
- Owner：compliance_qc_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P1
- 说明：Phase 1 超频阈值为单案件单日 3 次。
- 变更记录：
  - 2026-05-15：Phase 1 初版

## roi

### reduction_usage_rate
- 中文名：减免使用率
- 类型：ratio
- 分子：减免申请案件数
- 分母：可减免案件数
- 公式：`reduction_case_count / eligible_case_count`
- 粒度：stat_date, vendor_id, line_id, dpd_bucket
- 来源表：ods_reduction_application, dws_case_status_snapshot_di
- 过滤条件：`approval_status in (APPROVED, REJECTED)`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：Phase 1 以在催案件作为可减免案件代理。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### reduction_recovery_rate
- 中文名：减免回收率
- 类型：ratio
- 分子：减免后回款金额
- 分母：减免案件待还金额
- 公式：`repay_amount_after_reduction / reduction_case_outstanding_amount`
- 粒度：stat_date, vendor_id, line_id, dpd_bucket
- 来源表：ods_reduction_application, dws_case_status_snapshot_di
- 过滤条件：`reduction_case_count > 0`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P0
- 说明：金额口径不含已批准减免金额本身。
- 变更记录：
  - 2026-05-15：Phase 1 初版

### reduction_roi
- 中文名：减免 ROI
- 类型：score
- 分子：实际回款金额减反事实预估回款金额
- 分母：审批减免金额
- 公式：`(actual_repay - expected_repay_without_reduction) / approved_reduction_amount`
- 粒度：stat_date, vendor_id, line_id, dpd_bucket
- 来源表：ods_reduction_application, dws_case_status_snapshot_di
- 过滤条件：`approved_reduction_amount > 0`
- Owner：postloan_strategy_team
- 刷新频率：daily
- 版本：v1.0
- 优先级：P1
- 说明：Phase 1 反事实回款使用配置项 baseline_recovery_without_reduction 作为无减免回收率代理，默认值为 0.82，不做因果推断； 当前 dashboard / ADS 均只表达日切整体 ROI，vendor / line / dpd_bucket 粒度在样本和对照组不足时不拆分展示。 M3 可将该配置作为异常与归因的业务基线输入，M4 展示时需说明其为代理基线；后续补齐同条件历史客群或对照组后升级为分层基线。
- 变更记录：
  - 2026-05-15：Phase 1 初版
  - 2026-05-17：M3-prep 将 0.82 基线迁移到 configs/metric_params.yaml 并补充口径边界
