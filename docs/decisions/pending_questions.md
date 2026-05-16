# Pending Questions

This file records unresolved or recently-resolved questions that require Claude or user judgment.

## PRD vs Implementation Conflicts

### ✅ RESOLVED 2026-05-16 — Calculator 文件结构：按业务域聚合 vs 一指标一文件

- **背景**：PRD v6 §6.8 第 3 条写"`riskops/metrics/calculators/<metric_code>.py` 每个指标一个计算函数，函数名即 metric_code"；§14.4 T-15 写"一指标一文件"。
- **实现**：Codex 在 M2 阶段按业务域聚合成 5 个文件（`base.py / postloan.py / collection.py / compliance.py / roi.py`），通过 `riskops/metrics/dictionary.py` 的 `calculator_registry()` 把 26 个 `metric_code → Callable` 注册起来，函数名严格 = `metric_code`。
- **决议**（Claude / R2 review）：**保留按业务域聚合结构**。判断依据：
  1. PRD §6.8 第 3 条的目标是"代码与字典强对应"——当前实现通过 `calculator_registry()` + `calculate_metric(metric_code, ...)` 单一入口已经满足这一目标，对外接口与"一指标一文件"完全等价。
  2. 同域指标天然共享 helper（如 `_window_recovery` / `_due` / `_repay` / `_valid_calls`）；拆 26 文件会被迫复制或建立 import 链，工程价值为负。
  3. `validate_metric_quality.py` 的 `validate_p0_calculators()` 在 registry 维度强制 P0 指标必须有 calculator，配合 `metric_code` 唯一性 + 函数名相等约束，已经形成"代码不能漂移"的护栏。
- **后续动作**：PRD v6 §6.8 第 3 条 / §14.4 T-15 的字面表述需要修订为"函数名即 `metric_code`，按业务域聚合，`dictionary.py` 提供中央 registry"。**该修订作为独立 docs commit 落地，不打包进 M2 commit**。

## Metric Definition Questions

### ⚠️ OPEN — 同一 metric_code 在不同 ADS 表口径分歧

- **现象**：`ptp_rate` / `complaint_rate` 等指标在 `ads_postloan_dashboard_di`（走 calculator）与 `ads_vendor_performance_di`（在 `build_warehouse.py` 内联计算）的分母不一致：
  - dashboard 维度：`ptp_count / valid_contact_count`
  - vendor 维度：`ptp_count / connected_count`
- **业务原因**：vendor 粒度没有 vendor-level `valid_contact_count` 可用，必须降级到 `connected_count`。
- **风险**：违反 PRD §6.8 "代码与字典强对应"精神，看板与供应商表对同一名字的指标读出来数值不一致，存在解释成本。
- **拟处理时机**：M3（引擎核心）阶段，配合"指标在不同粒度的口径分级"机制一起做。
- **临时缓解**：M3 启动前如有疑问，以 `ads_postloan_dashboard_di` 的口径（来自 calculator）为准。

## Privacy Boundary Questions

- None recorded.

## Architecture Decision Questions

### ⚠️ MINOR — `reduction_roi` 硬编码 0.82 基线

- `riskops/metrics/calculators/roi.py:54` 把"无减免对照组的回收率"硬编码为 0.82。
- **拟处理**：M3 移到 `configs/metric_params.yaml` 或类似配置，避免业务参数散在代码里。
- 不阻塞 M2 commit。

### ⚠️ MINOR — Phase 2+ 13 个占位指标未生成

- `docs/codex_tasks.md` 阶段 4 C8 任务原 spec 写"39 个指标（26 实现 + 13 占位）"，M2 实际只产出 26 个完整指标。
- **决议**（Claude）：**采纳现状**，不补占位。判断依据：Phase 2+ 指标的真实定义要等对应 Phase 启动时才能写清楚，现在塞 13 个 `metric_code` 空架子既无业务价值、又违反"不要为虚构的未来需求做抽象"的项目约定。
- **后续动作**：`docs/codex_tasks.md` C8 spec 修订为"26 个 Phase 1 指标"，作为独立 docs commit 落地。
