# RiskOps Copilot

**A unified AI workbench for consumer finance risk operations: data analytics, metric attribution, risk modeling, and business reporting automation**

English | [简体中文](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/status-Phase%201%20Building-blue)](docs/prd/PRD_v6.md)
[![PRD](https://img.shields.io/badge/PRD-v6-green)](docs/prd/PRD_v6.md)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)

> **RiskOps Copilot** is a local-first AI analytics workbench that productizes the repetitive **analysis, attribution, reporting, QA, and script-writing** work across consumer finance risk operations — covering origination (pre-loan), in-life (mid-loan), collections (post-loan), compliance QA, and office document automation.
>
> Phase 1 focuses on a **post-loan show-room**: using synthetic data to tell a full story — M1 recovery rate drops → auto-attribute to customer mix, vendor performance, line capacity, process metrics, discount policy, and complaint-prone scripts → produce HTML weekly reports, PPT outlines, and collector script suggestions.

---

## Positioning

```
Synthetic Data → Data Foundation (DIM/ODS/DWD/DWS/ADS + privacy grading P0-P4)
              → Metric Assets (metric dictionary + lineage + version)
              → Engines (anomaly detection / attribution / visualization / report / QA / script)
              → AI Agent Orchestration (main agent + risk / collection / compliance / report experts)
              → Output Layer (TUI + HTML + Excel + PPT + Word + Feishu drafts)
```

**What it is NOT**: not a chatbot, not generic BI, not enterprise SaaS, no real production data, no real outbound call / SMS sending.

**What it IS**: a **vertical AI workbench demo** that tells a coherent business story, runs end-to-end, and produces screenshot-worthy artifacts for a portfolio. Also a personal knowledge asset for risk methodology.

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
| **Collection Copilot** | Text QA (11 dimensions + red-line scanning), compliant script recommendation, mock approval & sending with audit trail |
| **AI Agents** | Main orchestrator + 4 expert skill modules: risk analyst / collection strategy / compliance QA / report writer |

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
| Demo Script | 5-min live demo guide | M7 deliverable |
| Interview Pitch | Portfolio packaging | M7 deliverable |

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

## Roadmap

| Phase | Theme | Status |
|---|---|---|
| **Phase 1** | Post-loan show-room: M1 recovery attribution + Collection Copilot + Office automation | In progress |
| Phase 2 | Pre-loan + in-life risk copilot (application funnel, vintage, scorecard, limit management) | Planned |
| Phase 3 | Model & strategy closed loop (Champion/Challenger, Playbook) | Planned |
| Phase 4 | ASR & QA enhancement | Planned |
| Phase 5 | Office automation enhancement (Feishu API, knowledge base) | Planned |
| Phase 6 | Remote data sources & enterprise-ready foundation | Planned |

### Phase 1 Milestones

- **M0 Kickoff**: PRD v6 frozen, tech stack locked, scaffolding ← *current*
- **M1 Data Foundation**: synthetic data + 5-layer warehouse + metadata YAML
- **M2 Metric Assets**: metric dictionary v1.0 + calculation engine
- **M3 Core Engines**: anomaly detection + attribution + visualization
- **M4 Report & TUI**: 5-format reports + TUI main flow
- **M5 Collection Copilot**: QA + script + approval
- **M6 Agent Integration**: orchestrator + 4 experts
- **M7 Demo Packaging**: README + screenshots + demo video

See [PRD v6 §10 Phase 1 Delivery Plan](docs/prd/PRD_v6.md#10-第一期交付计划).

---

## Current Status

> Project is at **M0 Kickoff** stage: master PRD (v6), scaffolding, and repository initialized. **No runnable release yet.**
>
> Each milestone completion will publish a corresponding version (0.1.0 → 1.0.0).

---

## Quick Start

> Phase 1 code is not yet implemented. Below is the **target experience preview**, available after M4.

```bash
# Clone
git clone https://github.com/LeXiaoyao/riskops-copilot.git
cd riskops-copilot

# Install deps (after M0)
uv sync   # or poetry install

# Generate synthetic data (after M1)
python scripts/generate_synthetic_data.py --months 18 --scale medium

# Launch TUI (after M4)
riskops
```

Expected demo flow:

```
> /load synthetic_data/
> /dashboard postloan         # operations dashboard
> /anomaly M1_D7_recovery     # anomaly detection
> /explain M1_D7_recovery     # multi-dim attribution
> /vendor review              # vendor review
> /roi reduction_policy_A     # discount ROI
> /qc call_001.txt            # collection QA
> /script case_10086          # script recommendation
> /report weekly --format html,xlsx,ppt-outline
```

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
