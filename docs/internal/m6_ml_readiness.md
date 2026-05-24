# M6-D0 ML Modeling Readiness Check

## 1. 数据资产盘点

本次检查只读 `synthetic_data/`、`outputs/m3/`、`outputs/model_lab/` 和项目配置文件；未训练模型、未新增建模代码、未修改数据生成逻辑。`warehouse/` 目录当前不存在，现有数仓产物直接落在 `synthetic_data/dwd`、`synthetic_data/dws`、`synthetic_data/ads`。

### 1.1 synthetic_data 主要文件

- **synthetic_data/dim/dim_customer.parquet**
  - 格式：parquet
  - 行列：20,000 行，12 列
  - 样本粒度：客户级
  - 关键字段：`customer_id`、`customer_id_hash`、`mobile_masked`、`gender`、`age_group`、`province`、`city`、`occupation_type`、`customer_segment`、`risk_level_current`
- **synthetic_data/dim/dim_loan.parquet**
  - 格式：parquet
  - 行列：30,000 行，12 列
  - 样本粒度：借据级
  - 关键字段：`loan_id`、`customer_id`、`product_code`、`channel_code`、`loan_amount`、`loan_term`、`interest_rate`、`loan_status`、`first_due_date`、`mob`、`vintage_month`
- **synthetic_data/dim/dim_case.parquet**
  - 格式：parquet
  - 行列：10,000 行，12 列
  - 样本粒度：案件级
  - 关键字段：`case_id`、`customer_id`、`case_create_time`、`case_type`、`initial_dpd_bucket`、`initial_outstanding_amount`、`current_line_id`、`current_vendor_id`、`protect_flag`、`sensitive_flag`、`complaint_flag`、`balance_segment`
- **synthetic_data/dim/dim_case_loan_mapping.parquet**
  - 格式：parquet
  - 行列：10,000 行，7 列
  - 样本粒度：案件-借据映射级
  - 关键字段：`case_id`、`loan_id`、`customer_id`、`main_loan_flag`
- **synthetic_data/ods/ods_repayment_plan.parquet**
  - 格式：parquet
  - 行列：30,000 行，10 列
  - 样本粒度：还款计划 / 应还期次级
  - 关键字段：`plan_id`、`loan_id`、`customer_id`、`due_date`、`due_amount`
- **synthetic_data/ods/ods_repayment_detail.parquet**
  - 格式：parquet
  - 行列：8,405 行，8 列
  - 样本粒度：还款流水级
  - 关键字段：`repay_id`、`plan_id`、`loan_id`、`customer_id`、`repay_time`、`repay_amount`
- **synthetic_data/ods/ods_collection_action.parquet**
  - 格式：parquet
  - 行列：200,000 行，13 列
  - 样本粒度：催收触达动作级
  - 关键字段：`action_id`、`case_id`、`customer_id`、`vendor_id`、`line_id`、`collector_id`、`action_time`、`action_type`、`connected_flag`、`ptp_flag`、`ptp_fulfilled_flag`、`ai_outbound_flag`
- **synthetic_data/ods/ods_call_record.parquet**
  - 格式：parquet
  - 行列：66,666 行，7 列
  - 样本粒度：通话记录级
  - 关键字段：`call_id`、`action_id`、`case_id`、`call_start_time`、`duration_seconds`、`transcript_masked`
- **synthetic_data/ods/ods_sms_send_log.parquet**
  - 格式：parquet
  - 行列：39,855 行，7 列
  - 样本粒度：短信发送记录级
  - 关键字段：`message_id`、`action_id`、`case_id`、`customer_id`、`template_id`、`send_time`、`send_status`
- **synthetic_data/ods/ods_postloan_c_score.parquet**
  - 格式：parquet
  - 行列：10,000 行，5 列
  - 样本粒度：客户评分级
  - 关键字段：`score_id`、`customer_id`、`score_date`、`postloan_c_score`、`score_level`
- **synthetic_data/ods/ods_reduction_application.parquet**
  - 格式：parquet
  - 行列：621 行，7 列
  - 样本粒度：减免申请级
  - 关键字段：`reduction_id`、`case_id`、`customer_id`、`apply_time`、`apply_amount`、`approval_status`、`approved_amount`
