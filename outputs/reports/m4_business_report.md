# RiskOps Copilot M4-C 业务经营分析报告

> Demo Disclaimer: 本报告基于 synthetic_data / 合成数据生成，仅用于 M3 Demo 展示，不代表真实业务结论。

## 1. 执行摘要

- **本期异常发现**：共发现 8 个异常，其中 high 6 个、medium 2 个、low 0 个。
- **核心问题**：M1 D7 回收率下降。M1 回收率 从 19.43% 降至 15.30%，relative change 为 -21.27%。
- **初步归因方向**：Top drivers 指向 channel_code=ECOM、province=山东 / 上海、score_band=D / A，说明问题更像渠道、区域、客群结构与作业资源共同变化，而不是单个字段异常。
- **建议优先动作**：优先下钻 ECOM x vendor x line x score_band，并同步复核 AI 外呼覆盖、PTP 履约、减免使用率、投诉率和人均案量。
- **经营判断边界**：当前结论来自 synthetic data / 合成数据和 M3 规则输出，用于展示分析框架，不代表真实业务结论。

## 2. 异常总览

### 2.1 按 severity 汇总

- **high**：6 个
- **medium**：2 个
- **low**：0 个
- **基线窗口**：2026-03-19~2026-04-17
- **最近窗口**：2026-04-18~2026-05-17

### 2.2 高优先级异常列表

- **华东线路人均案量（avg_case_per_collector）**
  - severity：high
  - dimension：region=华东
  - baseline / recent：13.54 / 19.10
  - relative change：41.13%
  - 业务解释：人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。
  - 建议动作：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- **高余额高风险客群占比（high_balance_high_risk_share）**
  - severity：high
  - dimension：balance_segment+risk_level=HIGH+C/D
  - baseline / recent：0.59% / 0.75%
  - relative change：27.45%
  - 业务解释：高余额高风险客群占比上升会抬高贷后管理难度，可能加剧回收率和产能压力。
  - 建议动作：进入 M3-B 后拆分余额段、risk_level 和入案批次，识别结构变化贡献。
- **AI 外呼覆盖率（ai_call_coverage）**
  - severity：high
  - dimension：action_type=AI_OUTBOUND
  - baseline / recent：30.09% / 17.78%
  - relative change：-40.89%
  - 业务解释：AI 外呼覆盖下降说明自动化触达资源或策略发生变化，可能削弱早期提醒和低成本触达能力。
  - 建议动作：检查 AI 外呼线路容量、分案策略和人工替代触达占比。
- **减免使用率（reduction_usage_rate）**
  - severity：high
  - dimension：overall=ALL
  - baseline / recent：0.06% / 0.05%
  - relative change：-27.17%
  - 业务解释：减免使用率下降提示策略工具可能使用不足，需要检查授权、审批、客群准入和供应商执行。
  - 建议动作：下钻 vendor_id、line_id 与 dpd_bucket，确认减免授权、审批或策略门槛是否变化。
- **PTP 履约率（ptp_keep_rate）**
  - severity：high
  - dimension：overall=ALL
  - baseline / recent：49.68% / 43.58%
  - relative change：-12.28%
  - 业务解释：PTP 履约下降说明承诺还款后的跟进、客户还款意愿或策略工具支持出现压力。
  - 建议动作：下钻承诺还款客户的风险等级、余额段、催员和减免使用情况。
- **万案投诉率（complaint_per_10k_cases）**
  - severity：high
  - dimension：template_id=TPL_RISK_NOTICE
  - baseline / recent：54.20 / 122.48
  - relative change：125.96%
  - 业务解释：投诉率升高是合规侧过程风险信号，需要复核模板话术、发送时段和供应商执行。
  - 建议动作：下钻该模板的发送供应商、发送时段、投诉等级和具体话术，进入合规复核。

## 3. M1 D7 回收率下降专题

- **指标定位**：D7 回收率（recovery_rate_d7）用于观察 M1 阶段早期回收表现，是贷后经营里判断触达、承诺、资源投入是否有效的核心结果指标。
- **baseline**：19.43%
- **recent**：15.30%
- **relative change**：-21.27%
- **为什么这是核心问题**：M1 D7 回收率下降会提前反映新入案或早期逾期客群的回款压力，一旦持续恶化，后续 M1、M2+ 桶位的催收难度和资源成本都会上升。
- **可能影响环节**：渠道客群质量、区域供应商执行、line_id 作业队列承载、AI 外呼覆盖、人工跟进节奏、PTP 履约管理、减免策略使用和合规投诉风险。
- **当前边界**：本专题不重新定义指标口径，只解释 M3 已输出的 D7 回收率异常与 attribution 结果。

## 4. Top drivers 解释

### 1. channel_code=ECOM

- **baseline / recent**：23.90% / 6.29%
- **contribution_score**：15.26%
- **confidence**：medium
- **业务含义**：ECOM 代表电商渠道来源客群。该分组最近窗口 D7 回收率明显低于基线，说明问题可能集中在渠道客群质量、分案策略或触达资源匹配上。
- **可解释边界**：这是切片贡献信号，不等于 ECOM 是唯一根因；channel、province、score_band 之间可能存在样本重叠。
- **下一步下钻建议**：优先下钻 ECOM x vendor x line x score_band，确认是否由某个供应商、作业线或客群组合拉低。
- **M3 原始解释**：ECOM 分组的回收率下降对整体异常有可量化贡献。

