# RiskOps Copilot — Product Requirements Document (PRD v6)

> This document is the master requirements specification for the RiskOps Copilot project. v6 reorganizes v5 with **structural restructuring + completeness reinforcement**, aiming for: anyone can grasp the skeleton in 5 minutes, drill into details in 30 minutes, and engineers can break it down into tasks directly.
>
> v5 had solid business depth but scattered sections, missing priorities, missing technical constraints, missing acceptance criteria. v6 locks down **all "things to do and requirements"** with one scope matrix + one milestone table + one decision log, as the non-drifting baseline going forward.
>
> **Current status**: **all chapters complete** — §5 Data Foundation (5-layer table inventory + privacy details + PK ER + synthetic data spec + DQ rules), §6 Metric Assets (26 post-loan metrics with formulas), §7 Engines (6 engines with algorithm / acceptance / examples), §11 Roadmap (Phases 1–6 fully expanded). Next work shifts to metadata YAML-ization and code implementation (see §14.4).
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

This chapter defines Phase 1 data foundation: **layering rules, privacy boundaries, primary-key relationships, table inventory, synthetic data requirements, data-quality rules**. All engines, metrics, and agents are built on top of this chapter.

> **Authoritative source**: `metadata/tables.yaml` + `metadata/columns.yaml` (M1 deliverable). This chapter keeps only **purpose / grain / PK / key-field summary**. For full content with examples, see the Chinese version §5.

### 5.1 Data Layering

| Layer | Purpose | Privacy | Production Rule |
|---|---|---|---|
| **DIM** | Master dimensions (customer / loan / case / product / channel / vendor / line / collector / strategy) | P1-P4 coexist, **P4 only in raw_secure** | Slowly-changing, daily/weekly refresh |
| **ODS** | Simulated production-system raw streams (repayment / collection actions / notes / recordings / complaints / discounts / assignment decisions) | P4 simulatable but only in raw_secure | Mimics production, granular |
| **DWD** | Cleansed deduplicated fact tables | **No P4** | Cleansed from ODS, unified semantics |
| **DWS** | Wide topic tables (loan/case/customer snapshots, process wide, vendor-line capacity, profiles, tags) | No P4 | Aggregated by theme, analysis-ready |
| **ADS** | Application metric tables (dashboards, attribution, vendor / collector performance, discount ROI, compliance QA) | **No P4, no row-level by default** | Direct serving for dashboards & agents |

### 5.2 Privacy Grading (P0–P4)

| Level | Meaning | Typical Fields | DWD/DWS/ADS | Reports | LLM Context |
|---|---|---|---|---|---|
| **P0** | Non-sensitive public | product_code, province, city, dpd_bucket | ✓ | ✓ | ✓ |
| **P1** | Internal business keys | customer_id, loan_id, case_id, vendor_id | ✓ | ✓ | ✓ |
| **P2** | Masked personal | mobile_masked (e.g. 138****1234), customer_id_hash | ✓ | ✓ | ✓ |
| **P3** | Hash / ciphertext | id_no_hash, mobile_hash, bank_card_hash | ✓ | Not shown | **Not sent directly** |
| **P4** | Raw PII | id_no, mobile_no, customer_name, address | **✗** | **✗** | **✗** |

LLM context admission (**hard rule**): Orchestrator must scan field metadata before sending; P3 hashed only with masking note; **P4 never sent**.

### 5.3 Core Primary-Key Relationships

```
customer_id ──┬─── 1:N ─── loan_id ─── 1:N ─── plan_id ─── 1:N ─── repay_id
              │
              └─── 1:N ─── case_id ──┬── 1:N ─── action_id
                                     ├── 1:N ─── note_id
                                     ├── 1:N ─── decision_id
                                     └── M:N ─── loan_id (via dim_case_loan_mapping)

vendor_id ─── 1:N ─── line_id ─── 1:N ─── collector_id
```

### 5.4 Table Inventory

