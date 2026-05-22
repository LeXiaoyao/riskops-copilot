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
- **positive_rate**：28.1833%
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
  - AUC：0.611519
  - KS：0.187953
  - PR-AUC：0.423339
  - precision：0.360501
  - recall：0.504257
  - f1：0.420430
- **random_forest**
  - AUC：0.613896
  - KS：0.199485
  - PR-AUC：0.425937
  - precision：0.467752
  - recall：0.353359
  - f1：0.402587
- **best_model**：random_forest

## Best Model Metrics

- **model_type**：random_forest
- **AUC**：0.613896
- **KS**：0.199485
- **PR-AUC**：0.425937
- **precision**：0.467752
- **recall**：0.353359
- **f1**：0.402587
- **confusion_matrix**：tn=4536, fp=850, fn=1367, tp=747

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

- **decile 1**：sample_count=750, positive_rate=0.578667, lift=2.052980, cumulative_capture_rate=0.205298
- **decile 2**：sample_count=750, positive_rate=0.386667, lift=1.371807, cumulative_capture_rate=0.342479
- **decile 3**：sample_count=750, positive_rate=0.217333, lift=0.771050, cumulative_capture_rate=0.419584
- **decile 4**：sample_count=750, positive_rate=0.233333, lift=0.827815, cumulative_capture_rate=0.502365
- **decile 5**：sample_count=750, positive_rate=0.250667, lift=0.889309, cumulative_capture_rate=0.591296
- **decile 6**：sample_count=750, positive_rate=0.246667, lift=0.875118, cumulative_capture_rate=0.678808
- **decile 7**：sample_count=750, positive_rate=0.262667, lift=0.931883, cumulative_capture_rate=0.771996
- **decile 8**：sample_count=750, positive_rate=0.234667, lift=0.832545, cumulative_capture_rate=0.855251
- **decile 9**：sample_count=750, positive_rate=0.232000, lift=0.823084, cumulative_capture_rate=0.937559
- **decile 10**：sample_count=750, positive_rate=0.176000, lift=0.624409, cumulative_capture_rate=1.000000

## Feature Importance

- **num__postloan_c_score**：importance=0.122015, signed_weight=0.122015
- **num__log_due_amount**：importance=0.078021, signed_weight=0.078021
- **num__loan_amount**：importance=0.077611, signed_weight=0.077611
- **num__due_amount**：importance=0.072741, signed_weight=0.072741
- **num__interest_rate**：importance=0.062264, signed_weight=0.062264
- **num__initial_outstanding_amount**：importance=0.048378, signed_weight=0.048378
- **num__mob**：importance=0.046251, signed_weight=0.046251
- **num__outstanding_to_loan_ratio**：importance=0.038023, signed_weight=0.038023
- **cat__score_level_D**：importance=0.030346, signed_weight=0.030346
- **num__loan_term**：importance=0.024038, signed_weight=0.024038

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

_Generated at 2026-05-22T09:34:55+00:00_
