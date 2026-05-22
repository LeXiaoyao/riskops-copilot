# M6 Target Definition Boundary

## 1. Current Target

- **field name**：`is_recovered_d7`
- **semantic name**：D7 any-payment response
- **current formula**：`1 if repaid_amount_d7 > 0 else 0`
- **source table**：`synthetic_data/dws/dws_loan_status_snapshot_di.parquet`
- **business boundary**：the current label means the loan had any successful payment within the D7 window.

The current target is a legacy demo field name. It should be read as `d7_any_payment_response`, not as full recovery, full cure, or delinquency cleared.

## 2. Why The Current Definition Is Loose

- **partial payment is positive**：any `repaid_amount_d7 > 0` is counted as `1`, even if the payment is below the full due amount.
- **not full cure**：the label does not verify that DPD returned to 0.
- **not complete recovery**：the label does not require `recovery_rate_d7 >= 1`.
- **not clear delinquency**：the label does not compare DPD before and after payment.

This is acceptable for a synthetic offline baseline that demonstrates model-readiness plumbing, but reports must not describe it as full cure or complete recovery.

## 3. Ideal Cure-To-Current Target

A stricter cure-to-current label would require:

```text
is_cured_to_current_d7 =
  repaid_amount_d7 > 0
  and dpd_at_observation_date == 0
  and dpd_previous_day > 0
```

This target means the loan had a D7 payment response and moved from delinquent status to current status.

## 4. Why Current Synthetic Data Does Not Support Cure Target

- **daily snapshot coverage is limited**：`ods_loan_daily_snapshot` is not a full loan-level daily panel.
- **DPD does not cure after repayment**：current synthetic DPD is date-derived and does not fall back to 0 after repayment.
- **estimated cure positives are zero**：a read-only check found no `previous_day_dpd > 0` to `current_dpd = 0` cure transitions.
- **observation date is not D7 end**：`dws_loan_status_snapshot_di.stat_date` aligns with due date, not the D7 window end or cure observation date.

Because of these constraints, replacing the current target with cure-to-current would produce an unusable label under the current generated data.

This is a generator and warehouse limitation, not a model-training limitation. A cure target should be implemented as a separate generator + warehouse refinement rather than patched inside the ML dataset builder.

## 5. Current Decision

M6-D5D keeps the existing target calculation:

```text
is_recovered_d7 = repaid_amount_d7 > 0
```

The reporting and documentation must describe it as **D7 any-payment response prediction**. The current implementation does not claim full recovery, full cure, DPD clearance, or production-ready collection outcome modeling.

## 6. Future Work

To support cure-to-current in M6-D6 or M7:

- Generate a full loan-level daily status panel.
- Make DPD state respond to repayment events.
- Define observation date as D7 window end or another explicit prediction/evaluation cutoff.
- Add `dpd_previous_day`, `dpd_at_observation_date`, and cure flags in warehouse outputs.
- Update metric dictionary and model documentation to distinguish any-payment, full-payment, and cure-to-current targets.
- Add tests that verify positive cure labels require both payment and DPD state transition.
