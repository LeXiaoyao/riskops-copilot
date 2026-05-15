# RiskOps Copilot 产品需求文档（PRD v6）

> 本文档是 RiskOps Copilot 项目的需求总纲。v6 在 v5 的基础上做了**结构重组 + 完整性补强**，目标是：任何人 5 分钟看懂骨架，30 分钟挖到细节，工程同学可以直接据此拆解任务。
>
> v5 业务深度好但章节散布、缺优先级、缺技术约束、缺验收标准。v6 把所有"未来要做的点和要求"用一张范围矩阵 + 一张里程碑表 + 一张决策日志固定下来，作为后续不再漂移的基准。
>
> **当前文档状态**：**全部章节已写实**——§5 数据底座（五层表清单 + 隐私细则 + 主键 ER + 合成数据规范 + 数据质量规则）、§6 指标资产（贷后 26 个指标完整清单与公式）、§7 引擎能力（6 个引擎含算法/伪代码/验收/示例）、§11 路线图（Phase 1-6 全展开）。后续工作转向 metadata YAML 化与代码实现（详见 §14.4）。

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

本章定义 Phase 1 数据底座的**分层规则、隐私边界、主键关系、表清单、合成数据要求、数据质量规则**。所有引擎、指标、Agent 的工作都建立在本章之上。

> **唯一权威源**：表与字段的完整定义在 `metadata/tables.yaml` + `metadata/columns.yaml`（M1 产出）。本章只保留**用途/粒度/主键/关键字段摘要**，不重抄全部字段。

### 5.1 数据分层

| 层 | 说明 | 隐私边界 | 产出规则 |
|---|---|---|---|
| **DIM** | 主数据维表（客户/借据/案件/产品/渠道/供应商/线路/催员/策略） | P1-P4 字段共存，**P4 仅 raw_secure** | 慢变维度，日更或周更 |
| **ODS** | 模拟业务系统原始流水（还款/催收动作/催记/录音/投诉/减免/分案决策） | 可模拟 P4 但仅 raw_secure | 模拟生产系统，流水细 |
| **DWD** | 清洗去重的明细事实表 | **不允许 P4** | 从 ODS 清洗，统一口径与维度 |
| **DWS** | 主题宽表（借据/案件/客户日切、过程宽表、供应商线路产能、画像、标签） | 不允许 P4 | 按主题域聚合，便于分析 |
| **ADS** | 应用指标表（驾驶舱、归因、供应商绩效、催员绩效、减免 ROI、合规质检） | **不允许 P4，默认无明细** | 直接服务看板与 Agent |

分层加工方向：`ODS → DWD → DWS → ADS`；DIM 横向关联所有层。

### 5.2 隐私分级（P0–P4）

#### 5.2.1 分级规则

| 等级 | 含义 | 典型字段 | DWD/DWS/ADS | 报告 | LLM 上下文 |
|---|---|---|---|---|---|
| **P0** | 非敏感公开 | product_code, province, city, dpd_bucket | ✓ | ✓ | ✓ |
| **P1** | 业务内部键 | customer_id, loan_id, case_id, vendor_id, collector_id | ✓ | ✓ | ✓ |
| **P2** | 脱敏个人 | mobile_masked（如 138****1234）, customer_id_hash | ✓ | ✓ | ✓ |
| **P3** | 哈希 / 密文 | id_no_hash, mobile_hash, bank_card_hash, customer_name_encrypted | ✓ | 不展示 | **不直接送 LLM** |
| **P4** | 明文 PII | id_no, mobile_no, customer_name, address, bank_card_no | **✗** | **✗** | **✗** |

#### 5.2.2 加密 / 哈希 / 脱敏约定

- `*_hash`：SHA256 不可逆哈希；用于去重、关联、黑名单匹配。
- `*_encrypted`：可逆密文；Phase 1 用 AES-GCM 模拟，密钥不入库。
- `*_masked`：展示用脱敏；如 `mobile_masked` 只保留首三位与末四位。

#### 5.2.3 LLM 上下文准入规则（**强制**）

- Orchestrator 在向 LLM 发送上下文前，必须扫描字段元数据。
- P3 字段：默认不发送；如确需关联，只送哈希值并附"哈希字段，已脱敏"说明。
- P4 字段：**任何情况下不允许送入 LLM**；违反者属于 Bug。
- 报告生成时，模板必须基于 P0/P1/P2 字段；如必须展示个人，使用 `customer_id_hash + mobile_masked`。

详见 `metadata/privacy_policy.yaml`。

### 5.3 核心主键关系

#### 5.3.1 主键清单

| 主键 | 含义 | 备注 |
|---|---|---|
| `customer_id` | 客户号 | 贯穿贷前 / 贷中 / 贷后 |
| `customer_id_hash` | 客户号哈希 | 数仓与管理侧默认展示标识 |
| `loan_id` | 借据号 | 还款计划/明细/借据状态归属 |
| `plan_id` | 还款计划 ID | 每期应还计划 |
| `repay_id` | 还款流水 ID | 还款明细 |
| `case_id` | 案件编号 | 催收作业核心实体 |
| `action_id` | 催收动作 ID | 电话/短信/AI 外呼/语音 |
| `note_id` | 催记 ID | 催员作业文本记录 |
| `decision_id` | 分案决策 ID | 分案引擎流水 |
| `vendor_id` / `line_id` / `collector_id` | 供应商/线路/催员 ID | 资源维度 |

#### 5.3.2 关系图（文字版 ER）

```
customer_id ──┬─── 1:N ─── loan_id ─── 1:N ─── plan_id ─── 1:N ─── repay_id
              │
              └─── 1:N ─── case_id ──┬── 1:N ─── action_id
                                     ├── 1:N ─── note_id
                                     ├── 1:N ─── decision_id
                                     └── M:N ─── loan_id（经 dim_case_loan_mapping）

vendor_id ─── 1:N ─── line_id ─── 1:N ─── collector_id
                                  │
                                  └── 当前作业 case_id（关系动态）
```

详见 `metadata/key_relationships.yaml`。

### 5.4 表清单

#### 5.4.1 DIM 层（10 表）

| 表名 | 用途 | 粒度 | 主键 | 关键字段摘要 |
|---|---|---|---|---|
| `dim_customer` | 客户基础信息 | customer_id | customer_id | customer_id_hash, gender, age_group, province, occupation_type, customer_segment, risk_level_current, sensitive_flag, blacklist_flag |
| `dim_loan` | 借据基础属性 | loan_id | loan_id | customer_id, product_code, channel_code, loan_amount, loan_term, interest_rate, loan_status, first_due_date, mob, vintage_month |
| `dim_case` | 催收案件主数据 | case_id | case_id | customer_id, case_create_time, case_type, initial_dpd_bucket, initial_outstanding_amount, current_vendor_id, current_line_id, protect_flag, sensitive_flag, complaint_flag |
| `dim_case_loan_mapping` | 案件-借据 M:N 映射 | mapping_id | mapping_id | case_id, loan_id, customer_id, mapping_start_date, mapping_end_date, main_loan_flag |
| `dim_product` | 产品维表 | product_code | product_code | product_name, product_type, funder_type, interest_rate_min/max, term_min/max, online_flag |
| `dim_channel` | 渠道维表 | channel_code | channel_code | channel_name, channel_type, partner_name, online_flag |
| `dim_vendor` | 供应商维表 | vendor_id | vendor_id | vendor_name, vendor_type（自营/委外/AI外呼/律所）, max_capacity, settlement_method, compliance_level |
| `dim_collection_line` | 催收线路 | line_id | line_id | vendor_id, line_type（M1/M2/M3+/法诉/AI外呼）, dpd_bucket_scope, capacity_limit |
| `dim_collector` | 催员维表 | collector_id | collector_id | vendor_id, line_id, role_type, entry_date, skill_level, max_daily_case_capacity, compliance_level |
| `dim_strategy` | 策略维表 | strategy_id | strategy_id | strategy_type（分案/触达/减免/保护/法诉）, strategy_version, effective_start/end_date, owner_team |

