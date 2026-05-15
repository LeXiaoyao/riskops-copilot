# Changelog

本项目所有重要变更记录于此文件。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

> 项目当前处于**预发布**阶段（Phase 1 开发中），版本号尚未进入 `0.x` 正式发布序列。在此之前，重要变更以**文档版本（PRD vX）**和**里程碑（M0-M7）**为锚点。

---

## [Unreleased]

### Added
- 项目初始化：仓库结构、目录骨架、文档体系搭建中。

---

## 里程碑历史

### 2026-05-15 — 项目启动 / M0

**文档**
- 完成 PRD v6：在 v5 基础上重组结构，新增 TL;DR、范围矩阵、技术栈选型、AI Agent 设计规范、里程碑、风险登记、决策日志（ADR）等关键章节。
- 归档 PRD v1–v5 历史版本到 `docs/prd/history/`。
- 中英文双语 README 落地，中文为主、英文为辅。
- 确立 MIT 开源协议。

**工程**
- 创建项目目录骨架（按 PRD v6 §4.3 设计）：`riskops/`（代码）、`synthetic_data/`、`metadata/`、`schemas/`、`templates/`、`configs/`、`docs/`、`tests/`、`scripts/`。
- 初始化 Git 仓库并推送至 GitHub。
- 配置 `.gitignore`（数据/产物/敏感字段三层防护）。

**决策**
- ADR-001 ~ ADR-010：技术栈、Agent 编排方式、隐私边界、Phase 范围等关键决策固化。

---

## 版本规划占位

| 版本号 | 对应里程碑 | 预计内容 |
|---|---|---|
| 0.1.0 | M1 数据底座 | 合成数据生成器 + 五层数仓 + metadata yaml |
| 0.2.0 | M2 指标资产 | 指标字典 v1.0 + 计算引擎 |
| 0.3.0 | M3 引擎核心 | 异常检测 + 归因 + 可视化 |
| 0.4.0 | M4 报告与 TUI | 报告引擎 + TUI 主流程 |
| 0.5.0 | M5 催收 Copilot | 质检 + 话术 + 审批 |
| 0.6.0 | M6 Agent 整合 | Orchestrator + 专家 Agent |
| 0.7.0 | M7 演示包装 | README 完善 + 演示资产 |
| 1.0.0 | Phase 1 收官 | 首个可发布版本 |
