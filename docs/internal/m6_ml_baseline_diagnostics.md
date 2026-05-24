# M6 ML Baseline Diagnostics

## M6-D3 Vintage Robustness Check

- **目标**：对比同一 D7 recovery baseline 在包含 `vintage_month` 与排除 `vintage_month` 后的表现。
- **原因**：`vintage_month` 可能编码 synthetic data 的生成批次或时间差异，属于 batch/time artifact 风险。
- **边界**：不接真实数据、不接 LLM、不做 Agent、不做自动催收、不修改数据生成逻辑。
- **输出**：`outputs/model_lab/ml_baseline/robustness_check.json` 和 `outputs/model_lab/ml_baseline/robustness_check.md`。

## Feature Exclusion Rule

- **排除字段**：`vintage_month`。
- **防御性排除字段**：`first_due_date`、`case_create_date`、`case_create_time`。
- **说明**：`case_create_time` 只作为近 7 日过程窗口边界使用，不作为模型特征。

## Interpretation Rule

- **如果排除后 AUC / KS / PR-AUC 明显下降**：说明 baseline 主要依赖时间批次信号。
- **如果排除后指标仍接近**：说明当前 synthetic data 的稳定业务信号整体较弱，而不是模型已经足够强。
- **面试展示价值**：该检查展示如何识别数据泄漏或伪信号，避免把 batch/time artifact 误解释成业务规律。