#### 5.4.2 ODS 层（14 表）

| 表名 | 用途 | 粒度 | 主键 |
|---|---|---|---|
| `ods_repayment_plan` | 每笔借据每期应还计划 | plan_id | plan_id |
| `ods_repayment_detail` | 真实还款流水 | repay_id | repay_id |
| `ods_loan_daily_snapshot` | 借据日切片状态 | stat_date+loan_id | (stat_date, loan_id) |
| `ods_case_daily_snapshot` | 案件日切片状态 | stat_date+case_id | (stat_date, case_id) |
| `ods_customer_daily_snapshot` | 客户日切片 | stat_date+customer_id | (stat_date, customer_id) |
| `ods_case_flow` | 案件状态流转 | flow_id | flow_id |
| `ods_assignment_decision_log` | 分案决策流水 | decision_id | decision_id |
| `ods_postloan_c_score` | 贷后 C 卡分（历史快照） | score_id | score_id |
| `ods_collection_note` | 催记 | note_id | note_id |
| `ods_collection_action` | 催收动作（拨打/短信/AI外呼） | action_id | action_id |
| `ods_call_record` | 外呼录音/转写 | call_id | call_id |
| `ods_sms_send_log` | 短信/语音发送日志 | message_id | message_id |
| `ods_reduction_application` | 减免申请 | reduction_id | reduction_id |
| `ods_complaint` | 投诉记录 | complaint_id | complaint_id |

ODS 层关键字段示例（每表 5-10 个核心字段）见 `metadata/columns.yaml`。

#### 5.4.3 DWD 层（5 表）

| 表名 | 用途 | 粒度 | 来源 |
|---|---|---|---|
| `dwd_due_plan_detail_di` | 到期计划明细 | stat_date+plan_id | ods_repayment_plan + dim_loan |
| `dwd_repayment_detail_di` | 回款明细事实 | repay_id | ods_repayment_detail + dim_case + ods_case_daily_snapshot |
| `dwd_collection_action_detail_di` | 催收动作明细 | action_id | ods_collection_action + dim_collector |
| `dwd_case_flow_detail_di` | 案件流转明细 | flow_id | ods_case_flow + dim_strategy |
| `dwd_complaint_detail_di` | 投诉明细 | complaint_id | ods_complaint + dim_vendor + dim_collector |

清洗规则：去重、空值标准化、外键校验、字段类型统一、敏感字段过滤（移除 P4，保留 P2/P3 哈希）。

#### 5.4.4 DWS 层（5 主题宽表 + 3 画像/标签表）

**主题宽表**

| 表名 | 用途 | 粒度 |
|---|---|---|
| `dws_loan_status_snapshot_di` | 借据状态日切宽表（含 1/3/7/30 日回款窗口） | stat_date+loan_id |
| `dws_case_status_snapshot_di` | 案件状态日切宽表（含当日拨打/接通/PTP/回款） | stat_date+case_id |
| `dws_customer_status_snapshot_di` | 客户日切宽表（归户视角） | stat_date+customer_id |
| `dws_collection_process_wide_di` | 催收过程宽表（含首触达、PTP 履约、投诉） | stat_date+case_id |
| `dws_vendor_line_capacity_di` | 供应商线路产能宽表 | stat_date+vendor_id+line_id |

**画像 / 标签表**

| 表名 | 用途 | 粒度 |
|---|---|---|
| `dws_customer_profile_di` | 客户画像（基础/借款/还款/贷后/风险标签 50+ 字段） | stat_date+customer_id |
| `dws_collector_profile_di` | 催员画像（作业/结果/合规/话术 30+ 字段） | stat_date+collector_id |
| `dws_customer_postloan_tag_di` | 客户贷后标签日切（13 类标签） | stat_date+customer_id |

**贷后标签 6 大类**：账龄类 / 金额类 / 行为类 / 触达类 / 合规投诉类 / 策略类。

**Phase 2+ 占位表**：`dws_postloan_model_sample_di`（贷后建模样本宽表，Phase 1 表结构设计完成但暂不生成数据）。

#### 5.4.5 ADS 层（6 表）

| 表名 | 用途 | 服务对象 |
|---|---|---|
| `ads_postloan_dashboard_di` | 贷后经营驾驶舱日切（核心 15 指标） | 场景 S-A（管理者大盘） |
| `ads_recovery_attribution_di` | 回收率归因指标 | 场景 S-B（策略归因） |
| `ads_vendor_performance_di` | 供应商绩效日切 | 场景 S-C（供应商复盘） |
| `ads_collector_performance_di` | 催员绩效日切 | 督导/质检 |
| `ads_reduction_roi_di` | 减免 ROI 指标 | 场景 S-D（减免测算） |
| `ads_compliance_qc_di` | 合规质检指标 | 场景 S-E（质检） |

### 5.5 合成数据规范

#### 5.5.1 时间线设计

| 时间段 | 用途 | 数据特点 |
|---|---|---|
| T-18M ~ T-12M | 历史基线期 | 长期客户行为、借据表现、早期建模样本 |
| T-12M ~ T-6M | 模型训练期（Phase 2+ 用） | 样本量充足 |
| T-6M ~ T-3M | 验证期 | 用于策略稳定性评估 |
| T-3M ~ T-1M | OOT 测试期 | 跨期稳定性、PSI |
| 最近 90 天 | 经营分析期 | 用于贷后看板、催收运营、供应商、线路、回收率 |
| **最近 30 天** | **Demo 异常期** | **人为埋入 7 个故事线异常** |

#### 5.5.2 规模档位

| 档位 | 客户数 | 借据数 | 案件数 | 催收动作数 | 适用 |
|---|---:|---:|---:|---:|---|
| `small` | 20,000 | ~30,000 | ~10,000 | ~200,000 | 本地快速跑通 |
| `medium` | 80,000 | ~150,000 | ~50,000 | ~1,500,000 | 展示与分析（**默认**） |
| `large` | 150,000+ | ~300,000 | ~100,000 | ~5,000,000 | 建模与压力测试 |

#### 5.5.3 异常埋点清单（最近 30 天）

为支持 Demo 故事线归因，合成数据必须故意埋入以下 7 个异常：

