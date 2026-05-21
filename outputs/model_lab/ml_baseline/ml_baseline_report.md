# M6-D2 D7 Recovery Baseline Diagnostics

## Demo Disclaimer

- synthetic data only
- no real customer data
- no real model deployment
- no automated decisioning
- no collection automation
- no real financial conclusion
- synthetic data boundary: all inputs are generated offline demo data under `synthetic_data/`

## Dataset Summary

- **sample_count**：30000
- **positive_rate**：28.0167%
- **feature_count**：34
- **grain**：loan_id / 借据级

## Target Definition

- **target**：is_recovered_d7
- **definition**：1 if dws_loan_status_snapshot_di.repaid_amount_d7 > 0 else 0
- **evaluation-only fields**：repaid_amount_d7, recovery_rate_d7

## Business Feature Groups

- **loan features**：product_code, channel_code, loan_amount, loan_term, interest_rate, mob, vintage_month, due_amount, dpd_bucket
- **customer synthetic profile features**：age_group, gender, province, city, occupation_type, customer_segment, risk_level_current
- **postloan score features**：postloan_c_score, score_level
- **assignment context features**：initial_dpd_bucket, initial_outstanding_amount, balance_segment, current_vendor_id, current_line_id
- **synthetic governance labels**：protect_flag, sensitive_flag
- **recent process window features**：action_count, connected_count, ai_action_count, ptp_count, ptp_fulfilled_count, complaint_count, connect_rate, ai_coverage_rate, ptp_fulfillment_rate

## Leakage Control

- D7 result fields are target / evaluation only and are excluded from model features.
- loan_id, customer_id, case_id and masked/hash identity columns are excluded from model features.
- case features are joined through one main loan mapping per loan_id to avoid one-to-many sample inflation.
- current_vendor_id and current_line_id are assignment context signals, not customer intrinsic risk factors.
- protect_flag and sensitive_flag are synthetic labels, not real sensitive identity fields.
- Process window features are aggregated from the recent 7-day window ending on case_create_date and do not use repayment amount/date fields.

## Model Comparison

- **logistic**
  - AUC：0.539783
  - KS：0.072591
  - PR-AUC：0.304289
  - precision：0.300023
  - recall：0.615897
  - f1：0.403492
- **random_forest**
  - AUC：0.540511
  - KS：0.077699
  - PR-AUC：0.301325
  - precision：0.299533
  - recall：0.427416
  - f1：0.352226
- **best_model**：random_forest

## Best Model Metrics

- **model_type**：random_forest
- **AUC**：0.540511
- **KS**：0.077699
- **PR-AUC**：0.301325
- **precision**：0.299533
- **recall**：0.427416
- **f1**：0.352226
- **confusion_matrix**：tn=3299, fp=2100, fn=1203, tp=898

## Feature Diagnostics

- **logistic**
  - top_n：10
  - vintage_month_top_feature_count：10 / 10
  - vintage_month_top_feature_share：100.00%
  - vintage_month_top_importance_share：100.00%
  - vintage_month_artifact_warning：True
- **random_forest**
  - top_n：10
  - vintage_month_top_feature_count：0 / 10
  - vintage_month_top_feature_share：0.00%
  - vintage_month_top_importance_share：0.00%
  - vintage_month_artifact_warning：False
- **top_n**：10
- **vintage_month_top_feature_count**：0 / 10
- **vintage_month_top_feature_share**：0.00%
- **vintage_month_top_importance_share**：0.00%
- **vintage_month_artifact_warning**：True
- **interpretation**：at least one model shows vintage_month dominance and may reflect synthetic batch/time artifact

## Vintage Month Artifact Warning

- vintage_month is useful for demo diagnostics because it exposes whether synthetic calendar batches are driving separation.
- vintage_month should not be the final business explanation core; it may reflect batch/time artifact rather than customer or operation behavior.
- If vintage_month dominates top features, explain it as a synthetic-data diagnostic finding, not as a deployable policy reason.

## Decile Lift Table

- **decile 1**：sample_count=750, positive_rate=0.304000, lift=1.085198, cumulative_capture_rate=0.108520
- **decile 2**：sample_count=750, positive_rate=0.317333, lift=1.132794, cumulative_capture_rate=0.221799
- **decile 3**：sample_count=750, positive_rate=0.281333, lift=1.004284, cumulative_capture_rate=0.322228
- **decile 4**：sample_count=750, positive_rate=0.296000, lift=1.056640, cumulative_capture_rate=0.427891
- **decile 5**：sample_count=750, positive_rate=0.308000, lift=1.099476, cumulative_capture_rate=0.537839
- **decile 6**：sample_count=750, positive_rate=0.312000, lift=1.113755, cumulative_capture_rate=0.649215
- **decile 7**：sample_count=750, positive_rate=0.288000, lift=1.028082, cumulative_capture_rate=0.752023
- **decile 8**：sample_count=750, positive_rate=0.242667, lift=0.866254, cumulative_capture_rate=0.838648
- **decile 9**：sample_count=750, positive_rate=0.228000, lift=0.813898, cumulative_capture_rate=0.920038
- **decile 10**：sample_count=750, positive_rate=0.224000, lift=0.799619, cumulative_capture_rate=1.000000

## Feature Importance

- **num__due_amount**：importance=0.101177, signed_weight=0.101177
- **num__loan_amount**：importance=0.097489, signed_weight=0.097489
- **num__interest_rate**：importance=0.096204, signed_weight=0.096204
- **num__mob**：importance=0.061015, signed_weight=0.061015
- **num__postloan_c_score**：importance=0.056374, signed_weight=0.056374
- **num__initial_outstanding_amount**：importance=0.037247, signed_weight=0.037247
- **num__loan_term**：importance=0.035445, signed_weight=0.035445
- **cat__product_code_P_CASH**：importance=0.015303, signed_weight=0.015303
- **cat__occupation_type_工薪**：importance=0.014703, signed_weight=0.014703
- **cat__customer_segment_复借**：importance=0.014681, signed_weight=0.014681

## Why Baseline AUC Is Modest

- The data is synthetic and optimized for workflow demonstration, not for strong predictive signal.
- The D7 target is a broad recovery outcome, while many available signals are assignment or process context rather than direct willingness-to-pay features.
- Recent process features are useful for interview storytelling, but their observation window should be tightened before any production-like interpretation.
- vintage_month concentration indicates possible synthetic batch effects, so business interpretation should emphasize diagnostics rather than overclaiming predictive power.

## Business Interpretation

- This baseline ranks synthetic loans by probability of D7 recovery and is suitable for offline model-readiness demonstration only.
- Higher-ranked deciles should show higher observed recovery rate if the baseline has usable separation.
- Assignment and process features can help explain operational patterns, but they should not be interpreted as customer intrinsic risk attributes.

## Known Limitations

- Synthetic data can validate pipeline feasibility, not real-world predictive power.
- The model is not calibrated for production decisioning.
- Missing postloan scores are imputed by the preprocessing pipeline.
- Process features use a demo-friendly 7-day window ending on case_create_date; if upstream timing is not strict, they should be treated as diagnostic-only.
- No real customer data, LLM context, collection automation or deployment path is involved.

## Next Steps

- Add time-based validation once the synthetic calendar design supports a stricter observation cutoff.
- Add segment-level diagnostics for score_level, dpd_bucket, vendor and line stability.
- Consider removing or bucketing vintage_month in a later robustness check if artifact dominance remains high.

_Generated at 2026-05-21T02:10:42+00:00_
