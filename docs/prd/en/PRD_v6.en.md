# RiskOps Copilot — Product Requirements Document (PRD v6)

> This document is the master requirements specification for the RiskOps Copilot project. v6 reorganizes v5 with **structural restructuring + completeness reinforcement**, aiming for: anyone can grasp the skeleton in 5 minutes, drill into details in 30 minutes, and engineers can break it down into tasks directly.
>
> v5 had solid business depth but scattered sections, missing priorities, missing technical constraints, missing acceptance criteria. v6 locks down **all "things to do and requirements"** with one scope matrix + one milestone table + one decision log, as the non-drifting baseline going forward.
>
> **Current status**: skeleton complete + key new sections written + business-deep sections (data foundation / metric assets / engines) pending chapter-by-chapter migration from v5.
>
> **Note**: This is the English version. For the authoritative Chinese version, see [`../PRD_v6.md`](../PRD_v6.md). When the two versions diverge, **the Chinese version is the source of truth**.

---

## Document Changelog

| Version | Date | Major Changes | Author |
|---|---|---|---|
| v1 | before 2026-05-15 | Initial — post-loan show-room direction | - |
| v2 | before 2026-05-15 | Added Collection Copilot & compliance QA | - |
| v3 | before 2026-05-15 | Added office document automation | - |
| v4 | before 2026-05-15 | Expanded pre-loan & in-life modules blueprint | - |
| v5 | 2026-05-15 | Added warehouse layering, metric dictionary, long-window data, C-card modeling | - |
| **v6** | **2026-05-15** | **Structural restructure + scope matrix + tech stack + Agent spec + milestones + decision log** | - |

---

## Table of Contents

