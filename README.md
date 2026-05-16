# RiskOps Copilot

RiskOps Copilot 是一个面向消费金融风控全生命周期的本地化 AI 智能分析工作台。项目以合成数据为基础，逐步沉淀数据底座、指标资产、分析引擎和报告输出能力。

## 当前状态

- **阶段**：M0 骨架阶段
- **已完成**：仓库目录、Python 包结构、占位 CLI、基础测试与项目配置
- **未实现**：TUI、Agent、Dashboard、模型训练、催收质检、真实短信或语音触达
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

## M0 可用命令

```bash
python scripts/generate_synthetic_data.py --help
python scripts/build_warehouse.py --help
python scripts/render_docs.py --help
python scripts/validate_data_quality.py --help
python scripts/validate_metric_quality.py --help
pytest
```

## 下一步：M1 数据底座

1. 建立 metadata 与 schemas 的最小权威源。
2. 实现合成数据生成器，只生成合规的模拟数据。
3. 建立 DIM/ODS/DWD/DWS/ADS 五层本地数据目录与 DuckDB/Parquet 加工链路。
4. 补充数据质量校验规则，确保 P4 明文字段不进入数仓应用层。

## 合规声明

- 本项目仅使用合成数据。
- 不接入真实客户信息。
- 不真实触达客户，不发送真实短信或语音。
- 所有外发、审批、催收相关能力在当前阶段均为占位或后续 Mock 演示范围。
