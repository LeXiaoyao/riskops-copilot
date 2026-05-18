# M6-prep：Model Lab / Strategy Evaluation Lab 任务拆解

> 本文档只做 M6 规划和边界梳理，不包含 M6 功能代码。M6 后续实现必须继续遵守 synthetic data、指标字典唯一权威源、P4 不进 DWD/DWS/ADS/报告/LLM 的边界。

## 0. 任务分类与目标

- **任务分类**：新方案设计 / 后续实现拆解
- **本轮目标**：基于 PRD v6、M1-M5 已交付代码和输出，明确 M6 Model Lab / Strategy Evaluation Lab 的可执行范围
- **预期结果**：后续 Codex 可以按 M6-A 到 M6-E 分阶段实现，每阶段有清晰输入、输出、测试和禁止事项
- **本轮不做**：不写训练脚本，不新增模型引擎代码，不修改 anomaly / attribution / report / dashboard / CLI 的实现

## 一、M6 定位

M6 在 RiskOps Copilot 里的位置可以用一句大白话概括：前面已经能发现问题、解释问题、展示问题，M6 开始回答“如果我采取某个管理动作，大概值不值得做”。

- **M1 / M2 是数据和指标地基**
  - M1 提供 synthetic data、五层数仓和隐私边界。
  - M2 提供 `metadata/metric_dictionary.yaml` 和指标计算口径。
  - M6 只能复用这些口径，不能重新定义 M1/M2 指标。
- **M3 是异常检测和归因**
  - M3 已经能发现 M1 D7 回收率、AI 外呼覆盖、减免使用率、PTP 履约、投诉率、人均案量等异常信号。
  - M6 应该把这些信号转成策略评估场景，而不是重做异常检测。
- **M4 是报告和看板**
  - M4 已经把 M3 的异常和归因解释成业务经营报告。
  - M6 后续可以把策略评估摘要接入报告，但不应该重构 M4 报告引擎。
- **M5 是 CLI 演示入口**
  - M5 已经把 summary、anomalies、drivers、outputs、render-dashboard、render-report 串起来。
  - M6 后续可以新增 `strategy-eval` 命令，但不应该把 CLI 做成复杂交互系统。
- **M6 应该是 Model Lab / Strategy Evaluation Lab**
  - 更准确地说，第一版 M6 应该先做 Strategy Evaluation Lab：离线策略情景、规则化估算、ROI 解释和输出。
  - Model Lab 只做轻量占位或分数段模拟，不默认训练真实模型。
- **M6 不是什么**
  - 不是自动催收系统。
  - 不是 LLM Agent。
  - 不是真实业务决策系统。
  - 不接真实客户数据。
  - 不发短信、语音或 WhatsApp。
  - 不绕过人工审批。

## 二、M6 业务目标

M6 要解决的是贷后策略和风控运营里的“动作评估”问题：异常已经看到了，下一步管理动作能不能带来回收增量、成本是否可接受、影响面有多大。

- **离线评估异常后的管理动作**
  - 例如 AI 外呼覆盖率下降后，模拟恢复覆盖率是否能提升触达和回收。
  - 例如华东人均案量上升后，模拟增加人工产能是否缓解回收压力。
- **评估不同策略动作的 uplift / ROI / 影响面**
  - uplift 只做 demo estimate，表示规则假设下的增量估算。
  - ROI 只做成本收益测算，不代表真实财务结果。
  - 影响面包括覆盖客户数、涉及金额、影响指标和主要风险。
- **模拟客群分层、触达策略、减免策略、人工资源投入**
  - 客群分层：如 score_band=D 优先、HIGH balance + C/D risk 重点处理。
  - 触达策略：如提升 AI 外呼覆盖、恢复有效触达。
  - 减免策略：如提高合规减免使用率，估算减免成本和回收增益。
  - 人工资源：如提升 manual capacity，估算人力成本与回收改善。
- **面试展示价值**
  - M6 要展示“我不只是看异常，还能评估策略动作值不值得做”。
  - 业务表达重点不是模型炫技，而是策略判断、假设透明、边界清楚。

## 三、建议的 M6 子模块拆解

### M6-A：Strategy Scenario Schema

- **目标**：定义策略实验场景结构，让后续评估器有稳定输入。
- **核心动作**：新增可读 YAML 配置，例如 `configs/strategy_scenarios.yaml`。
- **场景示例**
  - `increase_ai_call_coverage`：提升 AI 外呼覆盖率。
  - `increase_manual_capacity`：增加人工催收产能。
  - `adjust_reduction_usage`：调整减免使用策略。
  - `vendor_reallocation`：供应商或作业线资源重分配。
  - `score_band_D_priority`：对 D 分客群提高处理优先级。
