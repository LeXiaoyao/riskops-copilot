# 数据血缘

> M1 仅记录血缘占位，不实现 M2 指标计算引擎。

- 阶段：M1
- 范围：lineage placeholders only; metric calculation lands in M2

## m1_recovery_rate_d7
- 中文名：M1 D7 回收率
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di, dwd_repayment_detail_di
- ODS：ods_repayment_plan, ods_repayment_detail

## connect_rate
- 中文名：接通率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action

## complaint_rate
- 中文名：投诉率
- ADS：ads_compliance_qc_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_complaint_detail_di
- ODS：ods_complaint, ods_sms_send_log
