# RiskOps Copilot Briefing

## Boundary

- This briefing is deterministic and rule-based.
- It does not call an LLM.
- It must not be used for automatic financial or collection decisioning.
- Inputs are synthetic demo outputs only.

## What Happened

- **anomaly_count**：7
- **severity_counts**：high=5, medium=2, low=0
- **window**：baseline=2026-03-20~2026-04-18, recent=2026-04-19~2026-05-18
- **target_metric**：M1 回收率（m1_recovery_rate）
- **target_relative_change**：-58.20%

## Why It May Be Happening

- Top drivers are directional attribution signals, not final root cause.
- **product_code=P_CONS**：contribution=5.59%; action=继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- **balance_segment=NORMAL**：contribution=5.28%; action=对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- **risk_level=high**：contribution=4.94%; action=对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- **channel_code=ECOM**：contribution=4.90%; action=继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- **score_band=B**：contribution=4.18%; action=对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

## What To Check

- Validate whether top attribution segments remain abnormal at vendor, line, and customer segment cuts.
- Check process evidence around AI coverage, manual capacity, connect rate, PTP, complaints, and reduction usage before action.
- Review offline assumptions behind scenario `increase_ai_call_coverage` before treating ROI as directional.
- Start drilldown from `product_code=P_CONS` because it has the highest contribution score.

## Strategy Lab Signal

- **priority_scenarios**：increase_ai_call_coverage, increase_manual_capacity, vendor_reallocation
- **top_strategy**：increase_ai_call_coverage
- **estimated_delta**：0.60%
- **roi_ratio**：36.50
- **positive_roi_count**：5

## ML Baseline Signal

- **recommended_target**：d7_any_payment_response
- **best_model**：logistic
- **row_count**：30000
- **positive_rate**：27.49%
- **AUC**：0.57
- **KS**：0.11
- **top_decile_capture_rate**：12.71%

## What Not To Conclude

- Do not treat this as a production model or real financial forecast.
- Do not treat attribution drivers as final root cause without operational validation.
- Do not use this briefing for automated collection action, SMS, voice, WhatsApp, or customer-level decisioning.
- Do not send PII or real customer data into LLM context.

## Next Actions

- 优先复核 AI 外呼覆盖下降的渠道和区域切片，离线评估恢复覆盖后的 D7 回收率改善空间。
- Run segment-level validation on the top drivers and confirm whether the signal is stable across recent days.
- Use model baseline only as a ranking diagnostics demo; keep production-model claims out of the narrative.
- Document any unresolved metric or timing ambiguity before expanding ML targets.

_Generated at 2026-05-28T11:39:47+00:00_
