"""DeepSeek function calling schemas for local RiskOps TUI tools."""

from __future__ import annotations

from typing import Any

TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "query_recovery_rate",
            "description": "查询M1 D7回收率时间序列，支持按渠道/区域/风险等级/产品/评分段分组，支持日期筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "segment_col": {
                        "type": "string",
                        "enum": ["channel_code", "province", "risk_level", "product_code", "score_band"],
                        "description": "分组维度",
                    },
                    "segment_val": {"type": "string", "description": "维度筛选值，如 ECOM、山东、D"},
                    "date_start": {"type": "string", "description": "起始日期 YYYY-MM-DD"},
                    "date_end": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_anomalies",
            "description": "查询异常检测结果，支持按严重程度和指标编码筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "severity": {"type": "string", "enum": ["high", "medium", "low"], "description": "异常等级"},
                    "metric_code": {"type": "string", "description": "指标编码，如 recovery_rate_d7、connect_rate"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_top_drivers",
            "description": "查询Top N归因因子",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {"type": "integer", "minimum": 1, "maximum": 20, "description": "返回条数，默认5"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_roi_scenarios",
            "description": "查询策略情景ROI数据，支持按scenario_id筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "scenario_id": {"type": "string", "description": "情景ID"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_vendor_performance",
            "description": "查询供应商绩效，包括接通率、PTP率、履约率和回收贡献线索",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "供应商ID，如 V_A、V_B、V_C、V_AI"},
                    "date_start": {"type": "string", "description": "起始日期 YYYY-MM-DD"},
                    "date_end": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_collector_performance",
            "description": "查询催收员绩效，包括日均案量、接通率、PTP率和合规得分",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "供应商ID"},
                    "date_start": {"type": "string", "description": "起始日期 YYYY-MM-DD"},
                    "date_end": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_segment_breakdown",
            "description": "按分组维度返回最近N天指标均值和趋势方向",
            "parameters": {
                "type": "object",
                "properties": {
                    "segment_col": {
                        "type": "string",
                        "enum": ["channel_code", "province", "risk_level", "product_code", "score_band"],
                        "description": "分组维度",
                    },
                    "metric": {"type": "string", "description": "指标字段，默认 recovery_rate_d7"},
                    "days": {"type": "integer", "minimum": 1, "maximum": 180, "description": "最近天数，默认30"},
                },
                "required": ["segment_col"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_case_detail",
            "description": "查询案件基本信息和最近30天状态快照，不返回P4敏感字段",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string", "description": "案件ID"},
                    "customer_id": {"type": "string", "description": "客户ID"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_collection_process",
            "description": "查询催收过程统计，支持按供应商、线路、催员、渠道、产品、区域、风险等级筛选",
            "parameters": {
                "type": "object",
                "properties": {
                    "segment_col": {
                        "type": "string",
                        "enum": ["vendor_id", "line_id", "collector_id", "channel_code", "product_code", "province", "risk_level"],
                        "description": "筛选维度",
                    },
                    "segment_val": {"type": "string", "description": "维度取值"},
                    "days": {"type": "integer", "minimum": 1, "maximum": 180, "description": "最近天数，默认30"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_data_overview",
            "description": "列出所有可查询parquet文件、行数、列名和日期范围",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]
