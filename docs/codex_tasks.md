# Codex 任务指令集

本文件是给 Codex（或其他代码生成助手）执行 M0 收尾到 M1 数据底座的完整任务清单。每个任务是一段独立可用的 prompt，**复制 → 粘贴到 Codex → 等结果**即可。

## Mandatory Pre-flight

Before starting any task, Codex must read:

- AGENTS.md
- CLAUDE.md
- docs/prd/PRD_v6.md
- docs/codex_tasks.md

Codex must identify the current milestone and must not work outside the requested milestone.

## 协作约定

1. **Codex 默认只 commit，不 push** — Claude review 后统一推送。
2. **架构决策（新依赖 / 新模式 / 新选型）必须停下问 Claude**，先开 ADR。
3. **隐私边界疑问（P4 字段、LLM 上下文）一律停下问 Claude**。
4. **歧义处理**：默认按 PRD v6 实现，并在产出文件的 `notes` 字段记录歧义点。
5. **每个任务完成后**：跑通对应的验收命令；如失败，先修后再 commit。
6. **commit message 格式**：`<阶段>: <内容简述>`，例如 `M1: metadata/tables.yaml 生成`。

## 项目上下文（每个 Codex 任务开头都先告诉它）

> 项目路径：`/Users/lexiaoyao/RiskOps_Copilot/`
> 需求总纲：`docs/prd/PRD_v6.md`（中文版，**唯一权威源**）
> AI 协作规范：`CLAUDE.md`（重点：范围控制、隐私分级、单一权威源、代码风格）
> 当前 git 状态：`main` 分支，最新 commit 是 PRD v6 全章节补强

---

## TODO 总清单（按依赖排序）

> 状态图例：✅ 已完成 / 🔥 下一步首要 / 🔄 进行中（已落地但未 commit / 部分完成） / ⚠️ 部分完成（待补强） / ⏳ 待办 / 🅿️ 阶段占位（依赖未到）
> 最近一次更新：2026-05-16
> 当前快照：M1 数据底座 commit `5978a13` 已 commit；GitHub 远程仓库已建好但未 push；主仓库 working tree 已开始 M2 工作（`metric_dictionary.yaml` / `calculators/*.py` / `test_metric*.py` 等 13 个 untracked + 8 个 modified，均未 commit）

### 阶段 1：M0 收尾 + GitHub 接入

| 序号 | 任务 | 负责 | 状态 | 依赖 | 备注 |
|---|---|---|---|---|---|
| **C1** | 创建 GitHub 远程仓库（用户手动） | 用户 | ✅ | — | https://github.com/LeXiaoyao/riskops-copilot 已建好 |
| **C2** | 首次推送到 GitHub（`git remote add origin` + `git push -u`） | Codex | 🔥 | C1 | 当前 `git remote -v` 为空；M1 4 个 commit 全部未推送 |
| **A1** | ADR-001 ~ ADR-010 详细版（每个一份独立文件） | Claude | ⏳ | — | 当前仅 PRD §13 表格汇总，未拆出单文件 |
| **A2** | `docs/demo_script_v0.md` 演示脚本 | Claude | ⏳ | — | 配合 M7 演示包装 |
| **A3** | `docs/interview_pitch.md` 面试讲稿 v1 | Claude | ⏳ | A2 | |

### 阶段 2：M1 数据底座（commit `5978a13` 已落地）

