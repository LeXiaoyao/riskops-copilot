# M6-D5D Feature Engineering Result

## 1. Goal

M6-D5D adds leakage-safe feature engineering to the offline ML baseline. The goal is not to tune AUC by changing the synthetic target, but to make the model dataset closer to a defensible post-loan modeling setup:

- clarify the target boundary
- add amount and delinquency pressure features
- rebuild process features from prediction-time ODS action windows
- block PTP fulfillment and D7 outcome leakage
- keep `postloan_c_score` framed as a synthetic proxy

No real customer data, LLM, Agent, automated collection action, external dataset, target rewrite, generator change, push, tag, or release is involved.

## 2. Target Boundary

- **field name**：`is_recovered_d7`
- **semantic name**：D7 any-payment response
- **current formula**：`1 if repaid_amount_d7 > 0 else 0`
- **positive rate**：0.281833

This target is not full cure, not DPD cleared to 0, and not complete recovery. Partial payment is counted as a positive label.

A stricter cure-to-current target would require:

```text
repaid_amount_d7 > 0
and dpd_at_observation_date == 0
and dpd_previous_day > 0
```

Current synthetic data does not support that target because `ods_loan_daily_snapshot` is not a full daily panel, synthetic DPD does not fall back to 0 after repayment, read-only estimation found zero cure positives, and `dws_loan_status_snapshot_di.stat_date` aligns with due date rather than D7 window end.

## 3. Feature Changes

### 3.1 Amount And DPD Features

- **log_due_amount**
  - Formula：`log1p(due_amount)`
  - Meaning：nonlinear due amount pressure
- **outstanding_to_loan_ratio**
  - Formula：`initial_outstanding_amount / loan_amount`
  - Meaning：case balance pressure relative to original loan amount
- **days_since_due_date**
  - Formula：`observation_date - due_date`, clipped at 0
  - Meaning：continuous delinquency timing signal
- **dpd_x_log_due_amount**
  - Formula：`days_since_due_date * log_due_amount`
  - Meaning：interaction of delinquency timing and amount pressure

### 3.2 ODS Action Window Features

The process window is rebuilt from `synthetic_data/ods/ods_collection_action.parquet`, not from the older DWS process wide table.

- **observation_date**：`dws_loan_status_snapshot_di.stat_date`
- **join path**：`loan_id -> dim_case_loan_mapping.case_id -> ods_collection_action.case_id`
- **window**：`observation_date - 6 days <= action_time date <= observation_date`

Added process features:

- **action_count_7d**
  - 7-day action count before or on observation date
- **connected_count_7d**
  - 7-day connected action count
- **connect_rate_7d**
  - `connected_count_7d / action_count_7d`, 0 when denominator is 0
- **ptp_count_7d**
  - 7-day PTP count from `ptp_flag`
- **ptp_rate_7d**
  - `ptp_count_7d / action_count_7d`, 0 when denominator is 0
- **days_since_last_action**
  - `observation_date - max(action_time <= observation_date)`
  - Missing when no prior action exists, then handled by the existing model imputer

### 3.3 Score And Process Interaction

- **score_x_connect_rate**
  - Formula：`(postloan_c_score / 100) * connect_rate_7d`
  - Meaning：synthetic risk score proxy crossed with prediction-window reachability

`postloan_c_score` is a synthetic post-loan C-score proxy. It is not a real trained C-card model. The current join still uses the latest score by customer, so `score_date <= observation_date` is a demo assumption to be refined later.

## 4. Leakage Controls

The following fields are blocked from D7 prediction features:

- `repaid_amount_d7`
- `recovery_rate_d7`
- `repay_amount`
- `repay_date`
- `repay_time`
- `ptp_fulfilled_flag`
- `ptp_fulfilled_count`
- `ptp_fulfillment_rate`

PTP features use `ptp_flag` only. PTP fulfillment is treated as a post-event outcome signal and is not used for D7 prediction.

## 5. Baseline Results

### 5.1 With Vintage

- AUC：0.615549
- KS：0.194021
- PR-AUC：0.426304

### 5.2 Without Vintage

- AUC：0.613896
- KS：0.199485
- PR-AUC：0.425937

The with-vintage and without-vintage metrics are close. The best RandomForest model is not materially dependent on `vintage_month`; the logistic model still shows a with-vintage artifact warning, which is kept as a diagnostic signal.

## 6. Top Feature Changes

Top features after the without-vintage run:

1. `num__postloan_c_score`
2. `num__log_due_amount`
3. `num__loan_amount`
4. `num__due_amount`
5. `num__interest_rate`
6. `num__initial_outstanding_amount`
7. `num__mob`
8. `num__outstanding_to_loan_ratio`
9. `cat__score_level_D`
10. `num__loan_term`

New features entering top 30:

- `log_due_amount`
- `outstanding_to_loan_ratio`

The ODS action process features enter the dataset and pass leakage tests, but do not enter top 30. This suggests the current synthetic target generation still does not strongly connect action, connect, and PTP process behavior to D7 any-payment response.

## 7. Why The Lift Is Valuable

- AUC improved from the prior weak baseline around 0.54 to around 0.614 without relying on `vintage_month`.
- KS improved into a more useful diagnostic range around 0.20.
- PR-AUC moved materially above the positive-rate baseline.
- The feature set now has explicit leakage guards for PTP fulfillment and D7 outcome fields.
- The target wording no longer overclaims cure, full recovery, or delinquency clearance.

This is a stronger portfolio artifact because the improvement comes from better dataset construction and clearer boundaries, not from changing the synthetic target or tuning the generator.

## 8. Known Limits

- The target remains D7 any-payment response, not cure-to-current.
- `observation_date` currently aligns with due date, not D7 window end.
- `postloan_c_score` is a synthetic proxy and still has a score-date demo assumption.
- Process features are prediction-window safe, but current synthetic repayment generation does not make process behavior a strong upstream driver.
- The outputs validate offline modeling readiness only; they are not production decisioning evidence.

## 9. Next Steps

M6-D6 or M7 should focus on synthetic target, generator, and warehouse refinement:

- generate a full loan-level daily status panel
- make DPD state respond to repayment events
- define D7 window end as an explicit evaluation cutoff
- add cure-to-current labels alongside any-payment labels
- make action, connect, PTP, complaint, and capacity signals influence synthetic repayment propensity
- add score-date filtering with `score_date <= observation_date`
