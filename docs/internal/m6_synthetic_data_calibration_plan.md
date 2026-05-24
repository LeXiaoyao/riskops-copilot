# M6-D4 Synthetic Data Calibration Plan

## 1. Scope

本计划只设计下一版合成数据校准方案，不修改生成代码、不重新生成 `synthetic_data/`、不训练新模型、不接入外部真实数据、不接 LLM、不做 Agent。

- **任务分类**：新方案设计
- **当前阶段**：M6-D4 Synthetic Data Calibration Plan
- **输入依据**：当前生成逻辑、M6-D0 readiness、M6-D2 baseline diagnostics、M6-D3 vintage robustness check、模型输出文件、指标字典
- **输出目标**：解释当前 D7 recovery baseline 信号弱的原因，并给出下一版合成数据校准方向

## 2. Current Evidence

- **当前 target**：`is_recovered_d7 = dws_loan_status_snapshot_di.repaid_amount_d7 > 0`
- **样本量**：30,000 loan-level samples
- **正样本率**：28.02%
- **without vintage RandomForest**
  - AUC：0.543278
  - KS：0.077319
  - PR-AUC：0.306061
- **with vintage RandomForest**
  - AUC：0.540511
  - KS：0.077699
  - PR-AUC：0.301325
- **vintage robustness 结论**：去掉 `vintage_month` 后模型没有崩，说明模型不是完全依赖月份批次；但指标仍接近随机排序，说明稳定业务信号整体偏弱。
- **Top feature 现象**：`due_amount`、`interest_rate`、`loan_amount`、`mob`、`postloan_c_score`、`loan_term` 排在前列；`connect_rate`、`ai_coverage_rate`、`ptp_count`、`ptp_fulfillment_rate`、`protect_flag`、`sensitive_flag` 的重要性很低。

## 3. Current Problem Diagnosis

### 3.1 Root Cause

当前 `make_repayment()` 里的还款生成概率主要由 `initial_dpd_bucket`、是否近期到期和是否缺少案件映射决定：

- **M1 且 recent**：约 0.14
- **M1 非 recent**：约 0.22
- **非 M1**：约 0.27
- **无案件映射**：约 0.30

这说明 D7 回收结果并没有显式吸收客户风险、贷后评分、余额压力、触达质量、PTP 履约、投诉、减免、保护标签、供应商线路等业务特征。

### 3.2 Why AUC / KS Is Low

- **target 和业务特征关系弱**
  D7 回收主要由少数时间和逾期桶规则随机采样出来，客户画像、贷后评分、过程行为对 target 的边际贡献不足。
- **vintage_month 批次效应明显但不是唯一支撑**
  M6-D3 显示 Logistic with vintage 的 top features 被 `vintage_month` 主导，存在 synthetic batch/time artifact 风险；但 RandomForest 去掉 vintage 后指标基本不降，说明模型不是只靠月份字段。
- **行为特征没有充分影响 `repaid_amount_d7`**
  `connect_rate`、`ptp_count`、`ptp_fulfillment_rate`、`ai_coverage_rate` 在模型重要性中靠后，和真实贷后场景中“触达-承诺-履约-回款”的路径不一致。
- **过程特征和回收结果之间缺少明确生成机制**
  行动、投诉、减免、还款分别生成，彼此有展示层面的统计关系，但没有通过一个统一的 repayment propensity 机制影响 D7 回收。
- **合成数据更适合 M1-M6 经营指标演示**
  当前数据能支撑 dashboard、供应商表现、投诉、减免 ROI、策略评估和 baseline pipeline 演示；但还不够适合 ML model lab 展示可解释的预测信号。

## 4. Recommended Calibration Targets

目标不是制造虚高 AUC，而是让合成数据更接近真实贷后建模场景：风险分层、触达行为、还款意愿、还款能力和运营动作共同影响 D7 recovery，同时保留足够噪声。

- **Logistic / RandomForest baseline AUC**
  - 目标区间：0.62-0.72
  - 解释：应能展示基础排序能力，但不应接近 0.80 以上，否则 synthetic signal 可能过强。
- **KS**
  - 目标区间：0.18-0.30
  - 解释：应能体现贷后分层效果，但不能把 target 写成几个强规则导致 KS 过高。
- **PR-AUC**
  - 目标：明显高于正样本率 baseline
  - 当前正样本率约 28.02%，因此 PR-AUC 应显著高于 0.28，而不是只到 0.30 附近。
