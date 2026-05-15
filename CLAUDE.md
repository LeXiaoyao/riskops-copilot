# CLAUDE.md — AI 开发助手项目指引

本文件为 Claude Code / Claude Agent SDK 等 AI 助手在本仓库工作时的项目级指引。Claude 在任何 session 开始时会自动读取本文件。

---

## 项目简介

**RiskOps Copilot** 是一个面向消费金融风控与贷后策略的本地化 AI 智能分析工作台。详见 [README.md](README.md) 和 [PRD v6](docs/prd/PRD_v6.md)。

当前阶段：**M0 启动期**（仓库与文档准备中，尚未开始代码实现）。

---

## 必读文档优先级

在做任何具体任务之前，按顺序确认：

1. **[PRD v6](docs/prd/PRD_v6.md)** — 需求总纲，**所有需求/范围/架构问题以此为准**
2. **[CHANGELOG.md](CHANGELOG.md)** — 当前进度和里程碑
3. **本文件（CLAUDE.md）** — 协作规范与项目约定

⚠️ 历史 PRD（v1–v5）已归档到 `docs/prd/history/`，**仅供考古参考，不作为需求依据**。

---

## 核心协作规范

## Claude / Codex Collaboration Rules

- 本仓库的 Agent 协作边界以 [AGENTS.md](AGENTS.md) 为准。
- Claude owns judgment-heavy decisions, including product, architecture, ADR, PRD, README narrative, privacy, metric, and business-risk review.
- Codex owns execution-heavy implementation, including metadata YAML, SQL schemas, Python scripts, tests, documentation rendering, and local git commits.
- Codex must read `AGENTS.md` before starting implementation.
- Any architecture, privacy, or metric ambiguity must be escalated before implementation continues.

### 1. 范围控制（最重要）

- **任何新需求先回 PRD v6 §2.1 范围矩阵对号入座**。
- Phase 1 = 贷后样板间，禁止把 Phase 2-6 的内容拉进来。
- 若发现需求落在 Out-of-Scope 或 Parking Lot，先在 `docs/decisions/` 写 ADR，**不能直接动手**。

### 2. 中文沟通，技术术语保留英文

- 对话和文档默认中文。
- 代码、标识符、API、技术专有名词（DPD、MOB、PTP、Vintage、AUC、KS、PSI 等）保留英文。
- 提交信息（commit message）用中文 + 英文混合也可，但需描述清楚 why。

### 3. 单一权威源原则

- **指标定义**：唯一权威源是 `metadata/metric_dictionary.yaml`，md 文档只引用 `metric_code`，不重抄口径。
- **表/字段定义**：唯一权威源是 `metadata/tables.yaml` + `metadata/columns.yaml`。
- **决策**：唯一权威源是 `docs/decisions/ADR-*.md` 和 PRD v6 §13。

修改任何上述内容时，**先改权威源，再让 md 通过 `scripts/render_docs.py` 自动渲染**。绝不在 md 里手抄。

### 4. 隐私分级（P0–P4）红线

| 等级 | 内容 | DWD/DWS/ADS | 报告 | LLM 上下文 |
|---|---|---|---|---|
| P0/P1/P2 | 公开/业务键/脱敏 | ✓ | ✓ | ✓ |
| P3 | 哈希/密文 | ✓ | 不展示 | 不直接送 |
| P4 | 明文 PII（姓名/身份证/手机号/地址） | **✗** | **✗** | **✗** |

- P4 字段只允许在 `synthetic_data/raw_secure/` 目录存在（已 gitignore）。
- 任何代码在向 LLM 发送上下文前，必须由 Orchestrator 过滤 P3/P4 字段。
- 测试覆盖：`tests/test_privacy.py` 必须验证 DWD 以上层无 P4 字段。

详见 PRD v6 §9。

### 5. 业务原则

- **结论先行**：报告先讲结论、再讲过程。
- **数据为底**：所有结论必须可追溯到数据；数据不足要明说，不臆造。
- **人工兜底**：AI 不直接外发、不直接外呼、不绕过审批。
- **合规红线**：催收话术禁止威胁/辱骂/冒充司法/诱导新贷/骚扰第三方/暴露隐私/超频/禁时段触达。

---

## 代码规范

### 6. 技术栈（已固化，不要漂移）

