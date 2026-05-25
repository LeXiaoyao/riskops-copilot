# Changelog

本项目所有重要变更记录于此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

> 项目当前是一个本地可运行的合成数据 demo / portfolio repo，不是生产风控服务。版本号在 `0.x` 序列内推进，里程碑（M1–M7）作为内部锚点。

---

## [Unreleased]

### Added
- M7-A State Recovery 目标可行性 guard：在 leakage / 时间窗 / 状态可观测性三个维度做诊断性检查，不是 production cure baseline。
- 公开 demo 导航与 architecture 文档梳理：README、`docs/architecture.md`、CLI summary、Model Lab 文案 demo boundary 措辞统一。
- M7-B Dashboard Portfolio 加层：Hero 双语 positioning 块、Portfolio at a Glance 5 模块导览卡、AI+ML Fusion 职责分层表、术语 glossary，面向无消金背景访客 30 秒读懂 demo。
- M7-C Deterministic Briefing：`riskops/engines/copilot/briefing_builder.py` 聚合 M3/strategy_eval/ROI/ML 为管理层单页简报；CLI `briefing`；规则模板不调 LLM。
- M7-D LLM 接入：`riskops/engines/copilot/llm_narrator.py`，调用 DeepSeek API 生成中文管理层 AI 摘要；`briefing --use-llm` 开关；LLM 层为可选，确定性层为权威信源。
- M7-E 全链路一键脚本：`scripts/run_all.sh` 从合成数据生成到 briefing 全流程，任意步骤失败即 exit。
- M7-F Excel 报告：`riskops/engines/report/excel_renderer.py`，生成 `m4_business_report.xlsx`（概览 / 异常信号 / 归因 Top5 / 策略ROI 四个 Sheet）；CLI `render-excel`。
- M7-G 面试讲稿：`docs/interview_pitch.md`，5 分钟结构化讲稿 + 12 节常见追问，中文为主。
- M7-H Plotly 可视化图表导出：`riskops/engines/visualization/chart_builder.py`，生成异常信号强度图 / 归因贡献图 / 策略ROI对比图（`outputs/visualization/`）；CLI `render-charts`。
- M7-I QC 合规关键词扫描：`riskops/engines/qc/compliance_scanner.py`，5 类违规词典（威胁恐吓/冒充司法/骚扰第三方/诱导新贷/辱骂）扫描催收话术，输出 risk_level / violations / Markdown 报告；CLI `qc-scan`。

### Notes
- 当前 trainable baseline 仍是 D7 any-payment response；state recovery 仅作为 feasibility / leakage guard 存在。
- 仓库不含真实客户数据；不做真实风控决策；不发送 SMS / voice / WhatsApp。
- LLM 层（M7-D）不做自动策略决策；所有 LLM 输出标注"仅供参考，需人工确认"。

---

## [0.6.0] — M6 Model Lab Strategy Evaluation MVP

### Added
- M6-A 策略情景 schema 与 5 个 demo scenario。
- M6-B 离线策略评估器（baseline / scenario / delta / caveats）。
- M6-C ROI Calculator：基于 demo cost assumptions 估算 cost / benefit / ROI / payback。
- Model Lab CLI 入口：`scenarios` / `strategy-eval` / `roi` / `model-lab` / `render-model-lab`。
- D7 any-payment response baseline（leakage-safe feature engineering）。
- C-score `score_date` availability guard：训练时强制 `score_date <= snapshot_date`，避免 future-leak。
- 合成数据过程行为校准（process calibration），用于支持 ML baseline 的可读性而非真实建模。

### Boundary
- baseline 目标限定为 **D7 any-payment response**，未承诺 cure-to-current、全额回收或生产催收结果建模。
- ROI 与收益数字来自 demo cost assumptions，不代表真实财务结果。

---

## [0.5.0] — M5 CLI / Demo Entry

### Added
- 统一 CLI 入口 `scripts/riskops_cli.py`：`summary` / `anomalies` / `drivers` / `outputs` / `render-dashboard` / `render-report`。
- CLI 文案与 README、Dashboard、Business Report 边界声明保持一致。

### Notes
- 本阶段为 CLI 串联式 demo entry，**未引入 TUI / 交互式终端 UI**。Textual / Rich 等 TUI 框架仍仅在历史 PRD 中作为远期方向出现，不在公开 demo 范围内。

---

## [0.4.0] — M4 Dashboard 与 Business Report

### Added
- 本地静态 Dashboard：`outputs/dashboard/dashboard.html`。
- M4 Business Report renderer：Markdown + HTML 双格式（`outputs/reports/m4_business_report.{md,html}`）。
- 报告内容由 M3 异常 / 归因 / 过程证据驱动，结论先行。

---

## [0.3.0] — M3 异常检测与归因

### Added
- 异常检测：M1 D7 回收率、AI 外呼覆盖、产能压力、减免使用、PTP 履约、投诉风险等信号的规则化检测。
- 归因引擎：围绕渠道、区域、客群分层、作业资源与过程证据，对 M1 D7 回收率下降做 Top-N 解释。
- 结构化 M3 summary 输出，供 M4 报告渲染消费。

---

## [0.2.0] — M2 指标资产

### Added
- 26 个贷后指标字典（结果 / 过程 / 合规 / ROI 四域）。
- Calculator registry：`metric_code → Callable`，按业务域聚合，函数名严格等于 `metric_code`。
- ADS 字段对齐与 metric lineage 落档。

---

## [0.1.0] — M1 数据底座

### Added
- 18 个月合成贷后数据生成器。
- 五层数仓骨架（DIM / ODS / DWD / DWS / ADS）。
- 主键关系、隐私分级 P0–P4、数据质量硬规则与软规则。

---

## 2026-05-15 — M0 项目启动

### Added
- PRD v6 骨架：在 v5 基础上重组结构，新增 TL;DR、范围矩阵、技术栈选型、隐私分级、里程碑、风险登记、决策日志（ADR）等关键章节。
- PRD v1–v5 归档至 `docs/prd/history/`。
- 中英文双语 README、MIT 协议、项目目录骨架、`.gitignore`。
- ADR-001 ~ ADR-010：技术栈、隐私边界、Phase 范围等关键决策固化。

---

## 关于未交付能力

PRD v6 描述了 Phase 1 完整范围（含催收质检、话术推荐、TUI 控制台、飞书草稿、PPT / Word 报告等）。当前公开 demo **仅交付** README 顶部 Milestone Status 与本 CHANGELOG 中列出的项；PRD 中其余条目视为 **planned but not delivered**，不构成当前公开仓库的能力承诺。
