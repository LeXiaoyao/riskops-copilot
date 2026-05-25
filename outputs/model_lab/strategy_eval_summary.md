# M6-B Offline Strategy Evaluation Summary

## 1. Demo Disclaimer

- 本报告基于 synthetic data / 合成数据和 M3 规则输出生成，仅用于离线 demo estimate，不代表真实业务结论、真实策略引擎或真实财务结果。
- synthetic data only
- no real customer data
- no real collection action
- no SMS / voice / WhatsApp
- no LLM decisioning

## 2. Executive Summary

- **scenario count**：5
- **target metric**：recovery_rate_d7
- **priority scenarios**：increase_ai_call_coverage, increase_manual_capacity, vendor_reallocation
- **判断边界**：所有结果都是 offline demo estimate，不是真实预测。
- **优先方向**：先看 AI 外呼覆盖补强、人工产能缓解和资源再分配；减免策略和 D 分客群优先级需要继续观察假设。

## 3. Scenario Results

### 提升 AI 外呼覆盖（increase_ai_call_coverage）

- **strategy_type**：contact_strategy
- **目标指标**：recovery_rate_d7 / M1 D7 recovery_rate_d7
- **target_anomaly_id**：M3A-ai_call_coverage-action_type-AI_OUTBOUND
- **baseline / scenario / estimated delta**：10.2698% / 10.8698% / 0.6000%
- **estimated_direction**：improve
- **confidence**：medium
- **影响客群**：action_type=AI_OUTBOUND, channel_code=ECOM
- **业务解释**：AI 外呼覆盖下降是 contact weakness 线索，离线模拟只评估触达补强可能带来的方向性改善。
- **推荐动作**：优先复核 AI 外呼覆盖下降的渠道和区域切片，离线评估恢复覆盖后的 D7 回收率改善空间。
- **caveats**：estimated_delta 是 demo estimate，不是真实预测。; 不改变 M1/M2/M3 指标口径。; 这是触达补强假设，不代表真实外呼动作，也不证明覆盖提升一定带来回收提升。

### 补充人工催收产能（increase_manual_capacity）

- **strategy_type**：capacity_strategy
- **目标指标**：recovery_rate_d7 / M1 D7 recovery_rate_d7
- **target_anomaly_id**：M3A-avg_case_per_collector-region-华东
- **baseline / scenario / estimated delta**：10.2698% / 10.6698% / 0.4000%
- **estimated_direction**：reduce_risk
- **confidence**：medium
- **影响客群**：region=华东, line_id=ALL
- **业务解释**：人均案量上升说明产能压力变大，离线模拟只评估补人工后是否可能缓解 M1 D7 压力。
- **推荐动作**：优先评估华东作业线临时增员或分案转移的影响面，观察产能压力缓解方向。
- **caveats**：estimated_delta 是 demo estimate，不是真实预测。; 不改变 M1/M2/M3 指标口径。; 人均案量是 capacity pressure signal，不是最终根因；仍需结合客群结构和触达质量验证。

### 调整减免使用策略（adjust_reduction_usage）

- **strategy_type**：settlement_strategy
- **目标指标**：recovery_rate_d7 / M1 D7 recovery_rate_d7
- **target_anomaly_id**：M3A-reduction_usage_rate-overall-ALL
- **baseline / scenario / estimated delta**：10.2698% / 10.5698% / 0.3000%
- **estimated_direction**：improve
- **confidence**：low
- **影响客群**：overall=ALL, dpd_bucket=M1
- **业务解释**：减免使用率下降提示 settlement tool 可能使用不足，离线模拟只观察回收改善方向。
- **推荐动作**：复核减免授权、审批门槛和适用客群，离线观察适度提高减免使用后的回收改善方向。
- **caveats**：estimated_delta 是 demo estimate，不是真实预测。; 不改变 M1/M2/M3 指标口径。; 该估算不代表真实减免审批，也不计算 ROI；成本收益留给 M6-C 单独处理。

### 供应商与作业线资源再分配（vendor_reallocation）

- **strategy_type**：allocation_strategy
- **目标指标**：recovery_rate_d7 / M1 D7 recovery_rate_d7
- **target_anomaly_id**：M3A-m1_recovery_rate-overall-ALL
- **baseline / scenario / estimated delta**：10.2698% / 10.7698% / 0.5000%
- **estimated_direction**：reduce_risk
- **confidence**：medium
- **影响客群**：region=华东, vendor_id=ALL, line_id=ALL
- **业务解释**：资源再分配围绕 channel / vendor / line / region 信号展开，用于评估资源组合调整的影响面。
- **推荐动作**：围绕 ECOM、山东、上海、华东和作业线组合做资源再分配模拟，避免直接写成供应商责任结论。
- **caveats**：estimated_delta 是 demo estimate，不是真实预测。; 不改变 M1/M2/M3 指标口径。; line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路；资源再分配只是离线估算。

### D 分客群优先跟进（score_band_D_priority）

- **strategy_type**：segmentation_strategy
- **目标指标**：recovery_rate_d7 / M1 D7 recovery_rate_d7
- **target_anomaly_id**：M3B-recovery_rate_d7-03
- **baseline / scenario / estimated delta**：10.9047% / 11.1047% / 0.2000%
- **estimated_direction**：monitor
- **confidence**：medium
- **影响客群**：score_band=D, dpd_bucket=M1
- **业务解释**：score_band=D 是高风险分层线索，离线模拟只评估提高跟进优先级的方向性价值。
- **推荐动作**：将 score_band=D 作为优先跟进分层线索，离线观察触达、PTP 和减免跟进策略的影响面。
- **caveats**：estimated_delta 是 demo estimate，不是真实预测。; 不改变 M1/M2/M3 指标口径。; score_band 是分层线索，不是最终根因；不生成真实客户名单，不训练或调用评分模型。

## 4. Business Boundary

- 不是真实策略引擎。
- 不自动决策。
- 不产生真实催收动作。
- 不发送 SMS / voice / WhatsApp。
- 不调用 LLM 做策略决策。
- 不代表真实财务结果。
- 不改变 M1/M2/M3 指标口径。