| 序号 | 任务 | 负责 | 状态 | 依赖 | 备注 |
|---|---|---|---|---|---|
| **C3** | `pyproject.toml` + 依赖初始化 | Codex | ✅ | — | commit `5978a13` |
| **C4** | `metadata/tables.yaml` 43 张表元信息 | Codex | ✅ | — | commit `5978a13`，10.7KB |
| **C5** | `metadata/columns.yaml` 全部字段字典 | Codex | ✅ | C4 | commit `5978a13`，72KB（注：主仓库已 modified，疑 M2 补字段） |
| **C6** | `metadata/privacy_policy.yaml` 隐私分级 | Codex | ⚠️ | C5 | 现版本仅 P0-P4 level 维度；缺字段级 `fields:` 列表（详见 C6'） |
| **C7** | `metadata/key_relationships.yaml` 主键关系 | Codex | ⚠️ | C4 | 现版本 10 条 relationships；缺 `entities:` 主键解释（详见 C7'） |
| **C10** | `schemas/{dim,ods,dwd,dws,ads}.sql` 五份建表 | Codex | ✅ | C5 | commit `5978a13`（注：`ads.sql` 主仓库已 modified） |
| **C11** | `scripts/render_docs.py` yaml → md 渲染 | Codex | ✅ | C5 | commit `5978a13`（注：主仓库已 modified，疑加 metric 渲染） |
| **C12** | `scripts/generate_synthetic_data.py` 合成数据生成器 | Codex | ✅ | C10 | commit `5978a13`，28KB（注：主仓库已 modified） |
| **C13** | `scripts/build_warehouse.py` 数仓加工 | Codex | ✅ | C10, C12 | commit `5978a13`，20KB（注：主仓库已 modified，疑 C17 替换占位 SQL） |
| **C14** | `tests/test_data_quality.py` 数据质量测试 | Codex | ⚠️ | C13 | 当前为 1 个聚合 pytest 用例 + `scripts/validate_data_quality.py`；缺 11 条规则拆分（详见 C14'） |

### 阶段 3：M1 收尾补强（基于 R1 review 列出的差距）

| 序号 | 任务 | 负责 | 状态 | 依赖 | 备注 |
|---|---|---|---|---|---|
| **C6'** | 补强 `privacy_policy.yaml`：增加字段级 `fields:` 列表（每字段 allowed_layers / allowed_in_reports / allowed_in_llm_context / masking_rule / hashing_rule） | Codex | ⏳ | C5 | 从 columns.yaml 抽取，覆盖全部 P3/P4 字段 |
| **C7'** | 补强 `key_relationships.yaml`：增加 `entities:` 字段，对 customer_id / loan_id / case_id 等主键给业务解释 + 加入 vendor/line/collector 资源维度关系 | Codex | ⏳ | C4 | |
| **C14'** | 拆 `tests/test_data_quality.py` 为 8 条硬规则 + 3 条软规则的独立 pytest 用例（DQ001-DQ008 / DQ101-DQ103） | Codex | ⏳ | C14 | 现 validator 已有逻辑，只需拆 pytest 入口 |
| **D1** | `docs/data_generation_log.md`：7 个异常埋点的验证 SQL + 预期值 + 实际跑出来的数值 | Codex | ⏳ | C12, C13 | C12 验收清单要求 |
| **R1** | Claude review M1 全产出（C3-C14 + C6'/C7'/C14'/D1） | Claude | 🔄 | M1 commit + 补强 | M1 commit 已可看；正式 review 建议在补强后 |
| **C15** | M1 收尾统一 push（含 CHANGELOG 收尾 + tag `v0.1.0` + GitHub Release） | Codex | ⏳ | R1, C2 | C2 完成后这一步顺势可做 |

### 阶段 4：M2 指标资产（主仓库 working tree 已落地，待 review + commit）

> 当前状态：所有 M2 产出均在主仓库 working tree 中（untracked / modified），尚未 commit。**Claude 启动 R2 review 之前不要再改主仓库 working tree，避免冲突。**

| 序号 | 任务 | 负责 | 状态 | 依赖 | 备注 |
|---|---|---|---|---|---|
| **C8** | `metadata/metric_dictionary.yaml` 39 个指标（26 实现 + 13 占位） | Codex | 🔄 | C4, C5 | 文件已生成（untracked），附带 `metric_owner.yaml` / `metric_change_log.yaml`，待 review |
| **C9** | `metadata/metric_lineage.yaml` 26 个指标完整血缘 | Codex | 🔄 | C8 | 已 modified（从 3 条占位扩展），待 review |
| **C16** | `riskops/metrics/calculators/<metric_code>.py` 26 个指标计算函数 | Codex | 🔄 | C8 | `base.py / postloan.py / collection.py / compliance.py / roi.py` 已生成（untracked），含 `riskops/metrics/dictionary.py` 入口 |
| **C17** | 把 `build_warehouse.py` 中 ADS 占位 SQL 替换为 calculators 调用 | Codex | 🔄 | C16 | `build_warehouse.py` / `ads.sql` / `validate_metric_quality.py` 均已 modified |
| **C18** | `tests/test_metric_calculation.py` 指标级单测（每个 metric_code 至少 1 个用例） | Codex | 🔄 | C16 | 实际产出 `test_metrics.py / test_metric_dictionary.py / test_metric_quality.py`（untracked） |
| **C19** | 跑 `render_docs.py metrics`，产出 `docs/metric_dictionary.md` | Codex | 🔄 | C8, C11 | `docs/metric_dictionary.md / docs/metric_lineage.md` 已生成（untracked） |
| **R2** | Claude review M2 产出（指标口径 vs PRD §6 / 计算函数 / 单测） | Claude | 🔥 | C8-C19 | M2 文件已全部在 working tree，等 R2 启动 |
| **C20** | M2 收尾 commit + push + tag `v0.2.0` + Release | Codex | ⏳ | R2, C15 | 建议 M1 推送先完成，再走 M2 |

