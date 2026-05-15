# RiskOps Copilot 产品需求文档（PRD v6）

> 本文档是 RiskOps Copilot 项目的需求总纲。v6 在 v5 的基础上做了**结构重组 + 完整性补强**，目标是：任何人 5 分钟看懂骨架，30 分钟挖到细节，工程同学可以直接据此拆解任务。
>
> v5 业务深度好但章节散布、缺优先级、缺技术约束、缺验收标准。v6 把所有"未来要做的点和要求"用一张范围矩阵 + 一张里程碑表 + 一张决策日志固定下来，作为后续不再漂移的基准。
>
> **当前文档状态**：骨架完成 + 关键新增章节写实 + 业务细节章节待逐章从 v5 迁移补强。

---

## 文档变更记录（Changelog）

| 版本 | 日期 | 主要变化 | 作者 |
|---|---|---|---|
| v1 | 2026-05-15 之前 | 初版，确立贷后样板间方向 | - |
| v2 | 2026-05-15 之前 | 补充催收 Copilot、合规质检 | - |
| v3 | 2026-05-15 之前 | 加入办公文档自动化 | - |
| v4 | 2026-05-15 之前 | 扩展贷前、贷中模块蓝图 | - |
| v5 | 2026-05-15 | 补充数仓分层、指标字典、长周期数据、C 卡建模 | - |
| **v6** | **2026-05-15** | **结构重组 + 范围矩阵 + 技术栈 + Agent 规范 + 里程碑 + 决策日志** | - |

---

## 目录

