# M6-A Strategy Scenario Schema

## 一、M6-A 是什么

M6-A 是 M6 Model Lab / Strategy Evaluation Lab 的输入契约层。它不做策略评估，也不算 ROI，只定义后续 M6-B 可以读取的策略场景配置。

本阶段新增 `configs/strategy_scenarios.yaml`，用 YAML 描述“如果我们采取某个贷后策略动作，后续 evaluator 应该围绕哪个异常、哪个指标、哪些客群、哪些假设去做离线模拟”。

## 二、为什么先做 strategy scenario schema

- **先固定输入口径**：M6-B evaluator、M6-C ROI calculator 和后续 CLI / report 都需要稳定字段，先做 schema 能避免后续各自发明配置格式。
- **先固定业务边界**：每个 scenario 都必须声明 synthetic data、无真实客户数据、无真实催收动作、无短信语音 WhatsApp、无 LLM 决策。
- **先固定 demo 叙事**：M3 已经发现 AI 外呼覆盖下降、人均案量上升、减免使用下降、score band 分层贡献信号等问题，M6-A 把这些信号整理成可执行的后续评估入口。
- **避免过早建模**：当前最重要的是策略动作的离线模拟框架，不是训练模型或引入重型 ML 依赖。

## 三、demo scenario 说明

### 1. increase_ai_call_coverage

- **业务含义**：提升 AI 外呼覆盖，验证触达补强是否可能改善 M1 D7 回收率。
- **策略类型**：`contact_strategy`
- **目标指标**：`recovery_rate_d7`
- **关联异常**：`M3A-ai_call_coverage-action_type-AI_OUTBOUND`
- **边界**：这只是离线模拟场景，不代表真实外呼动作，不发短信、语音或 WhatsApp。

### 2. increase_manual_capacity

- **业务含义**：补充人工催收产能，缓解人均案量过高带来的产能压力。
- **策略类型**：`capacity_strategy`
- **目标指标**：`recovery_rate_d7`
- **关联异常**：`M3A-avg_case_per_collector-region-华东`
- **边界**：人均案量是 capacity pressure signal，不是最终根因；该场景不代表真实排班或真实分案调整。

### 3. adjust_reduction_usage

- **业务含义**：调整减免使用策略，评估回收增益与减免费用之间的平衡。
- **策略类型**：`settlement_strategy`
- **目标指标**：`recovery_rate_d7`
- **关联异常**：`M3A-reduction_usage_rate-overall-ALL`
- **边界**：不代表真实减免审批，不生成客户级减免名单，不输出真实财务结论。

### 4. vendor_reallocation

- **业务含义**：对 vendor / line / region 组合做资源再分配，观察资源结构变化对回收表现的可能影响。
- **策略类型**：`allocation_strategy`
- **目标指标**：`recovery_rate_d7`
- **关联异常**：`M3A-m1_recovery_rate-overall-ALL`
- **边界**：line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路；该场景不代表真实供应商考核或真实分案动作。

### 5. score_band_D_priority

- **业务含义**：对 score_band=D 的高风险客群提高跟进优先级。
- **策略类型**：`segmentation_strategy`
- **目标指标**：`recovery_rate_d7`
- **关联异常**：`M3B-recovery_rate_d7-03`
- **边界**：score_band 是分层线索，不是最终根因；该场景不生成真实客户名单，不触发真实催收动作，不训练或调用评分模型。

## 四、每个 scenario 的固定边界

每个 scenario 的 `compliance_boundary` 必须包含以下 5 项。

- **synthetic_data_only**：只基于合成数据演示。
- **no_real_customer_data**：不接真实客户数据。
- **no_real_collection_action**：不产生真实催收动作。
- **no_sms_voice_whatsapp**：不发送短信、语音或 WhatsApp。
- **no_llm_decisioning**：不调用 LLM 做策略决策。

## 五、M6-A 不做什么

- 不做真实策略执行。
- 不做自动催收。
- 不做 LLM 决策。
- 不训练模型。
- 不接真实数据。
- 不写 Offline Strategy Evaluator。
- 不写 ROI calculator。
- 不修改 M1/M2/M3/M4/M5 核心逻辑。

## 六、后续 M6-B 如何读取这些 scenario

后续 M6-B 可以按以下流程读取 M6-A 配置。

1. 使用 `load_strategy_scenarios("configs/strategy_scenarios.yaml")` 加载场景列表。
2. 使用 `validate_strategy_scenarios(scenarios)` 校验字段、枚举、唯一性和合规边界。
3. 使用 `get_strategy_scenario_by_id(scenarios, scenario_id)` 选择单个场景。
4. 读取场景中的 `target_metric`、`target_anomaly_id`、`target_segments`、`levers`、`assumptions` 和 `constraints`。
5. 基于 synthetic ADS / `outputs/m3/m3_summary.json` 做 baseline / scenario / delta 离线估算。
6. 输出时继续保留 demo estimate 和 synthetic data 边界。

## 七、校验命令

```bash
python scripts/validate_strategy_scenarios.py
```

也可以显式指定配置路径。

```bash
python scripts/validate_strategy_scenarios.py --config configs/strategy_scenarios.yaml
```