---

## C1：创建 GitHub 远程仓库（用户手动）

不是 Codex 任务，**用户在浏览器完成**：

1. 打开 https://github.com/new
2. Repository name：`riskops-copilot`
3. Description：`面向消费金融风控与贷后策略的数据分析、指标归因、风险建模与经营报告自动化工作台 | A unified AI workbench for consumer finance risk operations`
4. Public（推荐）/ Private 自选
5. **不要勾选** "Add a README"、".gitignore"、"license"
6. 创建后**不要做任何额外操作**，把 URL 记下来。

---

## C2：Codex 指令 — 首次推送到 GitHub（🔥 当前最优先任务）

```
你在 /Users/lexiaoyao/RiskOps_Copilot/ 工作。GitHub 仓库已建好：
https://github.com/LeXiaoyao/riskops-copilot

当前本地状态：
- main 分支共 4 个 commit（M0 启动 / PRD v6 补强 / AGENTS 协作规范 / M1 数据底座）
- git remote -v 为空（还没接远程）
- working tree 有未 commit 的 M2 进度，**先 stash 隔离再 push，避免误推**

任务：
1. git stash push -u -m "M2-wip before first push"  把 M2 working tree 暂存
2. 确认 git status 干净
3. 添加 remote：git remote add origin https://github.com/LeXiaoyao/riskops-copilot.git
4. 推送：git push -u origin main
5. 验证 GitHub 仓库主页：
   - README 中文版徽章正常
   - 目录结构完整（riskops/ synthetic_data/ metadata/ schemas/ scripts/ tests/ docs/ templates/ configs/）
   - 4 个 commit 都在
6. git stash pop  恢复 M2 进度
7. 报告 push 结果（包含 GitHub commit URL）

注意：
- 只做 git 操作，不要修改文件，不要新增文件。
- 不要打 tag，tag v0.1.0 留到 C15 做。
- 不要 force push。
- stash pop 后若有冲突，立即停下问 Claude。
```

---

## C3：Codex 指令 — pyproject.toml 与依赖初始化

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
参考：PRD v6 §4.2 技术栈选型表

任务：生成 pyproject.toml，建立 Python 3.11+ 项目骨架。

依赖（生产）：
- duckdb >= 1.0
- pandas >= 2.0
- pyarrow >= 14.0（Parquet）
- numpy >= 1.26
- faker >= 25.0（合成数据）
- pyyaml >= 6.0
- jinja2 >= 3.1
- plotly >= 5.20
- openpyxl >= 3.1
- python-pptx >= 0.6
- python-docx >= 1.1
- textual >= 0.60（TUI）
- anthropic >= 0.30（LLM）
- click >= 8.1（CLI 入口）

依赖（开发）：
- pytest >= 8.0
- pytest-cov >= 5.0
- ruff >= 0.4（lint + format）
- mypy >= 1.10

要求：
1. 用 uv（推荐）或 poetry 都行，二选一并在 commit message 注明理由
2. 设置 entry point：riskops = "riskops.cli:main"
3. 包含 [tool.ruff]、[tool.pytest.ini_options]、[tool.mypy] 基础配置
4. 不要安装依赖，只生成配置文件
5. 同时创建 riskops/__init__.py、riskops/cli.py（cli.py 只放最小骨架：def main(): print("RiskOps Copilot v0.0.0 — 见 PRD v6 §10 里程碑")）

验收：
- 文件可被解析（运行 python -c "import tomllib; tomllib.load(open('pyproject.toml','rb'))" 不报错）
- ruff check . 不报错（即使没装也无所谓，只要配置语法合法）

