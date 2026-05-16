# 主键关系

> 由 `metadata/key_relationships.yaml` 自动渲染。

- `customer_id` → `loan_id`：1:N
- `customer_id` → `case_id`：1:N
- `case_id` → `loan_id`：M:N，经 `dim_case_loan_mapping`
- `loan_id` → `plan_id`：1:N
- `plan_id` → `repay_id`：1:N
- `case_id` → `action_id`：1:N
- `case_id` → `note_id`：1:N
- `case_id` → `decision_id`：1:N
- `vendor_id` → `line_id`：1:N
- `line_id` → `collector_id`：1:N
