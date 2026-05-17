# M3-A 异常检测结果

- 检测异常数：8
- high：6
- medium：2
- low：0

## Top anomalies

### 1. 万案投诉率
- metric_code：complaint_per_10k_cases
- severity：high
- dimension：template_id=TPL_RISK_NOTICE
- baseline_value：54.204512
- recent_value：122.478386
- change：68.273874 / 125.96%
- evidence_table：dwd_collection_action_detail_di+dwd_complaint_detail_di
- explanation：TPL_RISK_NOTICE 最近万案投诉率为 122.48，约为全模板均值 54.20 的 2.26 倍。
- recommended_next_step：下钻该模板的发送供应商、发送时段、投诉等级和具体话术，进入合规复核。

### 2. 华东线路人均案量
- metric_code：avg_case_per_collector
- severity：high
- dimension：region=华东
- baseline_value：13.535364
- recent_value：19.102200
- change：5.566836 / 41.13%
- evidence_table：dws_vendor_line_capacity_di
- explanation：华东线路人均案量从 13.54 升至 19.10，产能压力上升。
- recommended_next_step：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。

### 3. AI 外呼覆盖率
- metric_code：ai_call_coverage
- severity：high
- dimension：action_type=AI_OUTBOUND
- baseline_value：0.300850
- recent_value：0.177833
- change：-0.123017 / -40.89%
- evidence_table：dws_collection_process_wide_di
- explanation：AI 外呼覆盖率从 30.09% 降至 17.78%。
- recommended_next_step：检查 AI 外呼线路容量、分案策略和人工替代触达占比。

### 4. 高余额高风险客群占比
- metric_code：high_balance_high_risk_share
- severity：high
- dimension：balance_segment+risk_level=HIGH+C/D
- baseline_value：0.005902
- recent_value：0.007522
- change：0.001620 / 27.45%
- evidence_table：dws_customer_status_snapshot_di
- explanation：高余额高风险客群占比从 0.59% 升至 0.75%。
- recommended_next_step：进入 M3-B 后拆分余额段、risk_level 和入案批次，识别结构变化贡献。

### 5. 减免使用率
- metric_code：reduction_usage_rate
- severity：high
- dimension：overall=ALL
- baseline_value：0.000625
- recent_value：0.000455
- change：-0.000170 / -27.17%
- evidence_table：ads_reduction_roi_di
- explanation：减免使用率从 0.06% 降至 0.05%。
- recommended_next_step：下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。