**DIM Layer (10 tables)**: `dim_customer`, `dim_loan`, `dim_case`, `dim_case_loan_mapping`, `dim_product`, `dim_channel`, `dim_vendor`, `dim_collection_line`, `dim_collector`, `dim_strategy`.

**ODS Layer (14 tables)**: `ods_repayment_plan` (period repayment plans), `ods_repayment_detail` (actual repayment stream), `ods_loan_daily_snapshot`, `ods_case_daily_snapshot`, `ods_customer_daily_snapshot`, `ods_case_flow`, `ods_assignment_decision_log`, `ods_postloan_c_score`, `ods_collection_note`, `ods_collection_action`, `ods_call_record`, `ods_sms_send_log`, `ods_reduction_application`, `ods_complaint`.

**DWD Layer (5 tables)**: `dwd_due_plan_detail_di`, `dwd_repayment_detail_di`, `dwd_collection_action_detail_di`, `dwd_case_flow_detail_di`, `dwd_complaint_detail_di`.

**DWS Layer (5 wide + 3 profile/tag tables)**:
- Wide: `dws_loan_status_snapshot_di`, `dws_case_status_snapshot_di`, `dws_customer_status_snapshot_di`, `dws_collection_process_wide_di`, `dws_vendor_line_capacity_di`.
- Profile/Tag: `dws_customer_profile_di`, `dws_collector_profile_di`, `dws_customer_postloan_tag_di`.

**ADS Layer (6 tables)**: `ads_postloan_dashboard_di`, `ads_recovery_attribution_di`, `ads_vendor_performance_di`, `ads_collector_performance_di`, `ads_reduction_roi_di`, `ads_compliance_qc_di`.

> Field-level details: see Chinese §5.4 and (when ready) `metadata/tables.yaml`.

### 5.5 Synthetic Data Spec

**Timeline**:

| Range | Use | Notes |
|---|---|---|
| T-18M to T-12M | Historical baseline | Long-window customer behavior, vintage |
| T-12M to T-6M | Model training window (Phase 2+) | Sufficient sample |
| T-6M to T-3M | Validation window | Strategy stability |
| T-3M to T-1M | OOT testing | PSI, cross-period stability |
| Last 90 days | Business analysis window | Dashboards, operations |
| **Last 30 days** | **Demo anomaly window** | **7 injected storyline anomalies** |

**Scale tiers**:

| Tier | Customers | Loans | Cases | Actions | Use |
|---|---:|---:|---:|---:|---|
| `small` | 20K | ~30K | ~10K | ~200K | Local fast-iteration |
| `medium` | 80K | ~150K | ~50K | ~1.5M | Demo & analysis (**default**) |
| `large` | 150K+ | ~300K | ~100K | ~5M | Modeling & stress test |

**Seven injected anomalies (last 30 days)**:
1. M1 D7 recovery rate drops from 18.6% to 15.2% (core story)
2. East-China line per-collector caseload up 25% (capacity)
3. Vendor B connect rate down 6pct (execution)
4. High-balance customer share up 8pct (structure)
5. AI dialer coverage down 12pct (resource)
6. Discount usage down 4pct + PTP keep rate down 5pct (strategy)
7. One SMS template's complaint rate 2× the mean (compliance)

**No label leakage**: features only from before observation date; labels only from after; train / valid / OOT windows non-overlapping. CI-enforced.

### 5.6 Data Quality Rules

**Hard rules (CI must pass)**:

| ID | Rule |
|---|---|
| DQ-001 | DIM primary keys unique |
| DQ-002 | Foreign keys resolvable (e.g. `ods_repayment_detail.plan_id` → `ods_repayment_plan.plan_id`) |
| DQ-003 | Amounts non-negative (due / repaid / outstanding / reduction) |
| DQ-004 | No date leakage (`repay_time >= disburse_time`; label_date > feature_date) |
| DQ-005 | P4 isolation (no P4 fields in DWD/DWS/ADS, by name scan) |
| DQ-006 | Ratio range [0, 1] for rate metrics |
| DQ-007 | Case-loan mapping completeness (every case_id maps ≥ 1 loan_id) |
| DQ-008 | Time-series completeness (daily snapshot row count not dropping to zero) |

