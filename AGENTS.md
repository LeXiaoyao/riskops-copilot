# RiskOps Copilot Agent Rules

## 1. Collaboration Model

- Claude is responsible for judgment-heavy work:
  - Product planning
  - PRD updates
  - Architecture decisions
  - ADR writing
  - Scope decisions
  - Privacy boundary review
  - Metric definition review
  - Demo narrative
  - README / portfolio wording
  - Code review from business, risk, and compliance perspective

- Codex is responsible for execution-heavy work:
  - Repository structure
  - Metadata YAML files
  - SQL schemas
  - Python scripts
  - Synthetic data generation
  - Warehouse build scripts
  - Data quality tests
  - Metric quality tests
  - Documentation rendering scripts
  - Local git commits

## 2. Git Rules

- Codex may create local commits.
- Codex must not push to remote unless the user explicitly asks.
- Before every commit, Codex must run:
  - git status
  - pytest, if tests exist
  - relevant validation scripts
- Codex must confirm that no sensitive or generated large files are staged.

Never commit:
- .env
- raw_secure/
- synthetic_data/raw_secure/
- *.duckdb
- *.db
- large generated parquet/csv files
- reports/
- exports/
- real customer data

## 3. Scope Rules

- Codex must only work on the requested milestone.
- Do not jump ahead to Dashboard, TUI, Agent, model training, or collection QA unless the current task explicitly asks for it.
- Current phase order:
  - M0: project skeleton
  - M1: data foundation
  - M2: metric asset layer
  - M3: anomaly detection and attribution
  - M4: dashboard and reports
  - M5: TUI / Agent
  - M6: model lab
  - M7: collection QA and script recommendation

## 4. PRD Rules

- docs/prd/PRD_v6.md is the current product baseline.
- Codex must not directly rewrite the PRD baseline unless explicitly asked.
- If implementation conflicts with PRD, write the issue to:
  - docs/decisions/pending_questions.md
- If a design decision is needed, create an ADR draft under:
  - docs/decisions/ADR-xxxx-title.md

## 5. Privacy Rules

- P4 fields are plaintext sensitive fields, including:
  - customer_name
  - id_no
  - mobile_no
  - bank_card_no
  - address

Rules:
- P4 fields may only exist in raw_secure simulation data.
- P4 fields must not enter DWD / DWS / ADS.
- P4 fields must not enter reports.
- P4 fields must not enter LLM context.
- P4 fields must not be committed to git.
- If any privacy boundary is unclear, stop and ask the user.

## 6. Metric Rules

- All metric definitions must come from metadata/metric_dictionary.yaml.
- Do not hardcode business metric definitions only in Python.
- Every metric must include:
  - metric_code
  - Chinese name
  - numerator
  - denominator
  - formula
  - grain
  - source tables
  - owner
  - version
  - notes
- If a metric definition is ambiguous, follow PRD_v6 and record the ambiguity in the metric notes field.

## 7. Validation Rules

Every Codex task must end with validation.

Depending on the task, run:

- python scripts/generate_synthetic_data.py --help
- python scripts/build_warehouse.py --help
- python scripts/validate_data_quality.py
- python scripts/validate_metric_quality.py
- python scripts/render_docs.py --help
- pytest

If validation cannot run, explain why.

## 8. Reporting Rules

At the end of every task, Codex must report:

1. Files changed.
2. Commands run.
3. Validation results.
4. Known issues.
5. Next recommended step.
