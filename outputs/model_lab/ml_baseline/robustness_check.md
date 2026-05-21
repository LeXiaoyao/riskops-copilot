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
- **AUC**：0.540511
- **KS**：0.077699
- **PR-AUC**：0.301325

## Without Vintage Metrics

- **best_model**：random_forest
- **AUC**：0.543278
- **KS**：0.077319
- **PR-AUC**：0.306061

## Metric Deltas

- **delta_auc**：0.002767
- **delta_ks**：-0.000380
- **delta_pr_auc**：0.004736

## Top Features Before

- **num__due_amount**：importance=0.101177
- **num__loan_amount**：importance=0.097489
- **num__interest_rate**：importance=0.096204
- **num__mob**：importance=0.061015
- **num__postloan_c_score**：importance=0.056374
- **num__initial_outstanding_amount**：importance=0.037247
- **num__loan_term**：importance=0.035445
- **cat__product_code_P_CASH**：importance=0.015303
- **cat__occupation_type_工薪**：importance=0.014703
- **cat__customer_segment_复借**：importance=0.014681

## Top Features After

- **num__due_amount**：importance=0.110011
- **num__interest_rate**：importance=0.106377
- **num__loan_amount**：importance=0.105696
- **num__mob**：importance=0.072739
- **num__postloan_c_score**：importance=0.056222
- **num__loan_term**：importance=0.038436
- **num__initial_outstanding_amount**：importance=0.036135
- **cat__risk_level_current_B**：importance=0.015704
- **cat__customer_segment_复借**：importance=0.015651
- **cat__gender_F**：importance=0.015631

## Artifact Warning

- vintage_month remains a synthetic batch/time artifact risk even when the best model is only weakly affected.
- If excluding vintage_month leaves metrics close, the right conclusion is not that the model is strong; it is that current synthetic data has weak stable signal.
- If excluding vintage_month causes a large drop, the baseline is mostly using a time-batch shortcut and should not be used as business evidence.

## Interpretation

- **conclusion**：vintage_month shows artifact risk in at least one with-vintage model, but removing it leaves performance close; the synthetic data signal is weak and the baseline should be presented as a diagnostic demo.

_Generated at 2026-05-21T02:33:01+00:00_