**Soft rules (warning, non-blocking)**: DQ-101 day-over-day metric volatility, DQ-102 imbalanced sample ratio, DQ-103 null-rate spike.

Implementation: `tests/test_data_quality.py` + `riskops/data/quality/`.

### 5.7 Data Asset Deliverables

- **Authoritative YAML**: `metadata/tables.yaml`, `metadata/columns.yaml`, `metadata/key_relationships.yaml`, `metadata/privacy_policy.yaml`, `metadata/metric_lineage.yaml`.
- **Human-readable docs** (rendered from YAML): `docs/data_dictionary.md`, `docs/key_relationships.md`, `docs/privacy_policy.md`, `docs/data_lineage.md`.
- **SQL & scripts**: `schemas/{dim,ods,dwd,dws,ads}.sql`, `scripts/generate_synthetic_data.py`, `scripts/build_warehouse.py`, `scripts/render_docs.py`, `tests/test_data_quality.py`.

---

## 6. Metric Asset Spec

The metric dictionary is **the language system of RiskOps Copilot** — all engines and agents call by `metric_code`, never re-implement.

> **Authoritative source**: `metadata/metric_dictionary.yaml` (M2 deliverable). This chapter lists codes + formulas; full YAML fields (owner / change_log / grain / source_tables) live in the file.

### 6.1 Dictionary Schema

Each metric must include: `metric_code`, `metric_name_cn`, `business_domain`, `metric_type`, `numerator`, `denominator`, `formula`, `grain`, `source_tables`, `filter_condition`, `owner`, `refresh_frequency`, `version`, `priority`, `notes`, `change_log`. See Chinese §6.1 for full YAML example.

### 6.2 Phase 1 Metric Overview

| Domain | Count | P0 | P1 | Phase 1 |
|---|---:|---:|---:|---|
| Pre-loan | 5 | 0 | 0 | Placeholder (Phase 2) |
| In-life | 4 | 0 | 0 | Placeholder (Phase 2) |
| **Post-loan result** | **8** | **8** | **0** | **All implemented** |
| **Collection process** | **10** | **7** | **3** | **All implemented** |
| **Compliance QA** | **5** | **3** | **2** | **All implemented** |
| **Discount ROI** | **3** | **2** | **1** | **All implemented** |
| Model | 4 | 0 | 0 | Placeholder (Phase 2) |
| **Total (Phase 1)** | **26** | **20** | **6** | — |

### 6.3 Post-Loan Result Metrics (8, all P0)

| metric_code | English | Formula |
|---|---|---|
| `due_account_count` | Due account count | `count(distinct customer_id where due_date in window)` |
| `due_loan_count` | Due loan count | `count(distinct loan_id where due_date in window)` |
| `due_total_amount` | Total due amount | `sum(due_total_amount)` |
| `collection_entry_rate` | Collection entry rate | `collection_entry_count / due_account_count` |
| `recovery_rate_d7` | D7 recovery rate | `repay_amount_within_7d / initial_outstanding_amount` |
| `recovery_rate_d15` | D15 recovery rate | `repay_amount_within_15d / initial_outstanding_amount` |
| `recovery_rate_d30` | D30 recovery rate | `repay_amount_within_30d / initial_outstanding_amount` |
| `m1_recovery_rate` | M1 recovery rate | `m1_repay_amount / m1_initial_outstanding_amount` |

Convention: amount-based by default (no discount); count-based version named `recovery_case_rate_*`. Roll rate / vintage bad rate deferred to Phase 2.

### 6.4 Collection Process Metrics (10: 7 P0 + 3 P1)

