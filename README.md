# RiskOps Copilot

RiskOps Copilot 是一个面向消费金融风控全生命周期的本地化 AI 智能分析工作台。项目以合成数据为基础，逐步沉淀数据底座、指标资产、分析引擎和报告输出能力。

## 当前状态

- **阶段**：M5 CLI Interaction MVP 已完成，v0.5.0 已发布
- **已完成**：M1 数据底座、M2 指标资产、M3 异常检测与归因、M4 Static Dashboard、M4 Business Report Renderer、M5 CLI Interaction MVP
- **当前输出**：`outputs/dashboard/dashboard.html`、`outputs/reports/m4_business_report.md`、`outputs/reports/m4_business_report.html`
- **Next**：M6 Model Lab / Strategy Evaluation Lab planning
- **未实现**：Interactive TUI、Agent、模型训练、催收质检、真实短信或语音触达、真实客户数据接入
- **需求基准**：[PRD v6](docs/prd/PRD_v6.md)

## 技术栈

- **语言**：Python 3.11+
- **数据底座**：DuckDB、pandas、PyArrow
- **数据生成**：Faker、NumPy
- **配置**：PyYAML
- **测试**：pytest
- **可视化与报告**：Plotly、Jinja2、openpyxl、python-pptx、python-docx
- **TUI 框架占位**：Textual

## 目录结构

```text
RiskOps_Copilot/
├── riskops/                 # Python 主包
│   ├── data/                # 数据生成、数仓加工、数据质量
│   ├── metrics/             # 指标与计算器
│   ├── engines/             # 分析、归因、可视化、报告等引擎占位
│   ├── agents/              # Agent 目录占位，M0 不实现
│   └── tui/                 # TUI 目录占位，M0 不实现
├── synthetic_data/          # 合成数据分层目录
│   ├── raw_secure/          # P4 明文字段本地目录，不入库
│   ├── dim/
│   ├── ods/
│   ├── dwd/
│   ├── dws/
│   └── ads/
├── metadata/                # 元数据占位
├── schemas/                 # schema 占位
├── templates/               # HTML/PPT/Word/Excel 模板占位
├── configs/                 # 配置占位
├── docs/                    # PRD、ADR、截图等文档
├── reports/                 # 生成报告目录，不入库
├── exports/                 # 导出文件目录，不入库
├── scripts/                 # M0 占位 CLI
└── tests/                   # 基础结构测试
```

## M5 CLI 快速入口

```bash
python scripts/riskops_cli.py --help
python scripts/riskops_cli.py summary
python scripts/riskops_cli.py anomalies
python scripts/riskops_cli.py drivers
python scripts/riskops_cli.py outputs
python scripts/riskops_cli.py render-dashboard
python scripts/riskops_cli.py render-report
```

- **summary**：显示项目状态、anomaly 总数、数据边界、常用命令入口
- **anomalies**：高优先级异常列表（severity / baseline / recent / recommended next step）
- **drivers**：M1 D7 回收率下降 Top 5 drivers + 业务口径边界说明
- **outputs**：输出文件路径与存在状态
- **render-dashboard / render-report**：重新渲染 Dashboard 和 Business Report

## 可用命令（全量）

```bash
python scripts/generate_synthetic_data.py --help
python scripts/build_warehouse.py --help
python scripts/render_docs.py --help
python scripts/validate_strategy_scenarios.py
python scripts/run_strategy_eval.py
python scripts/run_roi_calculator.py
python scripts/validate_data_quality.py --help
python scripts/validate_metric_quality.py --help
python scripts/render_dashboard.py
python scripts/render_business_report.py
pytest
```

## 下一步：v0.5.0 发布后

1. 发布 v0.5.0 CLI Interaction MVP。
2. 继续保持 P4 明文字段不进入 DWD / DWS / ADS / Dashboard / Report。

## 合规声明

- 本项目仅使用合成数据。
- 不接入真实客户信息。
- 不真实触达客户，不发送真实短信或语音。
- 所有外发、审批、催收相关能力在当前阶段均为占位或后续 Mock 演示范围。