- **Top features 目标**
  - 更应来自 `postloan_c_score`、`score_level`、`dpd_bucket`、`initial_outstanding_amount`、`balance_segment`、`risk_level_current`、`connect_rate`、`ai_coverage_rate`、`ptp_count`、`ptp_fulfillment_rate`、`complaint_count`、`protect_flag`、`sensitive_flag`
  - 不应主要来自 `vintage_month`
  - `vintage_month` 可用于 robustness check，但不应成为业务解释核心

## 5. Latent Repayment Propensity Design

### 5.1 Recommended Mechanism

下一版可先生成一个隐含还款倾向，再用 sigmoid 转成 D7 回收概率：

```text
repayment_logit =
  base_rate
  + score_effect
  + risk_level_effect
  + dpd_effect
  + balance_effect
  + loan_amount_effect
  + action_intensity_effect
  + connect_effect
  + ai_outbound_effect
  + ptp_effect
  + reduction_effect
  - complaint_effect
  - sensitive_or_protect_effect
  - capacity_pressure_effect
  + vendor_line_effect
  + vintage_seasonality_effect
  + random_noise

recovery_probability_d7 = sigmoid(repayment_logit)
is_recovered_d7 ~ Bernoulli(recovery_probability_d7)
repaid_amount_d7 = is_recovered_d7 * due_amount * recovery_amount_ratio
```

### 5.2 Effect Definitions

- **base_rate**
  - 业务含义：控制整体 D7 回收率，使正样本率落在当前业务演示可接受范围，例如 20%-35%。
  - 校准方式：先固定总体回收率，再通过分层 effect 拉开不同样本的概率。
- **score_effect**
  - 业务含义：贷后评分越高，客户还款意愿和能力越强，D7 回收概率越高。
  - 设计建议：按 `postloan_c_score` 分箱或标准化后加入，不要让单一分数完全决定 target。
- **risk_level_effect**
  - 业务含义：`risk_level_current` 从 A 到 D 风险递增，D7 回收概率递减。
  - 设计建议：A/B/C/D 使用单调但温和的权重，避免和 score 完全重复。
- **dpd_effect**
  - 业务含义：逾期阶段越深，短期回收难度越高。
  - 设计建议：`CURRENT`、M1、M2、M3+ 单调递减；M1 内仍保留可回收空间。
- **balance_effect**
  - 业务含义：高余额案件还款压力更大，短期全额回收更难；但高余额也可能获得更多运营资源。
  - 设计建议：对 `balance_segment = HIGH` 设置负向主效应，并允许 action intensity 对高余额有部分抵消。
- **loan_amount_effect**
  - 业务含义：借款金额和应还金额越高，D7 内完成还款的难度越高。
  - 设计建议：用 log amount 或分箱，避免极端金额支配模型。
- **action_intensity_effect**
  - 业务含义：合理触达频次可以提升回收；过高频次可能代表难案或造成反效果。
  - 设计建议：使用非线性分段，例如 0 次为负、1-3 次为正、过高次数边际递减。
- **connect_effect**
  - 业务含义：有效接通是承诺还款和解释还款路径的前提，通常正向影响 D7 回收。
  - 设计建议：`connect_rate` 和 `connected_count` 正向，但需要受随机噪声和案件风险调节。
- **ai_outbound_effect**
  - 业务含义：AI 外呼对低风险、标准化提醒场景可能有效，对高风险或投诉敏感客群效果有限。
  - 设计建议：`ai_coverage_rate` 设置为弱正向，并与 `risk_level_current` 或 `protect_flag` 交互；不要让 AI 覆盖直接等于回收。
- **ptp_effect**
  - 业务含义：PTP 是明确还款意向，`ptp_count` 和 `ptp_fulfillment_rate` 应显著正向。
  - 设计建议：PTP 只能来自观察窗口内已发生的承诺；若预测时点在 PTP 之前，不能使用。
- **reduction_effect**
  - 业务含义：减免可提升部分高压力案件的还款概率，但也可能选择性发生在难案上。
  - 设计建议：approved reduction 弱正向，同时保留“被减免样本本身更难”的 selection effect。
- **complaint_effect**
  - 业务含义：投诉通常代表触达摩擦、话术风险或客户抵触，短期回收概率下降。
  - 设计建议：`complaint_count` 负向，但必须严格按预测窗口裁剪，避免使用 target 窗口之后的投诉。