- Python 3.11+
- 数据：DuckDB + pandas + Parquet
- TUI：Textual
- 可视化：Plotly（不要用 matplotlib，图丑）
- 报告：Jinja2 + openpyxl + python-pptx + python-docx
- LLM：Anthropic API（首选）
- 配置：YAML
- 测试：pytest

如需引入新依赖，**先开 ADR 讨论**。

### 7. 工程结构

完整目录见 [PRD v6 §4.3](docs/prd/PRD_v6.md#43-工程目录结构v6-新增一次定型) 或 [README.md](README.md)。
关键约定：
- 业务引擎放 `riskops/engines/<name>/`
- AI Agent 放 `riskops/agents/`
- 一次性脚本放 `scripts/`，**不要混进 `riskops/` 主代码**
- 测试与被测代码目录结构对应

### 8. 代码风格

- 函数与类要短，单一职责。
- **默认不写注释**——除非 WHY 不显然（隐藏约束、变通方案、易被误解的边界）。不要解释 WHAT。
- 命名优先于注释。`recovery_rate_d7` 比 `r7` 好太多。
- 不要为不存在的场景写错误处理。
- 不要为虚构的未来需求做抽象。

### 9. 测试要求

- 数据质量测试（`tests/test_data_quality.py`）必须全绿才能合并。
- 指标计算必须有对应单测。
- 跨层（ODS→DWD→DWS→ADS）加工必须有验证脚本。

### 10. 提交规范

- 一次 commit 做一件事。
- Commit message 描述 why，不只是 what。
- 不要在 commit message 里写 "Co-Authored-By: Claude" 之类——这是个人作品集，作者署名干净一些。
- 不要 push 到 main 之前不打招呼（除非用户明确说"直接推送"）。

---

## AI 助手任务模式

### 当用户让你做某件具体的事

1. 先看 PRD v6 对应章节。
2. 看 §2.1 范围矩阵确认是否 In-Scope。
3. 看是否有相关 ADR。
4. 如果是写代码，先看 `metadata/` 里的权威源。
5. 用 TodoWrite 拆任务，逐项完成。

### 当用户让你做需求/架构决策

1. **不要直接拍板**——这种事先问用户。
2. 给 2-3 个候选，每个写清取舍。
3. 用户决定后，在 `docs/decisions/` 写 ADR 落档。

### 当用户问"为什么这么设计"

1. 先查 ADR。
2. 再查 PRD v6 对应章节。
3. 找不到答案就说找不到，不要瞎编。

### 当用户让你"快速"或"先做个能跑的"

1. 仍然按 PRD v6 设计来。
2. 但可以省略：超前抽象、未来扩展点、过度的错误处理。
3. **绝不省略**：隐私边界、合规检查、数据质量校验、单一权威源。

---

## 当前阶段（M0）的工作重点

- ✅ 仓库与文档初始化（已完成大半）
- 🔄 PRD v6 业务章节逐步补强（§5 数据底座 / §6 指标资产 / §7 引擎）
- ⏳ 等待 M1 启动：合成数据生成器设计

**M0 阶段不要写 `riskops/` 主代码**，先把 PRD、metadata yaml、schemas SQL、ADR 写实。

---

## 常用查询入口

| 想找什么 | 去哪里 |
|---|---|
| 项目愿景 | `README.md` |
| 当前进度 | `CHANGELOG.md` |
| 完整需求 | `docs/prd/PRD_v6.md` |
| 范围边界 | `docs/prd/PRD_v6.md#2-范围与边界` |
| 技术栈 | `docs/prd/PRD_v6.md#42-技术栈选型` |
| 数据分层 | `docs/prd/PRD_v6.md#5-数据底座规范` |
| 指标定义 | `metadata/metric_dictionary.yaml`（M2 产出） |
| 表结构 | `metadata/tables.yaml`（M1 产出） |
| 决策记录 | `docs/decisions/` 和 `docs/prd/PRD_v6.md#13-决策日志adr` |
| 风险登记 | `docs/prd/PRD_v6.md#12-风险与依赖登记` |
| 历史 PRD | `docs/prd/history/` |

---

## 联系信息

- 作者 GitHub：[@LeXiaoyao](https://github.com/LeXiaoyao)
- 邮箱：xiaoyao201207@gmail.com
- 仓库：https://github.com/LeXiaoyao/riskops-copilot
