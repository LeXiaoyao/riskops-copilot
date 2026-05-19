# M6-C ROI & Cost-Benefit Calculator

## 1. M6-C 是什么

M6-C 是 Model Lab 里的 ROI / cost-benefit calculator。

它接在 M6-B Offline Strategy Evaluator 后面，用 M6-B 已经算出的 `estimated_delta` 做一个离线 demo 级别的成本收益估算。它回答的问题不是“真实业务能赚多少钱”，而是“如果这个策略假设成立，在一组固定 demo 成本假设下，收益和成本大概是什么方向”。

## 2. 为什么要做 ROI / cost-benefit calculator

M6-B 只告诉我们某个策略场景可能让 `recovery_rate_d7` 改善多少，例如 AI 外呼覆盖补强、人工产能补充、减免策略调整、供应商资源再分配、D 分客群优先跟进。

但策略讨论不能只看指标改善，还要看动作成本。M6-C 负责把“改善幅度”翻译成一组可读的 demo ROI 结果，方便后续 CLI / report 展示：

- **收益侧**：estimated_delta 带来的回收收益估算。
- **成本侧**：不同 strategy_type 对应不同成本模型。
- **净收益**：gross benefit 减去 action cost。
- **ROI ratio**：net benefit / action cost。
- **回本周期**：按 demo payback window 粗略估算。

## 3. 它和真实财务测算的区别

M6-C 不是财务模型，也不是经营预算模型。

真实财务测算通常需要真实账龄结构、余额分布、回收曲线、外呼供应商合同、人工排班、减免审批、账务核销、资金时间价值和风险合规成本。M6-C 都不接这些。

M6-C 只做 demo estimate：

- **数据来源**：只读 M6-B 的离线策略评估结果。
- **成本假设**：使用固定 demo assumptions。
- **收益假设**：把 `estimated_delta` 乘以 demo case base 和 unit recovery value。
- **业务含义**：用于比较策略方向，不代表真实财务结论。

## 4. 输入文件

默认读取：

```bash
outputs/model_lab/strategy_eval_results.json
```

该文件由 M6-B 生成，核心字段是每个 scenario 的：

- **scenario_id**：策略场景 ID。
- **scenario_name**：策略场景名称。
- **strategy_type**：成本模型类型。
- **target_metric**：目标指标，目前是 `recovery_rate_d7`。
- **estimated_delta**：M6-B 给出的离线 demo 改善幅度。

## 5. 默认 demo assumptions

M6-C 当前使用一组固定假设：

- **assumed_case_base**：10000
- **unit_recovery_value**：500
- **ai_call_unit_cost**：0.08
- **manual_capacity_unit_cost**：8.0
- **reduction_cost_rate**：0.15
- **vendor_reallocation_admin_cost**：3000
- **segmentation_priority_admin_cost**：2000
- **payback_window_days**：30

这些值只用于 demo，不代表真实合同、真实人力成本、真实减免成本或真实回收价值。

## 6. 成本收益测算逻辑

### 6.1 通用收益

所有场景的 gross benefit 使用同一个公式：

```text
gross benefit = estimated_delta × assumed_case_base × unit_recovery_value
```

### 6.2 contact_strategy

- **适用场景**：提升 AI 外呼覆盖。
- **成本公式**：`assumed_case_base × ai_call_unit_cost`
- **解释**：假设每个 demo case 产生一次 AI call 成本。

### 6.3 capacity_strategy

- **适用场景**：补充人工催收产能。
- **成本公式**：`assumed_case_base × 0.1 × manual_capacity_unit_cost`
- **解释**：假设 10% demo case 需要人工产能处理。

### 6.4 settlement_strategy

- **适用场景**：调整减免使用策略。
- **成本公式**：`gross_benefit × reduction_cost_rate`
- **解释**：把收益的一部分作为 demo 减免成本估算。

### 6.5 allocation_strategy

- **适用场景**：供应商与作业线资源再分配。
- **成本公式**：`vendor_reallocation_admin_cost`
- **解释**：使用固定 demo 管理成本。

### 6.6 segmentation_strategy

- **适用场景**：D 分客群优先跟进。
- **成本公式**：`segmentation_priority_admin_cost`
- **解释**：使用固定 demo 分层优先级调整成本。

## 7. 输出文件

运行：

```bash
python scripts/run_roi_calculator.py
```

默认生成：

- **JSON 输出**：`outputs/model_lab/roi_results.json`
- **Markdown 摘要**：`outputs/model_lab/roi_summary.md`

CLI 会打印：

- scenario 总数
- positive ROI 场景数
- highest ROI scenario
- 输出路径
- PASS / FAIL

## 8. 合规边界

M6-C 必须保留下面边界：

- synthetic data only
- demo cost assumptions
- no real customer data
- no real financial conclusion
- no real collection action
- no SMS / voice / WhatsApp
- no LLM decisioning

## 9. 后续 M6-E 如何接入 CLI / report

M6-E 可以把 M6-C 接进已有展示入口，但不需要改变 M6-C 的计算逻辑：

- **CLI integration**：在 CLI 输出里增加 ROI calculator 入口和输出文件状态。
- **report integration**：在报告或摘要里读取 `roi_summary.md` 或 `roi_results.json`，展示 demo ROI 结果。
- **边界延续**：所有 CLI / report 展示仍然必须显示 demo disclaimer 和合规边界。
- **不做真实动作**：M6-E 只展示，不触达客户，不发送短信、语音或 WhatsApp，不调用 LLM 做策略决策。
