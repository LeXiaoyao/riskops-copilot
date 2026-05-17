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

### ✅ RESOLVED 2026-05-17 — 同一 metric_code 在不同 ADS 表口径分歧

- **现象**：`ptp_rate` / `complaint_rate` 等指标在 `ads_postloan_dashboard_di`（走 calculator）与 `ads_vendor_performance_di`（在 `build_warehouse.py` 内联计算）的分母不一致：
  - dashboard 维度：`ptp_count / valid_contact_count`
  - vendor 维度：`ptp_count / connected_count`
- **业务原因**：vendor 粒度没有 vendor-level `valid_contact_count` 可用，必须降级到 `connected_count`。
- **风险**：违反 PRD §6.8 "代码与字典强对应"精神，看板与供应商表对同一名字的指标读出来数值不一致，存在解释成本。
- **处理结果**：不大改计算链路，保留 `ads_postloan_dashboard_di` 的 calculator 口径作为 dashboard 权威口径；`metadata/metric_dictionary.yaml` 已在
  `ptp_rate` / `complaint_rate` notes 中记录 vendor / collector 维度的降级分母、适用边界和 M3/M4 展示要求。
- **后续边界**：M3 归因默认读取 dashboard 权威口径；M4 如展示 vendor / collector 维度，必须标注降级口径，直到补齐同粒度有效沟通 / 投诉桥表。

## Privacy Boundary Questions

- None recorded.

## Architecture Decision Questions

### ✅ RESOLVED 2026-05-17 — `reduction_roi` 硬编码 0.82 基线

- `riskops/metrics/calculators/roi.py:54` 把"无减免对照组的回收率"硬编码为 0.82。
- **处理结果**：已新增 `configs/metric_params.yaml`，`reduction_roi` 从 `reduction_roi.baseline_recovery_without_reduction`
  读取基线；配置缺失时安全回退默认值 0.82，配置值非数字时抛出清晰错误。

### ⚠️ MINOR — Phase 2+ 13 个占位指标未生成

- `docs/codex_tasks.md` 阶段 4 C8 任务原 spec 写"39 个指标（26 实现 + 13 占位）"，M2 实际只产出 26 个完整指标。
- **决议**（Claude）：**采纳现状**，不补占位。判断依据：Phase 2+ 指标的真实定义要等对应 Phase 启动时才能写清楚，现在塞 13 个 `metric_code` 空架子既无业务价值、又违反"不要为虚构的未来需求做抽象"的项目约定。
- **后续动作**：`docs/codex_tasks.md` C8 spec 修订为"26 个 Phase 1 指标"，作为独立 docs commit 落地。

### ⚠️ M3-A FIELD LIMITATION — 部分异常因子还没有正式 metric_code

- **现象**：M3-A 需要检测 `avg_case_per_collector`、`high_balance_high_risk_share`、`ai_call_coverage` 等过程/结构异常，但当前 `metadata/metric_dictionary.yaml` 只覆盖 26 个 M2 Phase 1 指标，没有这些因子的正式指标定义。
- **处理结果**：异常检测引擎优先读取现有 ADS/DWS 字段做最小实现：
  - 华东线路人均案量读取 `dws_vendor_line_capacity_di.case_per_collector` 聚合结果，输出 `avg_case_per_collector`。
  - 高余额高风险客群占比读取 `dws_customer_status_snapshot_di.total_outstanding_amount` + `risk_level` 代理生成，输出 `high_balance_high_risk_share`。
  - AI 外呼覆盖率读取 `dws_collection_process_wide_di.ai_action_count / action_count`，输出 `ai_call_coverage`。
- **待拍板**：M3-B/M4 前是否把这些异常因子补进正式指标字典，或作为 attribution factor 而非 metric 管理。