1. **M1 D7 回收率**从 18.6% 降到 15.2%（核心故事）
2. **华东线路**人均案量提升 25%（产能不足）
3. **供应商 B 接通率**下降 6pct（执行问题）
4. **高余额客群**占比提升 8pct（结构变化）
5. **AI 外呼覆盖率**下降 12pct（资源问题）
6. **减免使用率**下降 4pct + PTP 履约率下降 5pct（策略问题）
7. **某短信模板投诉率**高于均值 2 倍（合规问题）

异常之间需有时序与因果关系，使归因引擎能输出"主因 + 次因 + 贡献度"的结构化结论。

#### 5.5.4 标签穿越约束

**强制规则**：
- 所有特征只能使用观察日（`sample_date`）**之前**的数据。
- 所有标签只能使用观察日**之后**指定窗口的数据。
- 训练 / 验证 / OOT 时间窗不允许重叠。
- 数据生成时统一打 `sample_date` 字段，由 CI 校验。

#### 5.5.5 隐私边界

- P4 明文字段仅在 `synthetic_data/raw_secure/` 目录生成（已 gitignore）。
- 默认数据生成流程产出 `*_hash`、`*_masked` 字段，**不产出明文**。
- 如需测试 P4 隔离逻辑，使用单独的 `--with-raw` flag 控制。

### 5.6 数据质量规则

#### 5.6.1 强制规则（CI 必须通过）

| 规则编号 | 规则 | 校验方式 |
|---|---|---|
| DQ-001 | DIM 主键唯一 | `count(distinct PK) == count(*)` |
| DQ-002 | 外键可关联 | `ods_repayment_detail.plan_id` 必须能关联 `ods_repayment_plan.plan_id` |
| DQ-003 | 金额非负 | 应还/回款/欠款/减免金额 ≥ 0 |
| DQ-004 | 日期不穿越 | `repay_time >= disburse_time`；标签日 > 特征日 |
| DQ-005 | P4 隔离 | DWD/DWS/ADS 不允许 P4 字段（字段名扫描） |
| DQ-006 | 比率范围 | 回收率/接通率/PTP 率等比率 ∈ [0, 1] |
| DQ-007 | 案件归户完整性 | 每个 `case_id` 至少关联 1 个 `loan_id` |
| DQ-008 | 时间序列完整性 | 日切表每个 stat_date 应有合理记录数（不能突降为零） |

#### 5.6.2 软规则（告警，不阻断）

| 规则编号 | 规则 | 阈值 |
|---|---|---|
| DQ-101 | 核心指标日环比波动 | 超过 30% 触发告警 |
| DQ-102 | 样本正负比 | 建模样本正负比 < 1:50 或 > 50:1 时告警 |
| DQ-103 | 字段空值率 | 非空字段空值率 > 5% 告警 |

数据质量规则代码实现：`tests/test_data_quality.py` + `riskops/data/quality/`。

### 5.7 数据资产输出物

#### 5.7.1 元数据文件（唯一权威源）

| 文件 | 内容 |
|---|---|
| `metadata/tables.yaml` | 所有表的元信息（表名/中文名/层级/主题/粒度/主键/用途） |
| `metadata/columns.yaml` | 所有字段的字典（字段名/中文/类型/主键/可空/隐私等级/口径） |
| `metadata/key_relationships.yaml` | 主键关系（5.3 节内容的机器可读版） |
| `metadata/privacy_policy.yaml` | 字段隐私分级 + 进入数仓/报告/LLM 规则 |
| `metadata/metric_lineage.yaml` | 指标血缘（指标 → DWS → DWD → ODS） |

#### 5.7.2 人工可读文档（从 yaml 自动渲染）

| 文档 | 渲染脚本 |
|---|---|
| `docs/data_dictionary.md` | `python scripts/render_docs.py data_dict` |
| `docs/key_relationships.md` | `python scripts/render_docs.py keys` |
| `docs/privacy_policy.md` | `python scripts/render_docs.py privacy` |
| `docs/data_lineage.md` | `python scripts/render_docs.py lineage` |

#### 5.7.3 SQL 与脚本

| 文件 | 内容 |
|---|---|
| `schemas/dim.sql`, `ods.sql`, `dwd.sql`, `dws.sql`, `ads.sql` | DuckDB 建表 SQL |
| `scripts/generate_synthetic_data.py` | 合成数据生成器 |
| `scripts/build_warehouse.py` | ODS → DWD → DWS → ADS 加工 |
| `scripts/render_docs.py` | yaml → md 文档渲染 |
| `tests/test_data_quality.py` | 数据质量测试 |

---


## 6. 指标资产规范

本章定义指标字典的字段结构、Phase 1 全部指标清单与口径、维护机制。**指标资产是 RiskOps Copilot 的语言系统**——所有引擎和 Agent 都通过 metric_code 调用，避免重复实现。

> **唯一权威源**：`metadata/metric_dictionary.yaml`（M2 产出）。本章列出指标编码与口径摘要；完整 YAML 字段（owner / change_log / grain / source_tables 等）以文件为准。

### 6.1 指标字典字段定义

每个指标必须具备以下字段：

```yaml
- metric_code: recovery_rate_d7              # 唯一英文编码
  metric_name_cn: D7回收率                    # 中文名
  business_domain: postloan_collection       # 业务域
  metric_type: ratio                         # ratio / amount / count / score
  numerator: 入催后7天内累计回款金额          # 分子口径（业务描述）
  denominator: 入催时点案件初始欠款金额       # 分母口径（业务描述）
  formula: repay_amount_7d / initial_outstanding_amount  # 计算公式
  grain: [date, vendor, line, collector, dpd_bucket]     # 可下钻维度
  source_tables:                             # 来源表
    - dim_case
    - dwd_repayment_detail_di
    - dws_case_status_snapshot_di
  filter_condition: case_create_date >= window_start
  owner: postloan_strategy_team              # 业务 owner
  refresh_frequency: daily
  version: v1.0
  priority: P0                               # P0/P1/P2/P3
  notes: 金额口径，不含减免；账户口径另设 recovery_case_rate_d7
  change_log:
    - 2026-05-15: 初版
```

### 6.2 Phase 1 指标清单总览

| 业务域 | 指标数 | P0 | P1 | Phase 1 实现状态 |
|---|---:|---:|---:|---|
| 贷前 | 5 | 0 | 0 | 占位（Phase 2 实现） |
| 贷中 | 4 | 0 | 0 | 占位（Phase 2 实现） |
| **贷后结果** | **8** | **8** | **0** | **Phase 1 全部实现** |
| **催收过程** | **10** | **7** | **3** | **Phase 1 全部实现** |
| **合规质检** | **5** | **3** | **2** | **Phase 1 全部实现** |
| **减免 ROI** | **3** | **2** | **1** | **Phase 1 全部实现** |
| 模型 | 4 | 0 | 0 | 占位（Phase 2 实现） |
| **合计（Phase 1）** | **26** | **20** | **6** | — |

### 6.3 贷后结果指标（8 个，全部 P0）

