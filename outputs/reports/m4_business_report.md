# RiskOps Copilot M4-C 业务经营分析报告

> Demo Disclaimer: 本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。

## 1. 执行摘要

- **本期异常发现**：共发现 6 个异常，其中 high 4 个、medium 2 个、low 0 个。
- **核心问题**：M1 D7 回收率下降。M1 回收率 从 24.57% 降至 10.27%，relative change 为 -58.20%。
- **初步归因方向**：Top drivers 指向 channel_code=ECOM、province=山东 / 上海、score_band=D / A，说明问题更像渠道、区域、客群结构与作业资源共同变化，而不是单个字段异常。
- **建议优先动作**：优先下钻 ECOM x vendor x line x score_band，并同步复核 AI 外呼覆盖、PTP 履约、减免使用率、投诉率和人均案量。
- **经营判断边界**：当前结论来自 synthetic data / 合成数据和 M3 规则输出，用于展示分析框架，不代表真实业务结论。

## 2. 异常总览

### 2.1 按 severity 汇总

- **high**：4 个
- **medium**：2 个
- **low**：0 个
- **基线窗口**：2026-03-20~2026-04-18
- **最近窗口**：2026-04-19~2026-05-18

### 2.2 高优先级异常列表

- **M1 回收率（m1_recovery_rate）**
  - severity：high
  - dimension：overall=ALL
  - baseline / recent：24.57% / 10.27%
  - relative change：-58.20%
  - 业务解释：该异常提示经营指标偏离历史基线，需要结合维度、过程证据和作业队列继续下钻。
  - 建议动作：进入 M3-B 后按供应商、线路、客群结构、AI 覆盖和减免策略下钻归因。
- **接通率（connect_rate）**
  - severity：high
  - dimension：vendor_id=V_B
  - baseline / recent：34.25% / 27.53%
  - relative change：-19.62%
  - 业务解释：该异常提示经营指标偏离历史基线，需要结合维度、过程证据和作业队列继续下钻。
  - 建议动作：下钻供应商 B 的线路、催员和触达时段，验证执行资源或号码质量问题。
- **华东线路人均案量（avg_case_per_collector）**
  - severity：high
  - dimension：region=华东
  - baseline / recent：13.54 / 19.10
  - relative change：41.13%
  - 业务解释：人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。
  - 建议动作：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- **AI 外呼覆盖率（ai_call_coverage）**
  - severity：high
  - dimension：action_type=AI_OUTBOUND
  - baseline / recent：30.25% / 17.75%
  - relative change：-41.32%
  - 业务解释：AI 外呼覆盖下降说明自动化触达资源或策略发生变化，可能削弱早期提醒和低成本触达能力。
  - 建议动作：检查 AI 外呼线路容量、分案策略和人工替代触达占比。

## 3. M1 D7 回收率下降专题

- **指标定位**：D7 回收率（recovery_rate_d7）用于观察 M1 阶段早期回收表现，是贷后经营里判断触达、承诺、资源投入是否有效的核心结果指标。
- **baseline**：24.57%
- **recent**：10.27%
- **relative change**：-58.20%
- **为什么这是核心问题**：M1 D7 回收率下降会提前反映新入案或早期逾期客群的回款压力，一旦持续恶化，后续 M1、M2+ 桶位的催收难度和资源成本都会上升。
- **可能影响环节**：渠道客群质量、区域供应商执行、line_id 作业队列承载、AI 外呼覆盖、人工跟进节奏、PTP 履约管理、减免策略使用和合规投诉风险。
- **当前边界**：本专题不重新定义指标口径，只解释 M3 已输出的 D7 回收率异常与 attribution 结果。

## 4. Top drivers 解释

### 1. risk_level=B

- **baseline / recent**：25.17% / 9.94%
- **contribution_score**：6.02%
- **confidence**：medium
- **业务含义**：risk_level=B 分组回收表现低于基线，是需要下钻验证的业务切片。
- **可解释边界**：该 driver 是统计切片信号，不单独构成最终根因。
- **下一步下钻建议**：继续按 vendor、line_id、score_band 和时间窗口下钻验证。
- **M3 原始解释**：B 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。

### 2. product_code=P_CONS

- **baseline / recent**：33.40% / 11.30%
- **contribution_score**：5.57%
- **confidence**：medium
- **业务含义**：product_code=P_CONS 分组回收表现低于基线，是需要下钻验证的业务切片。
- **可解释边界**：该 driver 是统计切片信号，不单独构成最终根因。
- **下一步下钻建议**：继续按 vendor、line_id、score_band 和时间窗口下钻验证。
- **M3 原始解释**：P_CONS 分组的回收率下降对整体异常有可量化贡献。

### 3. balance_segment=NORMAL

- **baseline / recent**：23.45% / 10.90%
- **contribution_score**：5.27%
- **confidence**：medium
- **业务含义**：balance_segment=NORMAL 分组回收表现低于基线，是需要下钻验证的业务切片。
- **可解释边界**：该 driver 是统计切片信号，不单独构成最终根因。
- **下一步下钻建议**：继续按 vendor、line_id、score_band 和时间窗口下钻验证。
- **M3 原始解释**：NORMAL 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。

