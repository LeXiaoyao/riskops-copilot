from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from riskops.engines.attribution.analyzer import AttributionAnalyzer
from riskops.engines.attribution.summary import render_markdown


def write_table(root: Path, layer: str, table: str, frame: pd.DataFrame) -> None:
    path = root / layer
    path.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path / f"{table}.parquet", index=False)


def make_dates() -> pd.DatetimeIndex:
    return pd.date_range("2026-03-19", periods=60, freq="D")


def build_attribution_fixture(root: Path) -> Path:
    dates = make_dates()
    loans = []
    mapping = []
    cases = []
    process = []
    for day_idx, date in enumerate(dates):
        recent = day_idx >= 30
        for idx, vendor_id in enumerate(["V_A", "V_B", "V_C", "V_D"]):
            loan_id = f"L{day_idx:02d}{idx:02d}"
            case_id = f"CASE{day_idx:02d}{idx:02d}"
            due_amount = 1000.0
            repaid = 220.0
            if recent and vendor_id in {"V_B", "V_C", "V_D"}:
                repaid = 80.0
            loans.append(
                {
                    "stat_date": date,
                    "loan_id": loan_id,
                    "customer_id": f"C{idx:03d}",
                    "product_code": "P_CASH" if idx % 2 else "P_CONS",
                    "dpd_bucket": "M1",
                    "due_amount": due_amount,
                    "repaid_amount_d7": repaid,
                    "recovery_rate_d7": repaid / due_amount,
                }
            )
            mapping.append({"loan_id": loan_id, "case_id": case_id, "customer_id": f"C{idx:03d}"})
            cases.append(
                {
                    "case_id": case_id,
                    "customer_id": f"C{idx:03d}",
                    "current_vendor_id": vendor_id,
                    "current_line_id": f"LINE_{vendor_id}",
                    "collector_id": f"COL_{vendor_id}",
                    "balance_segment": "HIGH" if vendor_id == "V_B" else "NORMAL",
                    "initial_outstanding_amount": due_amount,
                }
            )
            action_count = 10
            connected_count = 5 if not recent or vendor_id == "V_A" else 2
            process.append(
                {
                    "stat_date": date,
                    "case_id": case_id,
                    "vendor_id": vendor_id,
                    "line_id": f"LINE_{vendor_id}",
                    "collector_id": f"COL_{vendor_id}",
                    "action_count": action_count,
                    "ai_action_count": 4 if not recent else 1,
                    "connected_count": connected_count,
                    "ptp_count": 3,
                    "ptp_fulfilled_count": 2 if not recent else 1,
                    "complaint_count": 1 if recent and vendor_id == "V_D" else 0,
                    "connect_rate": connected_count / action_count,
                    "ptp_fulfillment_rate": (2 if not recent else 1) / 3,
                    "ai_coverage_rate": (4 if not recent else 1) / action_count,
                }
            )
    write_table(root, "dws", "dws_loan_status_snapshot_di", pd.DataFrame(loans))
    write_table(root, "dim", "dim_case_loan_mapping", pd.DataFrame(mapping))
    write_table(root, "dim", "dim_case", pd.DataFrame(cases).drop_duplicates("case_id"))
    write_table(root, "dws", "dws_collection_process_wide_di", pd.DataFrame(process))
    write_table(
        root,
        "dim",
        "dim_loan",
        pd.DataFrame({"loan_id": [row["loan_id"] for row in loans], "channel_code": ["APP"] * len(loans)}),
    )
    write_table(
        root,
        "dws",
        "dws_customer_status_snapshot_di",
        pd.DataFrame(
            {
                "stat_date": list(dates) * 4,
                "customer_id": [f"C{idx:03d}" for idx in range(4) for _ in dates],
                "risk_level": ["B"] * 60 + ["C"] * 60 + ["D"] * 60 + ["A"] * 60,
                "total_outstanding_amount": [10000, 40000, 45000, 12000] * 60,
            }
        ),
    )
    write_table(
        root,
        "dim",
        "dim_customer",
        pd.DataFrame(
            {
                "customer_id": [f"C{idx:03d}" for idx in range(4)],
                "province": ["北京", "上海", "江苏", "广东"],
                "risk_level_current": ["B", "C", "D", "A"],
            }
        ),
    )
    write_table(
        root,
        "dim",
        "dim_vendor",
        pd.DataFrame({"vendor_id": ["V_A", "V_B", "V_C", "V_D"], "vendor_name": ["供应商 A", "供应商 B", "供应商 C", "供应商 D"]}),
    )
    write_table(
        root,
        "dim",
        "dim_collection_line",
        pd.DataFrame(
            {
                "line_id": [f"LINE_V_{suffix}" for suffix in ["A", "B", "C", "D"]],
                "line_name": ["华北 M1", "华东 M1", "华南 M1", "西南 M1"],
                "region": ["华北", "华东", "华南", "西南"],
            }
        ),
    )
    write_table(
        root,
        "ods",
        "ods_postloan_c_score",
        pd.DataFrame(
            {
                "score_id": [f"S{idx}" for idx in range(4)],
                "customer_id": [f"C{idx:03d}" for idx in range(4)],
                "score_date": ["2026-03-01"] * 4,
                "postloan_c_score": [650, 550, 530, 700],
                "score_level": ["B", "C", "D", "A"],
            }
        ),
    )
    write_table(
        root,
        "ods",
        "ods_reduction_application",
        pd.DataFrame({"reduction_id": ["R1"], "case_id": ["CASE0000"], "customer_id": ["C000"], "apply_time": [dates[0]], "approved_amount": [10]}),
    )
    write_table(
        root,
        "dwd",
        "dwd_complaint_detail_di",
        pd.DataFrame({"complaint_id": ["CP1"], "case_id": ["CASE3003"], "customer_id": ["C003"], "complaint_date": [dates[30]]}),
    )
    anomaly_path = root / "anomaly_results.json"
    anomaly_path.write_text(
        json.dumps(
            {
                "anomalies": [
                    {
                        "anomaly_id": "M3A-m1_recovery_rate-overall-ALL",
                        "metric_code": "m1_recovery_rate",
                        "metric_name_cn": "M1 回收率",
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return anomaly_path


def test_attribution_analyzer_can_run(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    run = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7")
    assert run.results


def test_attribution_output_schema_complete(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    result = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7").results[0]
    assert set(result) == {
        "attribution_id",
        "target_anomaly_id",
        "target_metric_code",
        "target_metric_name_cn",
        "dimension_name",
        "dimension_value",
        "baseline_value",
        "recent_value",
        "contribution_score",
        "contribution_rank",
        "evidence",
        "business_interpretation",
        "recommended_action",
        "confidence",
        "notes",
    }


def test_recovery_rate_d7_outputs_top_3_drivers(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    run = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7")
    assert len(run.results) >= 3


def test_contribution_score_not_empty(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    run = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7")
    assert all(item["contribution_score"] is not None for item in run.results)


def test_evidence_not_empty(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    run = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7")
    assert all(item["evidence"] for item in run.results)


def test_missing_fields_does_not_crash(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    (tmp_path / "dim" / "dim_customer.parquet").unlink()
    run = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7")
    assert run.results
    assert run.warnings


def test_markdown_summary_can_render(tmp_path: Path) -> None:
    anomaly_path = build_attribution_fixture(tmp_path)
    run = AttributionAnalyzer(data_root=tmp_path, anomaly_json=anomaly_path).analyze("recovery_rate_d7")
    markdown = render_markdown(run.results, run.warnings)
    assert "# M1 D7 回收率下降归因摘要" in markdown