- **synthetic_data/ods/ods_complaint.parquet**
  - 格式：parquet
  - 行列：224 行，9 列
  - 样本粒度：投诉事件级
  - 关键字段：`complaint_id`、`case_id`、`customer_id`、`vendor_id`、`collector_id`、`template_id`、`complaint_time`、`complaint_type`、`complaint_level`
- **synthetic_data/ods/ods_loan_daily_snapshot.parquet**
  - 格式：parquet
  - 行列：240,000 行，7 列
  - 样本粒度：借据日切
  - 关键字段：`stat_date`、`loan_id`、`customer_id`、`dpd`、`dpd_bucket`、`outstanding_amount`、`loan_status`
- **synthetic_data/ods/ods_case_daily_snapshot.parquet**
  - 格式：parquet
  - 行列：424,315 行，9 列
  - 样本粒度：案件日切
  - 关键字段：`stat_date`、`case_id`、`customer_id`、`vendor_id`、`line_id`、`collector_id`、`case_status`、`dpd_bucket`、`outstanding_amount`
- **synthetic_data/ods/ods_customer_daily_snapshot.parquet**
  - 格式：parquet
  - 行列：353,997 行，7 列
  - 样本粒度：客户日切
  - 关键字段：`stat_date`、`customer_id`、`active_loan_count`、`active_case_count`、`total_outstanding_amount`、`max_dpd`、`risk_level`
- **synthetic_data/dwd/dwd_due_plan_detail_di.parquet**
  - 格式：parquet
  - 行列：30,000 行，10 列
  - 样本粒度：清洗后应还计划明细
  - 关键字段：`stat_date`、`plan_id`、`loan_id`、`customer_id`、`product_code`、`channel_code`、`due_date`、`due_amount`、`outstanding_amount`、`dpd_bucket`
- **synthetic_data/dwd/dwd_repayment_detail_di.parquet**
  - 格式：parquet
  - 行列：8,405 行，8 列
  - 样本粒度：清洗后还款流水
  - 关键字段：`repay_id`、`plan_id`、`loan_id`、`customer_id`、`repay_time`、`repay_date`、`repay_amount`
- **synthetic_data/dwd/dwd_collection_action_detail_di.parquet**
  - 格式：parquet
  - 行列：200,000 行，14 列
  - 样本粒度：清洗后触达动作级
  - 关键字段：`action_id`、`case_id`、`customer_id`、`vendor_id`、`line_id`、`collector_id`、`action_date`、`action_type`、`connected_flag`、`ptp_flag`、`ptp_fulfilled_flag`、`ai_outbound_flag`
- **synthetic_data/dwd/dwd_complaint_detail_di.parquet**
  - 格式：parquet
  - 行列：224 行，10 列
  - 样本粒度：清洗后投诉事件级
  - 关键字段：`complaint_id`、`case_id`、`customer_id`、`vendor_id`、`collector_id`、`template_id`、`complaint_date`、`complaint_type`、`complaint_level`
- **synthetic_data/dws/dws_loan_status_snapshot_di.parquet**
  - 格式：parquet
  - 行列：30,000 行，8 列
  - 样本粒度：借据级 D7 结果快照
  - 关键字段：`loan_id`、`customer_id`、`product_code`、`dpd_bucket`、`due_amount`、`repaid_amount_d7`、`recovery_rate_d7`
- **synthetic_data/dws/dws_case_status_snapshot_di.parquet**
  - 格式：parquet
  - 行列：424,315 行，12 列
  - 样本粒度：案件日切
  - 关键字段：`stat_date`、`case_id`、`customer_id`、`vendor_id`、`line_id`、`collector_id`、`dpd_bucket`、`outstanding_amount`、`action_count`、`connected_count`、`ptp_count`、`repaid_amount`
- **synthetic_data/dws/dws_customer_status_snapshot_di.parquet**
  - 格式：parquet
  - 行列：353,997 行，7 列
  - 样本粒度：客户日切
  - 关键字段：`stat_date`、`customer_id`、`active_loan_count`、`active_case_count`、`total_outstanding_amount`、`max_dpd`、`risk_level`
