# M3 异常归因结构化报告

> Demo Disclaimer: 本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。

## 1. 异常总览

- 异常数量：7
- high：5
- medium：2
- low：0
- 基线窗口：2026-03-20~2026-04-18
- 最近窗口：2026-04-19~2026-05-18

## 2. 归因目标异常

- 归因目标异常已在高优先级异常列表中展示。

## 3. 高优先级异常列表

### 1. M1 回收率（m1_recovery_rate）
- severity：high
- dimension：overall=ALL
- baseline：24.57%
- recent：10.27%
- change：-14.30% / -58.20%
- evidence_table：ads_postloan_dashboard_di
- explanation：最近窗口均值 10.27% 低于基线 24.57%，变化 -14.30%。
- recommended_next_step：进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。

### 2. 接通率（connect_rate）
- severity：high
- dimension：vendor_id=V_B
- baseline：34.25%
- recent：27.53%
- change：-6.72% / -19.62%
- evidence_table：ads_vendor_performance_di
- explanation：供应商 B 最近接通率 27.53%，低于基线 34.25%。
- recommended_next_step：下钻供应商 B 的线路、催员和触达时段，验证执行资源或号码质量问题。

### 3. 华东线路人均案量（avg_case_per_collector）
- severity：high
- dimension：region=华东
- baseline：13.54
- recent：19.10
- change：5.57 / 41.13%
- evidence_table：dws_vendor_line_capacity_di
- explanation：华东线路人均案量从 13.54 升至 19.10，产能压力上升。
- recommended_next_step：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。

### 4. 高余额高风险客群占比（high_balance_high_risk_share）
- severity：high
- dimension：overall=ALL
- baseline：12.00%
- recent：20.00%
- change：8.00% / 66.68%
- evidence_table：dws_customer_status_snapshot_di
- explanation：高余额高风险客群占比从 12.00% 升至 20.00%。
- recommended_next_step：进入后续归因阶段后拆分余额段、risk_level 和入案批次，识别结构变化贡献。

### 5. AI 外呼覆盖率（ai_call_coverage）
- severity：high
- dimension：action_type=AI_OUTBOUND
- baseline：30.25%
- recent：17.75%
- change：-12.50% / -41.32%
- evidence_table：dws_collection_process_wide_di
- explanation：AI 外呼覆盖率从 30.25% 降至 17.75%。
- recommended_next_step：检查 AI 外呼线路容量、分案策略和人工替代触达占比。

## 4. M1 D7 回收率下降归因摘要

- target_metric：D7 回收率（recovery_rate_d7）
- target_anomaly_id：M3A-m1_recovery_rate-overall-ALL
- attribution_count：10
- 主因：product_code=P_CONS
- 贡献度：5.59%
- 业务解释：P_CONS 分组的回收率下降对整体异常有可量化贡献。

## 5. Top 5 drivers

### 1. product_code=P_CONS
- contribution_score：5.59%
- baseline：33.40%
- recent：11.30%
- confidence：medium
- business_interpretation：P_CONS 分组的回收率下降对整体异常有可量化贡献。
- recommended_action：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。

### 2. balance_segment=NORMAL
- contribution_score：5.28%
- baseline：23.45%
- recent：10.90%
- confidence：medium
- business_interpretation：NORMAL 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。
- recommended_action：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

### 3. risk_level=high
- contribution_score：4.94%
- baseline：23.56%
- recent：5.44%
- confidence：medium
- business_interpretation：high 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。
- recommended_action：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

### 4. channel_code=ECOM
- contribution_score：4.90%
- baseline：28.66%
- recent：6.90%
- confidence：medium
- business_interpretation：ECOM 分组的回收率下降对整体异常有可量化贡献。
- recommended_action：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。

### 5. score_band=B
- contribution_score：4.18%
- baseline：24.96%
- recent：9.56%
- confidence：medium
- business_interpretation：B 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。
- recommended_action：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

## 6. 每个 driver 的 evidence

### 1. product_code=P_CONS
- segment_delta：baseline 33.40%，recent 11.30%，delta -22.10%，baseline_loan_count 135，recent_loan_count 138，recent_weight 40.26%。
- driver_linkage：接通率（connect_rate），baseline 35.71%，recent 41.67%，delta 5.95%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 21.43%，recent 16.67%，delta -4.76%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 78.57%，recent 83.33%，delta 4.76%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 2. balance_segment=NORMAL
- segment_delta：baseline 23.45%，recent 10.90%，delta -12.55%，baseline_loan_count 314，recent_loan_count 252，recent_weight 67.00%。
- driver_linkage：接通率（connect_rate），baseline 41.94%，recent 52.17%，delta 10.24%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 22.58%，recent 13.04%，delta -9.54%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 77.42%，recent 86.96%，delta 9.54%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 25.00%，recent 66.67%，delta 41.67%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 3. risk_level=high
- segment_delta：baseline 23.56%，recent 5.44%，delta -18.13%，baseline_loan_count 41，recent_loan_count 92，recent_weight 43.36%。
- driver_linkage：接通率（connect_rate），baseline 50.00%，recent 62.50%，delta 12.50%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 25.00%，recent 37.50%，delta 12.50%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 75.00%，recent 62.50%，delta -12.50%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 100.00%，delta 100.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 4. channel_code=ECOM
- segment_delta：baseline 28.66%，recent 6.90%，delta -21.76%，baseline_loan_count 125，recent_loan_count 131，recent_weight 35.82%。
- driver_linkage：接通率（connect_rate），baseline 54.55%，recent 50.00%，delta -4.55%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 18.18%，recent 25.00%，delta 6.82%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 81.82%，recent 75.00%，delta -6.82%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 50.00%，recent 0.00%，delta -50.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

