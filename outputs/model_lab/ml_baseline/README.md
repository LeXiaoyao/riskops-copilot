# M6-D ML Baseline Outputs

## Demo Boundary

- synthetic data only
- no real customer data
- no PII in model features
- no production model claim
- no automated financial or collection decisioning

## Files

- **metrics.json**：compact machine-readable metrics for CLI and briefing.
- **model_metrics.json**：backward-compatible full metrics payload.
- **feature_importance.csv**：model feature ranking.
- **lift_table.csv**：decile lift diagnostics.
- **ml_baseline_report.md**：human-readable diagnostic report.
- **robustness_check.json / .md**：vintage-month artifact robustness check.

## Key Metrics

- **row_count**：30000
- **positive_rate**：0.274933
- **train_test_split**：test_size=0.25, random_seed=20260521
- **AUC**：0.573920
- **KS**：0.110316
- **top_decile_capture_rate**：0.127061

## Leakage Guard Summary

- **pii_features_blocked**：True
- **outcome_features_blocked**：True
- **score_date_guard**：latest_score_on_or_before_observation_date_with_missing_impute_fallback