### 2. province=山东

- **baseline / recent**：29.45% / 12.73%
- **contribution_score**：6.52%
- **confidence**：medium
- **业务含义**：山东分组回收率下降，提示区域客群、供应商执行或本地作业线排布可能出现同步变化。
- **可解释边界**：province 是业务维度切片，不代表单纯地理线路，也不能直接推出区域供应商责任。
- **下一步下钻建议**：复核山东区域供应商、line_id、分案批次和 score_band 结构，区分客群结构变化与作业执行变化。
- **M3 原始解释**：山东 分组的回收率下降对整体异常有可量化贡献。

### 3. score_band=D

- **baseline / recent**：17.83% / 5.93%
- **contribution_score**：5.75%
- **confidence**：medium
- **业务含义**：D 分客群通常代表更高风险层。该层回收率下降会直接放大 M1 早期回收压力。
- **可解释边界**：score_band 是风险分层信号，不改变 D7 回收率口径，也不代表所有 D 分客群均不可回收。
- **下一步下钻建议**：检查 D 分客群触达优先级、催收资源投入、减免授权和 PTP 跟进策略。
- **M3 原始解释**：D 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。

### 4. province=上海

- **baseline / recent**：22.35% / 7.16%
- **contribution_score**：4.42%
- **confidence**：medium
- **业务含义**：上海分组回收率下降，可能与区域客群结构、触达资源切换或供应商执行节奏有关。
- **可解释边界**：province 只能说明该切片表现恶化，不能单独证明地理因素导致回收下降。
- **下一步下钻建议**：复核上海区域供应商和作业线，重点查看 AI 外呼覆盖、人工触达占比和 PTP 履约表现。
- **M3 原始解释**：上海 分组的回收率下降对整体异常有可量化贡献。

### 5. score_band=A

- **baseline / recent**：36.42% / 19.88%
- **contribution_score**：4.04%
- **confidence**：medium
- **业务含义**：A 分客群通常是较优风险层。该层也出现下降，说明问题可能不只发生在高风险客群，需关注流程或资源侧变化。
- **可解释边界**：A 分下降不等于模型分层失效；需要结合渠道、区域和作业线进一步验证。
- **下一步下钻建议**：检查 A 分客群是否发生渠道结构变化、触达覆盖下降或承诺还款跟进断点。
- **M3 原始解释**：A 客群组内回收表现恶化，是资产结构或客户风险迁徙层面的重要信号。

## 5. 产能压力分析

- **line_id 口径说明**：line_id 在本项目中表示催收作业线 / 催收单元 / 分案作业队列，不是电话线路，也不是单纯地理线路。
- **产能压力信号**：华东线路人均案量（avg_case_per_collector）从 13.54 升至 19.10，relative change 为 41.13%。
- **业务解释**：人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。
- **建议动作**：下钻华东各 line_id 的 active_case_count 与 active_collector_count，评估临时增员或分案转移。
- **分析边界**：人均案量 / 催员负荷属于 capacity pressure signal，用于提示资源承载压力，不是最终根因。最终判断仍需结合 vendor、line、score_band、触达和履约链路共同验证。

## 6. 过程证据链

- **证据链口径**：以下指标属于 process evidence，用于解释异常发生前后的过程变化，不单独构成根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：channel_code=ECOM
  - baseline / recent：46.15% / 7.14%
  - delta：-39.01%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：province=山东
  - baseline / recent：100.00% / 0.00%
  - delta：-100.00%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：province=上海
  - baseline / recent：33.33% / 0.00%
  - delta：-33.33%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：score_band=A
  - baseline / recent：25.00% / 0.00%
  - delta：-25.00%
  - 解释：process evidence，用于解释过程链路变化，不能单独视为最终根因。
- **人均案量 / 产能压力（avg_case_per_collector）**
  - driver：region=华东
  - baseline / recent：13.54 / 19.10
  - delta：+5.57
  - 解释：人均案量上升意味着催员负荷变重，是 capacity pressure signal，可能影响触达节奏和承诺还款跟进，但不是最终根因。
- **AI 外呼覆盖（ai_call_coverage）**
  - driver：action_type=AI_OUTBOUND
  - baseline / recent：30.09% / 17.78%
  - delta：-12.30%
  - 解释：AI 外呼覆盖下降说明自动化触达资源或策略发生变化，可能削弱早期提醒和低成本触达能力。
- **减免使用率（reduction_usage_rate）**
  - driver：overall=ALL
  - baseline / recent：0.06% / 0.05%
  - delta：-0.02%
  - 解释：减免使用率下降提示策略工具可能使用不足，需要检查授权、审批、客群准入和供应商执行。
- **PTP 履约（ptp_keep_rate）**
  - driver：overall=ALL
  - baseline / recent：49.68% / 43.58%
  - delta：-6.10%
  - 解释：PTP 履约下降说明承诺还款后的跟进、客户还款意愿或策略工具支持出现压力。
- **投诉率（complaint_per_10k_cases）**
  - driver：template_id=TPL_RISK_NOTICE
  - baseline / recent：54.20 / 122.48
  - delta：+68.27
  - 解释：投诉率升高是合规侧过程风险信号，需要复核模板话术、发送时段和供应商执行。

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
