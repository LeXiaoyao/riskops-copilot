# RiskOps Copilot Briefing（AI 增强版）

> **AI 摘要** 由 DeepSeek LLM 生成，仅供参考。
> 以下结构化数据段（What Happened 等）为确定性规则输出，是唯一可追溯的权威信源。

## AI 管理层摘要

**总体结论：当前贷后经营状态出现显著恶化，核心指标M1回收率较基线骤降58.20%，需立即启动人工核查与策略干预。** 观测窗口（2026-04-19至2026-05-18）内共识别6项异常，其中高风险4项、中风险2项。M1回收率（m1_recovery_rate）相对基线（2026-03-20至2026-04-18）下降58.20%，是本次风险简报最核心的负面信号，表明逾期M1阶段的回款能力出现系统性滑坡。

**主要归因信号集中在风险等级B、产品P_CONS、正常余额段、ECOM渠道和评分B档五个维度，需重点核查渠道ECOM与产品P_CONS的集中异常。** 其中，risk_level=B（贡献+6.02%）、balance_segment=NORMAL（贡献+5.27%）、score_band=B（贡献+4.17%）三个客群维度建议单独设定触达、减免和PTP跟进策略，不改变指标口径。而product_code=P_CONS（贡献+5.57%）与channel_code=ECOM（贡献+4.88%）建议继续下钻到供应商、线路和客群组合，验证是否存在集中异常——例如某ECOM供应商或某P_CONS线路的回收率断崖式下跌。

**策略Lab信号显示，提升AI外呼覆盖率（increase_ai_call_coverage）是当前最高ROI方向，但估算结果基于合成数据，不可直接用于资源分配决策。** 该情景估算可带来delta +0.60%的回收率提升，ROI倍数高达36.50，在所有5个正ROI情景中排名第一。其他优先情景包括增加人工产能（increase_manual_capacity）和供应商重配（vendor_reallocation）。需注意，ROI倍数36.50意味着每投入1元成本可产生36.50元收益，但该估算未考虑渠道冲突、客群重叠及执行延迟等现实因素，仅作为方向性参考。

**ML Baseline信号为demo级别，推荐建模目标为d7_any_payment_response，但AUC 0.57与KS 0.11表明当前模型区分能力极弱，不具备生产部署条件。** 最优模型为逻辑回归（logistic），Top Decile Capture为+12.71%，正样本率27.49%，样本量30000。AUC 0.57仅略高于随机水平（0.50），说明合成数据校准存在局限，不代表真实生产环境下的建模能力。该信号仅用于验证建模流程，不应作为客群排序或策略分层的依据。

**下一步需人工确认以下事项：** 1）核查ECOM渠道与P_CONS产品下各供应商、线路的M1回收率明细，定位集中异常点；2）针对risk_level=B、balance_segment=NORMAL、score_band=B三个客群，设计差异化触达与PTP策略试点；3）评估AI外呼覆盖提升的可行性，包括供应商产能、合规要求及客群接受度。**以上基于合成数据demo，不作为真实业务决策依据，所有策略动作需人工确认后方可执行。**

---
## Boundary

- This briefing is deterministic and rule-based.
- It does not call an LLM.
- It must not be used for automatic financial or collection decisioning.
- Inputs are synthetic demo outputs only.

## What Happened

- **anomaly_count**：6
- **severity_counts**：high=4, medium=2, low=0
- **window**：baseline=2026-03-20~2026-04-18, recent=2026-04-19~2026-05-18
- **target_metric**：M1 回收率（m1_recovery_rate）
- **target_relative_change**：-58.20%

## Why It May Be Happening

- Top drivers are directional attribution signals, not final root cause.
- **risk_level=B**：contribution=6.02%; action=对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- **product_code=P_CONS**：contribution=5.57%; action=继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- **balance_segment=NORMAL**：contribution=5.27%; action=对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。
- **channel_code=ECOM**：contribution=4.88%; action=继续按该维度下钻到供应商、线路和客群组合，验证是否存在集中异常。
- **score_band=B**：contribution=4.17%; action=对该客群单独设定触达、减免和 PTP 跟进策略，不改变指标口径。

## What To Check

- Validate whether top attribution segments remain abnormal at vendor, line, and customer segment cuts.
- Check process evidence around AI coverage, manual capacity, connect rate, PTP, complaints, and reduction usage before action.
- Review offline assumptions behind scenario `increase_ai_call_coverage` before treating ROI as directional.
- Start drilldown from `risk_level=B` because it has the highest contribution score.

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

_Generated at 2026-05-25T06:12:31+00:00_