commit message：M0: pyproject.toml 依赖初始化（uv/poetry 选型 + 工具配置）
```

---

## C4：Codex 指令 — metadata/tables.yaml 生成

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
参考：PRD v6 §5.4 表清单（中文版 1642 行那个），共 43 张表

任务：生成 metadata/tables.yaml，作为表元信息的唯一权威源。

每张表必须包含字段：
- table_name: 物理表名
- table_name_cn: 中文名
- layer: dim / ods / dwd / dws / ads
- domain: customer / loan / case / collection / vendor / compliance / metric 等
- grain: 粒度描述
- primary_key: 主键字段名（单个或多个）
- partition_key: 分区键（如 stat_date）
- purpose: 一句话用途
- source_tables: 上游表（DIM/ODS 可空；DWD/DWS/ADS 必填）
- refresh_frequency: daily / hourly / snapshot
- estimated_rows_medium: medium 档下的预估行数
- notes: 备注（歧义、待定项等）

要求：
1. 严格按 PRD v6 §5.4.1-§5.4.5 的表清单输出全部 43 张
2. YAML 结构：顶层 key 是 layer（dim/ods/dwd/dws/ads），下面是 tables 列表
3. 字段名 / 命名风格与 PRD 完全一致
4. 不要发明 PRD 未提及的表
5. notes 字段记录任何与 PRD 不一致或需要 Claude 拍板的地方

输出文件：metadata/tables.yaml

验收：
- python -c "import yaml; yaml.safe_load(open('metadata/tables.yaml'))" 不报错
- 表数：dim 10 + ods 14 + dwd 5 + dws 8 + ads 6 = 43

commit message：M1: metadata/tables.yaml 43 张表元信息（唯一权威源）
```

---

## C5：Codex 指令 — metadata/columns.yaml 全部字段字典

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C4 已完成（metadata/tables.yaml 存在）
参考：PRD v6 §5.4 每张表的"关键字段摘要"列

任务：生成 metadata/columns.yaml，每张表展开完整字段定义。

每个字段必须包含：
- field_name: 字段名
- field_name_cn: 中文名
- type: 数据类型（DuckDB 兼容：VARCHAR, BIGINT, DECIMAL(18,2), DATE, TIMESTAMP, BOOLEAN）
- nullable: true / false
- privacy_level: P0 / P1 / P2 / P3 / P4
- is_primary_key: true / false
- is_foreign_key: 关联到 "<table>.<field>" 或 null
- description: 字段口径说明
- enum_values: 如果是枚举，列出可选值
- notes: 备注

要求：
1. 顶层 key 是 table_name，下面 columns 列表
2. PRD §5.4 已列出"关键字段"的，必须 100% 覆盖
3. 对于 PRD 没有详细列出但必要的字段（如审计字段 create_time / update_time），自行补充并在 notes 注明 "补充字段"
4. **隐私分级严格按 §5.2.1**：
   - P0/P1/P2 可以进入 DWD/DWS/ADS
   - P3 哈希字段加注 "LLM 不直接发送"
   - P4 明文字段：DIM/ODS 表中可以出现，但必须标 P4 + notes: "仅 raw_secure 目录"
   - DWD/DWS/ADS 表**不允许** P4 字段，违反则报错停下问 Claude
5. 字段总数预估 ≥ 400

输出文件：metadata/columns.yaml

验收：
- yaml 可解析
- 跑一个简单脚本扫描所有 dwd_/dws_/ads_ 表，确认无 P4 字段
- DIM 客户表必须包含 customer_id, customer_id_hash, mobile_hash, mobile_masked, customer_name_encrypted（如果有 P4 字段也保留，标 P4）

