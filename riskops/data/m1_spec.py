"""M1 data foundation metadata specification."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]

DIM_TABLES = [
    ("dim_customer", "客户维表", "customer_id", "customer_id", "客户基础信息"),
    ("dim_loan", "借据维表", "loan_id", "loan_id", "借据基础属性"),
    ("dim_case", "案件维表", "case_id", "case_id", "催收案件主数据"),
    ("dim_case_loan_mapping", "案件借据映射维表", "mapping_id", "mapping_id", "案件与借据多对多映射"),
    ("dim_product", "产品维表", "product_code", "product_code", "产品主数据"),
    ("dim_channel", "渠道维表", "channel_code", "channel_code", "渠道主数据"),
    ("dim_vendor", "供应商维表", "vendor_id", "vendor_id", "供应商主数据"),
    ("dim_collection_line", "催收线路维表", "line_id", "line_id", "催收线路主数据"),
    ("dim_collector", "催员维表", "collector_id", "collector_id", "催员主数据"),
    ("dim_strategy", "策略维表", "strategy_id", "strategy_id", "策略主数据"),
]

ODS_TABLES = [
    ("ods_repayment_plan", "还款计划", "plan_id", "plan_id", "每笔借据每期应还计划"),
    ("ods_repayment_detail", "还款流水", "repay_id", "repay_id", "真实还款流水"),
    ("ods_loan_daily_snapshot", "借据日切", "stat_date+loan_id", ["stat_date", "loan_id"], "借据状态日切片"),
    ("ods_case_daily_snapshot", "案件日切", "stat_date+case_id", ["stat_date", "case_id"], "案件状态日切片"),
    ("ods_customer_daily_snapshot", "客户日切", "stat_date+customer_id", ["stat_date", "customer_id"], "客户状态日切片"),
    ("ods_case_flow", "案件流转", "flow_id", "flow_id", "案件状态流转流水"),
    ("ods_assignment_decision_log", "分案决策流水", "decision_id", "decision_id", "分案决策日志"),
    ("ods_postloan_c_score", "贷后 C 卡分", "score_id", "score_id", "贷后评分历史快照"),
    ("ods_collection_note", "催记", "note_id", "note_id", "催员作业文本记录"),
    ("ods_collection_action", "催收动作", "action_id", "action_id", "拨打、短信、AI 外呼等触达动作"),
    ("ods_call_record", "外呼记录", "call_id", "call_id", "外呼结果与录音转写引用"),
    ("ods_sms_send_log", "短信发送日志", "message_id", "message_id", "短信和语音发送流水"),
    ("ods_reduction_application", "减免申请", "reduction_id", "reduction_id", "减免申请与审批记录"),
    ("ods_complaint", "投诉记录", "complaint_id", "complaint_id", "投诉与合规事件记录"),
]

DWD_TABLES = [
    ("dwd_due_plan_detail_di", "到期计划明细", "stat_date+plan_id", ["stat_date", "plan_id"], "清洗后的到期计划明细"),
    ("dwd_repayment_detail_di", "回款明细事实", "repay_id", "repay_id", "清洗后的回款事实"),
    ("dwd_collection_action_detail_di", "催收动作明细", "action_id", "action_id", "清洗后的催收动作事实"),
    ("dwd_case_flow_detail_di", "案件流转明细", "flow_id", "flow_id", "清洗后的案件流转事实"),
    ("dwd_complaint_detail_di", "投诉明细", "complaint_id", "complaint_id", "清洗后的投诉事实"),
]

DWS_TABLES = [
    ("dws_loan_status_snapshot_di", "借据状态日切宽表", "stat_date+loan_id", ["stat_date", "loan_id"], "借据状态与回款窗口宽表"),
    ("dws_case_status_snapshot_di", "案件状态日切宽表", "stat_date+case_id", ["stat_date", "case_id"], "案件状态与作业结果宽表"),
    ("dws_customer_status_snapshot_di", "客户状态日切宽表", "stat_date+customer_id", ["stat_date", "customer_id"], "归户视角日切宽表"),
    ("dws_collection_process_wide_di", "催收过程宽表", "stat_date+case_id", ["stat_date", "case_id"], "触达、PTP、履约、投诉过程宽表"),
    ("dws_vendor_line_capacity_di", "供应商线路产能宽表", "stat_date+vendor_id+line_id", ["stat_date", "vendor_id", "line_id"], "供应商线路产能日切宽表"),
    ("dws_customer_profile_di", "客户画像日切", "stat_date+customer_id", ["stat_date", "customer_id"], "客户基础、借款、还款、贷后画像"),
    ("dws_collector_profile_di", "催员画像日切", "stat_date+collector_id", ["stat_date", "collector_id"], "催员作业、结果、合规画像"),
    ("dws_customer_postloan_tag_di", "客户贷后标签日切", "stat_date+customer_id", ["stat_date", "customer_id"], "客户贷后标签日切"),
]

ADS_TABLES = [
    ("ads_postloan_dashboard_di", "贷后经营驾驶舱日切", "stat_date", "stat_date", "贷后核心经营汇总"),
    ("ads_recovery_attribution_di", "回收率归因日切", "stat_date+factor_code", ["stat_date", "factor_code"], "回收率归因占位汇总"),
    ("ads_vendor_performance_di", "供应商绩效日切", "stat_date+vendor_id", ["stat_date", "vendor_id"], "供应商绩效日切"),
    ("ads_collector_performance_di", "催员绩效日切", "stat_date+collector_id", ["stat_date", "collector_id"], "催员绩效日切"),
    ("ads_reduction_roi_di", "减免 ROI 日切", "stat_date", "stat_date", "减免使用与回款 ROI 汇总"),
    ("ads_compliance_qc_di", "合规质检日切", "stat_date+template_id", ["stat_date", "template_id"], "投诉与合规质检汇总"),
]


def table_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for layer, domain, rows_spec in [
        ("DIM", "master_data", DIM_TABLES),
        ("ODS", "source_events", ODS_TABLES),
        ("DWD", "detail_fact", DWD_TABLES),
        ("DWS", "subject_wide", DWS_TABLES),
        ("ADS", "application_summary", ADS_TABLES),
    ]:
        for table_name, table_name_cn, grain, primary_key, description in rows_spec:
            rows.append(
                {
                    "table_name": table_name,
                    "table_name_cn": table_name_cn,
                    "layer": layer,
                    "domain": domain,
                    "grain": grain,
                    "primary_key": primary_key,
                    "description": description,
                    "owner": "RiskOps Data Foundation",
                    "phase": "M1",
                }
            )
    return rows


def c(
    name: str,
    cn: str,
    typ: str,
    privacy: str = "P0",
    nullable: bool = False,
    pk: bool = False,
    desc: str | None = None,
) -> dict[str, Any]:
    return {
        "column_name": name,
        "column_name_cn": cn,
        "data_type": typ,
        "nullable": nullable,
        "is_primary_key": pk,
        "privacy_level": privacy,
        "description": desc or cn,
    }


BASE_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "dim_customer": [
        c("customer_id", "客户号", "VARCHAR", "P1", pk=True),
        c("customer_id_hash", "客户号哈希", "VARCHAR", "P3"),
        c("mobile_masked", "脱敏手机号", "VARCHAR", "P2"),
        c("gender", "性别", "VARCHAR"),
        c("age_group", "年龄段", "VARCHAR"),
        c("province", "省份", "VARCHAR"),
        c("city", "城市", "VARCHAR"),
        c("occupation_type", "职业类型", "VARCHAR"),
        c("customer_segment", "客户分层", "VARCHAR"),
        c("risk_level_current", "当前风险等级", "VARCHAR"),
        c("sensitive_flag", "敏感客群标识", "BOOLEAN"),
        c("blacklist_flag", "黑名单标识", "BOOLEAN"),
    ],
    "dim_loan": [
        c("loan_id", "借据号", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("product_code", "产品编码", "VARCHAR"),
        c("channel_code", "渠道编码", "VARCHAR"),
        c("loan_amount", "放款金额", "DOUBLE"),
        c("loan_term", "借款期数", "INTEGER"),
        c("interest_rate", "年化利率", "DOUBLE"),
        c("loan_status", "借据状态", "VARCHAR"),
        c("disburse_time", "放款时间", "TIMESTAMP"),
        c("first_due_date", "首期应还日", "DATE"),
        c("mob", "账龄月", "INTEGER"),
        c("vintage_month", "Vintage 月", "VARCHAR"),
    ],
    "dim_case": [
        c("case_id", "案件编号", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("case_create_time", "案件创建时间", "TIMESTAMP"),
        c("case_type", "案件类型", "VARCHAR"),
        c("initial_dpd_bucket", "入案账龄桶", "VARCHAR"),
        c("initial_outstanding_amount", "入案待还金额", "DOUBLE"),
        c("balance_segment", "余额分层", "VARCHAR"),
        c("current_vendor_id", "当前供应商", "VARCHAR", "P1"),
        c("current_line_id", "当前线路", "VARCHAR", "P1"),
        c("protect_flag", "保护标识", "BOOLEAN"),
        c("sensitive_flag", "敏感客群标识", "BOOLEAN"),
        c("complaint_flag", "投诉标识", "BOOLEAN"),
    ],
    "dim_case_loan_mapping": [
        c("mapping_id", "映射编号", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("loan_id", "借据号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("mapping_start_date", "映射开始日", "DATE"),
        c("mapping_end_date", "映射结束日", "DATE", nullable=True),
        c("main_loan_flag", "主借据标识", "BOOLEAN"),
    ],
    "dim_product": [
        c("product_code", "产品编码", "VARCHAR", pk=True),
        c("product_name", "产品名称", "VARCHAR"),
        c("product_type", "产品类型", "VARCHAR"),
        c("funder_type", "资金方类型", "VARCHAR"),
        c("interest_rate_min", "最低年化利率", "DOUBLE"),
        c("interest_rate_max", "最高年化利率", "DOUBLE"),
        c("term_min", "最短期数", "INTEGER"),
        c("term_max", "最长期数", "INTEGER"),
        c("online_flag", "线上标识", "BOOLEAN"),
    ],
    "dim_channel": [
        c("channel_code", "渠道编码", "VARCHAR", pk=True),
        c("channel_name", "渠道名称", "VARCHAR"),
        c("channel_type", "渠道类型", "VARCHAR"),
        c("partner_name", "合作方名称", "VARCHAR"),
        c("online_flag", "线上标识", "BOOLEAN"),
    ],
    "dim_vendor": [
        c("vendor_id", "供应商编号", "VARCHAR", "P1", pk=True),
        c("vendor_name", "供应商名称", "VARCHAR"),
        c("vendor_type", "供应商类型", "VARCHAR"),
        c("region", "区域", "VARCHAR"),
        c("max_capacity", "最大产能", "INTEGER"),
        c("settlement_method", "结算方式", "VARCHAR"),
        c("compliance_level", "合规等级", "VARCHAR"),
    ],
    "dim_collection_line": [
        c("line_id", "线路编号", "VARCHAR", "P1", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_name", "线路名称", "VARCHAR"),
        c("region", "区域", "VARCHAR"),
        c("line_type", "线路类型", "VARCHAR"),
        c("dpd_bucket_scope", "账龄覆盖", "VARCHAR"),
        c("capacity_limit", "产能上限", "INTEGER"),
    ],
    "dim_collector": [
        c("collector_id", "催员编号", "VARCHAR", "P1", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("role_type", "角色类型", "VARCHAR"),
        c("entry_date", "入职日期", "DATE"),
        c("skill_level", "技能等级", "VARCHAR"),
        c("max_daily_case_capacity", "日最大案量", "INTEGER"),
        c("compliance_level", "合规等级", "VARCHAR"),
    ],
    "dim_strategy": [
        c("strategy_id", "策略编号", "VARCHAR", "P1", pk=True),
        c("strategy_type", "策略类型", "VARCHAR"),
        c("strategy_version", "策略版本", "VARCHAR"),
        c("effective_start_date", "生效开始日", "DATE"),
        c("effective_end_date", "生效结束日", "DATE", nullable=True),
        c("owner_team", "负责团队", "VARCHAR"),
    ],
}

ODS_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "ods_repayment_plan": [
        c("plan_id", "还款计划 ID", "VARCHAR", "P1", pk=True),
        c("loan_id", "借据号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("period_no", "期数", "INTEGER"),
        c("due_date", "应还日", "DATE"),
        c("due_principal", "应还本金", "DOUBLE"),
        c("due_interest", "应还利息", "DOUBLE"),
        c("due_fee", "应还费用", "DOUBLE"),
        c("due_amount", "应还总额", "DOUBLE"),
        c("plan_status", "计划状态", "VARCHAR"),
    ],
    "ods_repayment_detail": [
        c("repay_id", "还款流水 ID", "VARCHAR", "P1", pk=True),
        c("plan_id", "还款计划 ID", "VARCHAR", "P1"),
        c("loan_id", "借据号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("repay_time", "还款时间", "TIMESTAMP"),
        c("repay_amount", "还款金额", "DOUBLE"),
        c("repay_channel", "还款渠道", "VARCHAR"),
        c("repay_status", "还款状态", "VARCHAR"),
    ],
    "ods_loan_daily_snapshot": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("loan_id", "借据号", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("dpd", "逾期天数", "INTEGER"),
        c("dpd_bucket", "账龄桶", "VARCHAR"),
        c("outstanding_amount", "待还金额", "DOUBLE"),
        c("loan_status", "借据状态", "VARCHAR"),
    ],
    "ods_case_daily_snapshot": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("case_status", "案件状态", "VARCHAR"),
        c("dpd_bucket", "账龄桶", "VARCHAR"),
        c("outstanding_amount", "待还金额", "DOUBLE"),
    ],
    "ods_customer_daily_snapshot": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1", pk=True),
        c("active_loan_count", "有效借据数", "INTEGER"),
        c("active_case_count", "有效案件数", "INTEGER"),
        c("total_outstanding_amount", "总待还金额", "DOUBLE"),
        c("max_dpd", "最大逾期天数", "INTEGER"),
        c("risk_level", "风险等级", "VARCHAR"),
    ],
    "ods_case_flow": [
        c("flow_id", "流转 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("from_status", "原状态", "VARCHAR"),
        c("to_status", "新状态", "VARCHAR"),
        c("flow_time", "流转时间", "TIMESTAMP"),
        c("strategy_id", "策略编号", "VARCHAR", "P1"),
    ],
    "ods_assignment_decision_log": [
        c("decision_id", "决策 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("strategy_id", "策略编号", "VARCHAR", "P1"),
        c("decision_time", "决策时间", "TIMESTAMP"),
        c("decision_reason", "决策原因", "VARCHAR"),
    ],
    "ods_postloan_c_score": [
        c("score_id", "评分 ID", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("score_date", "评分日期", "DATE"),
        c("postloan_c_score", "贷后 C 卡分", "DOUBLE"),
        c("score_level", "评分等级", "VARCHAR"),
    ],
    "ods_collection_note": [
        c("note_id", "催记 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("note_time", "催记时间", "TIMESTAMP"),
        c("note_type", "催记类型", "VARCHAR"),
        c("note_text_masked", "脱敏催记文本", "VARCHAR", "P2"),
    ],
    "ods_collection_action": [
        c("action_id", "动作 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("action_time", "动作时间", "TIMESTAMP"),
        c("action_type", "动作类型", "VARCHAR"),
        c("template_id", "模板 ID", "VARCHAR", "P1", nullable=True),
        c("connected_flag", "接通标识", "BOOLEAN"),
        c("ptp_flag", "PTP 标识", "BOOLEAN"),
        c("ptp_fulfilled_flag", "PTP 履约标识", "BOOLEAN"),
        c("ai_outbound_flag", "AI 外呼标识", "BOOLEAN"),
    ],
    "ods_call_record": [
        c("call_id", "通话 ID", "VARCHAR", "P1", pk=True),
        c("action_id", "动作 ID", "VARCHAR", "P1"),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("call_start_time", "通话开始时间", "TIMESTAMP"),
        c("duration_seconds", "通话时长秒", "INTEGER"),
        c("recording_uri", "录音引用", "VARCHAR", "P1"),
        c("transcript_masked", "脱敏转写", "VARCHAR", "P2"),
    ],
    "ods_sms_send_log": [
        c("message_id", "消息 ID", "VARCHAR", "P1", pk=True),
        c("action_id", "动作 ID", "VARCHAR", "P1"),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("template_id", "模板 ID", "VARCHAR", "P1"),
        c("send_time", "发送时间", "TIMESTAMP"),
        c("send_status", "发送状态", "VARCHAR"),
    ],
    "ods_reduction_application": [
        c("reduction_id", "减免 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("apply_time", "申请时间", "TIMESTAMP"),
        c("apply_amount", "申请减免金额", "DOUBLE"),
        c("approved_amount", "审批减免金额", "DOUBLE"),
        c("approval_status", "审批状态", "VARCHAR"),
    ],
    "ods_complaint": [
        c("complaint_id", "投诉 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1", nullable=True),
        c("template_id", "模板 ID", "VARCHAR", "P1", nullable=True),
        c("complaint_time", "投诉时间", "TIMESTAMP"),
        c("complaint_type", "投诉类型", "VARCHAR"),
        c("complaint_level", "投诉等级", "VARCHAR"),
    ],
}


DWD_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "dwd_due_plan_detail_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("plan_id", "还款计划 ID", "VARCHAR", "P1", pk=True),
        c("loan_id", "借据号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("product_code", "产品编码", "VARCHAR"),
        c("channel_code", "渠道编码", "VARCHAR"),
        c("due_date", "应还日", "DATE"),
        c("due_amount", "应还总额", "DOUBLE"),
        c("outstanding_amount", "待还金额", "DOUBLE"),
        c("dpd_bucket", "账龄桶", "VARCHAR"),
    ],
    "dwd_repayment_detail_di": [
        c("repay_id", "还款流水 ID", "VARCHAR", "P1", pk=True),
        c("plan_id", "还款计划 ID", "VARCHAR", "P1"),
        c("loan_id", "借据号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("repay_time", "还款时间", "TIMESTAMP"),
        c("repay_date", "还款日期", "DATE"),
        c("repay_amount", "还款金额", "DOUBLE"),
        c("repay_status", "还款状态", "VARCHAR"),
    ],
    "dwd_collection_action_detail_di": [
        c("action_id", "动作 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("action_time", "动作时间", "TIMESTAMP"),
        c("action_date", "动作日期", "DATE"),
        c("action_type", "动作类型", "VARCHAR"),
        c("template_id", "模板 ID", "VARCHAR", "P1", nullable=True),
        c("connected_flag", "接通标识", "BOOLEAN"),
        c("ptp_flag", "PTP 标识", "BOOLEAN"),
        c("ptp_fulfilled_flag", "PTP 履约标识", "BOOLEAN"),
        c("ai_outbound_flag", "AI 外呼标识", "BOOLEAN"),
    ],
    "dwd_case_flow_detail_di": [
        c("flow_id", "流转 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("from_status", "原状态", "VARCHAR"),
        c("to_status", "新状态", "VARCHAR"),
        c("flow_time", "流转时间", "TIMESTAMP"),
        c("flow_date", "流转日期", "DATE"),
        c("strategy_id", "策略编号", "VARCHAR", "P1"),
    ],
    "dwd_complaint_detail_di": [
        c("complaint_id", "投诉 ID", "VARCHAR", "P1", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1"),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1", nullable=True),
        c("template_id", "模板 ID", "VARCHAR", "P1", nullable=True),
        c("complaint_time", "投诉时间", "TIMESTAMP"),
        c("complaint_date", "投诉日期", "DATE"),
        c("complaint_type", "投诉类型", "VARCHAR"),
        c("complaint_level", "投诉等级", "VARCHAR"),
    ],
}

DWS_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "dws_loan_status_snapshot_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("loan_id", "借据号", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("product_code", "产品编码", "VARCHAR"),
        c("dpd_bucket", "账龄桶", "VARCHAR"),
        c("due_amount", "应还金额", "DOUBLE"),
        c("repaid_amount_d7", "D7 回款金额", "DOUBLE"),
        c("recovery_rate_d7", "D7 回收率", "DOUBLE"),
    ],
    "dws_case_status_snapshot_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1"),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("dpd_bucket", "账龄桶", "VARCHAR"),
        c("outstanding_amount", "待还金额", "DOUBLE"),
        c("action_count", "动作数", "INTEGER"),
        c("connected_count", "接通数", "INTEGER"),
        c("ptp_count", "PTP 数", "INTEGER"),
        c("repaid_amount", "回款金额", "DOUBLE"),
    ],
    "dws_customer_status_snapshot_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1", pk=True),
        c("active_loan_count", "有效借据数", "INTEGER"),
        c("active_case_count", "有效案件数", "INTEGER"),
        c("total_outstanding_amount", "总待还金额", "DOUBLE"),
        c("max_dpd", "最大逾期天数", "INTEGER"),
        c("risk_level", "风险等级", "VARCHAR"),
    ],
    "dws_collection_process_wide_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("case_id", "案件编号", "VARCHAR", "P1", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("collector_id", "催员编号", "VARCHAR", "P1"),
        c("action_count", "动作数", "INTEGER"),
        c("ai_action_count", "AI 外呼动作数", "INTEGER"),
        c("connected_count", "接通数", "INTEGER"),
        c("ptp_count", "PTP 数", "INTEGER"),
        c("ptp_fulfilled_count", "PTP 履约数", "INTEGER"),
        c("complaint_count", "投诉数", "INTEGER"),
        c("connect_rate", "接通率", "DOUBLE"),
        c("ptp_fulfillment_rate", "PTP 履约率", "DOUBLE"),
        c("ai_coverage_rate", "AI 外呼覆盖率", "DOUBLE"),
    ],
    "dws_vendor_line_capacity_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1", pk=True),
        c("line_id", "线路编号", "VARCHAR", "P1", pk=True),
        c("region", "区域", "VARCHAR"),
        c("active_case_count", "在催案件数", "INTEGER"),
        c("active_collector_count", "在岗催员数", "INTEGER"),
        c("case_per_collector", "人均案量", "DOUBLE"),
    ],
    "dws_customer_profile_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1", pk=True),
        c("customer_id_hash", "客户号哈希", "VARCHAR", "P3"),
        c("mobile_masked", "脱敏手机号", "VARCHAR", "P2"),
        c("province", "省份", "VARCHAR"),
        c("customer_segment", "客户分层", "VARCHAR"),
        c("risk_level_current", "当前风险等级", "VARCHAR"),
        c("total_outstanding_amount", "总待还金额", "DOUBLE"),
    ],
    "dws_collector_profile_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("collector_id", "催员编号", "VARCHAR", "P1", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("line_id", "线路编号", "VARCHAR", "P1"),
        c("skill_level", "技能等级", "VARCHAR"),
        c("action_count", "动作数", "INTEGER"),
        c("connect_rate", "接通率", "DOUBLE"),
        c("complaint_count", "投诉数", "INTEGER"),
    ],
    "dws_customer_postloan_tag_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("customer_id", "客户号", "VARCHAR", "P1", pk=True),
        c("dpd_tag", "账龄标签", "VARCHAR"),
        c("balance_tag", "金额标签", "VARCHAR"),
        c("behavior_tag", "行为标签", "VARCHAR"),
        c("touch_tag", "触达标签", "VARCHAR"),
        c("compliance_tag", "合规投诉标签", "VARCHAR"),
        c("strategy_tag", "策略标签", "VARCHAR"),
    ],
}

ADS_COLUMNS: dict[str, list[dict[str, Any]]] = {
    "ads_postloan_dashboard_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("due_account_count", "到期账户数", "INTEGER"),
        c("due_loan_count", "到期借据数", "INTEGER"),
        c("due_total_amount", "到期应还金额", "DOUBLE"),
        c("collection_entry_rate", "入催率", "DOUBLE"),
        c("recovery_rate_d7", "D7 回收率", "DOUBLE"),
        c("recovery_rate_d15", "D15 回收率", "DOUBLE"),
        c("recovery_rate_d30", "D30 回收率", "DOUBLE"),
        c("m1_recovery_rate", "M1 回收率", "DOUBLE"),
        c("call_coverage_rate", "拨打覆盖率", "DOUBLE"),
        c("valid_coverage_rate", "有效覆盖率", "DOUBLE"),
        c("connect_rate", "接通率", "DOUBLE"),
        c("valid_contact_rate", "有效沟通率", "DOUBLE"),
        c("first_contact_hours", "首触达时效", "DOUBLE"),
        c("ptp_rate", "PTP 率", "DOUBLE"),
        c("ptp_keep_rate", "PTP 履约率", "DOUBLE"),
        c("avg_call_duration_per_call", "单通平均时长", "DOUBLE"),
        c("avg_call_duration_per_collector", "人均日通话时长", "DOUBLE"),
        c("collector_productivity", "作业人效", "DOUBLE"),
        c("complaint_rate", "投诉率", "DOUBLE"),
        c("complaint_per_10k_cases", "万案投诉率", "DOUBLE"),
        c("risk_phrase_hit_rate", "高风险话术命中率", "DOUBLE"),
        c("qa_fail_rate", "质检不合格率", "DOUBLE"),
        c("over_frequency_contact_rate", "超频触达率", "DOUBLE"),
        c("reduction_usage_rate", "减免使用率", "DOUBLE"),
        c("reduction_recovery_rate", "减免回收率", "DOUBLE"),
        c("reduction_roi", "减免 ROI", "DOUBLE"),
    ],
    "ads_recovery_attribution_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("factor_code", "因子编码", "VARCHAR", pk=True),
        c("factor_name", "因子名称", "VARCHAR"),
        c("factor_value", "因子值", "DOUBLE"),
        c("contribution_pct", "贡献占比", "DOUBLE"),
    ],
    "ads_vendor_performance_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1", pk=True),
        c("action_count", "动作数", "INTEGER"),
        c("call_coverage_rate", "拨打覆盖率", "DOUBLE"),
        c("connect_rate", "接通率", "DOUBLE"),
        c("ptp_rate", "PTP 率", "DOUBLE"),
        c("ptp_keep_rate", "PTP 履约率", "DOUBLE"),
        c("complaint_rate", "投诉率", "DOUBLE"),
    ],
    "ads_collector_performance_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("collector_id", "催员编号", "VARCHAR", "P1", pk=True),
        c("vendor_id", "供应商编号", "VARCHAR", "P1"),
        c("action_count", "动作数", "INTEGER"),
        c("connect_rate", "接通率", "DOUBLE"),
        c("ptp_keep_rate", "PTP 履约率", "DOUBLE"),
        c("first_contact_hours", "首触达时效", "DOUBLE"),
        c("avg_call_duration_per_call", "单通平均时长", "DOUBLE"),
        c("avg_call_duration_per_collector", "人均日通话时长", "DOUBLE"),
        c("collector_productivity", "作业人效", "DOUBLE"),
        c("complaint_count", "投诉数", "INTEGER"),
    ],
    "ads_reduction_roi_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("reduction_case_count", "减免案件数", "INTEGER"),
        c("approved_reduction_amount", "审批减免金额", "DOUBLE"),
        c("reduction_usage_rate", "减免使用率", "DOUBLE"),
        c("reduction_recovery_rate", "减免回收率", "DOUBLE"),
        c("reduction_roi", "减免 ROI", "DOUBLE"),
    ],
    "ads_compliance_qc_di": [
        c("stat_date", "统计日期", "DATE", pk=True),
        c("template_id", "模板 ID", "VARCHAR", "P1", pk=True),
        c("active_case_count", "在催案件数", "INTEGER"),
        c("complaint_count", "投诉数", "INTEGER"),
        c("complaint_rate", "投诉率", "DOUBLE"),
        c("complaint_per_10k_cases", "万案投诉率", "DOUBLE"),
        c("risk_phrase_hit_rate", "高风险话术命中率", "DOUBLE"),
        c("qa_fail_rate", "质检不合格率", "DOUBLE"),
        c("over_frequency_contact_rate", "超频触达率", "DOUBLE"),
    ],
}


def column_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in [BASE_COLUMNS, ODS_COLUMNS, DWD_COLUMNS, DWS_COLUMNS, ADS_COLUMNS]:
        for table_name, cols in source.items():
            for col in cols:
                item = deepcopy(col)
                item["table_name"] = table_name
                rows.append(item)
    return rows


PRIVACY_POLICY = {
    "levels": [
        {
            "level": "P0",
            "name": "非敏感公开分析字段",
            "warehouse_allowed": True,
            "report_allowed": True,
            "llm_allowed": True,
            "examples": ["product_code", "province", "city", "dpd_bucket"],
        },
        {
            "level": "P1",
            "name": "业务内部键",
            "warehouse_allowed": True,
            "report_allowed": True,
            "llm_allowed": True,
            "examples": ["customer_id", "loan_id", "case_id", "vendor_id", "collector_id"],
        },
        {
            "level": "P2",
            "name": "脱敏个人字段",
            "warehouse_allowed": True,
            "report_allowed": True,
            "llm_allowed": True,
            "examples": ["mobile_masked", "note_text_masked", "transcript_masked"],
        },
        {
            "level": "P3",
            "name": "哈希或密文字段",
            "warehouse_allowed": True,
            "report_allowed": False,
            "llm_allowed": False,
            "examples": ["customer_id_hash", "id_no_hash", "mobile_hash", "bank_card_hash"],
        },
        {
            "level": "P4",
            "name": "明文 PII",
            "warehouse_allowed": False,
            "report_allowed": False,
            "llm_allowed": False,
            "examples": ["customer_name", "id_no", "mobile_no", "bank_card_no", "address"],
        },
    ],
    "rules": [
        "P4 不得进入 DWD/DWS/ADS。",
        "P4 不得进入报告。",
        "P4 不得进入 LLM 上下文。",
        "P4 只允许在 synthetic_data/raw_secure/ 中存在。",
        "默认不生成 raw_secure，除非显式使用 --with-raw。",
    ],
    "p4_field_names": ["customer_name", "id_no", "mobile_no", "bank_card_no", "address"],
    "raw_secure_path": "synthetic_data/raw_secure/",
}


KEY_RELATIONSHIPS = {
    "relationships": [
        {"from": "customer_id", "to": "loan_id", "cardinality": "1:N", "via": None},
        {"from": "customer_id", "to": "case_id", "cardinality": "1:N", "via": None},
        {"from": "case_id", "to": "loan_id", "cardinality": "M:N", "via": "dim_case_loan_mapping"},
        {"from": "loan_id", "to": "plan_id", "cardinality": "1:N", "via": None},
        {"from": "plan_id", "to": "repay_id", "cardinality": "1:N", "via": None},
        {"from": "case_id", "to": "action_id", "cardinality": "1:N", "via": None},
        {"from": "case_id", "to": "note_id", "cardinality": "1:N", "via": None},
        {"from": "case_id", "to": "decision_id", "cardinality": "1:N", "via": None},
        {"from": "vendor_id", "to": "line_id", "cardinality": "1:N", "via": None},
        {"from": "line_id", "to": "collector_id", "cardinality": "1:N", "via": None},
    ]
}


METRIC_LINEAGE = {
    "phase": "M1",
    "scope": "lineage placeholders only; metric calculation lands in M2",
    "metrics": [
        {
            "metric_code": "m1_recovery_rate_d7",
            "metric_name_cn": "M1 D7 回收率",
            "ads_table": "ads_postloan_dashboard_di",
            "dws_tables": ["dws_loan_status_snapshot_di"],
            "dwd_tables": ["dwd_due_plan_detail_di", "dwd_repayment_detail_di"],
            "ods_tables": ["ods_repayment_plan", "ods_repayment_detail"],
        },
        {
            "metric_code": "connect_rate",
            "metric_name_cn": "接通率",
            "ads_table": "ads_vendor_performance_di",
            "dws_tables": ["dws_collection_process_wide_di"],
            "dwd_tables": ["dwd_collection_action_detail_di"],
            "ods_tables": ["ods_collection_action"],
        },
        {
            "metric_code": "complaint_rate",
            "metric_name_cn": "投诉率",
            "ads_table": "ads_compliance_qc_di",
            "dws_tables": ["dws_collection_process_wide_di"],
            "dwd_tables": ["dwd_complaint_detail_di"],
            "ods_tables": ["ods_complaint", "ods_sms_send_log"],
        },
    ],
}


def write_yaml(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120),
        encoding="utf-8",
    )


def duckdb_type(data_type: str) -> str:
    return data_type


def create_sql_for_layer(layer: str) -> str:
    tables = [row for row in table_rows() if row["layer"] == layer]
    columns_by_table: dict[str, list[dict[str, Any]]] = {}
    for row in column_rows():
        columns_by_table.setdefault(row["table_name"], []).append(row)

    statements: list[str] = []
    for table in tables:
        table_name = table["table_name"]
        columns = columns_by_table[table_name]
        column_lines = [f"    {col['column_name']} {duckdb_type(col['data_type'])}" for col in columns]
        pk = table["primary_key"]
        pk_cols = pk if isinstance(pk, list) else [pk]
        column_lines.append(f"    PRIMARY KEY ({', '.join(pk_cols)})")
        statements.append(f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(column_lines) + "\n);")
    return "\n\n".join(statements) + "\n"


def sync_metadata_and_schemas() -> None:
    write_yaml(ROOT / "metadata/tables.yaml", table_rows())
    write_yaml(ROOT / "metadata/columns.yaml", column_rows())
    write_yaml(ROOT / "metadata/privacy_policy.yaml", PRIVACY_POLICY)
    write_yaml(ROOT / "metadata/key_relationships.yaml", KEY_RELATIONSHIPS)
    if not (ROOT / "metadata/metric_lineage.yaml").exists():
        write_yaml(ROOT / "metadata/metric_lineage.yaml", METRIC_LINEAGE)
    for layer in ["DIM", "ODS", "DWD", "DWS", "ADS"]:
        (ROOT / f"schemas/{layer.lower()}.sql").write_text(create_sql_for_layer(layer), encoding="utf-8")


if __name__ == "__main__":
    sync_metadata_and_schemas()
