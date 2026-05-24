# RiskOps Copilot

**A synthetic demo for consumer finance post-loan risk operations: data analytics, metric attribution, offline strategy evaluation, and business reporting automation**

English | [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-Phase%201%20Building-blue)](docs/prd/PRD_v6.md)
[![PRD](https://img.shields.io/badge/PRD-v6-green)](docs/prd/PRD_v6.md)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)

> Public demo only: this project uses synthetic data only; it contains no real customer data, produces no real collection action, sends no SMS / voice / WhatsApp messages, and is not production risk decisioning.
>
> **RiskOps Copilot** is a local-first analytics demo that productizes repetitive **analysis, attribution, reporting, offline strategy evaluation, and ROI estimation** work for post-loan risk operations.
>
> Phase 1 focuses on a **post-loan show-room**: using synthetic data to tell a full story — M1 recovery rate drops → auto-attribute to customer mix, vendor performance, line capacity, process metrics, discount policy, and complaint-prone scripts → produce HTML weekly reports, PPT outlines, and collector script suggestions.

---

## Positioning

```
Synthetic Data → Data Foundation (DIM/ODS/DWD/DWS/ADS + privacy grading P0-P4)
              → Metric Assets (metric dictionary + lineage + version)
              → Engines (anomaly detection / attribution / visualization / report)
              → Model Lab (offline strategy evaluation / ROI calculator / baseline diagnostics)
              → Output Layer (CLI + static dashboard + Markdown / HTML reports)
```

**What it is NOT**: not a chatbot, not generic BI, not enterprise SaaS, no real production data, no real customer data, no real outbound call / SMS sending, and no production risk decisioning.

**What it IS**: a **vertical synthetic demo** that tells a coherent business story, runs end-to-end, and demonstrates risk operations methodology with local artifacts.

---

## Phase 1 Capabilities

| Module | Capabilities |
|---|---|
| **Data Foundation** | 18 months of synthetic post-loan data, 5-layer warehouse (DIM/ODS/DWD/DWS/ADS), complete primary-key relationships, P0-P4 privacy grading |
| **Metric Assets** | 23+ core post-loan metrics across result / process / compliance / ROI domains, YAML as single source of truth, with owner / lineage / version |
| **Anomaly Detection** | Statistical rules detecting trend / sudden-change / structural / process anomalies, with drill-down suggestions |
| **Attribution** | Six-layer decomposition (asset structure / customer mix / strategy / resource / process / compliance), Top-N contribution ranking + waterfall |
| **Visualization** | 10 consulting-grade charts (trend / funnel / waterfall / matrix / heatmap / radar), dual themes: `dark_dashboard` + `consulting_report` |
| **Reporting** | One command outputs HTML / Markdown / Excel / PPT outline / Word / Feishu-ready draft |
| **Model Lab** | Offline strategy evaluation, ROI calculator, and D7 any-payment response baseline diagnostics |
| **Boundary Controls** | Synthetic data only, no real customer data, no collection automation, no production risk decisioning |

---

## Target Users

| Role | Pain Point | What RiskOps Copilot Offers |
|---|---|---|
| Risk strategy analyst | Slow attribution, endless report writing | One-click attribution + report draft |
| Data / business analyst | Repetitive SQL & pivot tables | Auto-computed metrics + Excel attachments |
| Post-loan manager | Hard to see the big picture & vendor issues | Operations dashboard + vendor traffic-light |
| Front-line collector | Doesn't know how to talk to customer, fears compliance violations | Case summary + compliant script suggestion |
| Compliance / QA | Low QA coverage, missed red-line phrases | Text QA + red-line scanning |
| Product manager | Repeated PRD / deck writing | Document copilot |
| Business supervisor | No closed-loop on anomalies | Supervision checklist + remediation tracking |

---

## Documentation

| Document | Purpose | Status |
|---|---|---|
| [PRD v6](docs/prd/PRD_v6.md) | **Master requirements** (must-read) | Skeleton complete, content backfilling |
| [PRD v6 English](docs/prd/en/PRD_v6.en.md) | English version | In progress |
| [PRD History](docs/prd/history/) | v1–v5 evolution archive | Archived |
| [CHANGELOG](CHANGELOG.md) | Change log | Continuously updated |
| Data Dictionary | Rendered from `metadata/*.yaml` | M1 deliverable |
| Metric Dictionary | Rendered from `metadata/metric_dictionary.yaml` | M2 deliverable |
| Demo Script | 5-min live demo guide | Available |
| Interview Pitch | Portfolio packaging | Available |

---

## Tech Stack

- **Language**: Python 3.11+
- **Package manager**: uv or poetry
- **Data foundation**: DuckDB (columnar analytics) + Parquet / CSV
- **TUI**: Textual (Rich family)
- **Visualization**: Plotly (HTML reports) + ECharts (alternate)
- **Report engines**: Jinja2 + Plotly + openpyxl + python-pptx + python-docx
- **LLM**: Claude (Anthropic API) primary, OpenAI as fallback
- **Config**: YAML
- **Testing**: pytest

See [PRD v6 §4.2 Tech Stack Decisions](docs/prd/PRD_v6.md#42-技术栈选型v6-新增固定下来不再漂移).

---

## Project Structure

```
riskops-copilot/
├── riskops/              # Main code (CLI / data / metrics / engines / agents / TUI)
├── synthetic_data/       # Synthetic data (DIM/ODS/DWD/DWS/ADS 5 layers)
├── metadata/             # Single source of truth (tables / columns / metrics / lineage / privacy)
├── schemas/              # CREATE TABLE SQL
├── templates/            # Report templates (HTML/PPT/Word/Excel)
├── configs/              # Business configs (compliance rules / thresholds / attribution rules)
├── docs/                 # Documentation (PRD / data dict / decisions / demo)
│   ├── prd/
│   │   ├── PRD_v6.md
│   │   ├── history/      # v1-v5 archive
│   │   └── en/           # English versions
│   ├── decisions/        # ADRs
│   └── screenshots/      # README screenshots
├── reports/ exports/     # Generated artifacts (gitignored)
├── tests/                # Data quality & unit tests
└── scripts/              # One-off scripts (data gen / warehouse build / doc render)
```

Full design in [PRD v6 §4.3](docs/prd/PRD_v6.md#43-工程目录结构v6-新增一次定型).

---

## Milestone Status

For public positioning, this README only describes completed demo milestones and does not commit to future roadmap delivery.

- **v0.1.0 Data Foundation**: synthetic data, layered warehouse layout, data generation, and privacy boundary.
- **v0.2.0 Metric Asset Layer**: post-loan metric dictionary, metric lineage, and calculator registry.
- **v0.3.0 Anomaly Detection and Attribution**: anomaly detection and M1 D7 recovery attribution summary.
- **v0.4.0 Dashboard and Reports**: static dashboard and business report renderers.
- **v0.5.0 CLI Interaction MVP**: unified CLI entrypoint for summary, anomalies, drivers, outputs, dashboard, and reports.
- **v0.6.0 Model Lab Strategy Evaluation MVP**: offline strategy evaluation, ROI calculator, and model-lab CLI integration.

---

## Current Status

> Project is at **v0.6.0 Model Lab Strategy Evaluation MVP**. It is a local synthetic demo, not a production service.
>
> The current model target is **D7 any-payment response**, not cure-to-current, full recovery, DPD clearance, or production-ready collection outcome modeling.

---

## Quick Start

Run the local CLI against synthetic demo outputs only. The project contains no real customer data, is not production risk decisioning, and the current model target is **D7 any-payment response**, not cure-to-current, full recovery, or production collection outcome modeling.

```bash
python scripts/riskops_cli.py --help
python scripts/riskops_cli.py summary
python scripts/riskops_cli.py anomalies
python scripts/riskops_cli.py drivers
python scripts/riskops_cli.py outputs
python scripts/riskops_cli.py scenarios
python scripts/riskops_cli.py strategy-eval
python scripts/riskops_cli.py roi
python scripts/riskops_cli.py model-lab
python scripts/riskops_cli.py render-model-lab
python scripts/riskops_cli.py render-dashboard
python scripts/riskops_cli.py render-report
pytest
```

Common entry points:

- **--help**: list all currently supported demo CLI entry points.
- **summary**: project status, anomaly count, data boundary, and common commands.
- **anomalies**: high-priority anomaly list.
- **drivers**: top M1 D7 recovery drivers with interpretation boundaries.
- **outputs**: dashboard, report, and M3 output paths.
- **scenarios**: M6-A offline strategy scenarios.
- **strategy-eval**: M6-B offline strategy evaluation summary.
- **roi**: strategy scenario cost-benefit and ROI summary.
- **model-lab**: M6 strategy evaluation / ROI overview and demo boundary.
- **render-model-lab**: regenerate strategy evaluation and ROI outputs.
- **render-dashboard**: regenerate the local static dashboard.
- **render-report**: regenerate the Markdown / HTML business report.
- **pytest**: run the current test suite.

---

## Design Principles

1. **Business-first**: Lock metric definitions, attribution framework, and compliance rules **before** writing code.
2. **Data-grounded**: Every conclusion must be backed by data — no fabrication, no vague claims.
3. **Privacy graded**: P0-P4 five levels; P4 (raw PII) never enters warehouse application layer, reports, or LLM context.
4. **Human in the loop**: AI only generates suggestions and drafts; all outbound actions require human approval.
5. **Conclusion-first**: Reports lead with conclusions; exec version short, analyst version detailed.
6. **Single source of truth**: Metrics defined in YAML; docs only reference, never re-transcribe.
7. **Scope discipline**: Phase 1 = post-loan show-room only. New requirements must map to the scope matrix.

See [PRD v6 §9 Compliance & Privacy](docs/prd/PRD_v6.md#9-合规与隐私) and [§13 Decision Log](docs/prd/PRD_v6.md#13-决策日志adr).

---

## Contributing & Feedback

This is currently a **personal portfolio / learning project** — external code contributions are not accepted.

But the following channels are welcome:
- File [Issues](https://github.com/LeXiaoyao/riskops-copilot/issues) for business / technical suggestions
- Email the author at xiaoyao201207@gmail.com

---

## License

[MIT License](LICENSE) © 2026 LeXiaoyao

---

## Acknowledgements

This project draws on the author's years of front-line experience in consumer finance risk management and post-loan strategy. The documentation evolves from v1 (initial draft) to v6 (structured master), with the full archive in [docs/prd/history/](docs/prd/history/).