commit message：M1: metadata/columns.yaml 全表字段字典 + P0-P4 隐私分级
```

---

## C6：Codex 指令 — metadata/privacy_policy.yaml

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C5 已完成
参考：PRD v6 §5.2 隐私分级 + §9 合规与隐私

任务：从 metadata/columns.yaml 抽取所有字段，生成 metadata/privacy_policy.yaml，记录每个字段的隐私分级与处理规则。

结构：
- fields: 列表，每项 {field_name, privacy_level, allowed_layers, allowed_in_reports, allowed_in_llm_context, masking_rule, hashing_rule, notes}
- rules: 规则总览（P0-P4 各级的默认行为）

具体规则（必须严格执行）：
- P0/P1: 全部允许
- P2: 全部允许，展示时用脱敏值
- P3: DWD/DWS/ADS 允许；报告不展示；LLM 上下文：不直接发送哈希值，仅在必要时附 "已脱敏" 说明
- P4: 仅 DIM/ODS 的 raw_secure 子目录允许；其他全部禁止

输出：metadata/privacy_policy.yaml

验收：
- yaml 可解析
- 包含 customer_name / id_no / mobile_no / address / bank_card_no 五个 P4 字段，allowed_in_llm_context: false
- 包含至少 5 个 P3 字段（id_no_hash, mobile_hash, bank_card_hash 等），allowed_in_llm_context: "hashed_only_with_disclaimer"

commit message：M1: metadata/privacy_policy.yaml 字段级隐私策略
```

---

## C7：Codex 指令 — metadata/key_relationships.yaml

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
参考：PRD v6 §5.3 核心主键关系

任务：把 §5.3 的主键关系图机器可读化。

结构：
- relationships:
    - from: customer_id (in dim_customer)
      to: loan_id (in dim_loan)
      cardinality: 1:N
      via: dim_loan.customer_id
    - from: case_id (in dim_case)
      to: loan_id (in dim_loan)
      cardinality: M:N
      via: dim_case_loan_mapping
    （依此类推所有 §5.3 列出的关系）
- entities:
    - customer_id: 客户号，贯穿贷前/贷中/贷后
    - loan_id: ...
    （所有主键的解释）

要求：完整覆盖 §5.3 的所有关系（约 8 条）+ vendor/line/collector 资源维度关系。

输出：metadata/key_relationships.yaml

commit message：M1: metadata/key_relationships.yaml 主键关系机器可读版
```

---

## C8：Codex 指令 — metadata/metric_dictionary.yaml

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
参考：PRD v6 §6.3 ~ §6.6 全部指标清单（共 26 个 Phase 1 指标 + 13 个 Phase 2+ 占位）

任务：生成 metadata/metric_dictionary.yaml，唯一权威源。

每个指标的 YAML 结构（必填字段全在 §6.1）：
- metric_code (snake_case 唯一)
- metric_name_cn
- business_domain (postloan / collection / compliance / roi / preloan / midloan / model)
- metric_type (ratio / amount / count / score)
- numerator (业务描述)
- denominator (业务描述，若无则 null)
- formula (SQL-like 表达式)
- grain (维度列表)
- source_tables (上游表名列表)
- filter_condition
- owner (默认 postloan_strategy_team)
- refresh_frequency (daily)
- version (v1.0)
- priority (P0/P1/P2/P3)
- notes
- change_log:
    - 2026-05-15: 初版

要求：
1. Phase 1 全部 26 个指标必须有完整定义（贷后结果 8 + 催收过程 10 + 合规 5 + 减免 3）
2. Phase 2+ 占位 13 个：metric_code + business_domain + priority: P3 + notes: "Phase 2+ 实现" 即可，其他字段留空
3. source_tables 必须真实指向 metadata/tables.yaml 里存在的表名
4. **公式必须可执行 SQL 化**，例如 recovery_rate_d7 的 formula 应该写成：
   ```sql
   SUM(repay_amount_within_7d_after_case_create) / SUM(initial_outstanding_amount)
   ```
5. 任何与 PRD §6.3-§6.6 不一致的地方停下问 Claude

输出：metadata/metric_dictionary.yaml

验收：
- yaml 可解析
- 指标总数 = 39（26 + 13）
- metric_code 全局唯一
- P0 指标数 = 20

commit message：M2: metadata/metric_dictionary.yaml 39 个指标（Phase 1 实现 26 + 占位 13）
```

---

## C9：Codex 指令 — metadata/metric_lineage.yaml

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C4 + C8 完成
参考：PRD v6 §6.9.2 血缘维护

任务：从 metric_dictionary.yaml 推导每个指标的加工链路。

结构：
- recovery_rate_d7:
    ads_tables: [ads_postloan_dashboard_di]
    dws_tables: [dws_case_status_snapshot_di]
    dwd_tables: [dwd_repayment_detail_di]
    ods_tables: [ods_repayment_detail, ods_case_daily_snapshot]
  （依此类推 26 个 Phase 1 指标）