| metric_code | English | Formula | Priority |
|---|---|---|---|
| `call_coverage_rate` | Call coverage rate | `called_case_count / assigned_case_count` | P0 |
| `valid_coverage_rate` | Valid coverage rate | `valid_contact_case_count / assigned_case_count` | P0 |
| `connect_rate` | Connect rate | `connect_count / call_count` | P0 |
| `valid_contact_rate` | Valid contact rate | `valid_contact_count / connect_count` | P0 |
| `first_contact_hours` | First contact latency | `avg(first_contact_time - assign_time)` hours | P0 |
| `ptp_rate` | PTP rate | `ptp_count / valid_contact_count` | P0 |
| `ptp_keep_rate` | PTP keep rate | `kept_ptp_count / matured_ptp_count` | P0 |
| `avg_call_duration_per_call` | Avg call duration | `sum(duration_sec where connect=1) / connect_count` | P1 |
| `avg_call_duration_per_collector` | Daily duration per collector | `sum(duration_sec) / active_collector_count / work_days` | P1 |
| `collector_productivity` | Collector productivity | `repay_amount / active_collector_count` | P1 |

### 6.5 Compliance & Complaint Metrics (5: 3 P0 + 2 P1)

| metric_code | English | Formula | Priority |
|---|---|---|---|
| `complaint_rate` | Complaint rate | `complaint_case_count / active_case_count` | P0 |
| `complaint_per_10k_cases` | Complaint per 10k cases | `complaint_count / active_case_count * 10000` | P0 |
| `risk_phrase_hit_rate` | Risk phrase hit rate | `risk_phrase_hit_count / qa_checked_count` | P0 |
| `qa_fail_rate` | QA fail rate | `qa_fail_call_count / qa_checked_call_count` | P1 |
| `over_frequency_contact_rate` | Over-frequency rate | `over_frequency_case_count / contacted_case_count` | P1 |

### 6.6 Discount ROI Metrics (3: 2 P0 + 1 P1)

| metric_code | English | Formula | Priority |
|---|---|---|---|
| `reduction_usage_rate` | Discount usage rate | `reduction_case_count / eligible_case_count` | P0 |
| `reduction_recovery_rate` | Recovery rate after discount | `repay_amount_after_reduction / reduction_case_outstanding_amount` | P0 |
| `reduction_roi` | Discount ROI | `(actual_repay - expected_without_reduction) / approved_reduction_amount` | P1 |

`reduction_roi` uses historical-cohort means as counterfactual baseline in Phase 1; causal-inference / control-group method deferred to Phase 3.

### 6.7 Placeholders (Phase 2+)

- **Pre-loan**: `approval_rate`, `disbursement_conversion_rate`, `fpd_rate`, `bad_rate`, `vintage_bad_rate`
- **In-life**: `credit_utilization_rate`, `post_limit_increase_overdue_rate`, `transaction_reject_rate`, `risk_migration_rate`
- **Model**: `auc`, `ks`, `psi`, `lift`

### 6.8 Single-Source-of-Truth Principle

- Definitions only in YAML; this chapter is a reading aid.
- One file per metric in `riskops/metrics/calculators/<metric_code>.py`; function name = `metric_code`.
- Changes: edit YAML first (with change_log entry), CI validates, md auto-renders via `scripts/render_docs.py metrics`.

### 6.9 Maintenance (CI Validation)

- `metric_code` globally unique (snake_case)
- Required fields: `metric_code`, `metric_name_cn`, `business_domain`, `formula`, `grain`, `source_tables`, `owner`, `version`, `priority`
- `change_log` mandatory per change
- Enum: `business_domain` ∈ {preloan, midloan, postloan, collection, compliance, roi, model}; `priority` ∈ {P0, P1, P2, P3}

Lineage in `metadata/metric_lineage.yaml`: `metric_code → ADS → DWS → DWD → ODS`.

---

## 7. Engine Capabilities

Six core engines for Phase 1. Each engine follows the unified template: **Goal / Input / Output / Algorithm / Config / Acceptance / Example**. For full pseudocode and worked examples, see Chinese version §7.

Engine relationships: Anomaly Detection → Attribution → Reporting / Visualization. Collection QA + Script Recommendation form an independent sub-chain serving the Collection Copilot.

### 7.1 Anomaly Detection