- **sensitive_or_protect_effect**
  - 业务含义：保护或敏感标签意味着触达策略受限，短期强催收动作减少，D7 回收可能下降。
  - 设计建议：仅作为合成数据机制和合规分组评估使用，不作为自动加压策略依据。
- **capacity_pressure_effect**
  - 业务含义：供应商或线路产能紧张时，触达及时性和跟进质量下降。
  - 设计建议：用 line/vendor 层级 capacity utilization 生成弱负向影响。
- **vendor_line_effect**
  - 业务含义：供应商、线路、区域和作业模式存在稳定差异。
  - 设计建议：设置小幅随机效应，并在不同月份保持相对稳定；不能让某条线路直接决定 target。
- **vintage_seasonality_effect**
  - 业务含义：真实业务会有月份、节假日、账单批次等弱季节性。
  - 设计建议：只保留弱周期波动，用于 robustness check；不允许成为 top driver。
- **random_noise**
  - 业务含义：真实还款包含不可观测因素，例如收入到账、家庭事件、临时周转、平台外沟通。
  - 设计建议：保留足够噪声，避免 Logistic/RandomForest 指标虚高。

### 5.3 Anti-Leakage Rules

- 不使用 `repaid_amount_d7`、`recovery_rate_d7`、D7 窗口内还款流水生成模型特征。
- 不把 `is_recovered_d7` 直接写成若干特征的强规则。
- 过程特征必须有明确 observation window，例如入案前、入案首日、或预测时点前 7 天。
- 若 target 是 D7 回收，D7 结果窗口内才发生的投诉、减免审批、PTP 履约不能作为预测特征。
- `customer_id`、`loan_id`、`case_id`、`collector_id` 只用于 join 和审计，不作为模型可学习特征。

## 6. Field Influence Direction List

为避免终端截断，字段影响方向不用 Markdown 表格，改用分组列表呈现。

### 6.1 Score And Risk

- **字段**：`postloan_c_score`
  - 对 D7 回收概率影响方向：正向
  - 业务解释：贷后评分越高，短期还款能力和意愿越强。
  - 是否可作为模型特征：可以
  - 泄漏风险：低，前提是 `score_date` 早于预测时点。
- **字段**：`score_level`
  - 对 D7 回收概率影响方向：A/B 正向，C 中性偏负，D 负向
  - 业务解释：评分分层应带来可解释的风险梯度。
  - 是否可作为模型特征：可以
  - 泄漏风险：低，前提是分层来自预测前评分。
- **字段**：`risk_level_current`
  - 对 D7 回收概率影响方向：A 最高，D 最低
  - 业务解释：当前风险等级越差，D7 回收难度越高。
  - 是否可作为模型特征：可以
  - 泄漏风险：中，需确认不是用 D7 结果回填的后验标签。

### 6.2 DPD And Balance

- **字段**：`dpd_bucket`
  - 对 D7 回收概率影响方向：`CURRENT` / M1 高于 M2，高于 M3+
  - 业务解释：逾期越深，短期回款概率越低。
  - 是否可作为模型特征：可以
  - 泄漏风险：低，前提是取预测时点的 dpd。
- **字段**：`initial_dpd_bucket`
  - 对 D7 回收概率影响方向：M1 高于 M2，高于 M3+
  - 业务解释：入案初始逾期阶段影响回收难度。
  - 是否可作为模型特征：可以
  - 泄漏风险：低。
- **字段**：`initial_outstanding_amount`
  - 对 D7 回收概率影响方向：通常负向，允许中低余额更易回收
  - 业务解释：待还金额越高，短期还款压力越大。
  - 是否可作为模型特征：可以
  - 泄漏风险：低。
- **字段**：`balance_segment`
  - 对 D7 回收概率影响方向：`HIGH` 负向，`NORMAL` 中性或正向
  - 业务解释：高余额案件更难在 D7 内完成回款。
  - 是否可作为模型特征：可以
  - 泄漏风险：低，前提是入案时即可得。
- **字段**：`loan_amount`
  - 对 D7 回收概率影响方向：弱负向
  - 业务解释：大额贷款对应更高还款压力。
  - 是否可作为模型特征：可以
  - 泄漏风险：低。
- **字段**：`due_amount`
  - 对 D7 回收概率影响方向：弱负向
  - 业务解释：当期应还金额越高，D7 回款越难。
  - 是否可作为模型特征：可以
  - 泄漏风险：低，但不应让其成为唯一强驱动。

