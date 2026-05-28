"""M3-A statistical anomaly detector."""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import pandas as pd

from riskops.engines.anomaly.models import AnomalyConfig, AnomalyResult
from riskops.engines.anomaly.rules import (
    classify_severity,
    is_window_anomaly,
    load_anomaly_config,
    relative_change,
    trend_drop,
    window_bounds,
    window_means,
)
from riskops.metrics.dictionary import metric_by_code

ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = ROOT / "synthetic_data"


@dataclass
class DetectionRun:
    results: list[AnomalyResult]
    warnings: list[str]


class AnomalyDetector:
    def __init__(
        self,
        data_root: Path = DATA_ROOT,
        config_path: Path | None = None,
        recent_window_days: int | None = None,
        baseline_window_days: int | None = None,
    ) -> None:
        self.data_root = data_root
        config = load_anomaly_config(config_path) if config_path else load_anomaly_config()
        if recent_window_days is not None:
            config = replace(config, recent_window_days=recent_window_days)
        if baseline_window_days is not None:
            config = replace(config, baseline_window_days=baseline_window_days)
        self.config = config
        self.metric_definitions = metric_by_code()
        self.warnings: list[str] = []

    def detect(self) -> DetectionRun:
        self.warnings = []
        results: list[AnomalyResult] = []
        checks = [
            self._detect_m1_recovery_drop,
            self._detect_vendor_b_connect_drop,
            self._detect_east_capacity_spike,
            self._detect_high_balance_high_risk_share,
            self._detect_ai_call_coverage_drop,
            self._detect_reduction_usage_drop,
            self._detect_ptp_keep_drop,
        ]
        for check in checks:
            try:
                anomaly = check()
            except (FileNotFoundError, KeyError, ValueError) as exc:
                self.warnings.append(f"{check.__name__} skipped: {exc}")
                continue
            if anomaly is not None:
                results.append(anomaly)
        return DetectionRun(results=results, warnings=self.warnings)

    def _read_table(self, layer: str, table: str) -> pd.DataFrame:
        for suffix in ["parquet", "csv"]:
            path = self.data_root / layer / f"{table}.{suffix}"
            if path.exists():
                return pd.read_parquet(path) if suffix == "parquet" else pd.read_csv(path)
        raise FileNotFoundError(f"missing table file: {layer}/{table}")

    def _metric_name(self, metric_code: str, fallback: str) -> str:
        definition = self.metric_definitions.get(metric_code)
        if definition:
            return str(definition["metric_name_cn"])
        return fallback

    def _window_anomaly(
        self,
        frame: pd.DataFrame,
        *,
        metric_code: str,
        metric_name_cn: str,
        value_col: str,
        direction: str,
        anomaly_type: str,
        dimension_name: str,
        dimension_value: str,
        evidence_table: str,
        explanation_template: str,
        recommended_next_step: str,
        min_relative_change: float | None = None,
        min_absolute_change_pct: float | None = None,
    ) -> AnomalyResult | None:
        required = {"stat_date", value_col}
        missing = required - set(frame.columns)
        if missing:
            raise KeyError(f"{evidence_table} missing columns: {sorted(missing)}")
        baseline_value, recent_value, recent_window, baseline_window = window_means(
            frame,
            "stat_date",
            value_col,
            self.config.recent_window_days,
            self.config.baseline_window_days,
        )
        if not is_window_anomaly(
            baseline_value,
            recent_value,
            direction,
            self.config,
            min_relative_change=min_relative_change,
            min_absolute_change_pct=min_absolute_change_pct,
        ):
            return None
        absolute_change = recent_value - baseline_value
        rel_change = relative_change(baseline_value, recent_value)
        severity = classify_severity(absolute_change, rel_change, self.config)
        return AnomalyResult(
            anomaly_id=f"M3A-{metric_code}-{dimension_name}-{dimension_value}".replace(" ", "_"),
            metric_code=metric_code,
            metric_name_cn=metric_name_cn,
            anomaly_type=anomaly_type,  # type: ignore[arg-type]
            severity=severity,
            dimension_name=dimension_name,
            dimension_value=dimension_value,
            baseline_value=round(baseline_value, 6),
            recent_value=round(recent_value, 6),
            absolute_change=round(absolute_change, 6),
            relative_change=round(rel_change, 6),
            recent_window=recent_window,
            baseline_window=baseline_window,
            evidence_table=evidence_table,
            explanation=explanation_template.format(
                baseline_value=baseline_value,
                recent_value=recent_value,
                absolute_change=absolute_change,
                relative_change=rel_change,
            ),
            recommended_next_step=recommended_next_step,
        )

    def _detect_m1_recovery_drop(self) -> AnomalyResult | None:
        dashboard = self._read_table("ads", "ads_postloan_dashboard_di")
        metric_code = "m1_recovery_rate" if "m1_recovery_rate" in dashboard.columns else "recovery_rate_d7"
        return self._window_anomaly(
            dashboard,
            metric_code=metric_code,
            metric_name_cn=self._metric_name(metric_code, "M1 D7 回收率"),
            value_col=metric_code,
            direction="drop",
            anomaly_type="window_compare",
            dimension_name="overall",
            dimension_value="ALL",
            evidence_table="ads_postloan_dashboard_di",
            explanation_template="最近窗口均值 {recent_value:.2%} 低于基线 {baseline_value:.2%}，变化 {absolute_change:.2%}。",
            recommended_next_step="进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。",
        )

    def _detect_vendor_b_connect_drop(self) -> AnomalyResult | None:
        vendor = self._read_table("ads", "ads_vendor_performance_di")
        if "vendor_id" not in vendor.columns:
            raise KeyError("ads_vendor_performance_di missing vendor_id")
        vendor_b = vendor[vendor["vendor_id"].eq("V_B")]
        if vendor_b.empty:
            raise ValueError("ads_vendor_performance_di has no V_B rows")
        return self._window_anomaly(
            vendor_b,
            metric_code="connect_rate",
            metric_name_cn=self._metric_name("connect_rate", "接通率"),
            value_col="connect_rate",
            direction="drop",
            anomaly_type="window_compare",
            dimension_name="vendor_id",
            dimension_value="V_B",
            evidence_table="ads_vendor_performance_di",
            explanation_template="供应商 B 最近接通率 {recent_value:.2%}，低于基线 {baseline_value:.2%}。",
            recommended_next_step="下钻供应商 B 的线路、催员和触达时段，验证执行资源或号码质量问题。",
        )

    def _detect_east_capacity_spike(self) -> AnomalyResult | None:
        capacity = self._read_table("dws", "dws_vendor_line_capacity_di")
        required = {"stat_date", "region", "active_case_count", "active_collector_count"}
        missing = required - set(capacity.columns)
        if missing:
            raise KeyError(f"dws_vendor_line_capacity_di missing columns: {sorted(missing)}")
        east = capacity[capacity["region"].eq("华东")].copy()
        if east.empty:
            raise ValueError("dws_vendor_line_capacity_di has no 华东 rows")
        daily = east.groupby("stat_date", as_index=False).agg(
            active_case_count=("active_case_count", "sum"),
            active_collector_count=("active_collector_count", "sum"),
        )
        daily["case_per_collector"] = daily["active_case_count"] / daily["active_collector_count"].replace(0, pd.NA)
        return self._window_anomaly(
            daily,
            metric_code="avg_case_per_collector",
            metric_name_cn="华东线路人均案量",
            value_col="case_per_collector",
            direction="increase",
            anomaly_type="spike",
            dimension_name="region",
            dimension_value="华东",
            evidence_table="dws_vendor_line_capacity_di",
            explanation_template="华东线路人均案量从 {baseline_value:.2f} 升至 {recent_value:.2f}，产能压力上升。",
            recommended_next_step="下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。",
        )

    def _detect_high_balance_high_risk_share(self) -> AnomalyResult | None:
        customer = self._read_table("dws", "dws_customer_status_snapshot_di")
        required = {"stat_date", "customer_id", "total_outstanding_amount", "risk_level"}
        missing = required - set(customer.columns)
        if missing:
            raise KeyError(f"dws_customer_status_snapshot_di missing columns: {sorted(missing)}")
        frame = customer.copy()
        high_balance_threshold = pd.to_numeric(frame["total_outstanding_amount"], errors="coerce").median() * 2
        frame["high_balance_high_risk"] = (
            (pd.to_numeric(frame["total_outstanding_amount"], errors="coerce") >= high_balance_threshold)
            & frame["risk_level"].eq("high")
        )
        daily = frame.groupby("stat_date", as_index=False).agg(
            customer_count=("customer_id", "nunique"),
            high_balance_high_risk_count=("high_balance_high_risk", "sum"),
        )
        daily["high_balance_high_risk_share"] = daily["high_balance_high_risk_count"] / daily["customer_count"].replace(0, pd.NA)
        baseline_value, recent_value, recent_window, baseline_window = window_means(
            daily,
            "stat_date",
            "high_balance_high_risk_share",
            self.config.recent_window_days,
            self.config.baseline_window_days,
        )
        absolute_change = recent_value - baseline_value
        if absolute_change < 0.05:
            return None
        rel_change = relative_change(baseline_value, recent_value)
        severity = "high" if absolute_change >= 0.07 else "medium"
        return AnomalyResult(
            anomaly_id="M3A-high_balance_high_risk_share-overall-ALL",
            metric_code="high_balance_high_risk_share",
            metric_name_cn="高余额高风险客群占比",
            anomaly_type="window_compare",
            severity=severity,
            dimension_name="overall",
            dimension_value="ALL",
            baseline_value=round(baseline_value, 6),
            recent_value=round(recent_value, 6),
            absolute_change=round(absolute_change, 6),
            relative_change=round(rel_change, 6),
            recent_window=recent_window,
            baseline_window=baseline_window,
            evidence_table="dws_customer_status_snapshot_di",
            explanation=f"高余额高风险客群占比从 {baseline_value:.2%} 升至 {recent_value:.2%}。",
            recommended_next_step="进入后续归因阶段后拆分余额段、risk_level 和入案批次，识别结构变化贡献。",
        )

    def _detect_ai_call_coverage_drop(self) -> AnomalyResult | None:
        process = self._read_table("dws", "dws_collection_process_wide_di")
        required = {"stat_date", "action_count", "ai_action_count"}
        missing = required - set(process.columns)
        if missing:
            raise KeyError(f"dws_collection_process_wide_di missing columns: {sorted(missing)}")
        daily = process.groupby("stat_date", as_index=False).agg(action_count=("action_count", "sum"), ai_action_count=("ai_action_count", "sum"))
        daily["ai_call_coverage"] = daily["ai_action_count"] / daily["action_count"].replace(0, pd.NA)
        return self._window_anomaly(
            daily,
            metric_code="ai_call_coverage",
            metric_name_cn="AI 外呼覆盖率",
            value_col="ai_call_coverage",
            direction="drop",
            anomaly_type="window_compare",
            dimension_name="action_type",
            dimension_value="AI_OUTBOUND",
            evidence_table="dws_collection_process_wide_di",
            explanation_template="AI 外呼覆盖率从 {baseline_value:.2%} 降至 {recent_value:.2%}。",
            recommended_next_step="检查 AI 外呼线路容量、分案策略和人工替代触达占比。",
        )

    def _detect_reduction_usage_drop(self) -> AnomalyResult | None:
        reduction = self._read_table("ads", "ads_reduction_roi_di")
        return self._window_anomaly(
            reduction,
            metric_code="reduction_usage_rate",
            metric_name_cn=self._metric_name("reduction_usage_rate", "减免使用率"),
            value_col="reduction_usage_rate",
            direction="drop",
            anomaly_type="window_compare",
            dimension_name="overall",
            dimension_value="ALL",
            evidence_table="ads_reduction_roi_di",
            explanation_template="减免使用率从 {baseline_value:.2%} 降至 {recent_value:.2%}。",
            recommended_next_step="下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。",
        )

    def _detect_ptp_keep_drop(self) -> AnomalyResult | None:
        dashboard = self._read_table("ads", "ads_postloan_dashboard_di")
        anomaly = self._window_anomaly(
            dashboard,
            metric_code="ptp_keep_rate",
            metric_name_cn=self._metric_name("ptp_keep_rate", "PTP 履约率"),
            value_col="ptp_keep_rate",
            direction="drop",
            anomaly_type="window_compare",
            dimension_name="overall",
            dimension_value="ALL",
            evidence_table="ads_postloan_dashboard_di",
            explanation_template="PTP 履约率从 {baseline_value:.2%} 降至 {recent_value:.2%}。",
            recommended_next_step="下钻承诺还款客户的风险等级、余额段、催员和减免使用情况。",
        )
        if anomaly is not None:
            return anomaly
        if trend_drop(dashboard, "ptp_keep_rate"):
            self.warnings.append("ptp_keep_rate has recent consecutive declines but does not exceed configured window threshold")
        return None

    def _detect_template_complaint_ratio(self) -> AnomalyResult | None:
        action = self._read_table("dwd", "dwd_collection_action_detail_di")
        complaint = self._read_table("dwd", "dwd_complaint_detail_di")
        required_action = {"action_date", "action_type", "template_id", "action_id"}
        required_complaint = {"complaint_date", "template_id", "complaint_id"}
        missing_action = required_action - set(action.columns)
        missing_complaint = required_complaint - set(complaint.columns)
        if missing_action or missing_complaint:
            raise KeyError(f"template complaint inputs missing action={sorted(missing_action)} complaint={sorted(missing_complaint)}")

        sms = action[action["action_type"].eq("SMS") & action["template_id"].notna()].copy()
        if sms.empty:
            raise ValueError("no SMS template actions")
        baseline_start, baseline_end, recent_start, recent_end = window_bounds(sms, "action_date", self.config.recent_window_days, self.config.baseline_window_days)
        sms["action_date"] = pd.to_datetime(sms["action_date"], errors="coerce")
        complaint = complaint[complaint["template_id"].notna()].copy()
        complaint["complaint_date"] = pd.to_datetime(complaint["complaint_date"], errors="coerce")
        recent_sms = sms[(sms["action_date"] >= recent_start) & (sms["action_date"] <= recent_end)]
        recent_complaint = complaint[(complaint["complaint_date"] >= recent_start) & (complaint["complaint_date"] <= recent_end)]
        by_template = recent_sms.groupby("template_id", as_index=False).agg(action_count=("action_id", "nunique"))
        complaint_count = recent_complaint.groupby("template_id", as_index=False).agg(complaint_count=("complaint_id", "nunique"))
        by_template = by_template.merge(complaint_count, on="template_id", how="left").fillna({"complaint_count": 0})
        if len(by_template) < 2:
            raise ValueError("template-level complaint detection needs at least 2 templates")
        by_template["complaint_rate"] = by_template["complaint_count"] / by_template["action_count"].replace(0, pd.NA)
        global_rate = float(by_template["complaint_count"].sum() / by_template["action_count"].sum())
        if global_rate <= 0:
            raise ValueError("recent global template complaint rate is zero")
        top = by_template.sort_values("complaint_rate", ascending=False).iloc[0]
        recent_value = float(top["complaint_rate"])
        if recent_value < global_rate * self.config.complaint_multiplier_threshold:
            return None
        absolute_change = recent_value - global_rate
        rel_change = relative_change(global_rate, recent_value)
        severity = classify_severity(absolute_change, rel_change, self.config)
        template_id = str(top["template_id"])
        return AnomalyResult(
            anomaly_id=f"M3A-complaint_per_10k_cases-template_id-{template_id}",
            metric_code="complaint_per_10k_cases",
            metric_name_cn=self._metric_name("complaint_per_10k_cases", "万案投诉率"),
            anomaly_type="ratio_to_average",
            severity=severity,
            dimension_name="template_id",
            dimension_value=template_id,
            baseline_value=round(global_rate * 10_000, 6),
            recent_value=round(recent_value * 10_000, 6),
            absolute_change=round(absolute_change * 10_000, 6),
            relative_change=round(rel_change, 6),
            recent_window=f"{recent_start.date()}~{recent_end.date()}",
            baseline_window=f"recent_global_average:{recent_start.date()}~{recent_end.date()}",
            evidence_table="dwd_collection_action_detail_di+dwd_complaint_detail_di",
            explanation=f"{template_id} 最近万案投诉率为 {recent_value * 10_000:.2f}，约为全模板均值 {global_rate * 10_000:.2f} 的 {recent_value / global_rate:.2f} 倍。",
            recommended_next_step="下钻该模板的发送供应商、发送时段、投诉等级和具体话术，进入合规复核。",
        )