- [0. TL;DR](#0-tldr)
- [1. 产品愿景与价值主张](#1-产品愿景与价值主张)
- [2. 范围与边界](#2-范围与边界)
- [3. 目标用户与场景](#3-目标用户与场景)
- [4. 总体架构](#4-总体架构)
- [5. 数据底座规范](#5-数据底座规范)
- [6. 指标资产规范](#6-指标资产规范)
- [7. 引擎能力](#7-引擎能力)
- [8. AI Agent 设计](#8-ai-agent-设计)
- [9. 合规与隐私](#9-合规与隐私)
- [10. 第一期交付计划](#10-第一期交付计划)
- [11. 路线图](#11-路线图)
- [12. 风险与依赖登记](#12-风险与依赖登记)
- [13. 决策日志](#13-决策日志)
- [14. 附录](#14-附录)

---

## 0. TL;DR

### 0.1 一句话定位

**RiskOps Copilot 是一个面向消费金融风控全生命周期的本地化 AI 智能分析工作台**——以 TUI 为控制台、HTML/Excel/PPT/Word 为输出层，把风控策略人员、贷后管理者、数分商分、一线催员、质检合规人员的重复性分析、归因、报告、质检、话术工作产品化。

### 0.2 第一期范围（一句话）

用合成贷后数据演一个完整故事：**M1 D7 回收率下滑 → 自动归因到客群结构 + 华东线路产能 + 供应商 B 接通率 + AI 外呼覆盖率 + 减免使用率 + 投诉话术风险 → 输出 HTML 周报 + PPT 大纲 + 催员话术建议**。

### 0.3 最终目标（一句话）

证明这套方向**有业务价值、有产品形态、有技术实现路径、有可视化展示、有 AI 差异化、有从贷后扩展到贷前贷中的完整战略想象空间**——可作为面试作品集 + 个人风控方法论资产平台。

### 0.4 核心逻辑链

```
合成数据 → 数据底座（DIM/ODS/DWD/DWS/ADS + 隐私分级）
       → 指标资产（指标字典 + 血缘 + 版本）
       → 引擎（异常检测 / 归因 / 可视化 / 报告 / 质检 / 话术）
       → AI Agent 编排（主 Agent + 专家技能模块）
       → 输出层（TUI + HTML + Excel + PPT + Word + 飞书草稿）
```

### 0.5 不是什么（避免误解）

- 不是聊天机器人，不是通用 BI，不是企业级 SaaS。
- 不接真实金融数据，不做真实外呼/短信发送，不替代催员作业。
- 不追求完整权限/多租户/数据脱敏平台/监管报送。

---

## 1. 产品愿景与价值主张

> **迁移自 v5 §1**，骨架保留，结论收敛到下面三条。

### 1.1 愿景

把散落在 Excel / PPT / SQL / 飞书文档 / 个人经验里的风控策略知识，沉淀成一套可调用的垂直 AI 技能，让 RiskOps 团队（策略 / 数分 / 商分 / 贷后管理 / 催员 / 质检 / 产品）少做重复劳动，多做判断决策。

### 1.2 核心价值（六条）

1. **替代基础数分/商分工作**：自动拉数、做透视、出图、写结论。
2. **提高贷后策略分析效率**：M1/M1+ 回收率、PTP、投诉、ROI 快速归因。
3. **提升管理者洞察**：用自然语言问"为什么回收率掉了？哪个供应商拖后腿？"
4. **提升催员执行质量**：上下文摘要 + 分层 + 话术推荐 + 合规提醒 + 审批。
5. **提升质检合规覆盖**：录音/文本/模板的红线扫描和强度评分。
6. **沉淀策略知识资产**：指标字典 / 报告模板 / 诊断链路 / 策略 Playbook。

### 1.3 与 v5 §1.2 的对应关系

完全继承 v5 §1.2，无修改。后续修订只在本节追加，不重写。

---

## 2. 范围与边界

### 2.1 三栏范围矩阵（**v6 最重要的新增表**）

| 类别 | Phase 1 In-Scope（Must） | Phase 1 In-Scope（Should） | Phase 1 Out-of-Scope（Won't） | Parking Lot（Phase 2+） |
|---|---|---|---|---|
| **数据** | 合成贷后数据（≥18 个月）、DIM/ODS/DWD/DWS/ADS 五层、隐私分级 | 客户/催员画像日切表、贷后标签表 | 真实金融机构生产数据接入 | MySQL/PostgreSQL 远程连接、企业数据脱敏平台 |
| **指标** | 贷后结果/过程/合规/ROI 指标字典 v1.0、yaml 化 | 贷前/贷中指标占位（不计算） | 模型指标完整体系（AUC/KS/PSI/Lift） | 贷前贷中完整指标计算 |
| **引擎** | 异常检测（统计规则）、多维归因（贡献度排序+瀑布）、HTML 报告、Excel/PPT/Word 草稿 | 投诉风险地图、话术雷达图 | 复杂 ML 异常检测、因果推断 | 评分卡/XGBoost/SHAP 建模实验室 |
| **TUI** | 两栏布局、核心命令（load/dashboard/anomaly/explain/vendor/roi/qc/script/report） | 三栏布局、自然语言问答优化 | 多用户/权限/会话管理 | 企业化 Web Dashboard |
| **催收 Copilot** | 文本质检、合规扫描、话术推荐、Mock 审批+发送+留痕 | 音频 ASR 转写 | 真实短信/外呼发送 | 飞书/企微审批流对接 |
| **办公文档** | HTML/Markdown 周报、Excel 附表、PPT 大纲、Word 草稿、飞书友好 Markdown | 本地 Markdown 知识库搜索 | 飞书 API 真实写入 | 飞书多维表格同步、会议纪要 |
| **AI Agent** | 主 Agent + 5 个技能模块（Risk/Collection/Compliance/Report/Model 占位） | 上下文持久化、记忆系统 | 多 Agent 复杂编排框架 | 自动策略 Playbook 沉淀 |
| **合规** | 隐私分级 P0–P4、催收红线扫描、Mock 审批留痕 | 投诉保护策略 | 真实监管报送 | 监管报告自动化 |
| **演示** | README + 截图集 + 5 分钟演示脚本 | Demo 视频 | 在线 SaaS Demo | 企业试用方案 |

> **规则**：本表是范围唯一权威源。任何新需求先回到本表对号入座；新增需求若属 Out-of-Scope 或 Parking Lot，必须有明确理由记录在 §13 决策日志。

### 2.2 第一期不做什么（兜底声明）

- 不接真实生产数据。
- 不做真实自动外呼、短信批量发送。
- 不直接替代催收员作业。
- 不做完整 SaaS、多租户、企业审批流、监管报送。
- 不训练真实模型（数据底座支持，但 Phase 1 不出训练命令）。

### 2.3 长期定位（不在 Phase 1 实现，但要在数据底座预留）

覆盖**贷前 / 贷中 / 贷后 / 管理层 / 办公自动化**五大场景，详见 §11 路线图。

---

## 3. 目标用户与场景

### 3.1 角色清单（**新增：合并 v5 §3 和 §21**）

| 角色 ID | 角色 | 关键诉求 | 主要使用功能 |
|---|---|---|---|
| R1 | 风控策略人员 | 快速定位指标波动原因，把分析变成方案 | 异常检测、归因、Excel/Word 报告 |
| R2 | 基础数分 / 商分 | 不想重复写 SQL/Excel，要"有图有数有结论" | Dashboard、报告生成、SQL 生成 |
| R3 | 贷后管理者 | 看清盘面、找回收率波动原因、判断资源配置 | 经营驾驶舱、供应商分析、PPT |
| R4 | 一线催员 / 催收主管 | 知道客户怎么沟通、推荐话术、不踩合规线 | 案件摘要、话术推荐、合规检查 |
| R5 | 合规 / 质检人员 | 提高质检覆盖率、发现高风险话术 | 录音/文本质检、红线扫描 |
| R6 | 产品经理 / 经营负责人 | 把业务想法变成 PRD/PPT/会议材料 | 文档 Copilot、PRD 生成 |
| R7 | 业务督导 / 运营中台 | 盯执行、盯人效、盯异常闭环 | 督导驾驶舱、整改清单、工单 |
| R8 | 业务线 / 区域负责人 | 看经营盘面、资源配置决策 | 经营驾驶舱、月度复盘 PPT |
| R9 | 策略线负责人 / 风控决策者 | 评估策略体系健康度、风险收益平衡 | 策略追踪、Champion/Challenger 对比 |

### 3.2 角色-功能矩阵（**v6 新增**）

| 功能 \ 角色 | R1 策略 | R2 数分 | R3 贷后管理 | R4 催员 | R5 质检 | R6 PM | R7 督导 | R8 业务线 | R9 风控决策 |
|---|---|---|---|---|---|---|---|---|---|
| 经营驾驶舱 | ✓ | ✓ | ✓✓ | | | | ✓ | ✓✓ | ✓ |
| 异常检测 | ✓✓ | ✓ | ✓ | | | | ✓ | | ✓ |
| 多维归因 | ✓✓ | ✓ | ✓ | | | | | ✓ | ✓✓ |
| 供应商分析 | ✓ | | ✓✓ | | | | ✓✓ | ✓ | |
| 减免 ROI | ✓✓ | | ✓ | | | | | | ✓ |
| 投诉合规分析 | ✓ | | ✓ | | ✓✓ | | ✓ | | ✓ |
| 案件摘要 | | | | ✓✓ | | | | | |
| 话术推荐 | | | | ✓✓ | ✓ | | | | |
| 录音/文本质检 | | | | ✓ | ✓✓ | | ✓ | | |
| HTML 周报 | ✓ | ✓✓ | ✓ | | | ✓ | ✓ | ✓ | ✓ |
| Excel 附表 | ✓ | ✓✓ | ✓ | | | | | | |
| PPT 大纲 | ✓ | ✓ | ✓✓ | | | ✓ | | ✓✓ | ✓ |
| PRD/会议材料 | | | | | | ✓✓ | | | |

> 标注：✓✓ = 核心用户，✓ = 次要用户。空白 = 不直接服务。

### 3.3 七个核心 Demo 场景（Phase 1 全部要覆盖）

继承 v5 §6.2，原文搬入但加优先级：

| 场景 ID | 场景 | 优先级 | 关联角色 |
|---|---|---|---|
| S-A | 管理者查看贷后经营大盘 | P0 | R3, R8 |
| S-B | 策略人员分析回收率下滑 | P0 | R1, R9 |
| S-C | 供应商管理复盘 | P0 | R3, R7 |
| S-D | 减免策略 ROI 测算 | P1 | R1, R9 |
| S-E | 催收录音/文本质检 | P1 | R5 |
| S-F | 催员话术推荐与审批 | P1 | R4, R5 |
| S-G | 自动生成报告/PPT/Excel | P0 | R1, R2, R6 |

---

## 4. 总体架构

### 4.1 系统分层图

```
┌─────────────────────────────────────────────────────────────┐
│  输出层  TUI 控制台 │ HTML 报告 │ Excel │ PPT │ Word │ 飞书 │
├─────────────────────────────────────────────────────────────┤
│  Agent 层  主 Agent + Risk/Collection/Compliance/Report 专家 │
├─────────────────────────────────────────────────────────────┤
│  引擎层  异常检测 │ 归因 │ 可视化 │ 报告生成 │ 质检 │ 话术    │
├─────────────────────────────────────────────────────────────┤
│  指标层  指标字典（yaml）+ 计算引擎 + 血缘                    │
├─────────────────────────────────────────────────────────────┤
│  数据层  DIM / ODS / DWD / DWS / ADS（DuckDB / Parquet）      │
├─────────────────────────────────────────────────────────────┤
│  基础层  合成数据生成 │ 隐私分级 │ 数据质量规则                │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 技术栈选型（**v6 新增——固定下来不再漂移**）

| 层 | 选型 | 理由 | 替代方案 |
|---|---|---|---|
| 语言 | Python 3.11+ | 数据/AI 生态完备，本地化部署友好 | - |
| 包管理 | uv 或 poetry | 现代 Python 依赖管理 | pip + requirements.txt |
| 数据底座 | DuckDB | 单机柱式分析数据库，零运维，性能足够 18 个月数据 | SQLite（备用） |
| 数据格式 | Parquet（落盘）+ CSV（人工可读） | Parquet 列式压缩快；CSV 用于演示 | - |
| 数据生成 | numpy + pandas + Faker | 标准 | - |
| TUI 框架 | Textual（Rich 系） | 现代 TUI 库，支持响应式布局 | prompt_toolkit |
| 可视化 | Plotly（HTML 报告）+ ECharts（备选） | Plotly 单文件 HTML 自带交互，截图好看 | matplotlib（不选，图丑） |
| 报告引擎 | Jinja2 + Plotly + WeasyPrint（PDF 备选） | Jinja2 模板化 HTML，可扩展 PDF | - |
| Excel 生成 | openpyxl | 标准 | xlsxwriter |
| PPT 生成 | python-pptx | 标准 | - |
| Word 生成 | python-docx | 标准 | - |
| LLM | Claude（Anthropic API）首选 | 长上下文 + 工具调用稳定 | OpenAI（备用） |
| ASR（Phase 2） | 暂未决定 | 推迟到 Phase 4 选型 | Whisper（本地） |
| 配置 | YAML | 人工可读、可版本控制 | - |
| 测试 | pytest | 标准 | - |

### 4.3 工程目录结构（**v6 新增——一次定型**）

```
riskops_copilot/
├── pyproject.toml                # uv/poetry 配置
├── README.md
├── CLAUDE.md                     # AI 开发助手项目指引
├── PRD_v6.md -> ./docs/prd/      # 链接到当前 PRD
│
├── riskops/                      # 主代码
│   ├── __init__.py
│   ├── cli.py                    # TUI 入口
│   ├── data/                     # 数据层
│   │   ├── generators/           # 合成数据生成器
│   │   ├── warehouse/            # 数仓加工 ODS→DWD→DWS→ADS
│   │   └── quality/              # 数据质量检查
│   ├── metrics/                  # 指标计算引擎
│   │   ├── dictionary.py         # 指标字典加载
│   │   └── calculators/          # 各指标计算函数
│   ├── engines/                  # 业务引擎
│   │   ├── anomaly/              # 异常检测
│   │   ├── attribution/          # 归因
│   │   ├── visualization/        # 可视化
│   │   ├── report/               # 报告生成
│   │   ├── qc/                   # 催收质检
│   │   └── script/               # 话术推荐
│   ├── agents/                   # AI Agent
│   │   ├── orchestrator.py       # 主 Agent
│   │   ├── risk_analyst.py
│   │   ├── collection_strategy.py
│   │   ├── compliance_qa.py
│   │   ├── report_writer.py
│   │   └── prompts/              # Prompt 模板
│   └── tui/                      # 终端 UI
│
├── synthetic_data/               # 合成数据落盘
│   ├── dim/
│   ├── ods/
│   ├── dwd/
│   ├── dws/
│   └── ads/
│
├── metadata/                     # 元数据（唯一权威源）
│   ├── tables.yaml
│   ├── columns.yaml
│   ├── metric_dictionary.yaml
│   ├── metric_lineage.yaml
│   ├── privacy_policy.yaml
│   └── key_relationships.yaml
│
├── schemas/                      # 建表 SQL
│   ├── dim.sql
│   ├── ods.sql
│   ├── dwd.sql
│   ├── dws.sql
│   └── ads.sql
│
├── templates/                    # 报告模板
│   ├── html/
│   ├── ppt/
│   ├── word/
│   └── excel/
│
├── configs/                      # 业务配置
│   ├── compliance_rules.yaml
│   ├── anomaly_thresholds.yaml
│   └── attribution_rules.yaml
│
├── reports/                      # 生成的报告
├── exports/                      # 导出的 Excel/PPT/Word
│
├── docs/                         # 文档
│   ├── prd/
│   │   ├── PRD_v6.md             # 当前 PRD（本文件）
│   │   └── history/              # 历史版本
│   ├── data_dictionary.md        # 从 yaml 渲染
│   ├── metric_dictionary.md      # 从 yaml 渲染
│   ├── demo_script.md            # 演示脚本
│   └── decisions/                # ADR 决策记录
│
├── tests/
│   ├── test_data_quality.py
│   ├── test_metrics.py
│   └── test_engines/
│
└── scripts/                      # 一次性脚本
    ├── generate_synthetic_data.py
    ├── build_warehouse.py
    └── render_docs.py            # yaml → md 文档生成
```

### 4.4 TUI 与可视化的关系

继承 v5 §2.4：**终端发号施令，网页和文档展示成果**。

---

## 5. 数据底座规范

> **本章合并 v5 §8.1 + §15 + §15A + §22 四处散布内容**。当前为骨架，待逐章迁移补强。

### 5.1 数据分层

| 层 | 说明 | 隐私边界 |
|---|---|---|
| DIM | 主数据维表（客户/借据/案件/产品/渠道/供应商/线路/催员/策略） | P1-P4 字段共存，P4 仅 raw_secure |
| ODS | 模拟业务系统原始流水（还款/催收动作/催记/录音/投诉/减免/分案决策） | 可模拟 P4 但仅 raw_secure 目录 |
| DWD | 清洗去重的明细事实表 | 不允许 P4 |
| DWS | 主题宽表（借据/案件/客户日切、过程宽表、供应商线路产能、画像、标签） | 不允许 P4 |
| ADS | 应用指标表（驾驶舱、归因、供应商绩效、催员绩效、减免 ROI、合规质检） | 不允许 P4，默认无明细 |

### 5.2 隐私分级（P0–P4）

| 等级 | 含义 | 示例 | DWD/DWS/ADS | 报告 | LLM 上下文 |
|---|---|---|---|---|---|
| P0 | 非敏感公开 | product_code, province | ✓ | ✓ | ✓ |
| P1 | 业务内部 | customer_id, loan_id, case_id | ✓ | ✓ | ✓ |
| P2 | 脱敏个人 | mobile_masked, customer_id_hash | ✓ | ✓ | ✓ |
| P3 | 哈希/密文 | id_no_hash, mobile_hash | ✓ | 不展示 | 不直接送 |
| P4 | 明文敏感 | id_no, mobile_no, customer_name, address | ✗ | ✗ | ✗ |

### 5.3 核心主键关系

```
customer_id (1:N) loan_id (1:N) plan_id (1:N) repay_id
customer_id (1:N) case_id (1:N) action_id / note_id / decision_id
case_id (M:N) loan_id  通过 dim_case_loan_mapping
```

### 5.4 表清单（占位）

| 层 | 表数 | 迁移指引 |
|---|---|---|
| DIM | 10 | 迁移 v5 §15A.8（dim_customer / dim_loan / dim_case / dim_case_loan_mapping / dim_product / dim_channel / dim_vendor / dim_collection_line / dim_collector / dim_strategy） |
| ODS | 14 | 迁移 v5 §22.2 |
| DWD | 5 | 迁移 v5 §22.3 |
| DWS | 5+3 画像/标签 | 迁移 v5 §22.4 + §15A.11/15A.12 |
| ADS | 6 | 迁移 v5 §22.5 |

> **TODO（待补强）**：把所有表字段定义迁移到 `metadata/tables.yaml` 和 `metadata/columns.yaml`，md 只保留摘要。

### 5.5 合成数据规范

| 项 | 要求 |
|---|---|
| 时间窗 | 至少 18 个月 |
| 规模档位 | small（客户 2 万）/ medium（8 万）/ large（15 万+） |
| 异常埋点 | 最近 30 天埋入 v5 §15A.3 列出的 7 个故事线异常 |
| 标签穿越 | 严禁：特征只用观察日前，标签用观察日后 |
| 隐私 | P4 字段仅在 `raw_secure/` 目录生成，默认不进入分析流程 |

详见 v5 §15A.11 / §15A.13。

### 5.6 数据质量规则

迁移 v5 §15B.9，固化为 `tests/test_data_quality.py`。

### 5.7 数据资产输出物

- `metadata/*.yaml`（权威源）
- `docs/data_dictionary.md`（从 yaml 自动渲染）
- `docs/key_relationships.md`
- `docs/privacy_policy.md`

---

## 6. 指标资产规范

> **合并 v5 §8.2 + §15B**。当前为骨架。

### 6.1 指标字典字段定义

```yaml
- metric_code: recovery_rate_d7
  metric_name_cn: D7回收率
  business_domain: postloan_collection
  numerator: 入催后7天内累计回款金额
  denominator: 入催时点案件初始欠款金额
  formula: repay_amount_7d / initial_outstanding_amount
  grain: [date, vendor, line, collector, dpd_bucket]
  source_tables: [dim_case, ods_repayment_detail, dws_case_status_snapshot_di]
  filter_condition: case_create_date >= window_start
  owner: postloan_strategy_team
  refresh_frequency: daily
  version: v1.0
  notes: 金额口径，不含减免；账户口径另设 recovery_case_rate_d7
  change_log:
    - 2026-05-15: 初版
```

### 6.2 各业务域指标清单（Phase 1 优先级）

| 域 | 指标数 | Phase 1 P0 | Phase 1 P1 | 迁移指引 |
|---|---|---|---|---|
| 贷前 | 5 | 0 | 0（占位） | v5 §15B.1，Phase 2 实现 |
| 贷中 | 4 | 0 | 0（占位） | v5 §15B.2，Phase 2 实现 |
| 贷后结果 | 8 | 8 | 0 | v5 §15B.3，Phase 1 全部实现 |
| 催收过程 | 10 | 7 | 3 | v5 §15B.4 |
| 合规质检 | 5 | 3 | 2 | v5 §15B.5 |
| 减免 ROI | 3 | 2 | 1 | v5 §15B.6 |
| 模型 | 4 | 0 | 0（占位） | v5 §15B.7，Phase 2 实现 |

### 6.3 唯一权威源原则

- 指标定义只在 `metadata/metric_dictionary.yaml`。
- md 文档只引用 metric_code，不重抄口径。
- 计算函数与指标 code 一一对应。

### 6.4 维护机制

迁移 v5 §15B.8，落实为 PR 模板 + CI 检查（指标 code 唯一、yaml 字段完整、change_log 必填）。

---

## 7. 引擎能力

> **合并 v5 §4 + §8.3-§8.8 + §10**。每个引擎统一模板：目标 / 输入 / 输出 / 算法 / 验收。

### 7.1 异常检测引擎

| 项 | 内容 |
|---|---|
| 目标 | 识别核心指标的趋势/突变/结构/过程异常 |
| 输入 | ADS 指标日切表、阈值配置 |
| 输出 | 异常清单（指标/时间/当前值/基准值/幅度/等级/建议下钻） |
| 算法 | Phase 1 用统计规则：环比/同比/4 周均值±N σ/连续 N 天/过程指标背离 |
| 验收 | 在 Demo 数据上识别出全部 7 个埋点异常 |

详见 v5 §8.3。

### 7.2 归因引擎

| 项 | 内容 |
|---|---|
| 目标 | 把指标波动按六层（结构/客群/策略/资源/过程/合规）拆解到具体因子 |
| 输入 | 异常指标、维度配置、对照基准 |
| 输出 | 贡献度排序 Top N、瀑布图数据、归因结论文本 |
| 算法 | 分组对比 + 贡献度排序 + 结构变化拆解 + 过程指标相关性 + Top N 下钻 |
| 验收 | 对 M1 D7 回收率下降，归因能输出 v5 §8.4.3 示例水平的结论文本 |

详见 v5 §8.4。

### 7.3 可视化引擎

| 项 | 内容 |
|---|---|
| 目标 | 输出咨询报告级别的图表 |
| Phase 1 必做 10 图 | 经营总览卡片、M1 回收率趋势、催收过程漏斗、归因瀑布、供应商矩阵、线路热力、账龄余额段结构、减免 ROI、投诉风险地图、话术雷达 |
| 主题 | `dark_dashboard`（终端展示）+ `consulting_report`（PDF/PPT） |
| 技术 | Plotly + Jinja2 |
| 验收 | 截图能直接放 README 和简历 |

详见 v5 §8.5。

### 7.4 报告引擎

| 项 | 内容 |
|---|---|
| 目标 | HTML/Markdown/Excel/PPT/Word 多格式报告 |
| Phase 1 报告类型 | 经营日报、经营周报、归因报告、供应商复盘、减免 ROI、催收质检、PPT 大纲、Excel 附表、飞书草稿 |
| 报告结构 | 11 段标准结构（结论→指标→异常→归因→过程→供应商→ROI→合规→建议→跟进→附录） |
| 原则 | 先结论后过程；数据缺失要说明；不臆造 |
| 验收 | `/report weekly` 一条命令输出 5 种格式 |

详见 v5 §8.6 + §9。

### 7.5 催收质检引擎

| 项 | 内容 |
|---|---|
| 目标 | 文本/录音的合规、强度、投诉风险评分 |
| Phase 1 | 文本质检（11 维 + 红线识别）|
| Phase 2+ | 音频 ASR |
| 验收 | 跑通 v5 §8.7.2 全部 11 维度评分 |

详见 v5 §8.7。

### 7.6 话术推荐引擎

| 项 | 内容 |
|---|---|
| 目标 | 基于案件上下文生成合规话术，等待人工审批 |
| 原则 | AI 不直接发送、不直接外呼、不绕过人工 |
| 流程 | 生成 → 合规扫描 → 频次检查 → 人工审批 → Mock 发送 → 留痕 |
| 验收 | `/script case_xxx --channel sms` 跑通审批流 |

详见 v5 §8.8。

---

## 8. AI Agent 设计

> **v6 完整新增章节**。v5 §12 只列了 5 个 Agent 名字，没有编排规范、Prompt、上下文协议、成本估算。

### 8.1 Agent 角色与职责

| Agent | 职责 | Phase 1 | 工具调用 |
|---|---|---|---|
| **Orchestrator** | 解析用户命令、路由到专家、整合结果、维护对话上下文 | 必做 | 调用其他 Agent + 引擎 API |
| Risk Analyst | 指标分析、异常识别、多维归因、风险结论 | 必做 | 异常引擎、归因引擎、SQL |
| Collection Strategy | 分案/触达/减免/供应商策略建议 | 必做 | 指标查询、对照分析 |
| Compliance QA | 话术合规、录音质检、红线扫描 | 必做 | 质检引擎、规则库 |
| Report Writer | 周报/PPT/Word/飞书草稿 | 必做 | 报告引擎、模板 |
| Model Lab | 模型训练/评估/解释 | Phase 2+ 占位 | scikit-learn / lightgbm |

### 8.2 编排方式

Phase 1 采用**单主 Agent + 技能模块**模式，而非多 Agent 并行：
- Orchestrator 是唯一对外接口。
- 专家 Agent 实际上是带专用 Prompt + 工具集的"技能"，由 Orchestrator 同步调用。
- 不引入复杂多 Agent 框架（LangGraph/CrewAI 等），降低实现和调试成本。

Phase 2+ 再考虑：异步并行、消息总线、长期记忆。

### 8.3 上下文协议

| 上下文层 | 内容 | 持久化 |
|---|---|---|
| 项目级 | 当前项目、数据源、指标字典、已生成报告列表 | 落盘 `~/.riskops/project.yaml` |
| 会话级 | 本次对话历史、当前关注的指标/案件/供应商 | 内存 + 退出时落盘 |
| 调用级 | 单次工具调用的输入输出 | 仅日志 |

### 8.4 Prompt 模板规范

每个专家 Agent 必须有：
- `system_prompt.txt`：角色定义 + 业务边界 + 输出格式
- `examples/`：3-5 个 few-shot 示例
- `tools.yaml`：可调用工具清单和签名

#### 8.4.1 风险分析 Agent Prompt 原则

继承 v5 §13.1：
- 必须基于数据，不得臆造
- 数据不足要说明
- 先结论后证据
- 从结构/过程/策略/资源/合规/ROI 六个角度
- 输出像策略分析师不像 Chatbot
- 每个建议要有可执行动作

#### 8.4.2 催收 Agent Prompt 原则

继承 v5 §13.2：禁止威胁/恐吓/辱骂/骚扰/误导/绕过监管/骚扰第三方/超频深夜触达；所有发送必须人工审批。

#### 8.4.3 报告 Agent Prompt 原则

继承 v5 §13.3：管理层版简洁、分析师版详细、PPT 每页一结论、Excel 重口径、飞书重协作。

### 8.5 LLM 选型 / 成本 / 安全

| 维度 | 选择 | 备注 |
|---|---|---|
| 主 LLM | Claude（Anthropic API） | 长上下文 + 工具调用稳定 |
| 备选 | OpenAI GPT-4 | 通过配置切换 |
| 本地化备选 | Qwen / Llama（Ollama） | Phase 2+ 评估 |
| 单次任务预算 | < $0.50 | Demo 友好 |
| 上下文限制 | 不向 LLM 送 P3/P4 字段 | 由 Orchestrator 拦截 |
| 失败兜底 | LLM 不可用时退化到模板化输出 | 必做 |

### 8.6 Agent 验收标准

- Orchestrator 能正确解析 §11.1 所有命令并路由。
- 每个专家 Agent 在 Demo 数据上能输出符合 §13 Prompt 原则的内容。
- 全链路单次 Demo 跑通成本可估算且 < $5。

---

## 9. 合规与隐私

> **合并 v5 §14 + §15A.7 + §15A.9 + §15A.10**。

### 9.1 数据安全

- Phase 1 默认使用合成数据。
- 用户导入真实数据时强制提示脱敏要求。
- P3/P4 字段不进入 DWD/DWS/ADS、不进入报告、不送 LLM。

### 9.2 自动化决策边界

系统只生成建议和草稿，关键动作（外发、处置、法律动作、授信决策）必须人工确认。

### 9.3 催收合规红线

迁移 v5 §14.3，固化为 `configs/compliance_rules.yaml`：威胁/辱骂/冒充司法/诱导新增借贷/骚扰第三方/暴露隐私/超频/禁时段。

### 9.4 审计留痕

每次话术生成、审批、Mock 发送必须留痕（who/when/case/content/approval/result）。

### 9.5 Demo 中的合规演示

合成数据中故意埋入：
- 一条踩红线的话术 → 质检引擎识别
- 一次超频触达 → 合规扫描拦截
- 一个投诉敏感客户 → 推荐保护策略

---

## 10. 第一期交付计划

> **v6 完整新增**。把 v5 §16.1 的"功能列表"升级为可执行的里程碑 + 验收。

### 10.1 里程碑（建议时间线）

| 里程碑 | 时间窗 | 交付物 | 退出标准 |
|---|---|---|---|
| **M0 启动** | 第 1 周 | PRD v6 冻结、技术栈定型、工程目录建立 | 本文档 v6 评审通过 |
| **M1 数据底座** | 第 2-4 周 | 合成数据生成器、5 层数仓 SQL、metadata yaml、数据质量测试 | `python scripts/generate_synthetic_data.py --months 18 --scale medium` 跑通；`pytest tests/test_data_quality.py` 全绿 |
| **M2 指标资产** | 第 4-5 周 | 指标字典 yaml v1.0、计算引擎、ADS 指标表填充 | 贷后核心 20+ 指标可查询；指标 owner / 血缘 / 版本完整 |
| **M3 引擎核心** | 第 5-7 周 | 异常检测、归因、可视化三引擎 | Demo 数据上能识别 7 个埋点异常并归因 |
| **M4 报告与 TUI** | 第 7-9 周 | HTML/Excel/PPT/Word 报告、TUI 命令、Dashboard | `/report weekly` 输出 5 种格式；TUI 跑通 §11.1 所有 P0 命令 |
| **M5 催收 Copilot** | 第 9-10 周 | 文本质检、话术推荐、Mock 审批 | S-E / S-F 场景跑通 |
| **M6 Agent 整合** | 第 10-11 周 | Orchestrator + 4 个专家 Agent | 7 个 Demo 场景全部跑通 |
| **M7 演示包装** | 第 11-12 周 | README、截图、Demo 视频脚本、面试讲稿 | 5 分钟跑通主流程 |

### 10.2 验收清单（客观判定）

#### 数据底座
- [ ] 合成数据 18 个月、medium 档生成无报错
- [ ] DIM/ODS/DWD/DWS/ADS 五层表全部建立
- [ ] `metadata/*.yaml` 五个文件齐全
- [ ] 数据质量测试全绿
- [ ] P4 字段未泄漏到 DWD 及以上

#### 指标资产
- [ ] 贷后结果指标 8 个全部可计算
- [ ] 催收过程指标 P0 7 个全部可计算
- [ ] 合规质检指标 P0 3 个全部可计算
- [ ] 减免 ROI 指标 P0 2 个全部可计算
- [ ] 指标字典 yaml 字段完整、含 owner 和 change_log

#### 引擎
- [ ] 异常检测识别全部 7 个埋点异常
- [ ] 归因引擎输出 Top 5 因子 + 瀑布图数据
- [ ] 10 张图表全部可生成且有两种主题
- [ ] HTML 周报包含 11 段标准结构

#### 催收 Copilot
- [ ] 文本质检 11 维度评分输出
- [ ] 红线话术能被识别
- [ ] 话术推荐 → 合规扫描 → 频次检查 → 审批 → Mock 发送 → 留痕 全链路跑通

#### Agent
- [ ] Orchestrator 解析 §11.1 全部 P0 命令
- [ ] 4 个专家 Agent 各有独立 system_prompt
- [ ] 单次 Demo 跑通 LLM 成本估算 < $5

#### 演示
- [ ] README 截图 ≥ 8 张
- [ ] 5 分钟演示脚本 + 视频
- [ ] 面试讲稿 v1

### 10.3 演示资产清单

| 资产 | 用途 | 状态 |
|---|---|---|
| `README.md` | GitHub 首页 | M7 |
| `docs/demo_script.md` | 5 分钟现场演示脚本 | M7 |
| `docs/interview_pitch.md` | 面试讲稿 | M7 |
| `docs/screenshots/` | 8+ 张代表性截图 | M7 |
| `docs/demo_video.mp4` | 录屏 Demo | M7（可选）|
| `docs/data_dictionary.md` | 数据字典（从 yaml 渲染） | M1 |
| `docs/metric_dictionary.md` | 指标字典（从 yaml 渲染） | M2 |

---

## 11. 路线图

> 继承 v5 §16，仅补优先级标签。

### 11.1 Phase 1：贷后样板间（当前）

见 §10。

### 11.2 Phase 2：贷前 + 贷中风险经营 Copilot

迁移 v5 §16.2。重点：申请漏斗、首逾 / Vintage、评分卡 / XGBoost、AUC/KS/PSI、额度定价模拟、贷中预警、风险迁徙。

### 11.3 Phase 3：模型与策略闭环

迁移 v5 §16.3。重点：策略动作库、Champion/Challenger、策略 Playbook 自动沉淀。

### 11.4 Phase 4：录音 ASR 与质检增强

迁移 v5 §16.4。

### 11.5 Phase 5：办公文档自动化增强

迁移 v5 §16.5。

### 11.6 Phase 6：远程数据源与企业化雏形

迁移 v5 §16.6。

---

## 12. 风险与依赖登记

> **v6 完整新增**。

| ID | 风险/依赖 | 影响 | 概率 | 缓解措施 | 触发点 |
|---|---|---|---|---|---|
| R-01 | LLM API 成本失控 | 高 | 中 | Phase 1 限单次任务预算 $0.5；模板化兜底 | LLM 调用次数 |
| R-02 | 合成数据"不像真的" | 中 | 中 | 故事线设计 + 业务朋友 review | M1 退出前 |
| R-03 | Plotly HTML 图表样式不够"咨询风" | 中 | 中 | 提前调主题，做 2-3 个样例先 review | M3 中段 |
| R-04 | Textual TUI 学习成本 | 中 | 中 | M0 做最小可运行 demo 验证 | M0 |
| R-05 | 指标口径在多处不一致 | 高 | 高 | yaml 唯一权威源 + CI 校验 | M2 |
| R-06 | P4 字段泄漏到 LLM 上下文 | 高 | 低 | Orchestrator 强制拦截 + 单元测试 | M6 |
| R-07 | 演示故事讲不清 | 高 | 中 | M0 先写 demo_script v0，反向驱动设计 | M0 |
| R-08 | Phase 2/3 范围蔓延回 Phase 1 | 高 | 高 | 范围矩阵 §2.1 是唯一锚点；新需求需 ADR | 持续 |
| R-09 | DuckDB 性能在 large 档不够 | 低 | 低 | medium 档为主；large 档延后 | M1 |
| R-10 | ASR 选型推迟导致 Phase 4 卡壳 | 低 | 中 | Phase 4 前再决定 | Phase 4 启动 |

---

## 13. 决策日志（ADR）

> **v6 完整新增**。每个重要决策一行 ADR 摘要，详细 ADR 文件放 `docs/decisions/`。

| ADR ID | 决策 | 日期 | 状态 |
|---|---|---|---|
| ADR-001 | Phase 1 用 DuckDB 而非 SQLite/MySQL | 2026-05-15 | Accepted |
| ADR-002 | TUI 采用 Textual 而非 prompt_toolkit | 2026-05-15 | Accepted |
| ADR-003 | 可视化采用 Plotly 而非 matplotlib | 2026-05-15 | Accepted |
| ADR-004 | LLM 主用 Claude API | 2026-05-15 | Accepted |
| ADR-005 | Phase 1 采用单主 Agent + 技能模块，不引入多 Agent 框架 | 2026-05-15 | Accepted |
| ADR-006 | 指标字典以 yaml 为唯一权威源，md 不重抄口径 | 2026-05-15 | Accepted |
| ADR-007 | Phase 1 不接真实短信/外呼 SDK | 2026-05-15 | Accepted |
| ADR-008 | Phase 1 不训练 ML 模型，数据底座预留 | 2026-05-15 | Accepted |
| ADR-009 | ASR 选型推迟到 Phase 4 | 2026-05-15 | Deferred |
| ADR-010 | 飞书 API 写入推迟到 Phase 5；Phase 1 只产飞书友好 Markdown | 2026-05-15 | Accepted |

---

## 14. 附录

### 14.1 命令清单（继承 v5 §11，加优先级）

| 命令 | 优先级 | 说明 |
|---|---|---|
| `/load <path>` | P0 | 加载本地数据 |
| `/tables` / `/schema` / `/sample` / `/quality` | P0 | 数据检视 |
| `/sql <question>` | P1 | 生成 SQL |
| `/metrics` / `/metric <code>` / `/trend` / `/compare` | P0 | 指标查询 |
| `/dashboard postloan` | P0 | 经营驾驶舱 |
| `/anomaly` / `/anomaly <metric>` | P0 | 异常检测 |
| `/explain <metric>` / `/drilldown` / `/why` | P0 | 归因 |
| `/vendor review` | P0 | 供应商复盘 |
| `/roi <policy>` | P1 | 减免 ROI |
| `/case <id>` / `/script <id>` | P1 | 案件与话术 |
| `/qc <file>` | P1 | 质检 |
| `/approve` / `/reject` / `/mock-send` | P1 | 审批流 |
| `/report daily|weekly|vendor|roi|qc` | P0 | 报告 |
| `/export html|excel|ppt-outline|feishu` | P0 | 导出 |
| `/model *` | P3（Phase 2+）| 建模 |
| `/doc *` / `/ppt *` / `/word *` / `/feishu *` | P1 | 办公文档 |

### 14.2 词汇表

| 术语 | 含义 |
|---|---|
| DPD | Days Past Due，逾期天数 |
| MOB | Months on Book，账龄月数 |
| PTP | Promise to Pay，承诺还款 |
| Vintage | 按放款月份观察的资产表现曲线 |
| Roll Rate | 滚动率 / 迁徙率 |
| AUC/KS/PSI/Lift | 模型评估指标 |
| OOT | Out-of-Time，跨期验证 |
| FPD | First Payment Default，首逾 |

### 14.3 与 v5 章节对照表（迁移指引）

| v6 章节 | v5 来源章节 |
|---|---|
| §1 愿景 | v5 §1 |
| §2.1 范围矩阵 | v5 §2 + §6.1 整理重构 |
| §3 用户 | v5 §3 + §21 |
| §4.1 架构 | v5 §4 + §7 |
| §4.2 技术栈 | **新增** |
| §4.3 目录结构 | v5 §15A.10 + §15.2 整理 |
| §5 数据底座 | v5 §8.1 + §15 + §15A + §22 |
| §6 指标资产 | v5 §8.2 + §15B |
| §7 引擎 | v5 §4 + §8.3-§8.8 |
| §8 Agent | **重写**（v5 §12 + §13 仅作素材） |
| §9 合规 | v5 §14 + §15A.7/9/10 合并 |
| §10 交付计划 | **重写**（v5 §18 仅作素材） |
| §11 路线图 | v5 §16 |
| §12 风险 | **新增** |
| §13 决策日志 | **新增** |
| §14 命令/词汇 | v5 §11 + 新增词汇表 |

### 14.4 待办（v6 之后的补强任务）

- [ ] T-01：把 v5 §22 全部表字段迁移到 `metadata/tables.yaml` + `metadata/columns.yaml`
- [ ] T-02：把 v5 §15B 全部指标迁移到 `metadata/metric_dictionary.yaml`
- [ ] T-03：写 `docs/decisions/ADR-001` 到 `ADR-010` 详细版
- [ ] T-04：写 `docs/demo_script_v0.md`（反向驱动 M1-M7 设计）
- [ ] T-05：补 §5.4 各层表的字段摘要（保留在 md 的简版，详版在 yaml）
- [ ] T-06：补 §7 各引擎的算法细节（伪代码或公式）
- [ ] T-07：补 §8 每个专家 Agent 的 system_prompt 草稿
- [ ] T-08：把 v5 §17（作品集包装）整理进 §10.3 或独立成 `docs/interview_pitch.md`
- [ ] T-09：补 §10.1 里程碑的依赖关系图
- [ ] T-10：补完整的 §11 Phase 2-6 路线图（当前仅指向 v5）