- **输出重点**：schema/config，不训练模型，不读真实数据。
- **设计原则**
  - scenario 必须写清假设、目标指标、适用客群、估算参数和边界说明。
  - 参数必须易读、可审计、可测试。
  - 默认使用 synthetic data 演示口径。

### M6-B：Offline Strategy Evaluator

- **目标**：基于 synthetic ADS / M3 summary 做离线策略评估。
- **核心动作**：读取 M3 summary 和必要 ADS 表，输出 baseline / scenario / delta。
- **输入来源**
  - `outputs/m3/m3_summary.json`
  - synthetic warehouse 中的 ADS 表
  - M6-A 的 strategy scenario config
- **输出内容**
  - baseline 指标值
  - scenario 假设后的估算值
  - delta 和影响面
  - 使用了哪些假设
  - 哪些结果只能视为 demo estimate
- **边界**：重点是规则化估算，不是真 ML 训练，不做因果推断。

### M6-C：ROI & Cost-Benefit Calculator

- **目标**：把策略评估结果转成成本、收益、ROI、回收增量估算。
- **核心动作**：在 M6-B 的 delta 基础上计算收益和成本。
- **成本示例**
  - 人工催收人力成本。
  - AI 外呼调用成本。
  - 减免成本。
  - 供应商资源调整成本。
- **收益示例**
  - 预计回收增益。
  - 预计 PTP 履约改善。
  - 预计投诉风险变化的管理提醒。
- **边界声明**
  - 所有 ROI 都是 demo estimate。
  - 不代表真实财务结果。
  - 不作为真实策略上线依据。

### M6-D：Model Lab Stub / Score Simulation

- **目标**：给 Model Lab 留轻量入口，但不默认训练真实模型。
- **可选做法**
  - 做 score band simulation：基于现有 `score_band` 做规则分层和收益估算。
  - 做 logistic regression 占位说明：仅在确认依赖成本可接受后再考虑。
- **推荐第一版**：先只做规则模拟，不引入 sklearn，不引入 lightgbm，不新增训练命令。
- **边界**：不要承诺 AUC / KS / PSI / Lift，除非后续正式进入真实模型实验阶段。

### M6-E：Report / CLI Integration

- **目标**：把策略评估结果接入已有 business report 和 CLI 演示入口。
- **CLI 建议**
  - 后续命令：`python scripts/riskops_cli.py strategy-eval`
  - 输出应该短、清晰、可复制到面试演示中。
- **报告建议**
  - 在 business report 后续版本追加“策略评估摘要”。
  - 不重构前端，不重做 dashboard。
- **边界**：只接入 M6 输出摘要，不改 M3/M4 核心计算口径。

## 四、M6 输入输出设计

### 输入建议

- **`outputs/m3/m3_summary.json`**
  - 用途：读取异常总览、高优先级异常、M1 D7 attribution、process evidence。
  - 约束：只读，不改 M3 输出结构。
- **synthetic data / warehouse 中的 ADS 表**
  - 用途：提供 baseline 指标、分组金额、回收率、减免 ROI 等基础数据。
  - 约束：只读取合成 ADS，不读取 `raw_secure`。
- **`metadata/metric_dictionary.yaml`**
  - 用途：引用指标中文名、口径、owner、版本和 notes。
  - 约束：只读，不在 M6 中重写指标定义。
- **可选 `configs/strategy_scenarios.yaml`**
  - 用途：定义策略情景和估算参数。
  - 约束：新增配置可以做，但参数必须说明是假设。

### 输出建议

- **`outputs/model_lab/strategy_eval_results.json`**
  - 内容：机器可读的 baseline / scenario / delta / assumptions / limitations。
  - 用途：供 CLI、报告和测试读取。
- **`outputs/model_lab/strategy_eval_summary.md`**
  - 内容：业务可读的策略评估摘要。
  - 用途：面试展示和报告引用。
- **`outputs/model_lab/roi_summary.json`**
  - 内容：成本、收益、ROI、回收增量估算。
  - 用途：后续 ROI summary 和 CLI 输出。
- **后续 CLI 命令**
  - `python scripts/riskops_cli.py strategy-eval`
  - 输出一页以内，不做复杂交互。

## 五、业务口径边界

- **离线模拟**：M6 是离线策略模拟，不是线上策略引擎。
- **数据边界**：不接真实客户数据，不读取 P4 明文字段，不读取 `synthetic_data/raw_secure/`。
- **动作边界**：不产生真实催收动作，不发短信，不发语音，不发 WhatsApp。
- **智能边界**：不调用 LLM，不做 Agent，不自动决策。
- **指标边界**：不改变 M1/M2/M3 指标定义，不修改 `metadata/metric_dictionary.yaml`。
- **异常边界**：不重写 anomaly / attribution 逻辑，只消费已有输出。
- **ROI 边界**：所有 ROI 都是 demo estimate，不代表真实财务结果。
- **表达边界**：文案必须写清“基于 synthetic data / 合成数据”，不能把合成数据说成真实数据。