**Goal**: detect trend / sudden-change / structural / process anomalies on result and process metrics.

**Algorithm (Phase 1, statistical rules — no ML)**:

| Type | Rule | Default |
|---|---|---|
| Day-over-day | `abs(today - yesterday) / yesterday > threshold` | ±15% |
| Week-over-week | `abs(today - 7d_ago) / 7d_ago > threshold` | ±20% |
| Mean deviation | Off by N standard deviations from 28-day mean | 2σ |
| Sequential | N consecutive days of unidirectional movement | 5 days |
| Process-result divergence | Process metric deteriorates while result hasn't reflected yet | ≥ 3 days |
| Structural | A dimension's share changes beyond threshold | ±5pct |

**Severity**: `critical` (≥3σ or 7-day decline) / `high` (≥2σ or 25% MoM) / `medium` (≥1.5σ or 15%) / `low` (≥1σ).

**Acceptance**: recall 100% on the 7 injected anomalies, ≤ 3 false positives.

### 7.2 Attribution

**Goal**: decompose metric movement across the **six-layer framework**:

1. **Asset structure** — balance segment / DPD / risk level / channel / product mix changes
2. **Customer mix** — high-risk share, lost-contact share, willingness changes
3. **Strategy actions** — assignment / discount / AI dialer / SMS / protection policy changes
4. **Resource allocation** — vendor / line / collector capacity, per-collector caseload
5. **Process execution** — call coverage, connect rate, PTP, keep rate, first-contact latency
6. **Compliance constraints** — complaint guardrails, sensitive-customer protection, no-call rules

**Output**: Top-N contributors (default N=5), waterfall data (baseline → contributors → current), analyst-style conclusion text.

**Algorithm**: group-by comparison + contribution decomposition + structural-vs-within-group split + process-result correlation + Top-N recursive drill-down (depth ≤ 2).

**Acceptance**: for the M1 D7 drop, conclusion must include ≥ 4 layers and identify a primary cause (contribution > 30%).

### 7.3 Visualization

**Goal**: produce consulting-grade charts.

**Phase 1 must-do 10 charts**: operations overview cards, M1 recovery trend, collection process funnel, attribution waterfall, vendor performance matrix, line capacity heatmap, DPD/balance-segment structure, discount ROI, complaint risk map, script QA radar.

**Dual themes**: `dark_dashboard` (TUI/dashboard) + `consulting_report` (PDF/PPT/résumé).

**Tech**: Plotly (HTML/SVG/PNG) + Jinja2 templates per chart at `templates/html/charts/<chart>.json.j2`.

**Acceptance**: 10 charts × 2 themes all generate; 1920×1080 screenshots fit for README and résumé; ≥ 2 of 3 reviewers rate as "consulting-grade."

### 7.4 Reporting

**Goal**: assemble metrics + anomalies + attribution + visuals into multi-format reports.

**Report types**: daily / weekly / attribution / vendor review / discount ROI / collection QA / Feishu draft.

**11-section standard structure**: Conclusions → Metrics overview → Anomaly detection → Multi-dim attribution → Process metrics → Vendor / line → ROI → Compliance & complaints → Recommendations → Follow-ups → Appendix.

**Principles**: conclusion-first; data-grounded (traceable to table + filter); explicit about missing data; never fabricate; `--audience exec|analyst` switch for length.

**Acceptance**: `/report weekly` outputs 5 formats; HTML renders cleanly; PPT outline ≥ 9 pages each with title + conclusion + chart suggestion + speaker notes; Excel has detail + pivot.

### 7.5 Collection QA

**Goal**: score text (Phase 1) / audio (Phase 2+) for compliance, intensity, complaint risk; locate high-risk phrases.

**11 QA dimensions**: identity disclosure / fact statement / amount-date statement / objection handling / solution guidance / emotion control / collection intensity / red-line compliance / complaint risk / PTP confirmation / closing protocol.