### 4. channel_code=ECOM

- **baseline / recent**：28.66% / 6.90%
- **contribution_score**：4.88%
- **confidence**：medium
- **业务含义**：ECOM 代表电商渠道来源客群。该分组最近窗口 D7 回收率明显低于基线，说明问题可能集中在渠道客群质量、分案策略或触达资源匹配上。
- **可解释边界**：这是切片贡献信号，不等于 ECOM 是唯一根因；channel、province、score_band 之间可能存在样本重叠。
- **下一步下钻建议**：优先下钻 ECOM x vendor x line x score_band，确认是否由某个供应商、作业线或客群组合拉低。
- **M3 原始解释**：ECOM 分组的回收率下降对整体异常有可量化贡献。

### 5. score_band=B

- **baseline / recent**：24.96% / 9.56%
- **contribution_score**：4.17%
- **confidence**：medium
- **业务含义**：score_band=B 分组回收表现低于基线，是需要下钻验证的业务切片。
- **可解释边界**：该 driver 是统计切片信号，不单独构成最终根因。
- **下一步下钻建议**：继续按 vendor、line_id、score_band 和时间窗口下钻验证。
- **M3 原始解释**：B 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。

## 5. 产能压力分析

- **line_id 口径说明**：line_id 在本项目中表示催收作业线 / 催收单元 / 分案作业队列，不是电话线路，也不是单纯地理线路。
- **产能压力信号**：华东线路人均案量（avg_case_per_collector）从 13.54 升至 19.10，relative change 为 41.13%。
- **业务解释**：人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。
- **建议动作**：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- **分析边界**：人均案量 / 催员负荷属于 capacity pressure signal，用于提示资源承载压力，不是最终根因。最终判断仍需结合 vendor、line、score_band、触达和履约链路共同验证。

## 6. 过程证据链

- **证据链口径**：以下指标属于 process evidence，用于解释异常发生前后的过程变化，不单独构成根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：risk_level=B
  - baseline / recent：8.70% / 19.05%
  - delta：+10.35%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **PTP 履约（ptp_keep_rate）**
  - driver：risk_level=B
  - baseline / recent：33.33% / 100.00%
  - delta：+66.67%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：product_code=P_CONS
  - baseline / recent：21.43% / 16.67%
  - delta：-4.76%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：balance_segment=NORMAL
  - baseline / recent：22.58% / 13.04%
  - delta：-9.54%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **PTP 履约（ptp_keep_rate）**
  - driver：balance_segment=NORMAL
  - baseline / recent：25.00% / 66.67%
  - delta：+41.67%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：channel_code=ECOM
  - baseline / recent：18.18% / 25.00%
  - delta：+6.82%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **PTP 履约（ptp_keep_rate）**
  - driver：channel_code=ECOM
  - baseline / recent：50.00% / 0.00%
  - delta：-50.00%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：score_band=B
  - baseline / recent：12.50% / 8.33%
  - delta：-4.17%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **人均案量 / 产能压力（avg_case_per_collector）**
  - driver：region=华东
  - baseline / recent：13.54 / 19.10
  - delta：+5.57
  - 解释：人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：action_type=AI_OUTBOUND
  - baseline / recent：30.25% / 17.75%
  - delta：-12.50%
  - 解释：AI 外呼覆盖下降说明自动化触达资源或策略发生变化，可能削弱早期提醒和低成本触达能力。

## 7. 管理动作建议

- 优先下钻 ECOM x vendor x line x score_band，定位是否存在集中异常组合。
- 复核山东 / 上海区域供应商、催收作业线和分案队列表现。
- 检查 D 分客群触达策略、资源投入、减免授权和 PTP 跟进是否充分。
- 检查 AI 外呼覆盖下降原因，确认是容量、策略、名单分配还是人工替代导致。
- 检查 PTP 履约下降和减免使用不足问题，确认承诺后跟进与策略工具是否断档。
- 对 TPL_RISK_NOTICE 等投诉风险模板做合规复核，关注发送供应商、时段和话术。

## 8. 数据局限与合规说明

- 本报告使用 synthetic data / 合成数据，不包含真实客户数据。
- 报告不触发真实催收动作，不包含 SMS / voice automation。
- 报告不读取、不输出任何 P4 明文字段或字段值。
- 所有结论用于作品集和面试展示，不代表真实业务结论或真实风控建议。
- Top drivers 是切片贡献信号，跨维度可能重叠，不能简单相加为完整根因解释。

## 9. 后续产品路线

- M4 Dashboard polish：继续增强可读性、趋势展示和作品集说明。
- M5 TUI：提供命令行交互式工作台，串联异常、归因和报告生成。
- M6 Model Lab：建设回收率、PTP 履约、投诉风险等模型实验能力。
- M7 Collection QA：扩展催收质检、话术合规检查和策略推荐能力。