### 6.3 Process And Contact

- **字段**：`action_count`
  - 对 D7 回收概率影响方向：非线性，低频负向，适度正向，过高边际递减
  - 业务解释：无触达通常机会低，适度跟进提升回款，过高动作可能代表难案。
  - 是否可作为模型特征：可以
  - 泄漏风险：中，必须限定 observation window。
- **字段**：`connect_rate`
  - 对 D7 回收概率影响方向：正向
  - 业务解释：接通率高代表能有效传达还款提醒和方案。
  - 是否可作为模型特征：可以
  - 泄漏风险：中，必须只取预测时点前的触达。
- **字段**：`connected_count`
  - 对 D7 回收概率影响方向：正向但边际递减
  - 业务解释：接通次数越多，形成承诺或确认还款路径的机会越高。
  - 是否可作为模型特征：可以
  - 泄漏风险：中，必须限定 observation window。
- **字段**：`ai_coverage_rate`
  - 对 D7 回收概率影响方向：弱正向，可能因风险层级而变化
  - 业务解释：AI 外呼适合标准提醒和批量触达，但不能替代复杂人工协商。
  - 是否可作为模型特征：可以
  - 泄漏风险：中，需确认不包含 D7 结果窗口后的动作。
- **字段**：`ptp_count`
  - 对 D7 回收概率影响方向：正向
  - 业务解释：承诺还款是强意向信号。
  - 是否可作为模型特征：可以
  - 泄漏风险：高，只有预测时点前 PTP 可用。
- **字段**：`ptp_fulfillment_rate`
  - 对 D7 回收概率影响方向：强正向
  - 业务解释：历史承诺履约能力强的客户更可能 D7 回收。
  - 是否可作为模型特征：谨慎使用
  - 泄漏风险：高，不能使用当前 D7 窗口内履约结果。

### 6.4 Governance And Friction

- **字段**：`complaint_count`
  - 对 D7 回收概率影响方向：负向
  - 业务解释：投诉代表沟通摩擦、合规风险或客户抵触。
  - 是否可作为模型特征：谨慎使用
  - 泄漏风险：高，不能使用预测时点之后的投诉。
- **字段**：`protect_flag`
  - 对 D7 回收概率影响方向：负向或中性偏负
  - 业务解释：保护案件通常触达策略受限，短期回收动作减少。
  - 是否可作为模型特征：不建议用于自动策略加压；可用于分组诊断
  - 泄漏风险：中，需避免形成不当差别化催收。
- **字段**：`sensitive_flag`
  - 对 D7 回收概率影响方向：负向或中性偏负
  - 业务解释：敏感标签表示合规约束更强，过程动作需更保守。
  - 是否可作为模型特征：不建议用于自动策略加压；可用于合规边界评估
  - 泄漏风险：中，需避免敏感属性替代变量风险。

### 6.5 Assignment And Time

- **字段**：`current_vendor_id`
  - 对 D7 回收概率影响方向：小幅正负随机效应
  - 业务解释：不同供应商作业质量和覆盖能力不同。
  - 是否可作为模型特征：可以用于诊断；上线策略需谨慎
  - 泄漏风险：中，可能学到分配规则或批次差异。
- **字段**：`current_line_id`
  - 对 D7 回收概率影响方向：小幅正负随机效应
  - 业务解释：不同线路覆盖 DPD 和资源能力不同。
  - 是否可作为模型特征：可以用于诊断；上线策略需谨慎
  - 泄漏风险：中，可能学到分配规则。
- **字段**：`vintage_month`
  - 对 D7 回收概率影响方向：只允许弱季节性
  - 业务解释：月份可能反映账单批次、节假日和宏观环境，但在 synthetic data 中更容易变成 artifact。
  - 是否可作为模型特征：不建议进入主 baseline；用于 robustness check
  - 泄漏风险：高，可能成为批次捷径。

## 7. Public Data Reference Boundary

公开数据只能作为字段结构、分布和切分方法的参考，不得直接混入当前项目数据，不得引入真实客户数据，也不得下载或接入 Kaggle / 天池 / LendingClub / Home Credit 数据到本仓库。