| metric_code | 中文名 | 公式 | 粒度 |
|---|---|---|---|
| `due_account_count` | 到期账户数 | `count(distinct customer_id where due_date in window)` | date, product, channel, city, risk_level |
| `due_loan_count` | 到期借据数 | `count(distinct loan_id where due_date in window)` | date, product, channel |
| `due_total_amount` | 到期应还金额 | `sum(due_total_amount)` | date, product, channel |
| `collection_entry_rate` | 入催率 | `collection_entry_count / due_account_count` | date, product, dpd_bucket, risk_level |
| `recovery_rate_d7` | D7 回收率 | `repay_amount_within_7d_after_case_create / initial_outstanding_amount` | date, vendor, line, collector, dpd_bucket |
| `recovery_rate_d15` | D15 回收率 | `repay_amount_within_15d / initial_outstanding_amount` | 同上 |
| `recovery_rate_d30` | D30 回收率 | `repay_amount_within_30d / initial_outstanding_amount` | 同上 |
| `m1_recovery_rate` | M1 回收率 | `m1_repay_amount / m1_initial_outstanding_amount` | date, vendor, line, product, balance_segment, risk_level |

口径约定：
- 金额口径默认**不含减免**；账户口径以 `recovery_case_rate_*` 单独命名。
- 入催时点以 `case_create_date` 为锚；M1 以 `dpd_bucket = M1` 时的案件状态为锚。
- 滚动率 `roll_rate` / Vintage 坏账率 `vintage_bad_rate` 推迟到 Phase 2（需要更长观察期）。

### 6.4 催收过程指标（10 个，7 P0 + 3 P1）

| metric_code | 中文名 | 公式 | 优先级 |
|---|---|---|---|
| `call_coverage_rate` | 拨打覆盖率 | `called_case_count / assigned_case_count` | P0 |
| `valid_coverage_rate` | 有效覆盖率 | `valid_contact_case_count / assigned_case_count` | P0 |
| `connect_rate` | 接通率 | `connect_count / call_count` | P0 |
| `valid_contact_rate` | 有效沟通率 | `valid_contact_count / connect_count` | P0 |
| `first_contact_hours` | 首触达时效 | `avg(first_contact_time - assign_time)` 单位小时 | P0 |
| `ptp_rate` | PTP 率 | `ptp_count / valid_contact_count` | P0 |
| `ptp_keep_rate` | PTP 履约率 | `kept_ptp_count / matured_ptp_count` | P0 |
| `avg_call_duration_per_call` | 单通平均时长 | `sum(call_duration_sec where connect=1) / connect_count` | P1 |
| `avg_call_duration_per_collector` | 人均日通话时长 | `sum(call_duration_sec) / active_collector_count / work_days` | P1 |
| `collector_productivity` | 作业人效 | `repay_amount / active_collector_count` | P1 |

口径约定：
- "有效沟通"统一定义：接通且通话时长 ≥ 60 秒，且催记结果标记为有效。
- `ptp_keep_rate` 必须排除尚未到承诺日的 PTP，避免低估。
- 拨打 / 接通 / 有效沟通统计可按动作次数或案件去重两种口径，YAML 中以 `*_count` 与 `*_case_count` 区分。

### 6.5 合规与投诉指标（5 个，3 P0 + 2 P1）

| metric_code | 中文名 | 公式 | 优先级 |
|---|---|---|---|
| `complaint_rate` | 投诉率 | `complaint_case_count / active_case_count` | P0 |
| `complaint_per_10k_cases` | 万案投诉率 | `complaint_count / active_case_count * 10000` | P0 |
| `risk_phrase_hit_rate` | 高风险话术命中率 | `risk_phrase_hit_count / qa_checked_count` | P0 |
| `qa_fail_rate` | 质检不合格率 | `qa_fail_call_count / qa_checked_call_count` | P1 |
| `over_frequency_contact_rate` | 超频触达率 | `over_frequency_case_count / contacted_case_count` | P1 |

### 6.6 减免与 ROI 指标（3 个，2 P0 + 1 P1）

| metric_code | 中文名 | 公式 | 优先级 |
|---|---|---|---|
| `reduction_usage_rate` | 减免使用率 | `reduction_case_count / eligible_case_count` | P0 |
| `reduction_recovery_rate` | 减免回收率 | `repay_amount_after_reduction / reduction_case_outstanding_amount` | P0 |
| `reduction_roi` | 减免 ROI | `(actual_repay - expected_repay_without_reduction) / approved_reduction_amount` | P1 |

口径约定：
- `reduction_roi` 的"反事实回款"（`expected_repay_without_reduction`）通过历史同条件客群均值估算，Phase 1 不做因果推断；Phase 3 升级为对照组方法。
- 真实净增 vs 提前回款的拆分留待 Phase 3。

### 6.7 占位指标（Phase 2+ 实现，Phase 1 仅在数据底座预留字段）

**贷前域**：`approval_rate` / `disbursement_conversion_rate` / `fpd_rate` / `bad_rate` / `vintage_bad_rate`

**贷中域**：`credit_utilization_rate` / `post_limit_increase_overdue_rate` / `transaction_reject_rate` / `risk_migration_rate`

**模型域**：`auc` / `ks` / `psi` / `lift`

### 6.8 唯一权威源原则

- **定义只在 YAML**：`metadata/metric_dictionary.yaml` 是唯一权威源。
- **md 文档只引用 metric_code**：本章列出的口径摘要是阅读辅助；不允许在其他文档手抄口径。
- **代码与字典强对应**：`riskops/metrics/calculators/<metric_code>.py` 每个指标一个计算函数，函数名即 metric_code。
- **修改流程**：先改 YAML（含 change_log），CI 校验通过后才允许合并；md 通过 `scripts/render_docs.py metrics` 自动渲染。

### 6.9 指标资产维护机制

#### 6.9.1 元数据完整性（CI 校验）

| 校验项 | 规则 |
|---|---|
| metric_code 唯一性 | 全局唯一，命名风格 snake_case |
| 必填字段 | metric_code / metric_name_cn / business_domain / formula / grain / source_tables / owner / version / priority |
| change_log 必填 | 任何变更必须新增 change_log 一行 |
| 业务域枚举 | 限定为 preloan / midloan / postloan / collection / compliance / roi / model |
| 优先级枚举 | 限定为 P0 / P1 / P2 / P3 |

#### 6.9.2 血缘维护

`metadata/metric_lineage.yaml` 记录每个指标的加工链路：`metric_code → ADS 表 → DWS 表 → DWD 表 → ODS 表`。

#### 6.9.3 版本管理

- 同一 metric_code 允许多版本共存（如 v1.0 / v1.1），通过 `version` 字段区分。
- 历史口径变更必须保留旧版本和 change_log，便于报告复现。

#### 6.9.4 业务文档自动渲染

`docs/metric_dictionary.md` 从 YAML 自动渲染，包含：
- 按业务域分组的指标清单
- 每个指标的口径、公式、粒度、owner、版本
- change_log 时间轴

服务对象：非技术业务人员、面试展示、跨团队协作。

---


## 7. 引擎能力

本章定义 Phase 1 的六个核心引擎。每个引擎统一模板：**目标 / 输入 / 输出 / 算法 / 配置 / 验收 / 示例**。

引擎之间的关系：
- 异常检测 → 归因（异常是归因的触发器）
- 归因 → 报告 / 可视化（归因结论是报告的核心）
- 催收质检 + 话术推荐 是独立子链，服务 Collection Copilot 场景
- 所有引擎都通过指标字典调用 ADS / DWS 数据

