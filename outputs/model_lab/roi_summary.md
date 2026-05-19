# M6-C1 ROI Calculator Summary

## 1. Demo Disclaimer

- This ROI calculator uses synthetic data only and demo cost assumptions. It creates no real financial conclusion and no real collection action.
- synthetic data only
- demo cost assumptions
- no real customer data
- no real financial conclusion
- no real collection action
- no SMS / voice / WhatsApp
- no LLM decisioning

## 2. demo cost assumptions

- **assumed_case_base**：10000
- **unit_recovery_value**：500.00
- **ai_call_unit_cost**：0.08
- **manual_capacity_unit_cost**：8.00
- **reduction_cost_rate**：15.0000%
- **vendor_reallocation_admin_cost**：3,000.00
- **segmentation_priority_admin_cost**：2,000.00
- **payback_window_days**：30

## 3. Executive Summary

- **scenario count**：5
- **positive ROI scenarios**：5
- **highest ROI scenario**：提升 AI 外呼覆盖 / increase_ai_call_coverage / roi_ratio=36.5000

## 4. Scenario ROI Results

### 提升 AI 外呼覆盖（increase_ai_call_coverage）

- **strategy_type**：contact_strategy
- **estimated_delta**：0.6000%
- **gross_benefit**：30,000.00
- **action_cost**：800.00
- **net_benefit**：29,200.00
- **roi_ratio**：36.5000
- **payback_period_days**：0.8000
- **benefit_formula**：estimated_delta × assumed_case_base × unit_recovery_value
- **cost_formula**：assumed_case_base × ai_call_unit_cost

### 补充人工催收产能（increase_manual_capacity）

- **strategy_type**：capacity_strategy
- **estimated_delta**：0.4000%
- **gross_benefit**：20,000.00
- **action_cost**：8,000.00
- **net_benefit**：12,000.00
- **roi_ratio**：1.5000
- **payback_period_days**：12.0000
- **benefit_formula**：estimated_delta × assumed_case_base × unit_recovery_value
- **cost_formula**：assumed_case_base × 0.1 × manual_capacity_unit_cost

### 调整减免使用策略（adjust_reduction_usage）

- **strategy_type**：settlement_strategy
- **estimated_delta**：0.3000%
- **gross_benefit**：15,000.00
- **action_cost**：2,250.00
- **net_benefit**：12,750.00
- **roi_ratio**：5.6667
- **payback_period_days**：4.5000
- **benefit_formula**：estimated_delta × assumed_case_base × unit_recovery_value
- **cost_formula**：gross_benefit × reduction_cost_rate

### 供应商与作业线资源再分配（vendor_reallocation）

- **strategy_type**：allocation_strategy
- **estimated_delta**：0.5000%
- **gross_benefit**：25,000.00
- **action_cost**：3,000.00
- **net_benefit**：22,000.00
- **roi_ratio**：7.3333
- **payback_period_days**：3.6000
- **benefit_formula**：estimated_delta × assumed_case_base × unit_recovery_value
- **cost_formula**：vendor_reallocation_admin_cost

### D 分客群优先跟进（score_band_D_priority）

- **strategy_type**：segmentation_strategy
- **estimated_delta**：0.2000%
- **gross_benefit**：10,000.00
- **action_cost**：2,000.00
- **net_benefit**：8,000.00
- **roi_ratio**：4.0000
- **payback_period_days**：6.0000
- **benefit_formula**：estimated_delta × assumed_case_base × unit_recovery_value
- **cost_formula**：segmentation_priority_admin_cost
