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

- **best_model**：logistic
- **AUC**：0.573920
- **KS**：0.110316
- **PR-AUC**：0.322443

## Without Vintage Metrics

- **best_model**：logistic
- **AUC**：0.575035
- **KS**：0.110654
- **PR-AUC**：0.322921

## Metric Deltas

- **delta_auc**：0.001115
- **delta_ks**：0.000338
- **delta_pr_auc**：0.000478

## Top Features Before

- **cat__score_level_D**：importance=0.535414
- **cat__vintage_month_2026-04**：importance=0.433551
- **cat__risk_level_current_D**：importance=0.304228
- **cat__dpd_bucket_M3+**：importance=0.284929
- **cat__initial_dpd_bucket_M3+**：importance=0.284929
- **cat__vintage_month_2024-01**：importance=0.219354
- **cat__risk_level_current_A**：importance=0.204263
- **cat__vintage_month_2023-07**：importance=0.186497
- **cat__vintage_month_2025-12**：importance=0.184880
- **cat__occupation_type_小微业主**：importance=0.182918

## Top Features After

- **cat__score_level_D**：importance=0.525156
- **cat__risk_level_current_D**：importance=0.303313
- **cat__dpd_bucket_M3+**：importance=0.290116
- **cat__initial_dpd_bucket_M3+**：importance=0.290116
- **cat__risk_level_current_A**：importance=0.205458
- **cat__occupation_type_小微业主**：importance=0.184695
- **cat__balance_segment_HIGH**：importance=0.149290
- **cat__score_level_A**：importance=0.140724
- **cat__score_level___MISSING__**：importance=0.139286
- **cat__risk_level_current_C**：importance=0.120643

## Artifact Warning

- vintage_month remains a synthetic batch/time artifact risk even when the best model is only weakly affected.
- If excluding vintage_month leaves metrics close, the right conclusion is not that the model is strong; it is that current synthetic data has weak stable signal.
- If excluding vintage_month causes a large drop, the baseline is mostly using a time-batch shortcut and should not be used as business evidence.

## Interpretation

- **conclusion**：vintage_month shows artifact risk in at least one with-vintage model, but removing it leaves performance close; the synthetic data signal is weak and the baseline should be presented as a diagnostic demo.

_Generated at 2026-05-25T06:38:52+00:00_
