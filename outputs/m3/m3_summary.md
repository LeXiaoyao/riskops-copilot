# M3 异常归因结构化报告

> Demo Disclaimer: 本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。

## 1. 异常总览

- 异常数量：8
- high：6
- medium：2
- low：0
- 基线窗口：2026-03-19~2026-04-17
- 最近窗口：2026-04-18~2026-05-17

## 2. 归因目标异常

- anomaly_id：M3A-m1_recovery_rate-overall-ALL
- metric：M1 回收率（m1_recovery_rate）
- severity：medium
- dimension：overall=ALL
- baseline：19.43%
- recent：15.30%
- change：-4.13% / -21.27%
- evidence_table：ads_postloan_dashboard_di
- explanation：最近窗口均值 15.30% 低于基线 19.43%，变化 -4.13%。
- recommended_next_step：进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。

## 3. 高优先级异常列表

### 1. 华东线路人均案量（avg_case_per_collector）
- severity：high
- dimension：region=华东
- baseline：13.54
- recent：19.10
- change：5.57 / 41.13%
- evidence_table：dws_vendor_line_capacity_di
- explanation：华东线路人均案量从 13.54 升至 19.10，产能压力上升。
- recommended_next_step：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。

### 2. 高余额高风险客群占比（high_balance_high_risk_share）
- severity：high
- dimension：balance_segment+risk_level=HIGH+C/D
- baseline：0.59%
- recent：0.75%
- change：0.16% / 27.45%
- evidence_table：dws_customer_status_snapshot_di
- explanation：高余额高风险客群占比从 0.59% 升至 0.75%。
- recommended_next_step：进入 M3-B 后拆分余额段、risk_level 和入案批次，识别结构变化贡献。

### 3. AI 外呼覆盖率（ai_call_coverage）
- severity：high
- dimension：action_type=AI_OUTBOUND
- baseline：30.09%
- recent：17.78%
- change：-12.30% / -40.89%
- evidence_table：dws_collection_process_wide_di
- explanation：AI 外呼覆盖率从 30.09% 降至 17.78%。
- recommended_next_step：检查 AI 外呼线路容量、分案策略和人工替代触达占比。

### 4. 减免使用率（reduction_usage_rate）
- severity：high
- dimension：overall=ALL
- baseline：0.06%
- recent：0.05%
- change：-0.02% / -27.17%
- evidence_table：ads_reduction_roi_di
- explanation：减免使用率从 0.06% 降至 0.05%。
- recommended_next_step：下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。

### 5. PTP 履约率（ptp_keep_rate）
- severity：high
- dimension：overall=ALL
- baseline：49.68%
- recent：43.58%
- change：-6.10% / -12.28%
- evidence_table：ads_postloan_dashboard_di
- explanation：PTP 履约率从 49.68% 降至 43.58%。
- recommended_next_step：下钻承诺还款客户的风险等级、余额段、催员和减免使用情况。

### 6. 万案投诉率（complaint_per_10k_cases）
- severity：high
- dimension：template_id=TPL_RISK_NOTICE
- baseline：54.20
- recent：122.48
- change：68.27 / 125.96%
- evidence_table：dwd_collection_action_detail_di+dwd_complaint_detail_di
- explanation：TPL_RISK_NOTICE 最近万案投诉率为 122.48，约为全模板均值 54.20 的 2.26 倍。
- recommended_next_step：下钻该模板的发送供应商、发送时段、投诉等级和具体话术，进入合规复核。

## 4. M1 D7 回收率下降归因摘要

- target_metric：D7 回收率（recovery_rate_d7）
- target_anomaly_id：M3A-m1_recovery_rate-overall-ALL
- attribution_count：10
- 主因：channel_code=ECOM
- 贡献度：15.26%
- 业务解释：ECOM 分组的回收率下降对整体异常有可量化贡献。

## 5. Top 5 drivers

### 1. channel_code=ECOM
- contribution_score：15.26%
- baseline：23.90%
- recent：6.29%
- confidence：medium
- business_interpretation：ECOM 分组的回收率下降对整体异常有可量化贡献。
- recommended_action：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。

### 2. province=山东
- contribution_score：6.52%
- baseline：29.45%
- recent：12.73%
- confidence：medium
- business_interpretation：山东 分组的回收率下降对整体异常有可量化贡献。
- recommended_action：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。

### 3. score_band=D
- contribution_score：5.75%
- baseline：17.83%
- recent：5.93%
- confidence：medium
- business_interpretation：D 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。
- recommended_action：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

### 4. province=上海
- contribution_score：4.42%
- baseline：22.35%
- recent：7.16%
- confidence：medium
- business_interpretation：上海 分组的回收率下降对整体异常有可量化贡献。
- recommended_action：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。

### 5. score_band=A
- contribution_score：4.04%
- baseline：36.42%
- recent：19.88%
- confidence：medium
- business_interpretation：A 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。
- recommended_action：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

## 6. 每个 driver 的 evidence

