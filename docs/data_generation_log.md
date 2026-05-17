# D1 Data Generation Log

## 1. Run Scope

- 任务：D1 数据生成日志
- 目标：记录本次合成数据生成参数、表规模、异常埋点验证 SQL、实际验证结果、已知限制
- 数据根目录：`synthetic_data/`
- 输出格式：`parquet`
- 原始敏感明文：未生成，未使用 `--with-raw`
- 生成运行口径：脚本使用 `date.today()` 作为数据结束日；本次生成数据的最大业务日期为 `2026-05-16`

## 2. Generation Parameters

- 命令：`python scripts/generate_synthetic_data.py --months 18 --scale small --seed 20260515`
  - `months`：18
  - `scale`：small
  - `seed`：20260515
  - `output-format`：parquet，使用脚本默认值
  - `with-raw`：false，使用脚本默认值

- 生成脚本输出：
  - `generated dim_tables=10 ods_tables=14 scale=small format=parquet`
  - `customers=20000 loans=30000 cases=10000 actions=200000`

- 仓库构建命令：`python scripts/build_warehouse.py`
  - 构建输出：`built dwd_tables=5 dws_tables=8 ads_tables=6`

## 3. Date Ranges

- `dim/dim_case.case_create_time`
  - 最小日期：`2025-11-17`
  - 最大日期：`2026-05-16`
  - 覆盖自然日：180
  - 行数：10000

- `ods/ods_collection_action.action_time`
  - 最小日期：`2025-11-17`
  - 最大日期：`2026-05-16`
  - 覆盖自然日：181
  - 行数：200000

- `ods/ods_loan_daily_snapshot.stat_date`
  - 最小日期：`2026-03-18`
  - 最大日期：`2026-05-16`
  - 覆盖自然日：60
  - 行数：240000

- `ads/ads_postloan_dashboard_di.stat_date`
  - 最小日期：`2024-12-16`
  - 最大日期：`2026-05-16`
  - 覆盖自然日：517
  - 行数：517

## 4. Table Scale

### 4.1 DIM

- 层汇总：
  - 表数：10
  - 总行数：70439

- `dim_case`：10000
- `dim_case_loan_mapping`：10000
- `dim_channel`：3
- `dim_collection_line`：5
- `dim_collector`：420
- `dim_customer`：20000
- `dim_loan`：30000
- `dim_product`：3
- `dim_strategy`：4
- `dim_vendor`：4

### 4.2 ODS

- 层汇总：
  - 表数：14
  - 总行数：1434034

- `ods_assignment_decision_log`：10000
- `ods_call_record`：66666
- `ods_case_daily_snapshot`：424315
- `ods_case_flow`：10000
- `ods_collection_action`：200000
- `ods_collection_note`：40000
- `ods_complaint`：225
- `ods_customer_daily_snapshot`：353997
- `ods_loan_daily_snapshot`：240000
- `ods_postloan_c_score`：10000
- `ods_reduction_application`：621
- `ods_repayment_detail`：8184
- `ods_repayment_plan`：30000
- `ods_sms_send_log`：40026

### 4.3 DWD

- 层汇总：
  - 表数：5
  - 总行数：248409

- `dwd_case_flow_detail_di`：10000
- `dwd_collection_action_detail_di`：200000
- `dwd_complaint_detail_di`：225
- `dwd_due_plan_detail_di`：30000
- `dwd_repayment_detail_di`：8184

### 4.4 DWS

- 层汇总：
  - 表数：8
  - 总行数：1452234

- `dws_case_status_snapshot_di`：424315
- `dws_collection_process_wide_di`：199884
- `dws_collector_profile_di`：69741
- `dws_customer_postloan_tag_di`：353997
- `dws_customer_profile_di`：20000
- `dws_customer_status_snapshot_di`：353997
- `dws_loan_status_snapshot_di`：30000
- `dws_vendor_line_capacity_di`：300

### 4.5 ADS

- 层汇总：
  - 表数：6
  - 总行数：72196

- `ads_collector_performance_di`：69741
- `ads_compliance_qc_di`：517
- `ads_postloan_dashboard_di`：517
- `ads_recovery_attribution_di`：180
- `ads_reduction_roi_di`：517
- `ads_vendor_performance_di`：724

## 5. Anomaly Seeding Verification SQL

> 说明：当前运行环境未安装 `duckdb` Python 模块，因此本节 SQL 作为可复跑的校验口径记录；实际结果使用 pandas 读取同一批 parquet 文件做等价计算，未新增依赖。

### 5.1 高余额客群占比近期抬升

