# M6-D1 D7 Recovery Prediction Baseline

## Demo Disclaimer

- synthetic data only
- no real customer data
- no real model deployment
- no automated decisioning
- no collection automation
- no real financial conclusion

## Dataset Summary

- **sample_count**：30000
- **positive_rate**：28.0167%
- **feature_count**：25
- **grain**：loan_id / 借据级

## Target Definition

- **target**：is_recovered_d7
- **definition**：1 if dws_loan_status_snapshot_di.repaid_amount_d7 > 0 else 0
- **evaluation-only fields**：repaid_amount_d7, recovery_rate_d7

## Feature Groups

- **loan features**：product_code, channel_code, loan_amount, loan_term, interest_rate, mob, vintage_month, due_amount, dpd_bucket
- **customer synthetic profile features**：age_group, gender, province, city, occupation_type, customer_segment, risk_level_current
- **postloan score features**：postloan_c_score, score_level
- **assignment context features**：initial_dpd_bucket, initial_outstanding_amount, balance_segment, current_vendor_id, current_line_id
- **synthetic governance labels**：protect_flag, sensitive_flag

## Leakage Control

- D7 result fields are target / evaluation only and are excluded from model features.
- loan_id, customer_id, case_id and masked/hash identity columns are excluded from model features.
- case features are joined through one main loan mapping per loan_id to avoid one-to-many sample inflation.
- current_vendor_id and current_line_id are assignment context signals, not customer intrinsic risk factors.
- protect_flag and sensitive_flag are synthetic labels, not real sensitive identity fields.

## Model Metrics

- **model_type**：logistic
- **AUC**：0.538709
- **KS**：0.069541
- **PR-AUC**：0.302821
- **precision**：0.300562
- **recall**：0.611138
- **f1**：0.402950
- **confusion_matrix**：tn=2411, fp=2988, fn=817, tp=1284

## Decile Lift Table

- **decile 1**：sample_count=750, positive_rate=0.304000, lift=1.085198, cumulative_capture_rate=0.108520
- **decile 2**：sample_count=750, positive_rate=0.314667, lift=1.123275, cumulative_capture_rate=0.220847
- **decile 3**：sample_count=750, positive_rate=0.301333, lift=1.075678, cumulative_capture_rate=0.328415
- **decile 4**：sample_count=750, positive_rate=0.302667, lift=1.080438, cumulative_capture_rate=0.436459
- **decile 5**：sample_count=750, positive_rate=0.285333, lift=1.018563, cumulative_capture_rate=0.538315
- **decile 6**：sample_count=750, positive_rate=0.296000, lift=1.056640, cumulative_capture_rate=0.643979
- **decile 7**：sample_count=750, positive_rate=0.285333, lift=1.018563, cumulative_capture_rate=0.745835
- **decile 8**：sample_count=750, positive_rate=0.262667, lift=0.937649, cumulative_capture_rate=0.839600
- **decile 9**：sample_count=750, positive_rate=0.217333, lift=0.775821, cumulative_capture_rate=0.917182
- **decile 10**：sample_count=750, positive_rate=0.232000, lift=0.828177, cumulative_capture_rate=1.000000

## Feature Importance

- **cat__vintage_month_2023-09**：importance=0.287576, signed_weight=-0.287576
- **cat__vintage_month_2025-12**：importance=0.237456, signed_weight=-0.237456
- **cat__vintage_month_2025-05**：importance=0.193556, signed_weight=0.193556
- **cat__vintage_month_2024-03**：importance=0.182630, signed_weight=0.182630
- **cat__vintage_month_2026-02**：importance=0.169808, signed_weight=-0.169808
- **cat__vintage_month_2026-03**：importance=0.152530, signed_weight=-0.152530
- **cat__vintage_month_2025-02**：importance=0.137944, signed_weight=-0.137944
- **cat__vintage_month_2023-10**：importance=0.137101, signed_weight=0.137101
- **cat__vintage_month_2024-04**：importance=0.124737, signed_weight=0.124737
- **cat__vintage_month_2025-09**：importance=0.120831, signed_weight=0.120831

## Business Interpretation

- This baseline ranks synthetic loans by probability of D7 recovery and is suitable for offline model-readiness demonstration only.
- Higher-ranked deciles should show higher observed recovery rate if the baseline has usable separation.
- Assignment context features can help explain operational allocation patterns, but they should not be interpreted as customer risk attributes.

## Known Limitations

- Synthetic data can validate pipeline feasibility, not real-world predictive power.
- The model is not calibrated for production decisioning.
- Missing postloan scores are imputed by the preprocessing pipeline.
- No real customer data, LLM context, collection automation or deployment path is involved.

## Next Steps

- Add CLI integration only after M6-D1 outputs are accepted.
- Add model card / validation checklist before any future production-like discussion.
- Consider time-based validation in a later M6 task if the synthetic calendar design is expanded.

_Generated at 2026-05-21T01:21:21+00:00_