### 1. channel_code=ECOM
- segment_delta：baseline 23.90%，recent 6.29%，delta -17.61%，baseline_loan_count 125，recent_loan_count 131，recent_weight 35.47%。
- driver_linkage：接通率（connect_rate），baseline 23.08%，recent 35.71%，delta 12.64%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 46.15%，recent 7.14%，delta -39.01%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 53.85%，recent 92.86%，delta 39.01%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 2. province=山东
- segment_delta：baseline 29.45%，recent 12.73%，delta -16.73%，baseline_loan_count 50，recent_loan_count 58，recent_weight 15.97%。
- driver_linkage：接通率（connect_rate），baseline 50.00%，recent 50.00%，delta 0.00%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 100.00%，recent 0.00%，delta -100.00%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 0.00%，recent 100.00%，delta 100.00%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 3. score_band=D
- segment_delta：baseline 17.83%，recent 5.93%，delta -11.90%，baseline_loan_count 25，recent_loan_count 35，recent_weight 19.80%。
- driver_linkage：接通率（connect_rate），baseline 50.00%，recent 0.00%，delta -50.00%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 100.00%，recent 100.00%，delta 0.00%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 4. province=上海
- segment_delta：baseline 22.35%，recent 7.16%，delta -15.19%，baseline_loan_count 62，recent_loan_count 49，recent_weight 11.93%。
- driver_linkage：接通率（connect_rate），baseline 44.44%，recent 25.00%，delta -19.44%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 33.33%，recent 0.00%，delta -33.33%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 66.67%，recent 100.00%，delta 33.33%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 5. score_band=A
- segment_delta：baseline 36.42%，recent 19.88%，delta -16.54%，baseline_loan_count 16，recent_loan_count 21，recent_weight 10.01%。
- driver_linkage：接通率（connect_rate），baseline 50.00%，recent 100.00%，delta 50.00%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 25.00%，recent 0.00%，delta -25.00%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 75.00%，recent 100.00%，delta 25.00%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

## 7. process evidence / driver_linkage

- channel_code=ECOM：接通率（connect_rate），baseline 23.08%，recent 35.71%，delta 12.64%。
- channel_code=ECOM：AI 外呼覆盖率（ai_call_coverage），baseline 46.15%，recent 7.14%，delta -39.01%。
- channel_code=ECOM：人工触达占比（manual_call_coverage），baseline 53.85%，recent 92.86%，delta 39.01%。
- channel_code=ECOM：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- channel_code=ECOM：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- channel_code=ECOM：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- province=山东：接通率（connect_rate），baseline 50.00%，recent 50.00%，delta 0.00%。
- province=山东：AI 外呼覆盖率（ai_call_coverage），baseline 100.00%，recent 0.00%，delta -100.00%。
- province=山东：人工触达占比（manual_call_coverage），baseline 0.00%，recent 100.00%，delta 100.00%。
- province=山东：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- province=山东：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- province=山东：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=D：接通率（connect_rate），baseline 50.00%，recent 0.00%，delta -50.00%。
- score_band=D：AI 外呼覆盖率（ai_call_coverage），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=D：人工触达占比（manual_call_coverage），baseline 100.00%，recent 100.00%，delta 0.00%。
- score_band=D：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=D：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=D：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- province=上海：接通率（connect_rate），baseline 44.44%，recent 25.00%，delta -19.44%。
- province=上海：AI 外呼覆盖率（ai_call_coverage），baseline 33.33%，recent 0.00%，delta -33.33%。
- province=上海：人工触达占比（manual_call_coverage），baseline 66.67%，recent 100.00%，delta 33.33%。
- province=上海：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- province=上海：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- province=上海：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=A：接通率（connect_rate），baseline 50.00%，recent 100.00%，delta 50.00%。
- score_band=A：AI 外呼覆盖率（ai_call_coverage），baseline 25.00%，recent 0.00%，delta -25.00%。
- score_band=A：人工触达占比（manual_call_coverage），baseline 75.00%，recent 100.00%，delta 25.00%。
- score_band=A：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=A：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=A：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

## 8. 业务建议

- channel_code=ECOM：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- score_band=D：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- avg_case_per_collector:region=华东：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- high_balance_high_risk_share:balance_segment+risk_level=HIGH+C/D：进入 M3-B 后拆分余额段、risk_level 和入案批次，识别结构变化贡献。
- ai_call_coverage:action_type=AI_OUTBOUND：检查 AI 外呼线路容量、分案策略和人工替代触达占比。
- reduction_usage_rate:overall=ALL：下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。
- ptp_keep_rate:overall=ALL：下钻承诺还款客户的风险等级、余额段、催员和减免使用情况。
- complaint_per_10k_cases:template_id=TPL_RISK_NOTICE：下钻该模板的发送供应商、发送时段、投诉等级和具体话术，进入合规复核。

## 9. 数据局限

- synthetic_data：本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。
- attribution_note：按 M1 dpd_bucket 过滤后解释 recovery_rate_d7，未重新定义指标口径。
- method_boundary：贡献度为各维度切片的边际贡献，跨维度可能重叠，不可直接相加为整体下降的解释比例。

## 10. 下一步建议

- 继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- 对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- 下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- 进入 M3-B 后拆分余额段、risk_level 和入案批次，识别结构变化贡献。
- 检查 AI 外呼线路容量、分案策略和人工替代触达占比。
- 下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。
- 下钻承诺还款客户的风险等级、余额段、催员和减免使用情况。
- 下钻该模板的发送供应商、发送时段、投诉等级和具体话术，进入合规复核。