- **synthetic_data/dws/dws_collection_process_wide_di.parquet**
  - 格式：parquet
  - 行列：199,860 行，14 列
  - 样本粒度：案件-日期-催员过程宽表
  - 关键字段：`stat_date`、`case_id`、`vendor_id`、`line_id`、`collector_id`、`action_count`、`ai_action_count`、`connected_count`、`ptp_count`、`ptp_fulfilled_count`、`complaint_count`、`connect_rate`、`ptp_fulfillment_rate`、`ai_coverage_rate`
- **synthetic_data/dws/dws_customer_profile_di.parquet**
  - 格式：parquet
  - 行列：20,000 行，8 列
  - 样本粒度：客户画像级
  - 关键字段：`customer_id`、`customer_id_hash`、`mobile_masked`、`province`、`customer_segment`、`risk_level_current`、`total_outstanding_amount`
- **synthetic_data/dws/dws_customer_postloan_tag_di.parquet**
  - 格式：parquet
  - 行列：353,997 行，8 列
  - 样本粒度：客户贷后标签日切
  - 关键字段：`stat_date`、`customer_id`、`dpd_tag`、`balance_tag`、`behavior_tag`、`touch_tag`、`compliance_tag`、`strategy_tag`
- **synthetic_data/ads/ads_postloan_dashboard_di.parquet**
  - 格式：parquet
  - 行列：517 行，27 列
  - 样本粒度：日期指标聚合
  - 关键字段：`stat_date`、`recovery_rate_d7`、`m1_recovery_rate`、`call_coverage_rate`、`connect_rate`、`ptp_keep_rate`、`complaint_rate`、`reduction_roi`
- **synthetic_data/ads/ads_vendor_performance_di.parquet**
  - 格式：parquet
  - 行列：724 行，8 列
  - 样本粒度：供应商-日期指标聚合
  - 关键字段：`stat_date`、`vendor_id`、`action_count`、`call_coverage_rate`、`connect_rate`、`ptp_rate`、`ptp_keep_rate`、`complaint_rate`
- **synthetic_data/ads/ads_collector_performance_di.parquet**
  - 格式：parquet
  - 行列：69,884 行，11 列
  - 样本粒度：催员-日期指标聚合
  - 关键字段：`stat_date`、`collector_id`、`vendor_id`、`action_count`、`connect_rate`、`ptp_keep_rate`、`complaint_count`
- **synthetic_data/ads/ads_compliance_qc_di.parquet**
  - 格式：parquet
  - 行列：517 行，9 列
  - 样本粒度：日期-模板合规指标聚合
  - 关键字段：`stat_date`、`template_id`、`active_case_count`、`complaint_count`、`complaint_rate`、`complaint_per_10k_cases`
- **synthetic_data/ads/ads_reduction_roi_di.parquet**
  - 格式：parquet
  - 行列：517 行，6 列
  - 样本粒度：日期减免 ROI 指标聚合
  - 关键字段：`stat_date`、`reduction_case_count`、`approved_reduction_amount`、`reduction_usage_rate`、`reduction_recovery_rate`、`reduction_roi`

### 1.2 warehouse 和 outputs