**Red-line clauses (any hit → critical)**: threats / abuse / insinuation of illegal consequences / impersonating law enforcement / inducing new borrowing / privacy exposure to third parties / harassment of unrelated contacts / forbidden hours (21:00–08:00) / coercive vague phrasing.

**Algorithm (Phase 1)**: rule-based red-line matching → LLM scoring across 11 dimensions → fused output (red-line hit forces `compliance_score ≤ 30`).

**Acceptance**: on 100 hand-labeled samples — red-line recall ≥ 95%, false positives ≤ 10%; 11-dimension coverage 100%; supervisor-review flag accuracy ≥ 80%.

### 7.6 Script Recommendation

**Goal**: generate compliant script drafts based on case context; **never auto-send** — all sends require human approval.

**10 script types**: first-overdue reminder, D1 gentle reminder, D3 factual reminder, D7 solution guidance, D15 discount notice, PTP-due reminder, lost-contact recovery, low-pressure reminder for complaint-sensitive customers, supervisor-review notice for high-risk cases, missed-PTP follow-up.

**Approval flow**:
```
1. Agent generates draft (context + prompt template)
2. Compliance scan (same rule library as 7.5)
3. Frequency check (recent 7-day SMS ≤ 3, calls ≤ 5, etc.)
4. Show risk level + warnings
5. Collector confirmation
6. Supervisor review (mandatory for complaint-sensitive / high-risk)
7. Mock send (writes to ods_sms_send_log, no real outbound)
8. Audit trail (who / when / case / content / approval / result)
```

**Frequency defaults**:

| Channel | Daily cap | 7-day cap | Forbidden hours |
|---|---|---|---|
| SMS | 2 | 5 | 21:00–08:00 |
| AI dialer | 3 | 10 | 21:00–08:00 |
| Human call | 5 | 20 | 21:00–08:00 |

**Acceptance**: 7 script types all generate; compliance scan intercepts red-line drafts at generation; mock-send log fully auditable; demo flow `/script case_10086 --channel sms` runs end-to-end.

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

From Phase 1 post-loan show-room to Phase 6 enterprise foundation. For each Phase below: **goal, scope, key features, typical questions, exit criteria**.

> Phase 2-6 are **vision planning** — no committed timeline. After Phase 1, priorities decided based on feedback and resources.

### 11.1 Phase 1: Post-Loan Show-Room (Current)

See §10 for full delivery plan.

**Goal**: tell a complete story on synthetic post-loan data to prove product shape, business value, technical feasibility, AI differentiation.

**Core demo story**: M1 D7 recovery rate drops → auto-attribute to 6 contributors → produce weekly business report and collector script suggestions.

### 11.2 Phase 2: Pre-Loan + In-Life Risk Operations Copilot

**Goal**: extend product from post-loan single scenario to **full-lifecycle risk operations copilot** — prove the direction is not just a post-loan tool but a complete risk operations platform.

**Pre-loan scope**: application-to-disbursement funnel, FPD7/FPD30, MOB1/2/3 overdue, Vintage curves, score-band bad-rate, scorecard / LightGBM / XGBoost training with AUC/KS/PSI/Lift, SHAP explainability, Champion/Challenger comparison, threshold / limit / pricing simulator.

**In-life scope**: limit utilization, transaction success/reject/risk-hit rates, post-limit-increase overdue performance, customer risk migration (Sankey), behavior anomaly detection, intervention recommendations (limit increase / decrease / freeze / block / outreach).

**Typical questions**: why is approval rate down — channel quality vs rule tightening? Which decline rules are over-firing? Is the model drifting? Which features matter most? What's the regime-shift point on the volume-vs-bad-rate trade-off? Which customers are deteriorating and should be intervened on?

**Exit criteria**: pre-loan dictionary ≥ 15 metrics, in-life ≥ 10, fully YAML-ized; ≥ 1 scorecard + 1 XGBoost model trained / evaluated / explained / PSI-monitored; strategy simulator produces "threshold → volume/bad-rate/profit" sensitivity tables; second demo story (approval-rate anomaly attribution) runs.

