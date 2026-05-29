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

## Current Demo Capabilities

The table below lists what the public demo actually ships today. Items beyond this scope (collection QA, script recommendation, TUI console, Feishu draft, PPT / Word report, etc.) are described in PRD v6 but are **planned, not delivered**.

| Module | Capabilities |
|---|---|
| **Data Foundation** | 18 months of synthetic post-loan data, 5-layer warehouse (DIM / ODS / DWD / DWS / ADS), primary-key relationships, P0–P4 privacy grading |
| **Metric Assets** | 26 post-loan metrics across result / process / compliance / ROI domains; `metadata/metric_dictionary.yaml` as single source of truth; calculator registry keyed by `metric_code` |
| **Anomaly Detection** | Rule-based detection over M1 D7 recovery, AI-call coverage, capacity pressure, discount usage, PTP fulfillment, and complaint risk |
| **Attribution** | Top-N driver decomposition for M1 D7 recovery decline across channel / region / customer segment / collection resource / process evidence |
| **Dashboard & Report** | Local static dashboard (`outputs/dashboard/dashboard.html`) and Markdown / HTML business report (`outputs/reports/m4_business_report.{md,html}`) |
| **Model Lab** | Offline strategy evaluation (5 scenarios), ROI calculator (demo cost assumptions), and a D7 any-payment response baseline with leakage-safe features and `score_date` guard |
| **State Recovery (M7-A)** | Feasibility / leakage guard only — diagnostic, **not** a production cure baseline |
| **Boundary Controls** | Synthetic data only, no real customer data, no collection automation, no SMS / voice / WhatsApp, no LLM decisioning, not production risk decisioning |

---

## Who This Demo Is Aimed At

| Role | Pain Point | What This Demo Shows |
|---|---|---|
| Risk strategy analyst | Slow attribution, scattered metric definitions | One CLI from metrics → anomalies → drivers → business report |
| Data / business analyst | Repetitive SQL & pivot work for post-loan KPIs | Local warehouse + metric registry + rendered reports |
| Post-loan manager | Hard to see the big picture of M1 D7 recovery | Static dashboard + structured anomaly / driver narrative |
| Hiring reviewer | Wants to see how the author thinks about a vertical domain | A coherent, end-to-end synthetic story with clear boundaries |

Roles around front-line collectors, compliance QA, and document copilots appear in PRD v6 but are **not in scope** for the current public demo.

---

## Documentation

| Document | Purpose |
|---|---|
| [README.md](README.md) | Chinese entry point (primary narrative) |
| [docs/architecture.md](docs/architecture.md) | High-level architecture and layer breakdown |
| [PRD v6](docs/prd/PRD_v6.md) | Internal master requirements (includes planned-but-not-delivered scope) |
| [PRD v6 English](docs/prd/en/PRD_v6.en.md) | English mirror of PRD v6 (partial) |
| [PRD History](docs/prd/history/) | v1–v5 archive — historical context only |
| [CHANGELOG](CHANGELOG.md) | Release log, M1–M9 milestones |

---

## Tech Stack (mapped to modules)

Only components that the current public demo actually uses. Items listed in PRD v6 §4.2 but not yet wired in (TUI / Textual, ECharts, openpyxl, python-pptx, python-docx, LLM orchestration) are out of scope here.

- **pandas / DuckDB / Parquet** — synthetic data generation, 5-layer warehouse, ADS wide tables.
- **PyYAML** — single source of truth under `metadata/` (tables, columns, metrics, privacy grading).
- **scikit-learn** — D7 any-payment baseline and leakage-safe feature pipeline in Model Lab.
- **Jinja2 + static HTML + Plotly** — dashboard and business report rendering.
- **CLI (`scripts/riskops_cli.py`)** — the only demo entry point; wires summary / anomalies / drivers / model-lab / render-* commands.
- **pytest** — data quality, cross-layer consistency, privacy boundary, and CLI regression checks.

---

## Project Structure

```
riskops-copilot/
├── riskops/              # Library code (data / metrics / engines / model lab)
├── scripts/              # CLI entry point + one-off generation / rendering scripts
├── synthetic_data/       # Synthetic data (DIM / ODS / DWD / DWS / ADS, 5 layers)
├── metadata/             # Single source of truth (tables / columns / metrics / lineage / privacy)
├── schemas/              # CREATE TABLE SQL
├── templates/            # Report templates (HTML / Markdown)
├── configs/              # Business configs (thresholds / attribution rules)
├── outputs/              # Rendered dashboard, reports, and model-lab artifacts
├── docs/
│   ├── prd/              # PRD v6 + en/ + history/ (v1–v5 archive)
│   ├── decisions/        # ADRs
│   ├── internal/         # Engineering notes (not public demo entry)
│   └── screenshots/      # README screenshots
├── tests/                # Data quality & regression tests
└── reports/ exports/     # Generated artifacts (gitignored)
```

Full design in [PRD v6 §4.3](docs/prd/PRD_v6.md#43-工程目录结构v6-新增一次定型). Note that the PRD reflects the full Phase 1 plan; the directory above reflects what the public demo currently ships.

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

> Project is a local synthetic demo, not a production service.
>
> The current trainable baseline target is **D7 any-payment response**, not cure-to-current, full recovery, DPD clearance, or production-ready collection outcome modeling.

**Current capabilities:**

- Synthetic RiskOps demo with a D7 any-payment ML baseline (M6 model lab).
- C-score availability guard: training enforces `score_date <= snapshot_date` to prevent future leakage.
- Leakage-safe feature engineering: only features observable as of the snapshot day.
- State recovery target feasibility guard (M7-A): diagnostic only, **not** a production cure model.

**Current boundary:**

- Synthetic demo only, no real customer data.
- Not production risk decisioning, no real collection action.
- Current trainable baseline target is **D7 any-payment response**.
- State recovery is a feasibility / leakage guard, not a complete cure baseline.

**Next technical focus:**

- Model card describing target, features, metrics, and boundaries of the baseline.
- Dashboard explainability entry points.
- State recovery data foundation improvements.
- Config-driven pipeline (move key parameters out of code).

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

## Project Entry Points

- **Architecture**: [docs/architecture.md](docs/architecture.md)
- **ML Lab**: D7 any-payment baseline + leakage guard + score_date guard + vintage robustness
- **State Recovery**: feasibility guard only, not a production cure model

---

## Preview / Screenshots

For screenshots and visual walkthrough, see [docs/screenshots/README.md](docs/screenshots/README.md) — it lists the recommended CLI summary, Model Lab, and Dashboard captures. The Mermaid diagram in `docs/architecture.md` renders natively on GitHub.

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