---

### 7.1 异常检测引擎

**目标**：在结果指标和过程指标上自动识别趋势异常、突变异常、结构异常、过程异常，输出可下钻的异常清单。

**输入**：
- ADS 指标日切表（如 `ads_postloan_dashboard_di`）
- 阈值配置 `configs/anomaly_thresholds.yaml`
- 检测窗口（默认最近 14 天）

**输出**：每个异常包含字段
```
metric_code, anomaly_date, current_value, baseline_value, delta_pct,
delta_abs, severity, anomaly_type, suggested_drilldowns, evidence_chart_data
```

**算法（Phase 1 用统计规则，不引入复杂 ML）**：

| 检测类型 | 规则 | 默认参数 |
|---|---|---|
| 环比异常 | 当日相比前一日变化超过阈值 | ±15% |
| 同比异常 | 当日相比 7 天前变化超过阈值 | ±20% |
| 均值偏离 | 偏离过去 28 天均值超过 N 个标准差 | 2σ |
| 连续下降 | 连续 N 天单向变化 | 连续 5 天 |
| 过程-结果背离 | 过程指标恶化但结果指标暂未反映 | 过程恶化 + 结果稳定 ≥ 3 天 |
| 结构异常 | 某细分维度占比变化超过阈值 | ±5pct |

**严重度分级**：

| Severity | 标准 |
|---|---|
| `critical` | 偏离 ≥ 3σ 或连续 7 天恶化 |
| `high` | 偏离 ≥ 2σ 或环比超 25% |
| `medium` | 偏离 ≥ 1.5σ 或环比超 15% |
| `low` | 偏离 ≥ 1σ |

**伪代码**：
```python
def detect_anomalies(metric_code, window_days=14):
    series = load_metric_series(metric_code, window_days + 28)
    baseline = series[-(window_days+28):-window_days]
    recent = series[-window_days:]
    mu, sigma = baseline.mean(), baseline.std()

    anomalies = []
    for date, value in recent.items():
        if abs(value - mu) > 2 * sigma:
            anomalies.append(Anomaly(
                date=date, value=value, baseline=mu,
                severity=classify(value, mu, sigma),
                suggested_drilldowns=infer_drilldowns(metric_code),
            ))
    return anomalies
```

**验收**：在 §5.5.3 列出的 7 个埋点异常上，召回率 = 100%；误报数 ≤ 3 个。

**示例输出**：
> M1 D7 回收率最近 7 天从 18.6% 下降到 15.2%，下降 3.4pct，低于过去 28 天均值 2.1 个标准差，严重度为 high。建议下钻：供应商、线路、账龄结构、首触达时效。

---

### 7.2 归因引擎

**目标**：把指标波动按六层框架拆解到具体因子，输出"主因 + 次因 + 贡献度 + 证据"。

**六层归因框架**：

| 层 | 关注 | 数据源 |
|---|---|---|
| 1. 资产结构变化 | 案源是否变差（余额段/账龄/风险等级/渠道/产品） | DWS 案件状态宽表 |
| 2. 客户分层变化 | 高风险客户占比、失联客户占比、还款意愿 | DWS 客户画像 + 标签表 |
| 3. 策略动作变化 | 分案/减免/AI 外呼/短信策略调整 | DIM 策略表 + 流转表 |
| 4. 资源配置变化 | 供应商/线路/催员产能、人均案量 | DWS 供应商线路产能宽表 |
| 5. 过程执行变化 | 拨打覆盖、接通、PTP、履约、首触达 | DWS 催收过程宽表 |
| 6. 合规约束变化 | 投诉管控、敏感客群保护、禁呼规则 | ADS 合规质检表 |

**输入**：
- 异常指标（来自 7.1）
- 维度配置 `configs/attribution_rules.yaml`
- 对照基准（默认：过去 28 天均值）

**输出**：
- Top N 因子贡献度排名（默认 N=5）
- 瀑布图数据（基准值 → 各因子贡献 → 当前值）
- 归因结论文本（分析师风格）

**算法（Phase 1）**：

| 方法 | 用途 |
|---|---|
| 分组对比 | 按维度切分指标，比较各组与整体差异 |
| 贡献度分解 | `delta_contribution = (group_delta × group_weight)` |
| 结构变化拆解 | 区分"结构变化"和"组内变化"对总指标的影响 |
| 过程指标相关性 | 计算结果指标与过程指标的同步性 |
| Top N 下钻 | 在最大贡献维度内继续递归下钻（深度 ≤ 2） |

**伪代码**：
```python
def attribute(metric_code, anomaly_date):
    baseline = load_baseline(metric_code)
    current = load_current(metric_code, anomaly_date)
    total_delta = current.value - baseline.value

    contributions = []
    for dim in attribution_dims(metric_code):
        for group in groups(dim):
            group_delta = current.by(dim, group) - baseline.by(dim, group)
            weight = group_weight(dim, group)
            contributions.append(Contribution(
                dim=dim, group=group,
                contribution=group_delta * weight,
                contribution_pct=group_delta * weight / total_delta,
            ))

    top_n = sorted(contributions, key=abs(contribution), reverse=True)[:5]
    return top_n, build_waterfall(baseline, top_n, current)
```

**验收**：对 M1 D7 回收率下降异常，归因结论必须包含至少 4 个层次的因子，并指明主因（贡献度 > 30%）。

**示例输出**：
> 本周 M1 D7 回收率下降 3.4pct，主因不是单纯案源变差，而是"高余额高风险客群占比提升 + 华东线路产能不足 + 供应商 B 接通率下降 + 减免策略使用率降低"共同导致。其中供应商 B 对整体下降贡献约 0.9pct（27%），华东线路贡献约 0.7pct（21%），高余额客群结构变化贡献约 0.6pct（18%）。

---

### 7.3 可视化引擎

**目标**：把指标数据、异常、归因结果输出为咨询报告级别的图表。

**Phase 1 必做 10 张图**：

| 图表 | 数据源 | 用途 |
|---|---|---|
| 1. 经营总览卡片 | ADS 驾驶舱 | 核心 15 指标一屏展示 |
| 2. M1 回收率趋势图 | ADS 驾驶舱 + 异常清单 | 趋势 + 异常点标注 |
| 3. 催收过程漏斗图 | DWS 过程宽表 | 分案→覆盖→接通→有效沟通→PTP→履约 |
| 4. 归因瀑布图 | ADS 归因表 | 基准 → 各因子 → 当前 |
| 5. 供应商表现矩阵 | ADS 供应商绩效 | 横轴回收率、纵轴投诉率、气泡=案量 |
| 6. 线路产能热力图 | DWS 产能宽表 | 线路 × 日期 × 人均案量 |
| 7. 账龄/余额段结构图 | DWS 案件宽表 | 结构变化对回收率的影响 |
| 8. 减免 ROI 图 | ADS 减免 ROI | 减免金额 vs 回款提升 vs ROI |
| 9. 投诉风险地图 | ADS 合规质检 | 供应商/催员/话术维度 |
| 10. 话术质检雷达图 | 质检引擎输出 | 6 维评分 |

