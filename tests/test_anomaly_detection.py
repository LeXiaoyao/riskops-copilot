from __future__ import annotations

from pathlib import Path

import pandas as pd

from riskops.engines.anomaly.detector import AnomalyDetector


def write_table(root: Path, layer: str, table: str, frame: pd.DataFrame) -> None:
    path = root / layer
    path.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path / f"{table}.parquet", index=False)


def make_dates() -> pd.DatetimeIndex:
    return pd.date_range("2026-03-19", periods=60, freq="D")


def build_anomaly_fixture(root: Path) -> None:
    dates = make_dates()
    baseline = [0.20] * 30
    recent = [0.15] * 30
    dashboard = pd.DataFrame(
        {
            "stat_date": dates,
            "m1_recovery_rate": baseline + recent,
            "ptp_keep_rate": [0.50] * 30 + [0.43] * 30,
        }
    )
    write_table(root, "ads", "ads_postloan_dashboard_di", dashboard)

    vendor = pd.DataFrame(
        {
            "stat_date": list(dates) * 2,
            "vendor_id": ["V_B"] * 60 + ["V_A"] * 60,
            "connect_rate": [0.34] * 30 + [0.28] * 30 + [0.36] * 60,
        }
    )
    write_table(root, "ads", "ads_vendor_performance_di", vendor)

    reduction = pd.DataFrame(
        {
            "stat_date": dates,
            "reduction_usage_rate": [0.08] * 30 + [0.03] * 30,
        }
    )
    write_table(root, "ads", "ads_reduction_roi_di", reduction)

    capacity = pd.DataFrame(
        {
            "stat_date": dates,
            "region": ["华东"] * 60,
            "active_case_count": [100] * 30 + [140] * 30,
            "active_collector_count": [10] * 60,
            "line_id": ["L_EAST_M1"] * 60,
            "vendor_id": ["V_B"] * 60,
        }
    )
    write_table(root, "dws", "dws_vendor_line_capacity_di", capacity)

    customer_rows = []
    for idx, date in enumerate(dates):
        high_count = 1 if idx < 30 else 4
        for customer_idx in range(10):
            customer_rows.append(
                {
                    "stat_date": date,
                    "customer_id": f"C{customer_idx:03d}",
                    "total_outstanding_amount": 40_000 if customer_idx < high_count else 10_000,
                    "risk_level": "C" if customer_idx < high_count else "B",
                }
            )
    customer = pd.DataFrame(customer_rows)
    write_table(root, "dws", "dws_customer_status_snapshot_di", customer)

    process = pd.DataFrame(
        {
            "stat_date": dates,
            "case_id": [f"CASE{i:03d}" for i in range(60)],
            "action_count": [100] * 60,
            "ai_action_count": [30] * 30 + [18] * 30,
        }
    )
    write_table(root, "dws", "dws_collection_process_wide_di", process)

    action_rows = []
    complaint_rows = []
    for idx, date in enumerate(dates):
        for template_id in ["TPL_NORMAL", "TPL_RISK_NOTICE"]:
            for action_idx in range(50):
                action_rows.append(
                    {
                        "action_id": f"A{idx:03d}{template_id}{action_idx:03d}",
                        "action_date": date,
                        "action_type": "SMS",
                        "template_id": template_id,
                    }
                )
        if idx >= 30:
            complaint_rows.extend(
                {
                    "complaint_id": f"CMP{idx:03d}{complaint_idx:03d}",
                    "complaint_date": date,
                    "template_id": "TPL_RISK_NOTICE",
                }
                for complaint_idx in range(2)
            )
            complaint_rows.append(
                {
                    "complaint_id": f"CMP{idx:03d}N",
                    "complaint_date": date,
                    "template_id": "TPL_NORMAL",
                }
            )
    write_table(root, "dwd", "dwd_collection_action_detail_di", pd.DataFrame(action_rows))
    write_table(root, "dwd", "dwd_complaint_detail_di", pd.DataFrame(complaint_rows))


def test_detector_can_run(tmp_path: Path) -> None:
    build_anomaly_fixture(tmp_path)
    run = AnomalyDetector(data_root=tmp_path).detect()
    assert run.results


def test_anomaly_result_schema_complete(tmp_path: Path) -> None:
    build_anomaly_fixture(tmp_path)
    result = AnomalyDetector(data_root=tmp_path).detect().results[0].to_dict()
    assert set(result) == {
        "anomaly_id",
        "metric_code",
        "metric_name_cn",
        "anomaly_type",
        "severity",
        "dimension_name",
        "dimension_value",
        "baseline_value",
        "recent_value",
        "absolute_change",
        "relative_change",
        "recent_window",
        "baseline_window",
        "evidence_table",
        "explanation",
        "recommended_next_step",
    }


def test_detects_m1_recovery_drop(tmp_path: Path) -> None:
    build_anomaly_fixture(tmp_path)
    codes = {item.metric_code for item in AnomalyDetector(data_root=tmp_path).detect().results}
    assert "m1_recovery_rate" in codes


def test_detects_vendor_b_connect_drop(tmp_path: Path) -> None:
    build_anomaly_fixture(tmp_path)
    results = AnomalyDetector(data_root=tmp_path).detect().results
    assert any(item.metric_code == "connect_rate" and item.dimension_value == "V_B" for item in results)


def test_detects_reduction_usage_rate_drop(tmp_path: Path) -> None:
    build_anomaly_fixture(tmp_path)
    codes = {item.metric_code for item in AnomalyDetector(data_root=tmp_path).detect().results}
    assert "reduction_usage_rate" in codes


def test_severity_is_not_empty(tmp_path: Path) -> None:
    build_anomaly_fixture(tmp_path)
    results = AnomalyDetector(data_root=tmp_path).detect().results
    assert all(item.severity for item in results)


def test_missing_fields_warns_and_skips(tmp_path: Path) -> None:
    dates = make_dates()
    write_table(tmp_path, "ads", "ads_postloan_dashboard_di", pd.DataFrame({"stat_date": dates, "m1_recovery_rate": [0.2] * 60}))
    run = AnomalyDetector(data_root=tmp_path).detect()
    assert run.warnings