```sql
WITH case_period AS (
  SELECT
    CASE
      WHEN CAST(case_create_time AS DATE) >= DATE '2026-05-16' - INTERVAL 29 DAY
      THEN 'recent_30d'
      ELSE 'baseline'
    END AS period,
    case_id,
    balance_segment
  FROM read_parquet('synthetic_data/dim/dim_case.parquet')
)
SELECT
  period,
  COUNT(DISTINCT case_id) AS case_count,
  SUM(CASE WHEN balance_segment = 'HIGH' THEN 1 ELSE 0 END) AS high_balance_cases,
  AVG(CASE WHEN balance_segment = 'HIGH' THEN 1.0 ELSE 0.0 END) AS high_balance_rate
FROM case_period
GROUP BY period
ORDER BY period;
```

- 实际结果：
  - `baseline`
    - `case_count`：6440
    - `high_balance_cases`：1685
    - `high_balance_rate`：26.1646%
  - `recent_30d`
    - `case_count`：3560
    - `high_balance_cases`：1241
    - `high_balance_rate`：34.8596%
- 结论：近期 30 天高余额占比高于基线，埋点有效。

### 5.2 供应商 B 近期接通率下降，AI 外呼覆盖率近期下降

```sql
WITH action_period AS (
  SELECT
    CASE
      WHEN CAST(action_time AS DATE) >= DATE '2026-05-16' - INTERVAL 29 DAY
      THEN 'recent_30d'
      ELSE 'baseline'
    END AS period,
    CASE WHEN vendor_id = 'V_B' THEN 'V_B' ELSE 'OTHER' END AS vendor_group,
    action_id,
    connected_flag,
    ai_outbound_flag
  FROM read_parquet('synthetic_data/ods/ods_collection_action.parquet')
)
SELECT
  period,
  vendor_group,
  COUNT(*) AS action_count,
  AVG(CASE WHEN connected_flag THEN 1.0 ELSE 0.0 END) AS connect_rate,
  AVG(CASE WHEN ai_outbound_flag THEN 1.0 ELSE 0.0 END) AS ai_coverage_rate
FROM action_period
GROUP BY period, vendor_group
ORDER BY period, vendor_group;
```

- 实际结果：
  - `baseline / OTHER`
    - `action_count`：91015
    - `connect_rate`：36.0457%
    - `ai_coverage_rate`：29.9962%
  - `baseline / V_B`
    - `action_count`：75852
    - `connect_rate`：33.9701%
    - `ai_coverage_rate`：29.8700%
  - `recent_30d / OTHER`
    - `action_count`：18183
    - `connect_rate`：35.9512%
    - `ai_coverage_rate`：18.1323%
  - `recent_30d / V_B`
    - `action_count`：14950
    - `connect_rate`：28.2274%
    - `ai_coverage_rate`：17.3378%
- 结论：供应商 B 近期接通率显著低于自身基线和其他供应商；近期 AI 外呼覆盖率也低于基线，埋点有效。

### 5.3 风险短信模板投诉率高于普通模板

```sql
WITH sms AS (
  SELECT
    CASE WHEN template_id = 'TPL_RISK_NOTICE' THEN 'TPL_RISK_NOTICE' ELSE 'OTHER' END AS template_group,
    COUNT(*) AS sms_count
  FROM read_parquet('synthetic_data/ods/ods_sms_send_log.parquet')
  GROUP BY 1
),
complaint AS (
  SELECT
    CASE WHEN template_id = 'TPL_RISK_NOTICE' THEN 'TPL_RISK_NOTICE' ELSE 'OTHER' END AS template_group,
    COUNT(*) AS complaint_count
  FROM read_parquet('synthetic_data/ods/ods_complaint.parquet')
  GROUP BY 1
)
SELECT
  sms.template_group,
  sms.sms_count,
  COALESCE(complaint.complaint_count, 0) AS complaint_count,
  COALESCE(complaint.complaint_count, 0) * 1.0 / sms.sms_count AS complaint_rate
FROM sms
LEFT JOIN complaint
  ON sms.template_group = complaint.template_group
ORDER BY sms.template_group;
```

- 实际结果：
  - `OTHER`
    - `sms_count`：31828
    - `complaint_count`：127
    - `complaint_rate`：0.3990%
  - `TPL_RISK_NOTICE`
    - `sms_count`：8198
    - `complaint_count`：98
    - `complaint_rate`：1.1954%
- 结论：风险短信模板投诉率约为普通模板 3 倍，埋点有效。

### 5.4 近期减免使用率下降

```sql
WITH case_period AS (
  SELECT
    case_id,
    CASE
      WHEN CAST(case_create_time AS DATE) >= DATE '2026-05-16' - INTERVAL 29 DAY
      THEN 'recent_30d'
      ELSE 'baseline'
    END AS period
  FROM read_parquet('synthetic_data/dim/dim_case.parquet')
),
case_reduction AS (
  SELECT
    c.period,
    c.case_id,
    r.reduction_id,
    r.approval_status,
    r.approved_amount
  FROM case_period c
  LEFT JOIN read_parquet('synthetic_data/ods/ods_reduction_application.parquet') r
    ON c.case_id = r.case_id
)
SELECT
  period,
  COUNT(DISTINCT case_id) AS case_count,
  COUNT(reduction_id) AS reduction_case_count,
  SUM(CASE WHEN approval_status = 'APPROVED' THEN 1 ELSE 0 END) AS approved_count,
  SUM(COALESCE(approved_amount, 0)) AS approved_amount,
  COUNT(reduction_id) * 1.0 / COUNT(DISTINCT case_id) AS reduction_case_rate
FROM case_reduction
GROUP BY period
ORDER BY period;
```