**主题（双主题）**：
- `dark_dashboard`：深色金融科技风，适合 TUI 旁边的浏览器和大屏。
- `consulting_report`：白底咨询报告风，适合 PDF/PPT/简历截图。

**技术栈**：Plotly（输出 HTML/SVG/PNG）+ Jinja2（HTML 模板）。

**配置**：`templates/html/charts/<chart_name>.json.j2`，每张图一个模板，参数化数据源。

**验收**：
- 10 张图全部可生成，每张支持两种主题切换。
- 截图分辨率 ≥ 1920×1080，能直接放 README 和简历。
- 同事/朋友评审：3 人 review，至少 2 人评价"像咨询报告"。

---

### 7.4 报告引擎

**目标**：把指标、异常、归因、可视化整合成多格式报告。

**Phase 1 报告类型**：

| 报告类型 | 触发命令 | 主要格式 |
|---|---|---|
| 经营日报 | `/report daily` | HTML + Markdown |
| 经营周报 | `/report weekly` | HTML + MD + Excel + PPT 大纲 + Word |
| 归因报告 | `/report attribution <metric>` | HTML + MD |
| 供应商复盘 | `/report vendor` | HTML + Excel |
| 减免 ROI 报告 | `/report roi <policy>` | HTML + Excel |
| 催收质检报告 | `/report qc` | HTML + Markdown |
| 飞书草稿 | `/export feishu` | 飞书友好 Markdown |

**11 段标准结构**：

1. 核心结论（≤ 3 条）
2. 指标总览（4-6 个核心指标卡片）
3. 异常识别（来自 7.1）
4. 多维归因（来自 7.2）
5. 过程指标分析
6. 供应商/线路分析
7. ROI 测算
8. 合规与投诉风险
9. 策略建议（可执行动作 3-5 条）
10. 后续跟进事项
11. 附录（数据口径、SQL、图表）

**原则**：

- **先结论后过程**：每一节顶部必有一句话结论。
- **数据为底**：每条结论必须能追溯到具体表和过滤条件。
- **数据缺失要说明**：缺什么、为什么、影响什么。
- **不臆造**：模型未训练就说未训练；样本不足就说不足。
- **管理层版 vs 分析师版**：通过 `--audience exec|analyst` 切换详略。
- **PPT 每页一结论**：PPT 大纲严格遵循"页标题 = 结论"。

**模板架构**：
```
templates/
├── html/
│   ├── weekly_report.html.j2
│   ├── attribution.html.j2
│   ├── partials/
│   │   ├── header.html.j2
│   │   ├── conclusion_card.html.j2
│   │   └── chart_block.html.j2
├── ppt/
│   └── weekly_outline.pptx
├── word/
│   └── analyst_report.docx
└── excel/
    └── vendor_review.xlsx.j2
```

**验收**：
- `/report weekly` 一条命令输出 5 种格式，全部可打开。
- HTML 报告在浏览器中显示无样式错乱。
- PPT 大纲 ≥ 9 页，每页有标题 + 结论 + 图表建议 + 讲稿备注。
- Excel 附表含明细表 + 透视表。

---

### 7.5 催收质检引擎

**目标**：对文本（Phase 1）/ 录音（Phase 2+）输出合规、强度、投诉风险评分，标注高风险句子。

**Phase 1 仅做文本**：输入催记或转写文本，输出质检报告。

**输入**：
- 单文件（`call_001.txt`）或批量目录
- 合规规则库 `configs/compliance_rules.yaml`

**输出**：质检报告字段
```
file_id, compliance_score (0-100), pressure_score (0-100),
complaint_risk_score (0-100), customer_attitude_inferred,
ability_tag_inferred, issue_list, risk_phrase_locations,
suggested_alternative_phrases, supervisor_review_required,
protect_strategy_recommended
```

**11 个质检维度**：

| 维度 | 内容 |
|---|---|
| 1. 开场身份说明 | 是否合规说明身份与公司 |
| 2. 账单事实说明 | 是否清楚说明欠款事实 |
| 3. 金额与日期说明 | 是否说明应还金额和日期 |
| 4. 客户异议识别 | 是否识别并响应客户异议 |
| 5. 还款方案引导 | 是否引导可行还款方案 |
| 6. 情绪控制 | 沟通是否克制、专业 |
| 7. 催收强度 | 是否过度施压（评分） |
| 8. 合规红线 | 是否触发禁止表达（见下） |
| 9. 投诉风险 | 综合预测投诉概率 |
| 10. PTP 确认 | 如有承诺，是否明确金额日期 |
| 11. 结束语规范 | 是否合规结束 |

**红线识别清单**（违规即 critical）：

- 威胁、恐吓
- 辱骂、侮辱
- 暗示非法后果（坐牢、上征信黑名单不实表达）
- 冒充司法机关
- 诱导新增借贷还款
- 暴露债务隐私给第三方
- 对无关联系人施压（亲属、同事）
- 在禁止时段触达（21:00-08:00）
- 模糊但带压迫性的表达

**算法（Phase 1）**：

1. 规则匹配：合规红线词库 → 命中即标记。
2. LLM 评分：把文本 + 11 维 prompt 送 Claude，输出结构化评分。
3. 规则与 LLM 评分加权融合：规则命中红线时强制 `compliance_score ≤ 30`。

**验收**：
- 在 100 条人工标注样本上，红线召回率 ≥ 95%、误报率 ≤ 10%。
- 11 个维度评分覆盖率 100%。
- 主管复核标记的准确率：在标注样本上 ≥ 80%。

**示例输出**：
> 通话 call_023 质检评分：合规 52、强度 78（偏高）、投诉风险 65（高）。命中红线 1 条（"你不还钱我让你儿子来还" → 暗示骚扰第三方）。建议主管复核。建议替代表达："如方便可联系您直系亲属协助核实信息，我们仅就您本人欠款进行沟通。"

---

### 7.6 话术推荐引擎

**目标**：基于案件上下文生成合规话术草稿，**永远不直接外发**——所有触达必须人工审批。

**输入**：
- 案件 ID + 渠道（sms / voice / ai_call）
- 案件上下文（账龄、应还金额、历史触达、客户标签、风险等级、敏感标识）

**输出**：草稿包含
```
draft_id, case_id, channel, recommended_target, draft_content,
compliance_scan_result, frequency_check_result, approval_status,
risk_level, supervisor_review_required
```

**话术类型（10 类）**：

1. 首次逾期提醒
2. D1 温和提醒
3. D3 事实提醒
4. D7 方案引导
5. D15 减免提醒
6. PTP 到期前提醒
7. 失联修复提醒
8. 投诉敏感客户低强度提醒
9. 高风险客户人工复核建议
10. 已承诺未履约跟进

**核心审批流程**：

```
1. Agent 生成草稿（基于上下文 + Prompt 模板）
2. 合规规则扫描（调用 7.5 同款规则库）
3. 触达频次检查（最近 7 天 SMS ≤ 3 次、Call ≤ 5 次等）
4. 显示风险等级 + 注意事项
5. 催员人工确认
6. 主管复核（投诉敏感/高风险案件强制）
7. Mock 发送（写入 ods_sms_send_log，不真实外发）
8. 审计留痕（who / when / case / content / approval / result）
```

