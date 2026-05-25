# M6-D ML Modeling Readiness

## Conclusion

- **recommended_target**：d7_any_payment_response
- **reason**：cleanest available label, complete loan-level grain, usable class balance, and existing leakage guards
- **boundary**：synthetic data only; no real customer data; no PII; no automated decisioning.

## Candidate Targets

### d7_any_payment_response
- **decision**：selected_for_baseline
- **grain**：loan_id
- **row_count**：30000
- **positive_rate**：0.274933
- **label_source**：dws_loan_status_snapshot_di.repaid_amount_d7 > 0
- **leakage_risk**：low when repaid_amount_d7 and recovery_rate_d7 stay target/evaluation-only
- **notes**：Best first baseline because the label is complete, binary, and already guarded against direct outcome leakage.

### d7_state_recovery_proxy
- **decision**：feasibility_only
- **grain**：loan_id
- **row_count**：3058
- **positive_rate**：0.033355
- **label_source**：loan daily snapshots at observation and D7
- **leakage_risk**：medium until snapshot timing and strict cure definition are strengthened
- **notes**：Useful for readiness diagnostics, but current synthetic strict cure positives are not strong enough for the first trainable baseline.

### ptp_fulfillment
- **decision**：defer
- **grain**：collection_action
- **row_count**：14822
- **positive_rate**：0.492646
- **label_source**：ods_collection_action rows where ptp_flag is true, target ptp_fulfilled_flag
- **leakage_risk**：medium because this is a second-stage model after promise-to-pay exists
- **notes**：Potentially useful later, but less suitable as the first product-chain ML baseline than D7 response.

## Leakage Guard Summary

- **pii_features_blocked**：True
- **outcome_features_blocked**：True
- **score_date_guard**：latest_score_on_or_before_observation_date_with_missing_impute_fallback
- **future_score_blocked_count**：12536
- **feature_count**：39

## Demo Boundary

- synthetic data only
- no real customer data
- no PII in model features
- no future D7 outcome fields in features
- no production model claim
- no automated financial or collection decisioning

## Next Action

- run ml-baseline for the D7 any-payment response baseline and keep state_recovery as feasibility-only until stricter state labels improve

_Generated at 2026-05-25T06:38:54+00:00_