- **可参考方向**
  - 样本不平衡比例：正负样本率、违约 / 回收 / 履约标签稀疏度
  - 风险评分字段：score、score band、risk grade、rating
  - 历史逾期字段：DPD、历史逾期次数、最大逾期天数、近 N 期逾期
  - 贷款金额和期限字段：loan amount、installment、term、interest rate、outstanding balance
  - 行为窗口特征：近 N 天触达、接通、承诺、履约、投诉、减免
  - target 构造方式：固定窗口内是否还款、是否违约、是否迁徙、是否履约
  - train/test split 方法：时间切分、out-of-time validation、vintage robustness
- **不可做事项**
  - 不把公开数据样本拼进 synthetic data
  - 不复制公开数据中的真实客户字段
  - 不把公开数据标签分布当成当前项目真实业务结论
  - 不使用公开数据训练当前项目模型
  - 不通过 LLM 或外部服务补全客户级特征

## 8. Follow-Up Milestone Split

### M6-D4A. Calibrate D7 Target Generation Logic

- **核心动作**：在 `generate_synthetic_data.py` 中引入 latent repayment propensity，替代当前仅按 DPD / recent / missing mapping 的概率逻辑。
- **预计产出**：代码变更和单元测试。
- **边界**：只校准 synthetic 生成逻辑，不引入真实数据。

### M6-D4B. Regenerate Small Scale Synthetic Data

- **核心动作**：只重生 small scale synthetic data，用固定 seed 保证可复现。
- **预计产出**：新的本地 synthetic artifacts。
- **边界**：生成产物仍不提交大文件。

### M6-D4C. Rerun M1-M6 Full Chain

- **核心动作**：重跑数仓构建、数据质量、指标质量、M3 attribution、M6 model lab。
- **预计产出**：确认经营指标 demo 和 ML lab 都没有断链。
- **边界**：不跳到 Dashboard / TUI / Agent / model training lab 之外的新范围。

### M6-D4D. Compare Old Vs Calibrated Model Metrics

- **核心动作**：对比 old vs calibrated 的 AUC、KS、PR-AUC、lift、top features、vintage robustness。
- **预计产出**：差异报告。
- **边界**：重点验证“更真实、更可解释”，不是单纯追高指标。

### M6-D4E. Update ML Baseline Report

- **核心动作**：更新 M6 baseline diagnostics，解释校准后 feature importance 和 lift 是否符合业务机制。
- **预计产出**：更新后的 `ml_baseline_report.md` 和诊断说明。
- **边界**：继续保留 synthetic data disclaimer。

### M6-D4F. Prepare v0.7.0 Release Review

- **核心动作**：准备 release review，说明 synthetic calibration 的动机、边界、验证结果和残余风险。
- **预计产出**：release review 草稿或 pending questions。
- **边界**：仅准备 review，不 push、不 tag、不 release。

## 9. Risks And Boundaries

- **不能为了追求 AUC 过度增强信号**
  校准目标是合理分层，不是制造“完美模型”。如果 AUC 接近 0.80 或 KS 过高，应回头减弱 effect 或增加噪声。
- **不能引入真实客户数据**
  P4 字段和真实客户行为不得进入 DWD / DWS / ADS / reports / LLM context / git。
- **不能引入泄漏字段**
  `repaid_amount_d7`、`recovery_rate_d7`、D7 结果窗口内还款流水、后验投诉和后验履约不能作为模型特征。
- **不能把 target 直接写死为几个特征的强规则**
  必须通过 latent propensity、概率采样和噪声生成，不应出现“score_level=A 就一定回收”这类规则。
- **synthetic data 只能用于 demo 和方法展示**
  它可以展示数据工程、指标口径、诊断方法和模型实验流程，不能证明真实业务预测能力。
- **模型指标不代表真实业务预测能力**
  AUC / KS / PR-AUC 只说明 synthetic offline dataset 上的排序效果，不代表可上线策略、真实回收改善或合规有效性。
- **保护和敏感标签不能用于加压**
  `protect_flag` / `sensitive_flag` 可用于边界、样本过滤和分组诊断，不应用来提高催收强度。
- **vintage_month 只能用于稳健性检查**
  月份字段应作为 artifact 风险检查对象，而不是主解释变量。

## 10. Recommended Next Decision

建议后续进入 M6-D4A，最小范围修改 `generate_synthetic_data.py` 的 D7 target 生成逻辑：先引入可解释的 latent repayment propensity，再以 small scale 数据验证 old vs calibrated 的指标、lift 和 top features 是否进入目标区间。