### 11.3 Phase 3: Model & Strategy Closed Loop

**Goal**: stitch pre-loan / in-life / post-loan analytics into a **strategy closed loop** — discover risk → auto-attribute → suggest strategy → simulate ROI → human approval → monitor → auto-postmortem → distill Playbook.

**Scope**: unified customer risk profile, unified metric dictionary upgrade (cross-domain), strategy action library (historical strategies in one place), pre-launch simulation (counterfactual + risk-return + sensitivity), post-launch monitoring, Champion/Challenger, auto-postmortem reports, Playbook accumulation ("if X happens, suggest Y").

**Typical questions**: did this strategy genuinely lift recovery or just bring forward repayments? Which of Champion vs Challenger wins, and in which cohorts? What did we do in similar past situations? What's the suggested Playbook for the current issue?

**Exit criteria**: strategy library ≥ 30 historical strategies; ≥ 3 full closed-loop cycles complete; ≥ 1 Champion/Challenger comparison report.

### 11.4 Phase 4: ASR & QA Enhancement

**Goal**: extend QA from text to audio, lifting compliance coverage and training capability.

**Scope**: audio transcription (Mandarin, Cantonese, etc.), speaker diarization (agent vs customer vs third-party), risk-phrase localization on timeline, QA scoring expanded from 11 → 20+ dimensions, individualized training plans per collector, vendor-level QA dashboard, complaint case retrospectives (link recording → specific phrase), agent-training simulator (LLM role-plays customer types).

**Tech selection**: Whisper (local) vs Alibaba/Tencent/Volcano ASR — deferred to Phase 4 kickoff (per ADR-009).

**Exit criteria**: ASR accuracy ≥ 90% (Mandarin) / ≥ 85% (accented); red-line recall ≥ 95%; training simulator supports ≥ 5 customer archetypes.

### 11.5 Phase 5: Office Automation Enhancement

**Goal**: serve PMs, supervisors, and managers — not just analysts.

**Scope**: Word report enhancement (formal / consulting-style / exec-summary), PPT auto-generation (not just outline — full deliverable), Feishu API integration (real writes to docs / bitable / wiki), Excel template automation, historical-report knowledge base, meeting-note generation (from audio / transcript), PRD generation from requirement discussions, management-pitch material generation (style-adapted).

**Typical questions**: turn this week's analysis into a 30-slide consulting-style deck for Wednesday's exec review. Find all strategy docs mentioning "AI dialer" in the past six months. Convert this meeting recording into structured notes with action items. Give me the 5-minute version for the CEO.

**Exit criteria**: Feishu API real writes work; PPT auto-generation rated "directly usable" by ≥ 2 of 3 reviewers; knowledge base indexes ≥ 100 local docs with sub-2-second search.

### 11.6 Phase 6: Remote Data Sources & Enterprise Foundation

**Goal**: move from single-machine local demo to **small-team internal tool** — connect remote DBs, RBAC, audit, web dashboard, scheduling.

**Scope**: remote data sources (MySQL/PostgreSQL/Hive/MaxCompute/TBase), basic RBAC (admin / analyst / supervisor / collector), audit logging, enhanced masking for real-data ingestion, lightweight web dashboard (alternative to TUI), REST API service, Feishu / WeCom approval push, multi-user knowledge base, task scheduling.

**Boundary**: **NOT** full SaaS, multi-tenancy, or regulatory reporting — those are a different magnitude. **Enterprise-ready = 5–20-person team usable**, not high concurrency.

**Exit criteria**: at least 1 real remote data source connected (sandbox or masked); web dashboard works on Chrome/Safari; one 3–5-person team trial completed with feedback loop.

### 11.7 Cross-Phase Continuous Work

Spans all phases: documentation maintenance (PRD / dictionaries / ADRs), test coverage (DQ / metric calc / engine logic / agent behavior), demo asset refresh (screenshots / scripts / pitches per phase), performance (DuckDB tuning / LLM caching / template rendering), user feedback loop (via Issues → next-phase priorities).

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