要求：
1. 只为 Phase 1 实现的 26 个指标生成血缘；占位指标跳过
2. 链路必须真实（每张表都在 metadata/tables.yaml 里存在）
3. 同一指标可能横跨多张 ADS 表（如 recovery_rate_d7 在驾驶舱、归因表里都出现），全列出来

输出：metadata/metric_lineage.yaml

commit message：M2: metadata/metric_lineage.yaml 26 个指标血缘
```

---

## C10：Codex 指令 — schemas/*.sql 五份建表语句

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C5 完成
参考：PRD v6 §5.4 + metadata/columns.yaml

任务：从 metadata/columns.yaml 生成 5 份 DuckDB 建表 SQL。

文件：
- schemas/dim.sql （10 张表）
- schemas/ods.sql （14 张表）
- schemas/dwd.sql （5 张表）
- schemas/dws.sql （8 张表）
- schemas/ads.sql （6 张表）

要求：
1. 标准 DuckDB CREATE TABLE 语法
2. 主键用 PRIMARY KEY 约束
3. 外键用 -- FK: 注释标注（DuckDB 对外键约束支持有限，不强制）
4. 每张表前加注释块：表名 / 中文名 / 用途 / 粒度 / 数据量级
5. 字段顺序：主键 → 业务键 → 维度 → 度量 → 状态 → 审计字段
6. 字段后注释中文名 + 隐私等级，例如：customer_id VARCHAR NOT NULL, -- 客户号 P1
7. 文件开头加：CREATE SCHEMA IF NOT EXISTS dim;（依此类推）

验收：
- DuckDB CLI 执行 .read schemas/dim.sql 等不报错
- SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='dim' = 10

commit message：M1: schemas/*.sql 五份 DuckDB 建表语句（43 张表）
```

---

## C11：Codex 指令 — scripts/render_docs.py

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C5 + C8 完成
参考：PRD v6 §5.7.2 + §6.9.4