## 六、优先级建议

推荐实施顺序如下。

1. **M6-A：Strategy Scenario Schema**
   - 先固定输入结构，避免后续 evaluator 和 ROI 计算各自发明参数。
   - 成本低，风险小，最适合作为 M6 第一刀。
2. **M6-B：Offline Strategy Evaluator**
   - 有 schema 后再做 baseline / scenario / delta，能形成第一条业务闭环。
   - 先用规则估算，避免一开始陷入 ML 依赖和训练样本问题。
3. **M6-C：ROI & Cost-Benefit Calculator**
   - evaluator 有 delta 后，ROI 计算才有依据。
   - 成本收益假设可以在配置中透明表达。
4. **M6-E：CLI / Report Integration**
   - 等 JSON / Markdown 输出稳定后再接 CLI 和 report。
   - 避免展示层先行导致输出格式反复改。
5. **M6-D：Model Lab Stub / Score Simulation**
   - 可后置，因为真实建模不是当前最重要价值。
   - 第一版用 score band 规则模拟即可，不急着引入 sklearn。

## 七、每个子任务的验收标准

### M6-A：Strategy Scenario Schema

- **允许修改文件**
  - `configs/strategy_scenarios.yaml`
  - `docs/m6_prep_plan.md` 的状态补充
  - `tests/test_strategy_scenarios.py`
- **禁止修改文件**
  - `metadata/metric_dictionary.yaml`
  - `configs/anomaly_rules.yaml`
  - `riskops/engines/anomaly/`
  - `riskops/engines/attribution/`
  - `riskops/engines/report/`
  - `riskops/engines/dashboard/`
  - `scripts/generate_synthetic_data.py`
  - `scripts/build_warehouse.py`
- **需要新增测试**
  - YAML 可解析。
  - 每个 scenario 有 `scenario_id`、`description`、`target_metric_code`、`segment_filter`、`assumptions`、`limitations`。
  - `target_metric_code` 必须能在 `metadata/metric_dictionary.yaml` 找到。
  - scenario 不包含 P4 字段名。
- **验证命令**
  - `python -c "import yaml; yaml.safe_load(open('configs/strategy_scenarios.yaml'))"`
  - `pytest tests/test_strategy_scenarios.py`
  - `pytest`
- **commit message 建议**
  - `M6-A: add strategy scenario schema`

### M6-B：Offline Strategy Evaluator

- **允许修改文件**
  - `riskops/engines/strategy_eval/` 或 `riskops/engines/model_lab/`，二选一后保持一致
  - `scripts/evaluate_strategy_scenarios.py`
  - `tests/test_strategy_evaluator.py`
  - `docs/m6_prep_plan.md` 的状态补充
- **禁止修改文件**
  - `metadata/metric_dictionary.yaml`
  - `configs/anomaly_rules.yaml`
  - `riskops/engines/anomaly/`
  - `riskops/engines/attribution/`
  - `riskops/engines/report/`
  - `riskops/engines/dashboard/`
  - synthetic data 生成逻辑
- **需要新增测试**
  - 缺少 `outputs/m3/m3_summary.json` 时给出明确错误。
  - evaluator 输出包含 baseline / scenario / delta / assumptions / limitations。
  - 输出不包含 P4 字段。
  - evaluator 不修改输入文件。
- **验证命令**
  - `python scripts/evaluate_strategy_scenarios.py --help`
  - `python scripts/evaluate_strategy_scenarios.py`
  - `pytest tests/test_strategy_evaluator.py`
  - `pytest`
- **commit message 建议**
  - `M6-B: add offline strategy evaluator`

### M6-C：ROI & Cost-Benefit Calculator

- **允许修改文件**
  - `riskops/engines/strategy_eval/roi.py` 或同模块内等价文件
  - `configs/strategy_scenarios.yaml` 中的成本假设字段
  - `tests/test_strategy_roi.py`
  - `docs/m6_prep_plan.md` 的状态补充
- **禁止修改文件**
  - `metadata/metric_dictionary.yaml`
  - `riskops/metrics/calculators/`
  - `riskops/engines/anomaly/`
  - `riskops/engines/attribution/`
  - synthetic data 生成逻辑
- **需要新增测试**
  - 人工成本、AI 外呼成本、减免成本、预计回收增益均可计算。
  - ROI 分母为 0 时返回明确状态，不伪造无穷大收益。
  - 输出包含 demo estimate disclaimer。
  - 成本假设可追溯到配置。
- **验证命令**
  - `python scripts/evaluate_strategy_scenarios.py`
  - `pytest tests/test_strategy_roi.py`
  - `pytest`
- **commit message 建议**
  - `M6-C: add strategy ROI calculator`

### M6-D：Model Lab Stub / Score Simulation

