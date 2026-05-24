# M6-B Offline Strategy Evaluator

## 一、M6-B 是什么

M6-B 是一个轻量离线策略评估器。它读取 M6-A 的 `configs/strategy_scenarios.yaml` 和 M3 的 `outputs/m3/m3_summary.json`，把每个策略场景转成 baseline / scenario / estimated delta 的 demo estimate。

它的目标不是给出真实策略决策，而是让作品集能讲清楚：发现异常之后，可以把管理动作放进一个透明、可审计、可复现的离线评估框架里。

## 二、为什么先做 offline evaluator

- **承接 M3**：M3 已经给出异常、Top drivers 和 process evidence，M6-B 先把这些证据变成策略动作的评估入口。
- **承接 M6-A**：M6-A 已经固定 scenario schema，M6-B 只消费这些配置，不再发明输入格式。
- **避免过早复杂化**：当前不训练模型、不做 ROI、不接真实数据，用规则化估算先跑通闭环。
- **利于后续扩展**：M6-C 可以在 M6-B 的 `estimated_delta` 基础上接成本收益测算。

## 三、它和真实策略引擎的区别

- **M6-B**：离线 demo estimate，只读合成数据和 M3 输出，不产生真实动作。
- **真实策略引擎**：会接真实业务数据、客户名单、策略审批、执行系统和上线监控。
- **M6-B**：不自动决策，不训练模型，不调用 LLM。
- **真实策略引擎**：需要审批流、审计、权限、灰度、回滚、合规复核和线上监控。

## 四、它如何读取 M6-A scenario

1. `load_strategy_scenarios("configs/strategy_scenarios.yaml")` 加载策略场景。
2. `validate_strategy_scenarios(scenarios)` 校验必填字段、枚举、唯一性和合规边界。
3. evaluator 读取每个 scenario 的 `target_metric`、`target_anomaly_id`、`target_segments`、`assumptions`、`constraints` 和 `compliance_boundary`。
4. 输出结果沿用 scenario 的合规边界，不新增真实动作能力。

## 五、它如何读取 M3 summary

M6-B 当前读取 `outputs/m3/m3_summary.json` 中的四类证据。

- **high_priority_anomalies**：用于识别 AI 外呼覆盖、人均案量、减免使用率等过程异常。
- **attribution_target_anomaly**：用于取得 M1 当前 recent baseline。
- **m1_d7_attribution_summary.top_drivers**：用于识别 ECOM、province、score_band 等归因线索。
- **process_evidence**：用于补充 AI 外呼覆盖、人工触达、减免使用等过程证据链。

## 六、每个策略场景如何估算

### 1. increase_ai_call_coverage

- **估算逻辑**：如果 M3 中存在 AI 外呼覆盖下降或 process evidence 指向 contact weakness，则给出小幅正向 improvement estimate。
- **解释边界**：这是触达补强假设，不代表真实外呼动作，也不证明覆盖提升一定带来回收提升。

### 2. increase_manual_capacity

- **估算逻辑**：如果人均案量 / 产能压力 signal 存在，则给出 reduce_risk estimate。
- **解释边界**：人均案量是 capacity pressure signal，不是最终根因。

### 3. adjust_reduction_usage

- **估算逻辑**：如果 reduction usage 偏低或 process evidence 指向 settlement weakness，则给出 improvement / monitor 方向估算。
- **解释边界**：不代表真实减免审批，不计算 ROI。

### 4. vendor_reallocation

- **估算逻辑**：结合 Top drivers 中 channel / vendor / line / region 线索，输出 resource reallocation 建议。
- **解释边界**：line_id 是催收作业线 / 催收单元 / 分案作业队列，不是电话线路。

### 5. score_band_D_priority

- **估算逻辑**：如果 score_band=D 是 Top driver，则输出 segmentation priority estimate。
- **解释边界**：score_band 是分层线索，不是最终根因。

## 七、业务边界和合规边界

- 不是真实策略引擎。
- 不自动决策。
- 不接真实客户数据。
- 不产生真实催收动作。
- 不发送 SMS / voice / WhatsApp。
- 不调用 LLM 做策略决策。
- 不训练模型。
- 不代表真实财务结果。
- 不改变 M1/M2/M3 指标口径。
- 所有 `estimated_delta` 都是 demo estimate。

## 八、后续 M6-C 如何接上

M6-C ROI & Cost-Benefit Calculator 可以读取 `outputs/model_lab/strategy_eval_results.json`。

后续建议只新增成本收益层，不回头改 M6-B 的策略判断口径。

- **输入**：M6-B 的 `baseline_value`、`scenario_value`、`estimated_delta`、`assumptions_used`、`caveats`。
- **新增内容**：人工成本、AI 外呼成本、减免成本、预计回收增益、ROI。
- **继续保留边界**：所有 ROI 都必须写明 demo estimate，不代表真实财务结果。

## 九、运行命令

```bash
python scripts/run_strategy_eval.py
```

也可以显式指定输入输出路径。

```bash
python scripts/run_strategy_eval.py \
  --scenarios configs/strategy_scenarios.yaml \
  --m3-summary outputs/m3/m3_summary.json \
  --output-json outputs/model_lab/strategy_eval_results.json \
  --output-md outputs/model_lab/strategy_eval_summary.md
```
