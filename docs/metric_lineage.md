# 指标血缘

> 由 `metadata/metric_lineage.yaml` 自动渲染。

- 阶段：M2
- 范围：Phase 1 metric lineage from ADS to DWS, DWD, and ODS

## due_account_count
- 中文名：到期账户数
- ADS：ads_postloan_dashboard_di
- DWS：dws_customer_status_snapshot_di
- DWD：dwd_due_plan_detail_di
- ODS：ods_repayment_plan

## due_loan_count
- 中文名：到期借据数
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di
- ODS：ods_repayment_plan

## due_total_amount
- 中文名：到期应还金额
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di
- ODS：ods_repayment_plan

## collection_entry_rate
- 中文名：入催率
- ADS：ads_postloan_dashboard_di
- DWS：dws_case_status_snapshot_di
- DWD：dwd_due_plan_detail_di
- ODS：ods_repayment_plan, ods_case_daily_snapshot

## recovery_rate_d7
- 中文名：D7 回收率
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di, dwd_repayment_detail_di
- ODS：ods_repayment_plan, ods_repayment_detail

## recovery_rate_d15
- 中文名：D15 回收率
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di, dwd_repayment_detail_di
- ODS：ods_repayment_plan, ods_repayment_detail

## recovery_rate_d30
- 中文名：D30 回收率
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di, dwd_repayment_detail_di
- ODS：ods_repayment_plan, ods_repayment_detail

## m1_recovery_rate
- 中文名：M1 回收率
- ADS：ads_postloan_dashboard_di
- DWS：dws_loan_status_snapshot_di
- DWD：dwd_due_plan_detail_di, dwd_repayment_detail_di
- ODS：ods_repayment_plan, ods_repayment_detail

## call_coverage_rate
- 中文名：拨打覆盖率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di, dws_case_status_snapshot_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action, ods_case_daily_snapshot

## valid_coverage_rate
- 中文名：有效覆盖率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di, dws_case_status_snapshot_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action, ods_call_record

## connect_rate
- 中文名：接通率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action

## valid_contact_rate
- 中文名：有效沟通率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action, ods_call_record

## first_contact_hours
- 中文名：首触达时效
- ADS：ads_collector_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action, ods_assignment_decision_log

## ptp_rate
- 中文名：PTP 率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action

## ptp_keep_rate
- 中文名：PTP 履约率
- ADS：ads_vendor_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action

## avg_call_duration_per_call
- 中文名：单通平均时长
- ADS：ads_collector_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_call_record

## avg_call_duration_per_collector
- 中文名：人均日通话时长
- ADS：ads_collector_performance_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_call_record

## collector_productivity
- 中文名：作业人效
- ADS：ads_collector_performance_di
- DWS：dws_case_status_snapshot_di
- DWD：dwd_repayment_detail_di
- ODS：ods_repayment_detail

## complaint_rate
- 中文名：投诉率
- ADS：ads_compliance_qc_di
- DWS：dws_case_status_snapshot_di
- DWD：dwd_complaint_detail_di
- ODS：ods_complaint

## complaint_per_10k_cases
- 中文名：万案投诉率
- ADS：ads_compliance_qc_di
- DWS：dws_case_status_snapshot_di
- DWD：dwd_complaint_detail_di
- ODS：ods_complaint

## risk_phrase_hit_rate
- 中文名：高风险话术命中率
- ADS：ads_compliance_qc_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action

## qa_fail_rate
- 中文名：质检不合格率
- ADS：ads_compliance_qc_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_complaint_detail_di, dwd_collection_action_detail_di
- ODS：ods_complaint, ods_collection_action

## over_frequency_contact_rate
- 中文名：超频触达率
- ADS：ads_compliance_qc_di
- DWS：dws_collection_process_wide_di
- DWD：dwd_collection_action_detail_di
- ODS：ods_collection_action

## reduction_usage_rate
- 中文名：减免使用率
- ADS：ads_reduction_roi_di
- DWS：dws_case_status_snapshot_di
- DWD：无
- ODS：ods_reduction_application

## reduction_recovery_rate
- 中文名：减免回收率
- ADS：ads_reduction_roi_di
- DWS：dws_case_status_snapshot_di
- DWD：dwd_repayment_detail_di
- ODS：ods_reduction_application, ods_repayment_detail

## reduction_roi
- 中文名：减免 ROI
- ADS：ads_reduction_roi_di
- DWS：dws_case_status_snapshot_di
- DWD：dwd_repayment_detail_di
- ODS：ods_reduction_application, ods_repayment_detail