- **允许修改文件**
  - `riskops/engines/strategy_eval/score_simulation.py` 或同模块内等价文件
  - `tests/test_score_simulation.py`
  - `docs/m6_prep_plan.md` 的状态补充
- **禁止修改文件**
  - 不新增 sklearn / lightgbm / xgboost 依赖，除非先有 ADR 或用户明确批准。
  - 不新增真实模型训练脚本。
  - 不修改 `metadata/metric_dictionary.yaml`。
  - 不修改数仓和合成数据生成逻辑。
- **需要新增测试**
  - score band 输入能产生分层影响面估算。
  - 输出明确标记为 simulation，不是模型预测。
  - 不输出 AUC / KS / PSI / Lift，除非对应能力已正式实现。
- **验证命令**
  - `pytest tests/test_score_simulation.py`
  - `pytest`
- **commit message 建议**
  - `M6-D: add score band simulation stub`

### M6-E：Report / CLI Integration

- **允许修改文件**
  - `scripts/riskops_cli.py`
  - `riskops/interfaces/cli.py`
  - `riskops/engines/report/` 的模板或上下文读取逻辑
  - `tests/test_cli.py`
  - `tests/test_business_report.py`
  - README 中的命令说明
- **禁止修改文件**
  - `riskops/engines/anomaly/`
  - `riskops/engines/attribution/`
  - `riskops/engines/dashboard/`
  - `metadata/metric_dictionary.yaml`
  - `configs/anomaly_rules.yaml`
  - synthetic data 生成逻辑
- **需要新增测试**
  - `python scripts/riskops_cli.py strategy-eval` 可执行。
  - CLI 输出包含 baseline / scenario / delta / ROI / disclaimer。
  - business report 在 M6 输出缺失时仍能渲染 M4/M5 既有内容。
  - 不读取 P4 字段。
- **验证命令**
  - `python scripts/riskops_cli.py strategy-eval`
  - `python scripts/riskops_cli.py render-report`
  - `pytest tests/test_cli.py tests/test_business_report.py`
  - `pytest`
- **commit message 建议**
  - `M6-E: integrate strategy evaluation into CLI and report`

## 八、风险点

- **不要把 demo estimate 写成真实业务结论**
  - 改进建议：所有输出统一写明 synthetic data 和 demo estimate。
  - 预期效果：避免面试或作品集表达越界。
- **不要过早引入复杂 ML**
  - 改进建议：先做规则模拟和 score band simulation。
  - 预期效果：减少依赖成本，把重点放在策略评估闭环。
- **不要让模型实验污染 M1/M2/M3 指标口径**
  - 改进建议：M6 只引用 metric code，不重定义指标。
  - 预期效果：保持指标资产的一致性和可追溯性。
- **不要为了展示而把合成数据说成真实数据**
  - 改进建议：README、CLI、报告、JSON 输出都保留 synthetic data disclaimer。
  - 预期效果：符合隐私和作品集诚信边界。
- **不要让 CLI 输出变得太复杂**
  - 改进建议：`strategy-eval` 输出一页以内，默认只展示 Top scenarios。
  - 预期效果：适合 5 分钟 demo。
- **注意成本收益测算要解释假设**
  - 改进建议：每个 ROI 结果都带 `assumptions` 和 `limitations`。
  - 预期效果：让业务判断可审计、可挑战、可调整。

## 九、给后续 Codex 的最小可执行任务建议

- **M6-A task prompt summary**
  - 在 `/Users/lexiaoyao/RiskOps_Copilot` 工作，只实现 M6-A Strategy Scenario Schema。新增 `configs/strategy_scenarios.yaml` 和对应 schema 测试，场景包含 AI 外呼覆盖提升、人工产能提升、减免使用调整、供应商资源重分配、D 分客群优先。不要写 evaluator，不要训练模型，不要改 M1-M5 核心逻辑。运行 YAML 解析测试和 `pytest`，本地 commit。
- **M6-B task prompt summary**
  - 基于 M6-A 配置实现 Offline Strategy Evaluator。只读取 `outputs/m3/m3_summary.json` 和 synthetic ADS 数据，输出 `outputs/model_lab/strategy_eval_results.json` 与 `strategy_eval_summary.md`，包含 baseline / scenario / delta / assumptions / limitations。不要接真实数据，不要改 anomaly / attribution / report / dashboard / CLI 实现。新增 evaluator 测试并运行 `pytest`，本地 commit。
- **M6-C task prompt summary**
  - 在 M6-B 输出基础上实现 ROI & Cost-Benefit Calculator。新增成本收益估算逻辑，输出 `outputs/model_lab/roi_summary.json`，覆盖人工成本、AI 外呼成本、减免成本和预计回收增益。所有 ROI 必须标注 demo estimate，不代表真实财务结果。新增 ROI 测试并运行 `pytest`，本地 commit。