**频次检查规则**（默认，可配）：

| 渠道 | 单日上限 | 7 日上限 | 禁止时段 |
|---|---|---|---|
| SMS | 2 | 5 | 21:00-08:00 |
| AI 外呼 | 3 | 10 | 21:00-08:00 |
| 人工电话 | 5 | 20 | 21:00-08:00 |

**验收**：
- 7 种话术类型均能生成草稿。
- 合规扫描能在生成阶段拦截红线话术。
- Mock 发送写入日志完整可追溯。
- 整链路在 demo 数据上跑通：`/script case_10086 --channel sms` → 审批 → Mock 发送 → 留痕。

**示例**：

输入：
```
/script case_10086 --channel sms
```

Agent 输出草稿：
> 【XX 金融】尊敬的客户，您的借款 ¥3,200 已逾期 7 天。如有还款困难，可申请分期减免（最高减 20%）。请于今日 18:00 前联系 4001234567 或回复 1 协商方案。如已还款请忽略。

合规扫描：✓ 通过；频次：今日 0 次、本周 1 次 ✓；风险等级：低；等待催员审批。

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

本章描述从 Phase 1 贷后样板间到 Phase 6 企业化雏形的完整路线。每个 Phase 列出**目标、范围、关键功能、典型问题、可视化、退出标准**。

> Phase 2-6 是**愿景规划**，不承诺具体时间。Phase 1 完成后再根据反馈和资源决定下一 Phase 优先级。

### 11.1 Phase 1：贷后样板间（当前）

详见 §10 第一期交付计划。本节作为路线图视角的概述。

**目标**：用合成贷后数据演完整故事，证明产品形态、业务价值、技术可行性、AI 差异化。

**核心 Demo 故事**：M1 D7 回收率下滑 → 自动归因到 6 个因子 → 输出经营周报和催员话术建议。

**退出标准**：参考 §10.2 验收清单。

---

### 11.2 Phase 2：贷前 + 贷中风险经营 Copilot

#### 11.2.1 目标

把产品从贷后单场景扩展为**风控全生命周期 Copilot**——证明这套方向不止贷后小工具，而是从审批、额度、交易、预警、催收、回款、合规的完整风险经营平台。

#### 11.2.2 范围

##### 贷前模块

| 子模块 | 关键功能 |
|---|---|
| 贷前经营漏斗分析 | 申请-授信-放款漏斗、审批通过率、放款转化率、渠道质量、产品/城市/客群通过率 |
| 贷前风险表现分析 | FPD7 / FPD30、MOB1/2/3 逾期率、Vintage 曲线、按渠道/产品/评分段坏账率、策略前后对比 |
| 贷前模型实验室 | Logistic / LightGBM / XGBoost 训练、AUC/KS/PSI/Lift、Score Band 分箱、SHAP 解释、模型稳定性监控、Champion/Challenger |
| 贷前策略模拟器 | 审批阈值 / 额度 / 定价模拟，通过率-坏账率-收益 trade-off 测算 |

##### 贷中模块

| 子模块 | 关键功能 |
|---|---|
| 额度与交易监控 | 额度使用率、交易成功 / 拒绝 / 风险命中率、提额申请与通过率、提额后逾期表现、降额冻结止付 |
| 客户风险迁徙 | 风险等级迁徙、行为异常检测、还款能力变化、多头活跃度消费变化、预警名单生成 |
| 贷中干预策略 | 提额 / 降额 / 冻结 / 拦截 / 提醒 / 分层运营建议，策略效果回溯 |

#### 11.2.3 典型问题

- 最近通过率为什么下降？是渠道变差还是规则收紧？
- 哪些拒绝规则命中过高，可能存在误杀？
- 模型有没有漂移？哪些特征贡献最大？
- 调整审批阈值后，规模 / 坏账 / 收益的平衡点在哪？
- 哪些用户提额后风险抬升？
- 哪些客户正在变差，应该提前干预？

#### 11.2.4 可视化补充

- 申请-授信-放款漏斗图
- 渠道质量矩阵
- Vintage 曲线
- KS / ROC / Lift / PSI 模型评估图
- 风险等级 Sankey 迁徙图
- 提额前后表现对比图

#### 11.2.5 退出标准

- 贷前指标字典 ≥ 15 个、贷中 ≥ 10 个完整 yaml 化。
- 至少 1 个评分卡和 1 个 XGBoost 模型跑通训练 / 评估 / 解释 / PSI 监控。
- 策略模拟器可输出"调整审批阈值 → 规模 / 坏账 / 收益"敏感性表。
- Demo 故事二：通过率异常归因。

---

### 11.3 Phase 3：模型与策略闭环

#### 11.3.1 目标

把贷前、贷中、贷后的分析结果串成**策略闭环**——发现风险 → 自动归因 → 策略建议 → 模拟收益 → 人工审批 → 监控效果 → 自动复盘 → 沉淀 Playbook。

#### 11.3.2 范围

| 子模块 | 关键功能 |
|---|---|
| 统一客户风险画像 | 跨贷前 / 贷中 / 贷后的客户综合画像 |
| 统一指标字典升级 | 跨业务域指标合并、版本管理、口径一致性检查 |
| 策略动作库 | 历史策略集中管理（分案、减免、保护、阈值、规则、定价） |
| 策略上线前模拟 | 反事实模拟、风险收益预估、敏感性分析 |
| 策略上线后监控 | 自动监控核心指标，发现策略未达预期 |
| Champion / Challenger | 多策略并行、流量分配、效果对比 |
| 策略复盘报告 | 上线 - N 天后自动出复盘报告 |
| 策略 Playbook 沉淀 | 把成功经验抽象成"如果 X 发生，建议做 Y"的规则库 |

#### 11.3.3 典型问题

- 这个策略上线后，回收率是真涨了还是结构性反弹？
- Champion 和 Challenger 谁更好？什么客群下分别有优势？
- 历史上类似情况，我们做过什么？效果如何？
- 当前问题适合什么 Playbook？

#### 11.3.4 退出标准

- 策略动作库 ≥ 30 个历史策略入库。
- 完成 ≥ 3 次完整闭环（上线 → 监控 → 复盘 → Playbook 沉淀）。
- 至少 1 对 Champion/Challenger 对比报告。

---

### 11.4 Phase 4：录音 ASR 与质检增强

#### 11.4.1 目标

把催收质检从文本扩展到音频，提升合规覆盖率与训练能力。

#### 11.4.2 范围

| 子模块 | 关键功能 |
|---|---|
| 音频转写 | ASR 转文本，支持普通话、粤语等 |
| 说话人识别 | 区分坐席与客户、识别第三方接听 |
| 高风险句子定位 | 在录音时间轴上标注红线发言 |
| 质检评分体系 | 在 7.5 的 11 维基础上扩展为 20+ 维 |
| 催员训练建议 | 基于个人质检数据生成个性化训练计划 |
| 供应商质检看板 | 按供应商汇总 QA 表现、对比、奖惩建议 |
| 投诉案例复盘 | 投诉发生时关联录音、归因到具体话术 |
| 话术训练模拟器 | AI 扮演不同客户类型，催员练习异议处理 |