- 实际结果：
  - `baseline`
    - `case_count`：6440
    - `reduction_case_count`：515
    - `approved_count`：348
    - `approved_amount`：217525.58
    - `reduction_case_rate`：7.9969%
  - `recent_30d`
    - `case_count`：3560
    - `reduction_case_count`：106
    - `approved_count`：77
    - `approved_amount`：52534.01
    - `reduction_case_rate`：2.9775%
- 结论：近期减免使用率低于基线，埋点有效。

### 5.5 ADS 归因因子已生成

```sql
SELECT
  factor_code,
  COUNT(DISTINCT stat_date) AS days,
  COUNT(*) AS rows,
  AVG(contribution_pct) AS avg_contribution_pct
FROM read_parquet('synthetic_data/ads/ads_recovery_attribution_di.parquet')
GROUP BY factor_code
ORDER BY factor_code;
```

- 实际结果：
  - `AI_COVERAGE`
    - `days`：30
    - `rows`：30
    - `avg_contribution_pct`：22.0000%
  - `CAPACITY_EAST`
    - `days`：30
    - `rows`：30
    - `avg_contribution_pct`：11.5000%
  - `HIGH_BALANCE_SHARE`
    - `days`：30
    - `rows`：30
    - `avg_contribution_pct`：18.5000%
  - `REDUCTION_PTP`
    - `days`：30
    - `rows`：30
    - `avg_contribution_pct`：25.5000%
  - `SMS_COMPLAINT`
    - `days`：30
    - `rows`：30
    - `avg_contribution_pct`：29.0000%
  - `VENDOR_B_CONNECT`
    - `days`：30
    - `rows`：30
    - `avg_contribution_pct`：15.0000%
- 结论：6 个归因因子均覆盖最近 30 天，ADS 归因样例已生成。

## 6. Validation Results

- `python scripts/generate_synthetic_data.py --months 18 --scale small --seed 20260515`
  - 结果：PASS，退出码 0
  - 输出：`generated dim_tables=10 ods_tables=14 scale=small format=parquet`
  - 输出：`customers=20000 loans=30000 cases=10000 actions=200000`

- `python scripts/build_warehouse.py`
  - 结果：PASS，退出码 0
  - 输出：`built dwd_tables=5 dws_tables=8 ads_tables=6`
  - 观察：运行时出现本机 CPU cache 探测 warning，不影响退出码和产物生成

- `python scripts/validate_data_quality.py`
  - 结果：PASS，退出码 0
  - `DQ-001 DIM 主键唯一`：PASS
  - `DQ-002 外键可关联`：PASS
  - `DQ-003 金额非负`：PASS
  - `DQ-004 日期不穿越`：PASS
  - `DQ-005 P4 隔离`：PASS
  - `DQ-006 比率字段范围`：PASS
  - `DQ-007 case_id 至少关联 loan_id`：PASS
  - `DQ-008 日切表不突降为 0`：PASS
  - `DQ-009 default raw_secure data files absent`：PASS

- `pytest`
  - 结果：PASS，退出码 0
  - 收集用例：19
  - 通过用例：19
  - 失败用例：0

## 7. Known Limitations

- 运行日期非参数化：
  - 当前生成脚本使用 `date.today()` 决定数据结束日。
  - 同一命令在不同日期运行，业务日期范围会变化。
  - 本日志记录的是最大业务日期为 `2026-05-16` 的这次运行。

- 异常埋点验证尚未自动化：
  - 本日志记录了可复跑 SQL 和本次实际结果。
  - 当前 `scripts/validate_data_quality.py` 只覆盖 DQ-001 到 DQ-009，未把上述异常埋点 SQL 纳入自动校验。

- 当前运行环境缺少 `duckdb` Python 模块：
  - `pyproject.toml` 声明了 `duckdb` 依赖，但当前解释器未安装该模块。
  - 本次没有新增依赖，实际结果用 pandas 等价计算。

- 默认不生成 raw_secure：
  - 本次未使用 `--with-raw`。
  - `synthetic_data/raw_secure/` 没有生成明文 P4 文件。
  - P4 明文字段仍只允许存在于 raw_secure 模拟数据中，不进入 DWD、DWS、ADS 或报告。

- 指定脚本会调用元数据同步：
  - `generate_synthetic_data.py` 和 `build_warehouse.py` 会调用 `sync_metadata_and_schemas()`。
  - 若仓库内生成模板与已提交文件存在差异，运行脚本可能产生目标数据以外的同步改动。
  - 本次最终只保留 `docs/data_generation_log.md` 的代码库改动。