### 5. score_band=B
- segment_delta：baseline 24.96%，recent 9.56%，delta -15.40%，baseline_loan_count 90，recent_loan_count 79，recent_weight 43.19%。
- driver_linkage：接通率（connect_rate），baseline 37.50%，recent 33.33%，delta -4.17%。
- driver_linkage：AI 外呼覆盖率（ai_call_coverage），baseline 12.50%，recent 8.33%，delta -4.17%。
- driver_linkage：人工触达占比（manual_call_coverage），baseline 87.50%，recent 91.67%，delta 4.17%。
- driver_linkage：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- driver_linkage：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

## 7. process evidence / driver_linkage

- product_code=P_CONS：接通率（connect_rate），baseline 35.71%，recent 41.67%，delta 5.95%。
- product_code=P_CONS：AI 外呼覆盖率（ai_call_coverage），baseline 21.43%，recent 16.67%，delta -4.76%。
- product_code=P_CONS：人工触达占比（manual_call_coverage），baseline 78.57%，recent 83.33%，delta 4.76%。
- product_code=P_CONS：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- product_code=P_CONS：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- product_code=P_CONS：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- balance_segment=NORMAL：接通率（connect_rate），baseline 41.94%，recent 52.17%，delta 10.24%。
- balance_segment=NORMAL：AI 外呼覆盖率（ai_call_coverage），baseline 22.58%，recent 13.04%，delta -9.54%。
- balance_segment=NORMAL：人工触达占比（manual_call_coverage），baseline 77.42%，recent 86.96%，delta 9.54%。
- balance_segment=NORMAL：PTP 履约率（ptp_keep_rate），baseline 25.00%，recent 66.67%，delta 41.67%。
- balance_segment=NORMAL：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- balance_segment=NORMAL：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- risk_level=high：接通率（connect_rate），baseline 50.00%，recent 62.50%，delta 12.50%。
- risk_level=high：AI 外呼覆盖率（ai_call_coverage），baseline 25.00%，recent 37.50%，delta 12.50%。
- risk_level=high：人工触达占比（manual_call_coverage），baseline 75.00%，recent 62.50%，delta -12.50%。
- risk_level=high：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 100.00%，delta 100.00%。
- risk_level=high：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- risk_level=high：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- channel_code=ECOM：接通率（connect_rate），baseline 54.55%，recent 50.00%，delta -4.55%。
- channel_code=ECOM：AI 外呼覆盖率（ai_call_coverage），baseline 18.18%，recent 25.00%，delta 6.82%。
- channel_code=ECOM：人工触达占比（manual_call_coverage），baseline 81.82%，recent 75.00%，delta -6.82%。
- channel_code=ECOM：PTP 履约率（ptp_keep_rate），baseline 50.00%，recent 0.00%，delta -50.00%。
- channel_code=ECOM：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- channel_code=ECOM：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=B：接通率（connect_rate），baseline 37.50%，recent 33.33%，delta -4.17%。
- score_band=B：AI 外呼覆盖率（ai_call_coverage），baseline 12.50%，recent 8.33%，delta -4.17%。
- score_band=B：人工触达占比（manual_call_coverage），baseline 87.50%，recent 91.67%，delta 4.17%。
- score_band=B：PTP 履约率（ptp_keep_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=B：减免使用率（reduction_usage_rate），baseline 0.00%，recent 0.00%，delta 0.00%。
- score_band=B：投诉率（complaint_rate），baseline 0.00%，recent 0.00%，delta 0.00%。

## 8. 业务建议

- product_code=P_CONS：继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- balance_segment=NORMAL：对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- m1_recovery_rate:overall=ALL：进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。
- connect_rate:vendor_id=V_B：下钻供应商 B 的线路、催员和触达时段，验证执行资源或号码质量问题。
- avg_case_per_collector:region=华东：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- high_balance_high_risk_share:overall=ALL：进入后续归因阶段后拆分余额段、risk_level 和入案批次，识别结构变化贡献。
- ai_call_coverage:action_type=AI_OUTBOUND：检查 AI 外呼线路容量、分案策略和人工替代触达占比。

## 9. 数据局限

- synthetic_data：本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。
- attribution_note：按 M1 dpd_bucket 过滤后解释 recovery_rate_d7，未重新定义指标口径。
- method_boundary：贡献度为各维度切片的边际贡献，跨维度可能重叠，不可直接相加为整体下降的解释比例。

## 10. 下一步建议

- 继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- 对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- 进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。
- 下钻供应商 B 的线路、催员和触达时段，验证执行资源或号码质量问题。
- 下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- 进入后续归因阶段后拆分余额段、risk_level 和入案批次，识别结构变化贡献。
- 检查 AI 外呼线路容量、分案策略和人工替代触达占比。