- [0. TL;DR](#0-tldr)
- [1. Product Vision & Value Proposition](#1-product-vision--value-proposition)
- [2. Scope & Boundaries](#2-scope--boundaries)
- [3. Target Users & Scenarios](#3-target-users--scenarios)
- [4. Overall Architecture](#4-overall-architecture)
- [5. Data Foundation Spec](#5-data-foundation-spec)
- [6. Metric Asset Spec](#6-metric-asset-spec)
- [7. Engine Capabilities](#7-engine-capabilities)
- [8. AI Agent Design](#8-ai-agent-design)
- [9. Compliance & Privacy](#9-compliance--privacy)
- [10. Phase 1 Delivery Plan](#10-phase-1-delivery-plan)
- [11. Roadmap](#11-roadmap)
- [12. Risk & Dependency Register](#12-risk--dependency-register)
- [13. Decision Log (ADR)](#13-decision-log-adr)
- [14. Appendix](#14-appendix)

---

## 0. TL;DR

### 0.1 One-Liner Positioning

**RiskOps Copilot is a local-first AI analytics workbench for consumer-finance risk operations**, with TUI as the control console and HTML/Excel/PPT/Word as output layers, productizing the repetitive analysis, attribution, reporting, QA, and script-writing work of risk strategists, post-loan managers, data/business analysts, front-line collectors, and compliance/QA staff.

### 0.2 Phase 1 Scope (One-Liner)

Use synthetic post-loan data to tell a coherent story: **M1 D7 recovery rate drops → auto-attribute to customer mix + East-China line capacity + vendor B connect rate + AI dialer coverage + discount usage + complaint-prone scripts → output HTML weekly report + PPT outline + collector script suggestions.**

### 0.3 End Goal (One-Liner)

Prove that this direction has **business value, product form, technical implementation path, visualization, AI differentiation, and complete strategic imagination from post-loan extension to pre-loan / in-life** — usable as a portfolio piece and a personal risk-methodology asset platform.

### 0.4 Core Logic Chain

```
Synthetic data → Data Foundation (DIM/ODS/DWD/DWS/ADS + privacy grading)
              → Metric Assets (metric dictionary + lineage + version)
              → Engines (anomaly / attribution / visualization / report / QA / script)
              → AI Agent Orchestration (main agent + expert skill modules)
              → Output (TUI + HTML + Excel + PPT + Word + Feishu drafts)
```

### 0.5 What It Is NOT (avoiding misunderstanding)

- Not a chatbot, not generic BI, not enterprise SaaS.
- No real financial data, no real outbound calls / SMS sending, does not replace collectors.
- No full permissioning / multi-tenancy / enterprise data masking / regulatory reporting.

---

## 1. Product Vision & Value Proposition

> Migrated from Chinese §1. See Chinese version for full text. Key conclusions:

### 1.1 Vision

Distill the risk-strategy knowledge scattered across Excel / PPT / SQL / Feishu docs / personal experience into a callable set of vertical AI skills, so that RiskOps teams (strategy / analyst / post-loan manager / collector / QA / PM) do less repetitive labor and more judgment.

### 1.2 Six Core Values

1. **Replace base analyst / BA work**: auto pull / pivot / chart / conclude.
2. **Boost post-loan strategy efficiency**: fast attribution on M1/M1+ recovery, PTP, complaints, ROI.
3. **Sharpen management insight**: ask in natural language "why did recovery drop?", "which vendor dragged us down?".
4. **Lift collector execution**: case summary + segmentation + script recommendation + compliance check + approval.
5. **Expand QA coverage**: red-line scanning + intensity scoring on recordings / text / templates.
6. **Accumulate strategy knowledge assets**: metric dictionary, report templates, diagnostic chains, strategy playbooks.

---

## 2. Scope & Boundaries

### 2.1 Three-Column Scope Matrix (most important v6 addition)

| Category | Phase 1 In-Scope (Must) | Phase 1 In-Scope (Should) | Phase 1 Out-of-Scope (Won't) | Parking Lot (Phase 2+) |
|---|---|---|---|---|
| **Data** | Synthetic post-loan data ≥18 months, 5-layer DIM/ODS/DWD/DWS/ADS, privacy grading | Customer/collector profile snapshots, post-loan tags | Real production data ingestion | MySQL/PostgreSQL remote connection, enterprise masking |
| **Metrics** | Post-loan result / process / compliance / ROI dictionary v1.0, YAML | Pre-loan / in-life metric placeholders (not computed) | Full model metrics (AUC/KS/PSI/Lift) | Full pre-loan / in-life metric computation |
| **Engines** | Anomaly detection (statistical rules), multi-dim attribution (contribution + waterfall), HTML reports, Excel/PPT/Word drafts | Complaint risk map, script radar chart | Complex ML anomaly detection, causal inference | Scorecard / XGBoost / SHAP model lab |
| **TUI** | Two-pane layout, core commands (load/dashboard/anomaly/explain/vendor/roi/qc/script/report) | Three-pane layout, NL query optimization | Multi-user / permissioning / session mgmt | Enterprise web dashboard |
| **Collection Copilot** | Text QA, compliance scan, script suggestion, mock approval + send + audit | Audio ASR transcription | Real SMS / outbound call sending | Feishu / WeCom approval flow integration |
| **Office Automation** | HTML/Markdown weekly, Excel attachment, PPT outline, Word draft, Feishu-friendly Markdown | Local Markdown knowledge base search | Real Feishu API write | Feishu bitable sync, meeting notes |
| **AI Agents** | Main agent + 5 skill modules (Risk/Collection/Compliance/Report/Model placeholder) | Context persistence, memory system | Complex multi-agent orchestration framework | Auto strategy Playbook accumulation |
| **Compliance** | P0–P4 privacy grading, collection red-line scan, mock approval audit | Complaint protection strategy | Real regulatory reporting | Automated regulatory reports |
| **Demo** | README + screenshot set + 5-min demo script | Demo video | Hosted SaaS demo | Enterprise trial plan |

> **Rule**: This table is the single source of truth for scope. Any new requirement must map back to this table; if it falls in Out-of-Scope or Parking Lot, it requires a recorded reason in §13 Decision Log.

### 2.2 What Phase 1 Does Not Do (Backstop)

- No real production data.
- No real outbound calls / batch SMS sending.
- No replacement of collector workforce.
- No full SaaS, multi-tenancy, enterprise approval flow, regulatory reporting.
- No model training (data foundation supports it, but Phase 1 ships no training commands).

### 2.3 Long-Term Positioning (not in Phase 1 but reserved in data foundation)

Covers five domains: pre-loan / in-life / post-loan / management / office automation. See §11 Roadmap.

---

## 3. Target Users & Scenarios

> Migrated and consolidated from Chinese §3 (R1–R9 roles, role-feature matrix, seven core demo scenarios S-A to S-G). See Chinese version for full table.

Quick reference:

- **R1** Risk Strategist · **R2** Data/BI Analyst · **R3** Post-Loan Manager · **R4** Collector / Supervisor · **R5** Compliance / QA · **R6** Product Manager · **R7** Operations Supervisor · **R8** Business Line / Regional Head · **R9** Strategy Head / Decision Maker

- **S-A** to **S-G**: Manager dashboard / Strategist analyzing recovery drop / Vendor review / Discount ROI / Collection QA / Script recommendation / Auto report generation.

---

## 4. Overall Architecture

### 4.1 System Layers

```
┌────────────────────────────────────────────────────────────┐
│  Output    TUI │ HTML │ Excel │ PPT │ Word │ Feishu         │
├────────────────────────────────────────────────────────────┤
│  Agent     Orchestrator + Risk/Collection/Compliance/Report │
├────────────────────────────────────────────────────────────┤
│  Engines   Anomaly │ Attribution │ Viz │ Report │ QA │ Script│
├────────────────────────────────────────────────────────────┤
│  Metrics   Metric dict (YAML) + Calculator + Lineage         │
├────────────────────────────────────────────────────────────┤
│  Data      DIM / ODS / DWD / DWS / ADS (DuckDB / Parquet)    │
├────────────────────────────────────────────────────────────┤
│  Base      Synthetic data gen │ Privacy grading │ DQ rules   │
└────────────────────────────────────────────────────────────┘
```

### 4.2 Tech Stack Decisions (v6 lock-in)

| Layer | Choice | Rationale | Alternative |
|---|---|---|---|
| Language | Python 3.11+ | Complete data/AI ecosystem, local-deploy friendly | - |
| Package mgr | uv or poetry | Modern Python dep mgmt | pip + requirements.txt |
| Data foundation | DuckDB | Single-machine columnar analytics, zero-ops | SQLite (fallback) |
| Data format | Parquet (storage) + CSV (human-readable) | Parquet for compression/speed; CSV for demo | - |
| Data gen | numpy + pandas + Faker | Standard | - |
| TUI | Textual (Rich family) | Modern TUI, reactive layout | prompt_toolkit |
| Visualization | Plotly (HTML) + ECharts (alt) | Plotly single-file HTML, interactive, screenshot-ready | matplotlib (rejected: ugly) |
| Report engine | Jinja2 + Plotly + WeasyPrint (PDF alt) | Templated HTML, extensible to PDF | - |
| Excel | openpyxl | Standard | xlsxwriter |
| PPT | python-pptx | Standard | - |
| Word | python-docx | Standard | - |
| LLM | Claude (Anthropic API) primary | Long context + stable tool use | OpenAI (fallback) |
| ASR (Phase 2) | TBD | Deferred to Phase 4 | Whisper (local) |
| Config | YAML | Human-readable, versionable | - |
| Testing | pytest | Standard | - |

### 4.3 Engineering Directory Structure (v6 — locked once)

See Chinese version §4.3 for the full tree (riskops/ + synthetic_data/ + metadata/ + schemas/ + templates/ + configs/ + docs/ + tests/ + scripts/).

### 4.4 TUI vs Visualization

Inherits Chinese §2.4: **the terminal gives orders, the web and documents present results.**

---

## 5. Data Foundation Spec

> Skeleton only. See Chinese version §5 for full text. Pending migration of v5 §8.1 + §15 + §15A + §22 contents.

Layers: DIM (10 tables) → ODS (14 tables) → DWD (5 tables) → DWS (5 + 3 profile/tag tables) → ADS (6 tables).

Privacy grading P0–P4: P4 raw PII never enters DWD/DWS/ADS, reports, or LLM context.

Core PK relationships: `customer_id (1:N) loan_id (1:N) plan_id (1:N) repay_id`; `customer_id (1:N) case_id (1:N) action_id / note_id / decision_id`; `case_id (M:N) loan_id` via `dim_case_loan_mapping`.

Synthetic data: ≥18 months, scale `small`/`medium`/`large`, last-30-day anomaly injections, strict no-label-leakage.

**Authoritative source**: `metadata/tables.yaml` + `metadata/columns.yaml` (M1 deliverable). The Markdown only references, never re-transcribes.

---

## 6. Metric Asset Spec

> Skeleton only. See Chinese version §6 for full text. Pending migration of v5 §8.2 + §15B contents.

**Authoritative source**: `metadata/metric_dictionary.yaml` (M2 deliverable). Each metric has: `metric_code`, `metric_name_cn`, `business_domain`, `numerator`, `denominator`, `formula`, `grain`, `source_tables`, `filter_condition`, `owner`, `refresh_frequency`, `version`, `change_log`.

Phase 1 priority: Post-loan result (8 P0) + process (7 P0 + 3 P1) + compliance (3 P0 + 2 P1) + discount ROI (2 P0 + 1 P1). Pre-loan / in-life / model metrics are placeholders (Phase 2+).

---

## 7. Engine Capabilities

> Skeleton only. See Chinese version §7 for full text.

Six engines, each with unified template (Goal / Input / Output / Algorithm / Acceptance):

1. **Anomaly Detection** — statistical rules (z-score, sequential drops, process-vs-result divergence). Acceptance: detect all 7 injected anomalies in demo data.
2. **Attribution** — group comparison + contribution ranking + structural decomposition + Top-N drill-down. Acceptance: M1 D7 drop attribution produces analyst-grade conclusion text.
3. **Visualization** — 10 charts × 2 themes (`dark_dashboard` + `consulting_report`). Plotly + Jinja2.
4. **Reporting** — 11-section standard structure, conclusion-first principle, 5 formats (HTML/MD/Excel/PPT/Word).
5. **Collection QA** — Phase 1: text only (11 dimensions + red-line detection). Phase 2+: audio ASR.
6. **Script Recommendation** — gen → compliance scan → frequency check → human approval → mock send → audit log.

---

## 8. AI Agent Design

> **Completely new in v6**. v5's §12 only listed 5 agent names; this section adds orchestration, prompts, context protocol, cost estimates.

### 8.1 Roles & Responsibilities

| Agent | Responsibility | Phase 1 | Tool Calls |
|---|---|---|---|
| **Orchestrator** | Parse user commands, route to experts, integrate results, maintain conversation context | Required | Calls other agents + engine APIs |
| Risk Analyst | Metric analysis, anomaly identification, multi-dim attribution, risk conclusion | Required | Anomaly engine, attribution engine, SQL |
| Collection Strategy | Assignment / outreach / discount / vendor strategy suggestions | Required | Metric queries, comparative analysis |
| Compliance QA | Script compliance, recording QA, red-line scanning | Required | QA engine, rule library |
| Report Writer | Weekly / PPT / Word / Feishu drafts | Required | Report engine, templates |
| Model Lab | Model training / evaluation / explanation | Phase 2+ placeholder | scikit-learn / lightgbm |

### 8.2 Orchestration Approach

Phase 1 uses **single main agent + skill modules** pattern rather than multi-agent parallelism:
- Orchestrator is the sole external interface.
- Expert agents are effectively "skills" with dedicated prompts + tool sets, called synchronously by the orchestrator.
- No complex multi-agent framework (LangGraph / CrewAI), keeping implementation and debugging simple.

Phase 2+ may consider: async parallelism, message bus, long-term memory.

### 8.3 Context Protocol

| Context Layer | Content | Persistence |
|---|---|---|
| Project-level | Current project, data sources, metric dictionary, generated reports list | `~/.riskops/project.yaml` on disk |
| Session-level | Conversation history, current metric/case/vendor in focus | In-memory + dump on exit |
| Call-level | Per-tool-call I/O | Logs only |

### 8.4 Prompt Template Spec

Each expert agent must have:
- `system_prompt.txt`: role definition + business boundary + output format
- `examples/`: 3–5 few-shot examples
- `tools.yaml`: callable tools list + signatures

Prompt principles (inheriting Chinese §13.1–13.3):
- **Risk analysis**: data-grounded, no fabrication, conclusion-first, six analytical angles, executable suggestions.
- **Collection**: no threats / abuse / impersonation of law enforcement / inducement of new borrowing / third-party harassment / over-frequency / forbidden-hour contact; all sending requires human approval.
- **Reporting**: short for exec, detailed for analyst, one conclusion per PPT page, dictionary discipline for Excel, collaborative format for Feishu.

### 8.5 LLM Choice / Cost / Safety

| Dimension | Choice | Note |
|---|---|---|
| Primary LLM | Claude (Anthropic API) | Long context + stable tool use |
| Fallback | OpenAI GPT-4 | Switchable via config |
| Local fallback | Qwen / Llama (Ollama) | Phase 2+ evaluation |
| Per-task budget | < $0.50 | Demo-friendly |
| Context restriction | Never send P3/P4 fields | Orchestrator-enforced |
| LLM failure fallback | Degrade to templated output | Required |

### 8.6 Acceptance

- Orchestrator correctly parses all §14.1 commands and routes.
- Each expert agent produces output conforming to its prompt principles on demo data.
- Full demo cost estimable and < $5.

---

## 9. Compliance & Privacy

> See Chinese §9. Key rules:

- Phase 1 default uses synthetic data.
- P3/P4 fields never enter DWD/DWS/ADS, reports, or LLM context.
- AI only generates suggestions and drafts; key actions (sending, disposition, legal, credit) require human confirmation.
- Collection red lines (from v5 §14.3) codified in `configs/compliance_rules.yaml`: threats / abuse / impersonation / inducement of new borrowing / third-party harassment / privacy exposure / over-frequency / forbidden hours.
- Audit trail: every script generation, approval, mock send is logged (who / when / case / content / approval / result).

---

## 10. Phase 1 Delivery Plan

> Completely new in v6. Upgrades v5 §16.1's "feature list" into an executable milestones + acceptance plan.

### 10.1 Milestones

| Milestone | Time Window | Deliverable | Exit Criteria |
|---|---|---|---|
| **M0 Kickoff** | Week 1 | PRD v6 frozen, tech stack locked, scaffolding | This doc v6 review passes |
| **M1 Data Foundation** | Week 2-4 | Synthetic data generator, 5-layer warehouse SQL, metadata YAML, DQ tests | `python scripts/generate_synthetic_data.py --months 18 --scale medium` runs; `pytest tests/test_data_quality.py` all green |
| **M2 Metric Assets** | Week 4-5 | Metric dictionary YAML v1.0, calculation engine, ADS tables populated | 20+ post-loan core metrics queryable; owner / lineage / version complete |
| **M3 Core Engines** | Week 5-7 | Anomaly + attribution + visualization | Detects 7 injected anomalies and attributes them |
| **M4 Report & TUI** | Week 7-9 | HTML/Excel/PPT/Word reports, TUI commands, dashboard | `/report weekly` outputs 5 formats; TUI runs all §14.1 P0 commands |
| **M5 Collection Copilot** | Week 9-10 | Text QA, script recommendation, mock approval | S-E / S-F scenarios run end-to-end |
| **M6 Agent Integration** | Week 10-11 | Orchestrator + 4 expert agents | All 7 demo scenarios run |
| **M7 Demo Packaging** | Week 11-12 | README, screenshots, demo video script, interview pitch | 5-min full demo flow |

### 10.2 Acceptance Checklist

See Chinese §10.2 for the complete checklist organized by module (Data / Metrics / Engines / Collection Copilot / Agents / Demo).

### 10.3 Demo Assets

See Chinese §10.3 (README, demo script, interview pitch, screenshots, demo video, data dictionary, metric dictionary).

---

## 11. Roadmap

| Phase | Theme | Migration Source |
|---|---|---|
| Phase 1 | Post-loan show-room (current) | §10 |
| Phase 2 | Pre-loan + in-life risk operations copilot | v5 §16.2 |
| Phase 3 | Model & strategy closed loop | v5 §16.3 |
| Phase 4 | ASR & QA enhancement | v5 §16.4 |
| Phase 5 | Office automation enhancement | v5 §16.5 |
| Phase 6 | Remote data sources & enterprise foundation | v5 §16.6 |

---

## 12. Risk & Dependency Register

> Completely new in v6. See Chinese §12 for the full 10-row table (R-01 LLM cost / R-02 synthetic data realism / R-03 chart aesthetics / R-04 Textual learning curve / R-05 metric inconsistency / R-06 P4 leakage / R-07 demo story / R-08 scope creep / R-09 DuckDB perf / R-10 ASR deferral).

---

## 13. Decision Log (ADR)

> Completely new in v6. Each ADR has a one-line summary; details in `docs/decisions/`.

| ADR | Decision | Date | Status |
|---|---|---|---|
| ADR-001 | Phase 1 uses DuckDB rather than SQLite/MySQL | 2026-05-15 | Accepted |
| ADR-002 | TUI uses Textual rather than prompt_toolkit | 2026-05-15 | Accepted |
| ADR-003 | Visualization uses Plotly rather than matplotlib | 2026-05-15 | Accepted |
| ADR-004 | LLM primary = Claude API | 2026-05-15 | Accepted |
| ADR-005 | Phase 1 single main agent + skills, no multi-agent framework | 2026-05-15 | Accepted |
| ADR-006 | Metric dictionary YAML as single source of truth | 2026-05-15 | Accepted |
| ADR-007 | Phase 1 does not integrate real SMS / outbound SDK | 2026-05-15 | Accepted |
| ADR-008 | Phase 1 does not train ML models, data foundation reserved | 2026-05-15 | Accepted |
| ADR-009 | ASR selection deferred to Phase 4 | 2026-05-15 | Deferred |
| ADR-010 | Feishu API write deferred to Phase 5; Phase 1 only emits Feishu-friendly Markdown | 2026-05-15 | Accepted |

---

## 14. Appendix

### 14.1 Command List

See Chinese §14.1 (`/load`, `/dashboard`, `/anomaly`, `/explain`, `/vendor`, `/roi`, `/qc`, `/script`, `/report`, etc., with P0–P3 priorities).

### 14.2 Glossary

| Term | Meaning |
|---|---|
| DPD | Days Past Due |
| MOB | Months on Book |
| PTP | Promise to Pay |
| Vintage | Asset performance curve by disbursement month |
| Roll Rate | Migration rate between DPD buckets |
| AUC/KS/PSI/Lift | Model evaluation metrics |
| OOT | Out-of-Time validation |
| FPD | First Payment Default |

### 14.3 v5 ↔ v6 Migration Map

See Chinese §14.3.

### 14.4 Backlog (post-v6 reinforcement tasks)

- T-01: Migrate all v5 §22 table fields into `metadata/tables.yaml` + `metadata/columns.yaml`
- T-02: Migrate all v5 §15B metrics into `metadata/metric_dictionary.yaml`
- T-03: Write detailed ADR-001 to ADR-010 in `docs/decisions/`
- T-04: Write `docs/demo_script_v0.md` (reverse-driving M1-M7 design)
- T-05: Add per-layer table-field summaries in §5.4 (brief in MD, detail in YAML)
- T-06: Add engine algorithm details in §7 (pseudocode or formulas)
- T-07: Add expert-agent `system_prompt` drafts in §8
- T-08: Integrate v5 §17 (portfolio packaging) into §10.3 or `docs/interview_pitch.md`
- T-09: Add dependency graph for §10.1 milestones
- T-10: Complete §11 Phase 2-6 roadmap (currently only points to v5)