任务：写一个脚本，从 metadata/*.yaml 渲染人工可读的 markdown 文档。

脚本支持子命令：
- python scripts/render_docs.py data_dict   → docs/data_dictionary.md
- python scripts/render_docs.py metrics     → docs/metric_dictionary.md
- python scripts/render_docs.py keys        → docs/key_relationships.md
- python scripts/render_docs.py privacy     → docs/privacy_policy.md
- python scripts/render_docs.py lineage     → docs/data_lineage.md
- python scripts/render_docs.py all         → 全部渲染

要求：
1. 用 Jinja2 模板（templates/docs/*.md.j2）
2. 文档结构合理（按 layer 分组、按 domain 分组、含目录、含 H2 章节）
3. 文档顶部加："# ... 字典\n\n> 由 scripts/render_docs.py 从 metadata/<yaml> 自动渲染。**不要手动编辑**。\n> 修改方式：编辑对应 YAML 后重新跑 render_docs。"
4. 用 click 做命令行参数

模板文件路径：templates/docs/{data_dict,metrics,keys,privacy,lineage}.md.j2

验收：
- python scripts/render_docs.py all 不报错
- 生成的 5 份 md 在浏览器或 VSCode 中查看，格式合理无错位

commit message：M1: scripts/render_docs.py + 5 份 Jinja2 模板（yaml → md 渲染）
```

---

## C12：Codex 指令 — scripts/generate_synthetic_data.py（最大任务）

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C5 + C10 完成
参考：PRD v6 §5.5 合成数据规范

⚠️ 这是 M1 最大的工程任务，预估 800-1500 行代码。
⚠️ **如果你不确定任何业务规则，立刻停下问 Claude，不要凭直觉发挥。**

任务：生成合成数据生成器，能产出 18 个月、medium 档（8 万客户）的全套 DIM/ODS 数据。

命令行接口：
python scripts/generate_synthetic_data.py \
    --months 18 \
    --scale medium \
    --seed 20260515 \
    --anomaly-window-days 30 \
    --output-format parquet \
    --with-raw  # 是否生成 raw_secure 目录的 P4 明文字段

参数：
- --scale: small / medium / large（见 §5.5.2 规模档位表）
- --output-format: csv / parquet（默认 parquet）
- --seed: 随机种子，保证可复现
- --months: 总跨度
- --anomaly-window-days: 最近 N 天埋入异常（默认 30）

输出目录：
- synthetic_data/dim/<table>.parquet (或 csv)
- synthetic_data/ods/<table>.parquet
- 如果 --with-raw：synthetic_data/raw_secure/<table>_raw.parquet（含 P4 明文）

业务规则（重中之重）：

【时间线】严格按 §5.5.1 六段时间线生成：
- 历史基线、训练期、验证期、OOT、经营分析、Demo 异常窗

【7 个异常埋点】严格按 §5.5.3，必须埋入且可验证：
1. M1 D7 回收率最近 30 天从 18.6% → 15.2%
2. 华东线路人均案量 +25%
3. 供应商 B 接通率 -6pct
4. 高余额客群占比 +8pct
5. AI 外呼覆盖率 -12pct
6. 减免使用率 -4pct + PTP 履约率 -5pct
7. 某短信模板投诉率 = 均值 × 2

【主键完整性】
- customer_id (1:N) loan_id (1:N) plan_id (1:N) repay_id
- customer_id (1:N) case_id (1:N) action_id / note_id / decision_id
- case_id (M:N) loan_id 通过 dim_case_loan_mapping

【隐私分级】
- 默认输出：所有 P4 字段直接产生哈希/脱敏版（id_no → id_no_hash, mobile_no → mobile_hash + mobile_masked, customer_name → customer_name_encrypted）
- --with-raw：在 raw_secure/ 目录额外产出 P4 明文（用 Faker），但只在该目录
- raw_secure/ 已 gitignore，不入库

【标签无穿越】
- 所有日切表的 stat_date 必须严格递增
- 特征字段（如 c_score）的日期 < 标签字段（如 label_repay_7d）的日期

【可复现】
- 同 --seed 出同样数据
- 写一份 docs/data_generation_log.md 记录每次生成的参数和异常埋点验证结果

代码结构：
- scripts/generate_synthetic_data.py（CLI 入口）
- riskops/data/generators/dim_generator.py
- riskops/data/generators/ods_generator.py
- riskops/data/generators/anomaly_injector.py
- riskops/data/generators/utils.py（Faker 配置、哈希函数）

验收：
1. python scripts/generate_synthetic_data.py --months 18 --scale medium --seed 20260515 跑通，耗时 < 10 分钟
2. synthetic_data/dim/ 下 10 个 parquet 文件
3. synthetic_data/ods/ 下 14 个 parquet 文件
4. 7 个埋点异常可被 SQL 验证（在 docs/data_generation_log.md 中给出验证 SQL 和预期结果）
5. raw_secure/ 默认不生成
6. 跑 --with-raw 时 raw_secure/ 生成，但 git status 不显示（gitignore 生效）

⚠️ 如果遇到以下情况，立即停下问 Claude：
- 7 个异常的具体数值实现不清楚
- 同一客户的多笔借据如何归户成案件
- C 卡分（ods_postloan_c_score）的具体分布
- 投诉率、PTP 履约率等基线值如何确定

commit message：M1: scripts/generate_synthetic_data.py + DIM/ODS 数据生成器（含 7 个异常埋点）
```

---

## C13：Codex 指令 — scripts/build_warehouse.py 数仓加工

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C10 + C12 完成
参考：PRD v6 §5.1 分层加工方向

任务：把 ODS 数据加工成 DWD / DWS / ADS 三层。

命令行：
python scripts/build_warehouse.py --layers all
python scripts/build_warehouse.py --layers dwd,dws
python scripts/build_warehouse.py --rebuild  # 重建（清空 DuckDB）

加工逻辑：
- ODS → DWD: 清洗去重、外键校验、字段统一、P4 字段过滤
- DWD → DWS: 主题聚合、日切宽表生成
- DWS → ADS: 指标计算（调用 riskops/metrics/calculators/<metric_code>.py）

⚠️ 计算函数现在还不存在，先用占位 SQL 直接计算到 ADS。calculators 模块在 M2 阶段补。

代码结构：
- scripts/build_warehouse.py（CLI 入口）
- riskops/data/warehouse/dwd_builder.py
- riskops/data/warehouse/dws_builder.py
- riskops/data/warehouse/ads_builder.py
- riskops/data/warehouse/db.py（DuckDB 连接管理，存储到 ./riskops.duckdb）

验收：
1. python scripts/generate_synthetic_data.py 后接 python scripts/build_warehouse.py --rebuild 一气呵成
2. DuckDB 中 5 个 schema 各表非空
3. 简单 SQL 验证：SELECT recovery_rate_d7 FROM ads_postloan_dashboard_di WHERE stat_date = '2026-05-14' 能返回合理数值

commit message：M1: scripts/build_warehouse.py + DWD/DWS/ADS 加工器
```

---

## C14：Codex 指令 — tests/test_data_quality.py 数据质量测试

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/
前置：C13 完成
参考：PRD v6 §5.6 数据质量规则

任务：写 8 条硬规则（CI 必过）+ 3 条软规则（告警）的 pytest 测试。

文件：tests/test_data_quality.py

硬规则（assert，不通过则失败）：
1. test_dq001_dim_primary_key_unique
2. test_dq002_foreign_keys_resolvable
3. test_dq003_amounts_non_negative
4. test_dq004_no_date_leakage
5. test_dq005_p4_isolation（扫描 dwd_/dws_/ads_ 表，断言无 P4 字段名）
6. test_dq006_ratio_in_range_0_1（recovery_rate_*, connect_rate, ptp_rate 等）
7. test_dq007_case_loan_mapping_completeness
8. test_dq008_time_series_completeness（日切表 stat_date 连续性）

软规则（warning 而非 fail，用 pytest.warns 或 logging.warning）：
9. test_dq101_metric_day_over_day_volatility（> 30% 告警）
10. test_dq102_sample_balance（> 50:1 告警）
11. test_dq103_null_rate_spike（> 5% 告警）

数据准备：
- conftest.py：fixture 在测试 session 开始时跑 generate_synthetic_data + build_warehouse（小规模 small 档 + 固定 seed）
- 测试连接 DuckDB 跑 SQL

验收：
- pytest tests/test_data_quality.py -v 全绿
- 输出包含 11 条测试结果

commit message：M1: tests/test_data_quality.py 11 条数据质量规则（8 硬 + 3 软）
```

---

## R1：Claude review 清单（Codex 完成 C3-C14 后）

Claude 启动 review 时关注：

1. **隐私边界**：DWD/DWS/ADS 表绝对无 P4 字段
2. **指标口径**：metadata/metric_dictionary.yaml 与 PRD v6 §6 一致
3. **异常埋点**：7 个异常都能在数据中验证
4. **可复现性**：同 seed 出同样数据
5. **代码风格**：CLAUDE.md 中的约定（短函数、命名、无多余注释）
6. **测试覆盖**：DQ 测试全绿
7. **commit message**：是否描述清楚 why

---

## C15：Codex 指令 — M1 完成后统一 push

```
项目路径：/Users/lexiaoyao/RiskOps_Copilot/

前置：Claude 已 review C3-C14 所有 commit，给出绿灯。

任务：
1. 检查 git log，确认所有 commit 都按规范写好
2. git push origin main
3. 在 GitHub 上检查：
   - 仓库 commit 数 = 本地 commit 数
   - README 在主页正常显示
   - PRD v6 链接可点
   - synthetic_data/、metadata/、schemas/ 目录可见
4. 创建 release tag：git tag -a v0.1.0 -m "M1 数据底座完成"
5. git push --tags
6. 在 GitHub Releases 页面创建 Release v0.1.0，标题"M1 数据底座完成"，描述引用 CHANGELOG.md 对应章节

commit message：（如有 CHANGELOG 更新）M1: 数据底座里程碑收尾 + Release v0.1.0
```

---

## 附录：常见歧义处理

| 歧义 | 默认处理 | 何时问 Claude |
|---|---|---|
| 字段隐私分级不明 | 按最严判（取最敏感的） | 影响 DWD 准入时必须问 |
| 表的某字段 PRD 没列 | 加上并在 notes 标"补充" | 影响主键/外键时必须问 |
| 异常埋点幅度 | 严格按 §5.5.3 | 如有冲突必须问 |
| 性能优化（索引/分区） | 先简单实现，标 TODO | 重大重构必须问 |
| 新增依赖 | **必须问** Claude 并写 ADR | 总是 |
