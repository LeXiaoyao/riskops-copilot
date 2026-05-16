from __future__ import annotations

from scripts.validate_metric_quality import REQUIRED_FIELDS, validate_p0_calculators, validate_required_fields, validate_unique_codes
from riskops.metrics.dictionary import load_metric_dictionary


EXPECTED_CODES = {
    "due_account_count",
    "due_loan_count",
    "due_total_amount",
    "collection_entry_rate",
    "recovery_rate_d7",
    "recovery_rate_d15",
    "recovery_rate_d30",
    "m1_recovery_rate",
    "call_coverage_rate",
    "valid_coverage_rate",
    "connect_rate",
    "valid_contact_rate",
    "first_contact_hours",
    "ptp_rate",
    "ptp_keep_rate",
    "avg_call_duration_per_call",
    "avg_call_duration_per_collector",
    "collector_productivity",
    "complaint_rate",
    "complaint_per_10k_cases",
    "risk_phrase_hit_rate",
    "qa_fail_rate",
    "over_frequency_contact_rate",
    "reduction_usage_rate",
    "reduction_recovery_rate",
    "reduction_roi",
}


def test_metric_dictionary_contains_phase1_codes() -> None:
    metrics = load_metric_dictionary()
    codes = {item["metric_code"] for item in metrics}
    assert EXPECTED_CODES == codes


def test_metric_dictionary_required_fields_and_uniqueness() -> None:
    metrics = load_metric_dictionary()
    validate_unique_codes(metrics)
    validate_required_fields(metrics)
    for item in metrics:
        assert REQUIRED_FIELDS <= set(item)


def test_p0_metrics_have_calculators() -> None:
    validate_p0_calculators(load_metric_dictionary())
