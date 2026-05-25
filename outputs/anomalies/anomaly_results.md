# M3-A 异常检测结果

- 检测异常数：6
- high：4
- medium：2
- low：0

## Top anomalies

### 1. M1 回收率
- metric_code：m1_recovery_rate
- severity：high
- dimension：overall=ALL
- baseline_value：0.245676
- recent_value：0.102698
- change：-0.142978 / -58.20%
- evidence_table：ads_postloan_dashboard_di
- explanation：最近窗口均值 10.27% 低于基线 24.57%，变化 -14.30%。
- recommended_next_step：进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。

### 2. AI 外呼覆盖率
- metric_code：ai_call_coverage
- severity：high
- dimension：action_type=AI_OUTBOUND
- baseline_value：0.302521
- recent_value：0.177509
- change：-0.125011 / -41.32%
- evidence_table：dws_collection_process_wide_di
- explanation：AI 外呼覆盖率从 30.25% 降至 17.75%。
- recommended_next_step：检查 AI 外呼线路容量、分案策略和人工替代触达占比。

### 3. 华东线路人均案量
- metric_code：avg_case_per_collector
- severity：high
- dimension：region=华东
- baseline_value：13.535364
- recent_value：19.102200
- change：5.566836 / 41.13%
- evidence_table：dws_vendor_line_capacity_di
- explanation：华东线路人均案量从 13.54 升至 19.10，产能压力上升。
- recommended_next_step：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。

### 4. 接通率
- metric_code：connect_rate
- severity：high
- dimension：vendor_id=V_B
- baseline_value：0.342522
- recent_value：0.275303
- change：-0.067219 / -19.62%
- evidence_table：ads_vendor_performance_di
- explanation：供应商 B 最近接通率 27.53%，低于基线 34.25%。
- recommended_next_step：下钻供应商 B 的线路、催员和触达时段，验证执行资源或号码质量问题。

### 5. 减免使用率
- metric_code：reduction_usage_rate
- severity：medium
- dimension：overall=ALL
- baseline_value：0.000566
- recent_value：0.000434
- change：-0.000132 / -23.30%
- evidence_table：ads_reduction_roi_di
- explanation：减免使用率从 0.06% 降至 0.04%。
- recommended_next_step：下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。