- **warehouse/**
  - 状态：目录不存在
  - 结论：不影响本轮 readiness 判断，因为 M1 build script 当前把 DWD/DWS/ADS 写回 `synthetic_data/`
- **outputs/m3/m3_summary.json**
  - 状态：存在
  - 用途：提供 M3 异常、D7 attribution 和过程证据
- **outputs/model_lab/**
  - 状态：存在 M6-A/B/C/E 相关 JSON/Markdown 输出
  - 文件：`strategy_eval_results.json`、`strategy_eval_summary.md`、`roi_results.json`、`roi_summary.md`
  - 用途：当前是策略评估和 ROI demo 输出，不是训练数据

## 2. Target 可行性

### 2.1 字段存在性

- **直接存在**
  - `recovery_rate_d7`：存在于 `dws_loan_status_snapshot_di` 和 `ads_postloan_dashboard_di`
  - `repaid_amount_d7`：存在于 `dws_loan_status_snapshot_di`
  - `dpd`：存在于 `ods_loan_daily_snapshot`
  - `due_date`：存在于 `ods_repayment_plan` 和 `dwd_due_plan_detail_di`
  - `repay_date`、`repay_amount`：存在于 `dwd_repayment_detail_di`
  - `outstanding_amount`：存在于 DWD/DWS 多张表
  - `case_id`、`customer_id`：存在于案件、触达、投诉、减免、映射等多张表
- **未直接存在，但可构造**
  - `is_recovered_d7`：可由 `repaid_amount_d7 > 0` 或 `recovery_rate_d7 > 0` 构造
  - `paid_d7` / `recovery_flag_d7` / `repayment_flag_d7`：可按同一 D7 回收逻辑构造
  - `overdue_day`：无同名字段，可用 `dpd` 作为近似
- **不存在**
  - `recovered_d7`
  - `is_recovered_d7`
  - `recovery_flag_d7`
  - `repayment_flag_d7`
  - `paid_d7`

### 2.2 候选 target 判断

- **D7 是否回收**
  - 可行性：强
  - 构造方式：借据级用 `dws_loan_status_snapshot_di.repaid_amount_d7 > 0`；案件级通过 `dim_case_loan_mapping` 拼回 `case_id`
  - 样本量：借据级 30,000 行，正样本 8,405，正样本率 28.02%；案件级 10,000 行，正样本 2,314，正样本率 23.14%
  - 结论：最适合 M6-D1 第一个 ML baseline
- **是否迁徙到更高逾期阶段**
  - 可行性：中
  - 构造方式：可用 `ods_loan_daily_snapshot` 或 `dws_customer_status_snapshot_di` 对比同一 `loan_id` / `customer_id` 在不同 `stat_date` 的 `dpd_bucket` 或 `max_dpd`
  - 限制：需要定义观察窗口和迁徙标签，本轮不改数据逻辑时仍可由日切数据离线构造
- **是否投诉**
  - 可行性：中
  - 构造方式：案件级 `case_id in dwd_complaint_detail_di` 或 `dim_case.complaint_flag`
  - 样本量：案件级 10,000 行，正样本 219，正样本率 2.19%
  - 限制：正样本稀疏，更适合后续做 risk screening，不适合作为首个 baseline
- **是否 PTP 履约**
  - 可行性：中到强
  - 构造方式：动作级用 `ptp_flag = true` 样本上的 `ptp_fulfilled_flag`；案件级用 `ptp_count > 0` 后的 `ptp_fulfilled_count > 0`
  - 样本量：PTP 动作 14,787 行，履约率 49.67%；有 PTP 的案件 7,747 个，案件级履约率 67.02%
  - 限制：target 依赖已经发生的 PTP，业务上是二阶段模型，不适合作为 M6-D1 第一刀
- **是否需要人工催收**
  - 可行性：弱
  - 构造方式：可用 `case_type`、`current_line_id`、`action_type` 近似，但缺少明确人工介入 label
  - 限制：当前字段更像策略分配结果，不是独立 target

- **是否高风险案件**
  - 可行性：中
  - 构造方式：可用 `dim_case.case_type = HIGH_RISK`，当前正样本 810 / 10,000，正样本率 8.10%
  - 限制：`case_type` 本身是生成时的分案/分类结果，容易变成规则复现，不如 D7 回收更能展示真实结果预测

## 3. 特征可行性

### 3.1 可用候选特征

- **客户画像**
  - `age_group`
  - `gender`
  - `province`
  - `city`
  - `occupation_type`
  - `customer_segment`
  - `risk_level_current`
  - `total_outstanding_amount`
  - `active_loan_count`
  - `active_case_count`
  - `max_dpd`
  - `risk_level`
- **借款 / 账单特征**
  - `product_code`
  - `channel_code`
  - `loan_amount`
  - `loan_term`
  - `interest_rate`
  - `mob`
  - `vintage_month`
  - `due_amount`
  - `outstanding_amount`
  - `initial_outstanding_amount`
  - `balance_segment`
- **逾期阶段**
  - `initial_dpd_bucket`
  - `dpd_bucket`
  - `dpd`
  - `dpd_tag`
- **历史还款行为**
  - `loan_status`
  - 历史窗口内的 `repay_amount` 聚合
  - 历史窗口内是否有成功还款
  - 注意：做 D7 target 时，必须只取预测时间点之前的还款行为，不能使用 D7 结果窗口内的还款流水
- **催收触达行为**
  - `action_count`
  - `connected_count`
  - `connect_rate`
  - `ptp_count`
  - `first_contact_hours`
  - `avg_call_duration_per_call`
  - `avg_call_duration_per_collector`
  - 注意：做 D7 首版 baseline 时建议先使用入案前或入案首日可得字段；若使用过程特征，需要在文档中明确 observation window
- **AI 外呼行为**
  - `ai_action_count`
  - `ai_coverage_rate`
  - `action_type = AI_OUTBOUND`
  - `line_type = AI外呼`
- **PTP / 减免 / 投诉相关**
  - `ptp_count`
  - `ptp_rate`
  - `reduction_case_count`
  - `approved_reduction_amount`
  - `reduction_usage_rate`
  - `complaint_count`
  - `complaint_rate`
  - 注意：这些字段多数是过程或结果后验指标，必须按预测时点裁剪
- **vendor / line / region / score_band**
  - `vendor_id`
  - `current_vendor_id`
  - `line_id`
  - `current_line_id`
  - `region`
  - `collector_id`
  - `score_level`
  - `postloan_c_score`
  - 评分覆盖：在 10,000 个案件样本中，`postloan_c_score` 可拼到 5,030 个案件，覆盖率 50.30%
- **时间窗口特征**
  - `case_create_time`
  - `due_date`
  - `first_due_date`
  - `score_date`
  - `stat_date`
  - 可派生：月份、星期、距到期天数、距入案天数、入案批次

### 3.2 建模字段覆盖率

- **案件级基础样本**
  - 行数：10,000
  - 唯一案件：10,000
  - 唯一客户：7,865
- **100% 可拼齐的核心字段**
  - 案件键：`case_id`、`customer_id`、`loan_id`
  - 案件属性：`case_type`、`initial_dpd_bucket`、`initial_outstanding_amount`、`balance_segment`
  - 分配属性：`current_vendor_id`、`current_line_id`
  - 借据属性：`product_code`、`channel_code`、`loan_amount`、`loan_term`、`interest_rate`、`mob`
  - 客户属性：`age_group`、`province`、`city`、`occupation_type`、`customer_segment`、`risk_level_current`
  - 动作聚合：`action_count`、`connected_count`、`ptp_count`、`ai_action_count`
  - D7 label：`is_recovered_d7`
- **非满覆盖但有价值**
  - `postloan_c_score`、`score_level`：覆盖 5,030 / 10,000 个案件，覆盖率 50.30%

### 3.3 不能直接用的字段

- **D7 target 泄漏字段**
  - `repaid_amount_d7`
  - `recovery_rate_d7`
  - `repay_time`
  - `repay_date`
  - `repay_amount`
  - D7 窗口内派生的任何还款金额、还款次数、是否还款
- **PTP target 泄漏字段**
  - 预测 PTP keep 时不能把 `ptp_fulfilled_flag`、`ptp_fulfilled_count` 作为特征
- **投诉 target 泄漏字段**
  - 预测 complaint risk 时不能把 `complaint_flag`、`complaint_count`、`complaint_level`、`complaint_time` 作为特征
- **结果后验和指标聚合字段**
  - `ads_postloan_dashboard_di` 中的结果指标不适合作为明细模型特征
  - `ads_compliance_qc_di`、`ads_reduction_roi_di` 的聚合结果只能做监控或分组分析，不宜直接进入案件级 baseline
- **P4 / 明显身份字段**
  - `customer_name`
  - `id_no`
  - `mobile_no`
  - `bank_card_no`
  - `address`
  - 本次未读取 `raw_secure` 明文字段；`synthetic_data/raw_secure` 目录当前无文件
- **不建议进入首版模型的身份替代字段**
  - `customer_id`
  - `customer_id_hash`
  - `mobile_masked`
  - `case_id`
  - `loan_id`
  - `collector_id`
  - 说明：这些字段可用于 join、切分和审计，但不应作为模型可学习特征
- **合规保护字段**
  - `sensitive_flag`
  - `protect_flag`
  - 建议只用于样本过滤、合规边界或分组评估，不作为自动提升催收强度的特征

## 4. 推荐首个 ML Demo Task

### 4.1 推荐结论

推荐首个任务选择 **A. D7 recovery prediction**。

### 4.2 推荐理由

- **为什么最适合**
  - 有明确结果口径：`metadata/metric_dictionary.yaml` 已定义 `recovery_rate_d7`
  - 有真实可构造 label：`dws_loan_status_snapshot_di.repaid_amount_d7 > 0`
  - 有客户级、案件级、借据级和过程级可拼接特征
  - 正负样本比例合理：借据级正样本率 28.02%，案件级正样本率 23.14%
  - 与 M3/M6 现有叙事一致：M3 已围绕 M1 / D7 回收率做异常和归因，M6-A/B/C/E 也以 `recovery_rate_d7` 作为策略评估目标
- **target 定义**
  - 借据级：`is_recovered_d7 = 1 if repaid_amount_d7 > 0 else 0`
  - 案件级：通过 `dim_case_loan_mapping` 把借据 D7 label 拼回 `case_id`
  - 首版建议以案件级为主，因为 M6 策略动作、触达、供应商、线路都围绕 `case_id`
- **样本粒度**
  - 首选：案件级，10,000 行
  - 备选：借据级，30,000 行
  - 说明：案件级更贴合贷后运营策略；借据级样本更多但触达和投诉等过程字段需要再拼案件映射
- **正负样本比例**
  - 案件级：正样本 2,314 / 10,000，正样本率 23.14%
  - 借据级：正样本 8,405 / 30,000，正样本率 28.02%
  - 判断：适合二分类 baseline，不需要在 D1 引入复杂采样策略
- **可用特征**
  - 客户画像：年龄段、省份、城市、职业、客户分层、当前风险等级
  - 借据属性：产品、渠道、金额、期限、利率、MOB
  - 案件属性：初始逾期阶段、初始待还金额、余额段、供应商、线路
  - 评分字段：`postloan_c_score`、`score_level`，但覆盖率只有 50.30%，首版可做可选特征或缺失值处理
  - 过程特征：首版如要使用，必须固定 observation window，避免 D7 label 泄漏
- **评价指标**
  - AUC：主指标，适合二分类排序能力展示
  - KS：风控作品集常用，适合解释分层区分度
  - PR-AUC：正样本约 23%，可作为补充
  - precision / recall：用于解释 top-risk 或 top-opportunity 分组

### 4.3 其他候选任务排序

- **B. PTP keep prediction**
  - 适合度：第二优先级
  - 原因：样本和正负比例好，但业务上依赖先发生 PTP，是二阶段模型
- **C. complaint risk prediction**
  - 适合度：第三优先级
  - 原因：投诉标签明确，但正样本率 2.19%，首版 baseline 容易被类别不平衡主导
- **D. high-risk case detection**
  - 适合度：第四优先级
  - 原因：`case_type = HIGH_RISK` 可用，但更像复现生成规则，不如 D7 回收有业务结果含义
- **E. collection channel response prediction**
  - 适合度：第五优先级
  - 原因：`connected_flag` 样本多且正样本率 34.70%，但更偏触达过程优化，不如 D7 回收能串起 M3/M6 主线

## 5. M6-D1 最小实现方案

### 5.1 前提判断

- **数据支持**
  - 当前 synthetic DWD/DWS 足够支持案件级 D7 recovery baseline
- **依赖状态**
  - `pyproject.toml` 当前没有 `scikit-learn`
  - M6-D1 如要正式训练 LogisticRegression / RandomForest / GradientBoostingClassifier，需要先获得新增 `scikit-learn` 依赖授权
  - 不建议引入 `xgboost` 或 `lightgbm`

### 5.2 建议新增文件

- **riskops/engines/model_lab/dataset.py**
  - 动作：构造案件级建模样本
  - 输入：`synthetic_data/dim`、`synthetic_data/dwd`、`synthetic_data/dws`
  - 输出：内存 DataFrame，不落真实客户数据
- **riskops/engines/model_lab/baseline.py**
  - 动作：训练 sklearn baseline、计算指标、导出解释性结果
  - 模型：首选 `LogisticRegression`
  - 备选：`RandomForestClassifier` 或 `GradientBoostingClassifier`
- **scripts/run_model_lab_baseline.py**
  - 动作：命令行入口
  - 输出：只写 `outputs/model_lab/model_metrics.json`、`outputs/model_lab/feature_importance.csv`、`outputs/model_lab/model_lab_report.md`
- **tests/test_model_lab_dataset.py**
  - 动作：验证样本粒度、target 构造、P4 字段隔离、泄漏字段排除
- **tests/test_model_lab_baseline.py**
  - 动作：验证输出结构和指标字段

### 5.3 数据集和切分

- **样本粒度**
  - 首版使用案件级，一行一个 `case_id`
- **target**
  - `is_recovered_d7 = repaid_amount_d7 > 0`
- **特征范围**
  - 首版只使用入案时已知字段：客户画像、借据属性、案件初始属性、供应商/线路、评分字段
  - 过程特征默认不进首版，除非 D1 明确加入 observation window
- **切分方式**
  - 优先时间切分：按 `case_create_time` 排序，前 70% 训练，后 30% 测试
  - 备选随机切分：只在时间字段不可用时使用，并固定 seed
- **模型**
  - 第一版：`LogisticRegression`
  - 第二步对照：`RandomForestClassifier` 或 `GradientBoostingClassifier`
  - 不保存大模型文件；如需保存，只保存小型 JSON 指标和 CSV 解释结果
- **指标**
  - `AUC`
  - `KS`
  - `PR-AUC`
  - `precision`
  - `recall`

### 5.4 输出设计

- **outputs/model_lab/model_metrics.json**
  - 内容：样本量、正负样本比例、特征数、模型名、AUC、KS、PR-AUC、precision、recall、训练/测试窗口、数据声明
- **outputs/model_lab/feature_importance.csv**
  - 内容：特征名、重要性或系数、方向
  - 限制：不包含 `customer_id`、`case_id`、`loan_id`、P4 字段
- **outputs/model_lab/model_lab_report.md**
  - 内容：业务解释、模型指标、Top features、限制说明、synthetic data disclaimer

### 5.5 测试建议

- **数据集测试**
  - 每行唯一 `case_id`
  - `is_recovered_d7` 只能取 0 / 1
  - 正样本率在合理范围内，例如 5% 到 60%
  - 输出字段不包含 P4 字段
  - 输出字段不包含 D7 泄漏字段：`repaid_amount_d7`、`recovery_rate_d7`、`repay_time`、`repay_date`、`repay_amount`
- **训练输出测试**
  - JSON 包含 `auc`、`ks`、`pr_auc`、`precision`、`recall`
  - Markdown 报告包含 synthetic data disclaimer
  - CSV 不包含身份字段和 P4 字段

## 6. 风险与边界

- **数据边界**
  - 本轮只读 synthetic data
  - 不接真实客户数据
  - 不读取或输出 raw P4 明文字段
- **建模边界**
  - 本轮不训练模型
  - 本轮不新增模型代码
  - M6-D1 也应只做离线 baseline，不做真实业务决策
- **泄漏风险**
  - D7 模型不能使用 `repaid_amount_d7`、`recovery_rate_d7`、还款流水等结果字段作为特征
  - 过程特征必须定义 observation window，否则容易把 D7 期间动作结果作为特征
- **依赖风险**
  - 当前项目依赖没有 `scikit-learn`
  - M6-D1 前需要明确是否允许新增该依赖
- **业务解释边界**
  - 所有结果必须注明 synthetic data / 合成数据
  - 模型输出只能用于作品集展示和离线实验，不代表真实策略上线依据
- **合规边界**
  - 不做自动催收
  - 不发短信、语音或 WhatsApp
  - 不接 LLM
  - 不做 Agent

## 7. 是否建议进入 M6-D1

建议进入 M6-D1，但范围应收窄为 **D7 recovery prediction baseline**。

- **进入理由**
  - 有案件级和借据级样本
  - 有可构造 D7 target
  - 有足够的非泄漏特征
  - 正负样本比例适合 baseline
  - 与 M3 D7 attribution 和 M6 strategy evaluation 主线一致
- **进入条件**
  - 用户授权是否新增 `scikit-learn`
  - M6-D1 明确只做 synthetic data offline baseline
  - 首版不用过程特征，或明确 observation window
  - 不保存大模型文件，不输出明细身份字段
- **不建议的方向**
  - 不做 score simulation stub
  - 不做 LLM / Agent
  - 不做自动催收动作
  - 不把 ADS 聚合指标硬拼成明细模型特征

## 8. M6-D1 D7 Recovery Prediction Baseline

### 8.1 实现范围

- **任务分类**：真实可跑的 ML baseline，不是 score simulation，也不是规则假模型。
- **样本粒度**：借据级 `loan_id`。
- **主表**：`synthetic_data/dws/dws_loan_status_snapshot_di.parquet`。
- **拼接表**：`dim_loan`、`dim_customer`、`ods_postloan_c_score`、`dim_case_loan_mapping`、`dim_case`。
- **输出目录**：`outputs/model_lab/ml_baseline/`。

### 8.2 Target 定义

- **target 字段**：`is_recovered_d7`。
- **构造逻辑**：`1 if repaid_amount_d7 > 0 else 0`。
- **评估口径**：`repaid_amount_d7` 和 `recovery_rate_d7` 只用于 target / 评估，不进入模型特征。

### 8.3 泄漏与隐私边界

- **泄漏字段排除**：`repaid_amount_d7`、`recovery_rate_d7`、`repay_amount`、`repay_date`、`repay_time`、`loan_status`、`case_status`、`ptp_fulfilled_flag`、`reduction_recovery_rate`。
- **身份字段排除**：`loan_id`、`customer_id`、`case_id`、`customer_id_hash`、`mobile_masked`、`id_card`、`phone_no`、`customer_name`。
- **案件拼接控制**：只保留每个 `loan_id` 的一条主借据案件映射，避免一对多样本膨胀。
- **作业分配字段说明**：`current_vendor_id` 和 `current_line_id` 是合成作业分配线索，不是客户本体风险因素。
- **合成标签说明**：`protect_flag` 和 `sensitive_flag` 是合成标签，不是真实敏感身份字段。

### 8.4 Baseline 结果快照

- **模型类型**：sklearn LogisticRegression + ColumnTransformer Pipeline。
- **预处理**：数值变量使用 median impute + StandardScaler；类别变量使用 constant impute + OneHotEncoder。
- **切分方式**：`train_test_split(test_size=0.25, random_state=20260521, stratify=y)`。
- **默认运行命令**：`python scripts/run_ml_baseline.py`。
- **报告文件**：`outputs/model_lab/ml_baseline/ml_baseline_report.md`。

## 9. M6-D2 Feature Engineering & Model Diagnostics

### 9.1 实现范围

- **任务分类**：在 M6-D1 baseline 上做轻量特征增强和诊断，不重做 target、不改数据生成逻辑。
- **新增特征来源**：继续只读 `synthetic_data/` 下的合成数据表。
- **模型范围**：保留 LogisticRegression baseline，新增 RandomForestClassifier 离线对照，不保存模型文件。
- **输出目录**：继续写入 `outputs/model_lab/ml_baseline/`。

### 9.2 业务特征增强

- **评分特征**：`postloan_c_score`、`score_level`。
- **案件初始特征**：`initial_dpd_bucket`、`initial_outstanding_amount`、`balance_segment`。
- **分配上下文特征**：`current_vendor_id`、`current_line_id`。
- **合成治理标签**：`protect_flag`、`sensitive_flag`。
- **近期过程窗口特征**：`action_count`、`connected_count`、`ai_action_count`、`ptp_count`、`ptp_fulfilled_count`、`complaint_count`、`connect_rate`、`ai_coverage_rate`、`ptp_fulfillment_rate`。

### 9.3 诊断边界

- **vintage_month 诊断**：报告 top features 中 `vintage_month` 的数量占比和重要性占比。
- **artifact warning**：如果 `vintage_month` 在 top features 中占比过高，标记为可能的 synthetic batch/time artifact。
- **业务解释边界**：`vintage_month` 可用于 demo 诊断，但不应作为最终业务解释核心。
- **过程窗口限制**：近期过程特征按 `case_create_date` 截止的 7 天窗口聚合；如果上游动作时间与观察点不严格，报告中按 diagnostic-only limitation 处理。

### 9.4 泄漏控制

- **仍排除 D7 结果字段**：`repaid_amount_d7`、`recovery_rate_d7`。
- **仍排除还款流水字段**：`repay_amount`、`repay_date`、`repay_time`。
- **仍排除身份字段**：`loan_id`、`customer_id`、`case_id`、`customer_id_hash`、`mobile_masked` 和 P4 明文字段。
- **不接入项**：不接真实数据、不接 LLM、不做 Agent、不做自动催收。
