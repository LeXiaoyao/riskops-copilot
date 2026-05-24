# M6-D3 Vintage Robustness Check

## Purpose

- This check compares the same offline baseline with and without `vintage_month`.
- `vintage_month` is a synthetic batch/time artifact risk because it can encode calendar-generation differences.
- If not excluded, the model may learn batch differences instead of stable business behavior.
- This is for interview demonstration: it shows how to identify leakage-like pseudo-signal before overclaiming model quality.

## Synthetic Data Boundary

- Inputs are synthetic offline demo data only.
- No real customer data is read.
- No LLM, Agent, automated collection action, deployment, tag or release is involved.

## With Vintage Metrics

- **best_model**：random_forest
- **AUC**：0.567209
- **KS**：0.107892
- **PR-AUC**：0.313021

## Without Vintage Metrics

- **best_model**：logistic
- **AUC**：0.569109
- **KS**：0.106997
- **PR-AUC**：0.320282

## Metric Deltas

- **delta_auc**：0.001900
- **delta_ks**：-0.000895
- **delta_pr_auc**：0.007261

## Top Features Before

- **num__loan_amount**：importance=0.088075
- **num__log_due_amount**：importance=0.083766
- **num__due_amount**：importance=0.083356
- **num__interest_rate**：importance=0.080847
- **num__mob**：importance=0.053922
- **num__postloan_c_score**：importance=0.045241
- **num__initial_outstanding_amount**：importance=0.035322
- **num__outstanding_to_loan_ratio**：importance=0.034984
- **num__loan_term**：importance=0.029996
- **cat__risk_level_current_D**：importance=0.019214

## Top Features After

- **cat__risk_level_current_D**：importance=0.359167
- **cat__risk_level_current_A**：importance=0.246327
- **cat__balance_segment_HIGH**：importance=0.137339
- **cat__risk_level_current_B**：importance=0.135838
- **num__connect_rate_7d**：importance=0.120332
- **cat__current_vendor_id_V_B**：importance=0.117085
- **cat__dpd_bucket_M3+**：importance=0.110088
- **cat__initial_dpd_bucket_M3+**：importance=0.110088
- **cat__occupation_type_自由职业**：importance=0.098029
- **cat__age_group_46-55**：importance=0.091239

## Artifact Warning

- vintage_month remains a synthetic batch/time artifact risk even when the best model is only weakly affected.
- If excluding vintage_month leaves metrics close, the right conclusion is not that the model is strong; it is that current synthetic data has weak stable signal.
- If excluding vintage_month causes a large drop, the baseline is mostly using a time-batch shortcut and should not be used as business evidence.

## Interpretation

- **conclusion**：vintage_month shows artifact risk in at least one with-vintage model, but removing it leaves performance close; the synthetic data signal is weak and the baseline should be presented as a diagnostic demo.

_Generated at 2026-05-24T03:14:30+00:00_
