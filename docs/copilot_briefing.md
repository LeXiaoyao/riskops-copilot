# Copilot Briefing — 边界说明

## 定位

**本模块属于 M7 Demo 包装层**，不是 PRD v6 §10.1 规划的 M5「催收 Copilot」或 M8 LLM Agent 层。

- 功能：把 M3 / strategy_eval / ROI / ML 的已有输出，聚合成一份面向访客 / 管理层的单页简报（`outputs/copilot/briefing.md`）。
- 实现：确定性规则模板组合，**不调用 LLM**，不做自主推理。
- 入口：`python scripts/riskops_cli.py briefing`
- 核心模块：`riskops/engines/copilot/briefing_builder.py`

## 边界（不可突破）

| 约束 | 说明 |
|---|---|
| 合成数据 only | 不接触真实客户数据 |
| 无 PII | briefing 输出中不含任何 P4 字段 |
| 不调 LLM | 无自动决策，无推理，无生成内容 |
| 不发通知 | 不触发短信 / 语音 / WhatsApp / 飞书消息 |
| 不做催收动作 | 不直接外呼，不绕过人工审批 |
| 非生产模型 | ML 指标仅作 demo 展示，不代表真实预测能力 |

## Briefing 结构

| 章节 | 内容 |
|---|---|
| What Happened | 异常数量、severity 分布、目标指标变动幅度 |
| Why It May Be Happening | Top attribution drivers + 过程证据框架（方向性，非最终根因）|
| What To Check | 下一步人工验证清单 |
| Strategy Lab Signal | 离线策略情景估算与 ROI 方向 |
| ML Baseline Signal | 训练目标、模型指标与免责说明 |
| What Not To Conclude | 明确禁止的解读（生产模型、自动决策等）|
| Next Actions | 手工验证与文档化步骤 |

## 与 PRD 规划的关系

- **M5 催收 Copilot**（PRD §10.1）= 文本质检、话术推荐、Mock 审批 — **尚未实现**。
- **M8 LLM / Agent 层**（PRD AI+ML 架构图）= LLM 摘要、自然语言解释、报告草稿路由 — **尚未实现**。
- `riskops/agents/` 目录保留作为上述两者的占位符；`briefing_builder` 是独立的规则引擎，不占用该命名空间。
