# M6-D2 D7 Payment Response Baseline Diagnostics

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
- **positive_rate**：27.3667%
- **feature_count**：38
- **exclude_vintage_month**：True
- **grain**：loan_id / 借据级

## Target Definition

- **target**：is_recovered_d7
- **semantic name**：d7_any_payment_response
- **definition**：1 if dws_loan_status_snapshot_di.repaid_amount_d7 > 0 else 0
- **evaluation-only fields**：repaid_amount_d7, recovery_rate_d7
- **boundary**：this target means any D7 payment response; it is not full cure, not DPD cleared to 0, and not complete recovery. Partial payment is counted as positive.

## Business Feature Groups

- **loan features**：product_code, channel_code, loan_amount, loan_term, interest_rate, mob, due_amount, dpd_bucket
- **customer synthetic profile features**：age_group, gender, province, city, occupation_type, customer_segment, risk_level_current
- **postloan score features**：postloan_c_score, score_level, score_x_connect_rate
- **assignment context features**：initial_dpd_bucket, initial_outstanding_amount, balance_segment, current_vendor_id, current_line_id
- **synthetic governance labels**：protect_flag, sensitive_flag
- **recent process window features**：action_count_7d, connected_count_7d, connect_rate_7d, ptp_count_7d, ptp_rate_7d, days_since_last_action, ai_action_count, complaint_count, ai_coverage_rate

## Leakage Control

- D7 result fields are target / evaluation only and are excluded from model features.
- loan_id, customer_id, case_id and masked/hash identity columns are excluded from model features.
- case features are joined through one main loan mapping per loan_id to avoid one-to-many sample inflation.
- current_vendor_id and current_line_id are assignment context signals, not customer intrinsic risk factors.
- protect_flag and sensitive_flag are synthetic labels, not real sensitive identity fields.
- postloan_c_score is a synthetic post-loan C-score proxy, not a real trained C-card model.
- ODS action window features are aggregated from the 7-day window ending on observation_date and do not use repayment amount/date fields or PTP fulfillment fields.

## Model Comparison

- **logistic**
  - AUC：0.569109
  - KS：0.106997
  - PR-AUC：0.320282
  - precision：0.308945
  - recall：0.619094
  - f1：0.412194
- **random_forest**
  - AUC：0.566544
  - KS：0.106333
  - PR-AUC：0.314291
  - precision：0.321903
  - recall：0.425231
  - f1：0.366422
- **best_model**：logistic

## Best Model Metrics

- **model_type**：logistic
- **AUC**：0.569109
- **KS**：0.106997
- **PR-AUC**：0.320282
- **precision**：0.308945
- **recall**：0.619094
- **f1**：0.412194
- **confusion_matrix**：tn=2604, fp=2843, fn=782, tp=1271

## Feature Diagnostics

- **logistic**
  - top_n：10
  - vintage_month_top_feature_count：0 / 10
  - vintage_month_top_feature_share：0.00%
  - vintage_month_top_importance_share：0.00%
  - vintage_month_artifact_warning：False
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
- **vintage_month_artifact_warning**：False
- **interpretation**：vintage_month is present but does not dominate top features

## Vintage Month Artifact Warning

- vintage_month is useful for demo diagnostics because it exposes whether synthetic calendar batches are driving separation.
- vintage_month should not be the final business explanation core; it may reflect batch/time artifact rather than customer or operation behavior.
- If vintage_month dominates top features, explain it as a synthetic-data diagnostic finding, not as a deployable policy reason.

## Decile Lift Table

- **decile 1**：sample_count=750, positive_rate=0.350667, lift=1.281052, cumulative_capture_rate=0.128105
- **decile 2**：sample_count=750, positive_rate=0.330667, lift=1.207988, cumulative_capture_rate=0.248904
- **decile 3**：sample_count=750, positive_rate=0.313333, lift=1.144666, cumulative_capture_rate=0.363371
- **decile 4**：sample_count=750, positive_rate=0.302667, lift=1.105699, cumulative_capture_rate=0.473941
- **decile 5**：sample_count=750, positive_rate=0.250667, lift=0.915733, cumulative_capture_rate=0.565514
- **decile 6**：sample_count=750, positive_rate=0.285333, lift=1.042377, cumulative_capture_rate=0.669752
- **decile 7**：sample_count=750, positive_rate=0.248000, lift=0.905991, cumulative_capture_rate=0.760351
- **decile 8**：sample_count=750, positive_rate=0.237333, lift=0.867024, cumulative_capture_rate=0.847053
- **decile 9**：sample_count=750, positive_rate=0.228000, lift=0.832927, cumulative_capture_rate=0.930346
- **decile 10**：sample_count=750, positive_rate=0.190667, lift=0.696542, cumulative_capture_rate=1.000000

## Feature Importance

- **cat__risk_level_current_D**：importance=0.359167, signed_weight=-0.359167
- **cat__risk_level_current_A**：importance=0.246327, signed_weight=0.246327
- **cat__balance_segment_HIGH**：importance=0.137339, signed_weight=-0.137339
- **cat__risk_level_current_B**：importance=0.135838, signed_weight=0.135838
- **num__connect_rate_7d**：importance=0.120332, signed_weight=0.120332
- **cat__current_vendor_id_V_B**：importance=0.117085, signed_weight=-0.117085
- **cat__dpd_bucket_M3+**：importance=0.110088, signed_weight=-0.110088
- **cat__initial_dpd_bucket_M3+**：importance=0.110088, signed_weight=-0.110088
- **cat__occupation_type_自由职业**：importance=0.098029, signed_weight=-0.098029
- **cat__age_group_46-55**：importance=0.091239, signed_weight=-0.091239

## Why Baseline AUC Is Modest

- The data is synthetic and optimized for workflow demonstration, not for strong predictive signal.
- The D7 target is a broad recovery outcome, while many available signals are assignment or process context rather than direct willingness-to-pay features.
- Recent process features are useful for interview storytelling, but their observation window should be tightened before any production-like interpretation.
- vintage_month concentration indicates possible synthetic batch effects, so business interpretation should emphasize diagnostics rather than overclaiming predictive power.

## Business Interpretation

- This baseline ranks synthetic loans by probability of D7 any-payment response and is suitable for offline model-readiness demonstration only.
- Higher-ranked deciles should show higher observed recovery rate if the baseline has usable separation.
- Assignment and process features can help explain operational patterns, but they should not be interpreted as customer intrinsic risk attributes.

## Known Limitations

- Synthetic data can validate pipeline feasibility, not real-world predictive power.
- The model is not calibrated for production decisioning.
- Missing postloan scores are imputed by the preprocessing pipeline.
- Process features use a demo-friendly 7-day window ending on case_create_date; if upstream timing is not strict, they should be treated as diagnostic-only.
- The target is not a cure-to-current label; supporting that target would require synthetic DPD state transitions and warehouse target refinement.
- No real customer data, LLM context, collection automation or deployment path is involved.

## Next Steps

- Add time-based validation once the synthetic calendar design supports a stricter observation cutoff.
- Add segment-level diagnostics for score_level, dpd_bucket, vendor and line stability.
- Consider removing or bucketing vintage_month in a later robustness check if artifact dominance remains high.

_Generated at 2026-05-24T03:14:30+00:00_