#### 11.4.3 技术选型

- ASR：候选 Whisper（本地）、阿里 / 腾讯云 ASR、火山引擎。Phase 4 启动时再决定（参考 ADR-009）。
- 说话人分离：pyannote.audio 或商用方案。

#### 11.4.4 典型问题

- 上周 200 通录音里有多少触发了红线？分布在哪些催员？
- 哪些话术在哪类客户下投诉风险最高？
- 这个催员需要补什么训练？
- 这通录音为什么被投诉？关键时间点在哪？

#### 11.4.5 退出标准

- ASR 转写准确率 ≥ 90%（普通话）、≥ 85%（带方言口音）。
- 红线召回率 ≥ 95%。
- 话术训练模拟器支持 ≥ 5 种典型客户类型。

---

### 11.5 Phase 5：办公文档自动化增强

#### 11.5.1 目标

让 RiskOps Copilot 不仅替代基础数分商分工作，还能服务产品经理、运营督导、业务管理的整套文档协作流。

#### 11.5.2 范围

| 子模块 | 关键功能 |
|---|---|
| Word 报告增强 | 正式分析报告、咨询风格、管理层摘要版 |
| PPT 自动生成 | 不止大纲，直接生成可演示的 PPT 文件 |
| 飞书文档 API | 真实写入飞书文档、多维表格、知识库 |
| Excel 模板自动化 | 标准化日报 / 周报 / 月报底表 |
| 历史报告知识库 | 读取本地 Markdown / Word / PDF / Excel，搜索历史策略 |
| 会议纪要生成 | 从录音 / 转写 / 文字稿自动结构化 |
| PRD 生成 | 从需求讨论自动生成 PRD 草稿 |
| 管理层汇报材料 | 自动适配不同管理层风格 |
| 策略评审材料 | 自动整合策略 + 数据 + 风险 + 建议 |

#### 11.5.3 典型问题

- 把这周的分析变成 30 页 PPT，咨询风格，本周三汇报用。
- 找出过去半年所有提到"AI 外呼"的策略文档。
- 把这个会议录音转成结构化纪要，附行动项。
- 给我一份给 CEO 看的 5 分钟版本。

#### 11.5.4 退出标准

- 飞书 API 真实写入跑通。
- PPT 自动生成质量：3 人评审、≥ 2 人评价"可直接使用"。
- 知识库索引 ≥ 100 篇本地文档，搜索响应 ≤ 2 秒。

---

### 11.6 Phase 6：远程数据源与企业化雏形

#### 11.6.1 目标

从单机本地 Demo 走向**小团队可用的内部工具**——连接远程数据库、加权限审计、提供 Web Dashboard、支持任务调度。

#### 11.6.2 范围

| 子模块 | 关键功能 |
|---|---|
| 远程数据源 | MySQL / PostgreSQL / Hive / 阿里 MaxCompute / 腾讯 TBase 连接 |
| 权限角色 | 基础 RBAC：管理员 / 分析师 / 督导 / 催员 |
| 审计日志 | 谁在何时查看 / 修改 / 生成什么 |
| 数据脱敏增强 | 真实数据接入时的字段级脱敏 |
| Web Dashboard | 浏览器访问，替代 TUI 的轻量 Web 版 |
| API 服务 | 把核心能力暴露为 REST API |
| 消息审批流 | 飞书 / 企微推送审批 |
| 企业知识库 | 多人共享的策略 / 报告 / Playbook 库 |
| 任务调度 | 定时跑日报、定时数据质量监控、定时报警 |

#### 11.6.3 边界

- **不做完整 SaaS / 多租户 / 监管报送**——那是另一个量级的项目。
- **企业化雏形 = 5-20 人小团队可用**，不追求大规模并发。

#### 11.6.4 退出标准

- 接入至少 1 个真实远程数据源（沙箱或脱敏数据）。
- Web Dashboard 在 Chrome / Safari 上可用。
- 完成 1 次小团队（3-5 人）试用反馈循环。

---

### 11.7 跨 Phase 持续工作

下列工作贯穿所有 Phase，不归属任何单一 Phase：

| 工作 | 描述 |
|---|---|
| 文档资产维护 | PRD / 指标字典 / 数据字典 / ADR 持续更新 |
| 测试覆盖率 | 数据质量、指标计算、引擎逻辑、Agent 行为单测 |
| 演示资产更新 | 每个 Phase 完成后更新 README 截图、Demo 脚本、面试讲稿 |
| 性能优化 | DuckDB 查询调优、LLM 调用缓存、模板渲染加速 |
| 用户反馈循环 | 通过 Issues 收集反馈，决定下一个 Phase 优先级 |

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

**M0 阶段已完成**：

- [x] T-05：补 §5.4 各层表的字段摘要 — **已在 §5.4 完成**（10 DIM + 14 ODS + 5 DWD + 8 DWS + 6 ADS 表全部列出关键字段，详版留待 yaml）
- [x] T-06：补 §7 各引擎的算法细节 — **已在 §7 完成**（6 个引擎全部包含目标 / 输入 / 输出 / 算法 / 伪代码 / 验收 / 示例）
- [x] T-10：补完整的 §11 Phase 2-6 路线图 — **已在 §11 完成**（Phase 2-6 全部包含目标 / 范围 / 典型问题 / 退出标准）
- [x] §6 指标资产清单与公式 — **已在 §6 完成**（贷后 26 个指标全部列出 metric_code、中文名、公式、优先级）

**M1（数据底座）阶段交付**：

- [ ] T-01：把表字段迁移到 `metadata/tables.yaml` + `metadata/columns.yaml`（权威源；md 中的字段摘要将由 `scripts/render_docs.py` 反向校验同步）
- [ ] T-12：写 `schemas/*.sql` 五个建表 SQL（DuckDB 方言）
- [ ] T-13：写 `scripts/generate_synthetic_data.py` 合成数据生成器（含异常埋点）
- [ ] T-14：写 `tests/test_data_quality.py` 数据质量测试（DQ-001 ~ DQ-008 全覆盖）

**M2（指标资产）阶段交付**：

- [ ] T-02：把 §6 全部指标迁移到 `metadata/metric_dictionary.yaml`
- [ ] T-15：写 `riskops/metrics/calculators/<metric_code>.py` 计算函数（一指标一文件）
- [ ] T-16：写 `metadata/metric_lineage.yaml` 血缘

**M3-M7 阶段交付（参考 §10.1 里程碑）**：

- [ ] T-07：补 §8 每个专家 Agent 的 `system_prompt.txt` 草稿（M6 启动前完成）
- [ ] T-04：写 `docs/demo_script_v0.md`（反向驱动 M1-M7 设计，M0 末完成最佳）
- [ ] T-08：把 v5 §17（作品集包装）整理为独立 `docs/interview_pitch.md`（M7 完成）
- [ ] T-09：补 §10.1 里程碑依赖关系图（M0 末或 M1 启动前）

**ADR 详细版**：

- [ ] T-03：写 `docs/decisions/ADR-001.md` 到 `ADR-010.md` 详细版（每个决策一篇，包含 Context / Decision / Consequences / Alternatives）
