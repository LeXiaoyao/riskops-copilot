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
- **AUC**：0.615549
- **KS**：0.194021
- **PR-AUC**：0.426304

## Without Vintage Metrics

- **best_model**：random_forest
- **AUC**：0.613896
- **KS**：0.199485
- **PR-AUC**：0.425937

## Metric Deltas

- **delta_auc**：-0.001653
- **delta_ks**：0.005464
- **delta_pr_auc**：-0.000367

## Top Features Before

- **num__postloan_c_score**：importance=0.121092
- **num__loan_amount**：importance=0.075015
- **num__due_amount**：importance=0.068120
- **num__log_due_amount**：importance=0.065885
- **num__interest_rate**：importance=0.055985
- **num__initial_outstanding_amount**：importance=0.050339
- **num__mob**：importance=0.039539
- **num__outstanding_to_loan_ratio**：importance=0.029064
- **cat__score_level_D**：importance=0.023942
- **num__ai_coverage_rate**：importance=0.022664

## Top Features After

- **num__postloan_c_score**：importance=0.122015
- **num__log_due_amount**：importance=0.078021
- **num__loan_amount**：importance=0.077611
- **num__due_amount**：importance=0.072741
- **num__interest_rate**：importance=0.062264
- **num__initial_outstanding_amount**：importance=0.048378
- **num__mob**：importance=0.046251
- **num__outstanding_to_loan_ratio**：importance=0.038023
- **cat__score_level_D**：importance=0.030346
- **num__loan_term**：importance=0.024038

## Artifact Warning

- vintage_month remains a synthetic batch/time artifact risk even when the best model is only weakly affected.
- If excluding vintage_month leaves metrics close, the right conclusion is not that the model is strong; it is that current synthetic data has weak stable signal.
- If excluding vintage_month causes a large drop, the baseline is mostly using a time-batch shortcut and should not be used as business evidence.

## Interpretation

- **conclusion**：vintage_month shows artifact risk in at least one with-vintage model, but removing it leaves performance close; the synthetic data signal is weak and the baseline should be presented as a diagnostic demo.

_Generated at 2026-05-22T09:34:55+00:00_
