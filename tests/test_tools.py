from __future__ import annotations

from riskops.tui.tools import (
    get_data_overview,
    query_case_detail,
    query_recovery_rate,
    query_segment_breakdown,
    query_vendor_performance,
)


def test_query_recovery_rate_no_segment() -> None:
    result = query_recovery_rate()

    assert result["tool"] == "query_recovery_rate"
    assert result["row_count"] > 0
    assert result["result"]
    assert "recovery_rate_d7" in result["result"][0]


def test_query_recovery_rate_with_segment() -> None:
    result = query_recovery_rate(segment_col="channel_code", segment_val="ECOM", date_start="2026-04-01")

    assert result["tool"] == "query_recovery_rate"
    assert result["row_count"] > 0
    assert all(item["channel_code"] == "ECOM" for item in result["result"])


def test_query_vendor_performance_returns_vendors() -> None:
    result = query_vendor_performance()

    assert result["tool"] == "query_vendor_performance"
    assert result["row_count"] == 4
    assert {item["vendor_id"] for item in result["result"]} == {"V_A", "V_B", "V_C", "V_AI"}


def test_query_segment_breakdown_channels() -> None:
    result = query_segment_breakdown(segment_col="channel_code")

    assert result["tool"] == "query_segment_breakdown"
    assert result["row_count"] > 1
    assert all(item["segment_col"] == "channel_code" for item in result["result"])


def test_query_case_detail_no_pii() -> None:
    result = query_case_detail(case_id="CASE00000000")

    assert result["tool"] == "query_case_detail"
    assert result["row_count"] == 1
    serialized = str(result["result"])
    assert "id_no" not in serialized
    assert "mobile_no" not in serialized
    assert "bank_card_no" not in serialized
    assert "customer_name" not in serialized
    assert "address" not in serialized


def test_get_data_overview_lists_files() -> None:
    result = get_data_overview()

    assert result["tool"] == "get_data_overview"
    assert result["row_count"] > 0
    assert any(item["file"].endswith("ads_postloan_dashboard_di.parquet") for item in result["result"])
