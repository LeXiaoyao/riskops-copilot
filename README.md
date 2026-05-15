# RiskOps Copilot

**面向消费金融风控与贷后策略的数据分析、指标归因、风险建模与经营报告自动化工作台**

[English](README.en.md) | 简体中文

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-Phase%201%20Building-blue)](docs/prd/PRD_v6.md)
[![PRD](https://img.shields.io/badge/PRD-v6-green)](docs/prd/PRD_v6.md)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)

> **RiskOps Copilot** 是一个本地化的 AI 智能分析工作台，把消费金融风控（贷前/贷中/贷后）、催收策略、合规质检、办公文档自动化等场景中的**重复性分析、归因、报告、质检、话术**工作产品化。
>
> 第一期聚焦**贷后样板间**：用合成数据演一个完整故事——M1 回收率下滑 → 自动归因到客群结构、供应商、线路、过程指标、减免策略、投诉话术 → 输出 HTML 周报、PPT 大纲、催员话术建议。

---

## 项目定位

```
合成数据 → 数据底座（DIM/ODS/DWD/DWS/ADS + 隐私分级 P0-P4）
       → 指标资产（指标字典 + 血缘 + 版本）
       → 引擎（异常检测 / 归因 / 可视化 / 报告 / 质检 / 话术）
       → AI Agent 编排（主 Agent + 风险/催收/合规/报告专家）
       → 输出层（TUI + HTML + Excel + PPT + Word + 飞书草稿）
```

**不是什么**：不是聊天机器人、不是通用 BI、不是企业级 SaaS、不接真实生产数据、不做真实外呼/短信发送。

**是什么**：一个能讲故事、能跑通、能截图放简历的**垂直 AI 工作台 Demo**，同时是个人风控方法论资产库。

---

## 核心能力（Phase 1 范围）

| 模块 | 能力 |
|---|---|
| **数据底座** | 合成贷后数据 18 个月，五层数仓（DIM/ODS/DWD/DWS/ADS），主键关系完备，隐私 P0-P4 分级 |
| **指标资产** | 贷后结果/过程/合规/ROI 共 23 个核心指标，yaml 唯一权威源，含 owner / 血缘 / 版本 |
| **异常检测** | 统计规则识别趋势/突变/结构/过程异常，输出异常清单与建议下钻维度 |
| **多维归因** | 按结构/客群/策略/资源/过程/合规六层拆解，Top N 贡献度排序 + 瀑布图 |
| **可视化** | 10 张咨询报告级图表（趋势/漏斗/瀑布/矩阵/热力/雷达），支持深色仪表盘 + 白底报告双主题 |
| **报告生成** | 一条命令输出 HTML / Markdown / Excel 附表 / PPT 大纲 / Word / 飞书草稿 |
| **催收 Copilot** | 文本质检（11 维 + 红线扫描）、合规话术推荐、Mock 审批与发送留痕 |
| **AI Agent** | 主 Agent + 风险分析 / 催收策略 / 合规质检 / 报告写作 四个专家技能模块 |

---

## 七大目标用户

| 角色 | 痛点 | RiskOps Copilot 提供 |
|---|---|---|
| 风控策略人员 | 指标波动归因慢，报告写不完 | 一键归因 + 报告草稿 |
| 数分 / 商分 | 重复拉数做透视 | 自动指标计算 + Excel 附表 |
| 贷后管理者 | 看不清盘面，定位不到供应商问题 | 经营驾驶舱 + 供应商红黄绿灯 |
| 一线催员 | 不知道客户怎么沟通、怕踩合规线 | 案件摘要 + 合规话术推荐 |
| 合规 / 质检 | 质检覆盖率低，红线话术漏检 | 文本质检 + 红线扫描 |
| 产品经理 | PRD / 汇报材料反复写 | 文档 Copilot |
| 业务督导 | 异常没闭环 | 督导清单 + 整改追踪 |

---

## 文档导览

| 文档 | 用途 | 状态 |
|---|---|---|
| [PRD v6](docs/prd/PRD_v6.md) | **需求总纲**（必读） | 骨架完成，逐章补强中 |
| [PRD 历史版本](docs/prd/history/) | v1–v5 演进档案 | 已归档 |
| [CHANGELOG](CHANGELOG.md) | 变更记录 | 持续更新 |
| 数据字典 | `metadata/*.yaml` 渲染 | M1 产出 |
| 指标字典 | `metadata/metric_dictionary.yaml` 渲染 | M2 产出 |
| Demo 脚本 | 5 分钟现场演示 | M7 产出 |
| 面试讲稿 | 作品集包装 | M7 产出 |

---

## 技术栈

- **语言**：Python 3.11+
- **包管理**：uv 或 poetry
- **数据底座**：DuckDB（柱式分析）+ Parquet / CSV
- **TUI**：Textual（Rich 系）
- **可视化**：Plotly（HTML 报告） + ECharts（备选）
- **报告引擎**：Jinja2 + Plotly + openpyxl + python-pptx + python-docx
- **LLM**：Claude（Anthropic API）首选，OpenAI 备选
- **配置**：YAML
- **测试**：pytest

详见 [PRD v6 §4.2 技术栈选型](docs/prd/PRD_v6.md#42-技术栈选型v6-新增固定下来不再漂移)。

---

## 项目结构

```
riskops-copilot/
├── riskops/              # 主代码（CLI / 数据 / 指标 / 引擎 / Agent / TUI）
├── synthetic_data/       # 合成数据（DIM/ODS/DWD/DWS/ADS 五层）
├── metadata/             # 元数据唯一权威源（表/字段/指标/血缘/隐私）
├── schemas/              # 建表 SQL
├── templates/            # 报告模板（HTML/PPT/Word/Excel）
├── configs/              # 业务配置（合规规则/异常阈值/归因规则）
├── docs/                 # 文档（PRD / 数据字典 / 决策 / 演示）
│   ├── prd/
│   │   ├── PRD_v6.md
│   │   ├── history/      # v1-v5 归档
│   │   └── en/           # 英文版
│   ├── decisions/        # ADR
│   └── screenshots/      # README 截图
├── reports/ exports/     # 生成的产物（不入库）
├── tests/                # 数据质量与单元测试
└── scripts/              # 一次性脚本（数据生成 / 数仓加工 / 文档渲染）
```

完整目录设计见 [PRD v6 §4.3](docs/prd/PRD_v6.md#43-工程目录结构v6-新增一次定型)。

---

## 路线图

| Phase | 主题 | 状态 |
|---|---|---|
| **Phase 1** | 贷后样板间：M1 回收率异常归因 + 催收 Copilot + 办公文档自动化 | 进行中 |
| Phase 2 | 贷前 + 贷中风险经营 Copilot（申请漏斗、Vintage、评分卡、提额降额） | 规划中 |
| Phase 3 | 模型与策略闭环（Champion/Challenger、Playbook 沉淀） | 规划中 |
| Phase 4 | 录音 ASR 与质检增强 | 规划中 |
| Phase 5 | 办公文档自动化增强（飞书 API、知识库） | 规划中 |
| Phase 6 | 远程数据源与企业化雏形 | 规划中 |

### Phase 1 里程碑

- **M0 启动**：PRD v6 冻结、技术栈定型、工程骨架建立 ← *当前*
- **M1 数据底座**：合成数据 + 五层数仓 + metadata yaml
- **M2 指标资产**：指标字典 v1.0 + 计算引擎
- **M3 引擎核心**：异常检测 + 归因 + 可视化
- **M4 报告与 TUI**：5 格式报告 + TUI 主流程
- **M5 催收 Copilot**：质检 + 话术 + 审批
- **M6 Agent 整合**：Orchestrator + 4 专家
- **M7 演示包装**：README + 截图 + 演示视频

详见 [PRD v6 §10 第一期交付计划](docs/prd/PRD_v6.md#10-第一期交付计划)。

---

## 当前状态

> 项目处于 **M0 启动阶段**：完成需求总纲（PRD v6）、工程骨架与仓库初始化。**尚未发布可运行版本**。
>
> 后续每完成一个里程碑，会发布对应版本（0.1.0 → 1.0.0）。

---

## 快速开始

> Phase 1 代码尚未实现。下方为**目标体验**预览，待 M4 完成后正式可用。

```bash
# 克隆仓库
git clone https://github.com/LeXiaoyao/riskops-copilot.git
cd riskops-copilot

# 安装依赖（待 M0 末实装）
uv sync   # 或 poetry install

# 生成合成数据（待 M1 实装）
python scripts/generate_synthetic_data.py --months 18 --scale medium

# 启动 TUI（待 M4 实装）
riskops
```

预期 Demo 流程：

```
> /load synthetic_data/
> /dashboard postloan       # 经营驾驶舱
> /anomaly M1_D7_回收率     # 异常检测
> /explain M1_D7_回收率     # 多维归因
> /vendor review            # 供应商复盘
> /roi reduction_policy_A   # 减免 ROI
> /qc call_001.txt          # 催收质检
> /script case_10086        # 话术推荐
> /report weekly --format html,xlsx,ppt-outline
```

---

## 设计原则

1. **业务先行**：先把指标口径、归因框架、合规规则想清楚，再写代码。
2. **数据为底**：所有结论必须有数据支撑，不臆造、不模糊。
3. **隐私分级**：P0-P4 五级，P4 明文敏感字段绝不进入数仓应用层、报告、LLM 上下文。
4. **人工兜底**：AI 只生成建议和草稿，所有外发动作必须人工审批。
5. **结论先行**：报告必须先讲结论再讲过程，管理层版要短、分析师版要细。
6. **唯一权威源**：指标定义在 yaml，文档只引用不重抄。
7. **范围克制**：Phase 1 只做贷后样板间，新需求先回范围矩阵对号入座。

详见 [PRD v6 §9 合规与隐私](docs/prd/PRD_v6.md#9-合规与隐私) 和 [§13 决策日志](docs/prd/PRD_v6.md#13-决策日志adr)。

---

## 贡献与反馈

本项目目前为**个人作品集 + 学习项目**，暂不接受外部代码贡献。

但欢迎以下形式的交流：
- 通过 [Issues](https://github.com/LeXiaoyao/riskops-copilot/issues) 反馈业务/技术建议
- 通过邮箱 xiaoyao201207@gmail.com 联系作者

---

## License

[MIT License](LICENSE) © 2026 LeXiaoyao

---

## 致谢

本项目灵感来自作者多年消费金融风控与贷后策略一线经验。文档版本演进自 v1（初版）到 v6（结构化总纲），完整演进档案见 [docs/prd/history/](docs/prd/history/)。
