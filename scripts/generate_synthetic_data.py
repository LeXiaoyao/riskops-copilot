"""Generate M1 synthetic DIM and ODS data."""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from riskops.data.m1_spec import sync_metadata_and_schemas


OUTPUT_ROOT = ROOT / "synthetic_data"

SCALE_CONFIG = {
    "small": {"customers": 20_000, "loans": 30_000, "cases": 10_000, "actions": 200_000, "collectors": 420},
    "medium": {"customers": 80_000, "loans": 150_000, "cases": 50_000, "actions": 1_500_000, "collectors": 1_800},
    "large": {"customers": 150_000, "loans": 300_000, "cases": 100_000, "actions": 5_000_000, "collectors": 3_200},
}

PRODUCTS = [
    ("P_CASH", "现金贷", "现金分期", "自营", 0.108, 0.18, 3, 12, True),
    ("P_CONS", "消费分期", "消费金融", "联合贷", 0.092, 0.168, 6, 24, True),
    ("P_MERCH", "场景贷", "场景分期", "助贷", 0.098, 0.19, 3, 18, True),
]
CHANNELS = [
    ("APP", "自有 App", "自营", "RiskOps", True),
    ("ECOM", "电商场景", "场景", "ECom Partner", True),
    ("OFFLINE", "线下门店", "线下", "Offline Partner", False),
]
VENDORS = [
    ("V_A", "供应商 A", "委外", "华北", 120_000, "按回款", "A"),
    ("V_B", "供应商 B", "委外", "华东", 160_000, "按回款", "B"),
    ("V_C", "供应商 C", "委外", "华南", 100_000, "按案件", "A"),
    ("V_AI", "AI 外呼", "AI外呼", "全国", 300_000, "按触达", "A"),
]
LINES = [
    ("L_NORTH_M1", "V_A", "华北 M1", "华北", "M1", "M1", 50_000),
    ("L_EAST_M1", "V_B", "华东 M1", "华东", "M1", "M1", 70_000),
    ("L_EAST_M2", "V_B", "华东 M2", "华东", "M2", "M2", 40_000),
    ("L_SOUTH_M1", "V_C", "华南 M1", "华南", "M1", "M1", 45_000),
    ("L_AI_M1", "V_AI", "AI 外呼 M1", "全国", "AI外呼", "M1", 120_000),
]
STRATEGIES = [
    ("S_ASSIGN_BASE", "分案", "v1.0", "策略运营"),
    ("S_TOUCH_BASE", "触达", "v1.0", "催收运营"),
    ("S_REDUCTION_BASE", "减免", "v1.0", "贷后策略"),
    ("S_PROTECT_BASE", "保护", "v1.0", "合规"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate M1 synthetic RiskOps DIM/ODS data.")
    parser.add_argument("--months", type=int, default=18)
    parser.add_argument("--scale", choices=sorted(SCALE_CONFIG), default="small")
    parser.add_argument("--seed", type=int, default=20260515)
    parser.add_argument("--output-format", choices=["csv", "parquet"], default="parquet")
    parser.add_argument("--with-raw", action="store_true")
    return parser


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_df(df: pd.DataFrame, layer: str, table: str, output_format: str) -> None:
    path = OUTPUT_ROOT / layer
    path.mkdir(parents=True, exist_ok=True)
    target = path / f"{table}.{output_format}"
    if output_format == "csv":
        df.to_csv(target, index=False)
    else:
        df.to_parquet(target, index=False)


def random_dates(rng: np.random.Generator, start: pd.Timestamp, end: pd.Timestamp, size: int) -> pd.Series:
    days = max((end - start).days, 1)
    return pd.Series(start + pd.to_timedelta(rng.integers(0, days + 1, size=size), unit="D"))


def make_static_dims(config: dict[str, int], rng: np.random.Generator, end_date: pd.Timestamp) -> dict[str, pd.DataFrame]:
    product = pd.DataFrame(
        PRODUCTS,
        columns=[
            "product_code",
            "product_name",
            "product_type",
            "funder_type",
            "interest_rate_min",
            "interest_rate_max",
            "term_min",
            "term_max",
            "online_flag",
        ],
    )
    channel = pd.DataFrame(CHANNELS, columns=["channel_code", "channel_name", "channel_type", "partner_name", "online_flag"])
    vendor = pd.DataFrame(
        VENDORS,
        columns=["vendor_id", "vendor_name", "vendor_type", "region", "max_capacity", "settlement_method", "compliance_level"],
    )
    line = pd.DataFrame(
        LINES,
        columns=["line_id", "vendor_id", "line_name", "region", "line_type", "dpd_bucket_scope", "capacity_limit"],
    )
    strategy = pd.DataFrame(
        [
            (sid, typ, ver, end_date.date() - pd.Timedelta(days=540), pd.NaT, owner)
            for sid, typ, ver, owner in STRATEGIES
        ],
        columns=["strategy_id", "strategy_type", "strategy_version", "effective_start_date", "effective_end_date", "owner_team"],
    )

    collector_count = config["collectors"]
    line_choices = rng.choice(line["line_id"].to_numpy(), size=collector_count, p=[0.18, 0.30, 0.16, 0.18, 0.18])
    collector = pd.DataFrame({"collector_id": [f"COL{i:05d}" for i in range(collector_count)], "line_id": line_choices})
    collector = collector.merge(line[["line_id", "vendor_id"]], on="line_id", how="left")
    collector["role_type"] = np.where(collector["line_id"].eq("L_AI_M1"), "AI", "人工")
    collector["entry_date"] = random_dates(rng, end_date - pd.Timedelta(days=900), end_date - pd.Timedelta(days=30), collector_count)
    collector["skill_level"] = rng.choice(["S", "A", "B", "C"], size=collector_count, p=[0.08, 0.38, 0.42, 0.12])
    collector["max_daily_case_capacity"] = np.where(collector["role_type"].eq("AI"), 600, rng.integers(80, 180, collector_count))
    collector["compliance_level"] = rng.choice(["A", "B"], size=collector_count, p=[0.82, 0.18])
    return {
        "dim_product": product,
        "dim_channel": channel,
        "dim_vendor": vendor,
        "dim_collection_line": line,
        "dim_collector": collector,
        "dim_strategy": strategy,
    }


def make_customers(config: dict[str, int], rng: np.random.Generator) -> pd.DataFrame:
    n = config["customers"]
    customer_id = np.array([f"C{i:08d}" for i in range(n)])
    province = rng.choice(["上海", "江苏", "浙江", "广东", "北京", "山东", "四川"], size=n)
    return pd.DataFrame(
        {
            "customer_id": customer_id,
            "customer_id_hash": [stable_hash(x) for x in customer_id],
            "mobile_masked": [f"13{rng.integers(0, 10)}****{rng.integers(0, 10000):04d}" for _ in range(n)],
            "gender": rng.choice(["M", "F"], size=n),
            "age_group": rng.choice(["18-25", "26-35", "36-45", "46-55", "56+"], size=n, p=[0.10, 0.38, 0.30, 0.17, 0.05]),
            "province": province,
            "city": np.where(province == "上海", "上海", np.where(province == "北京", "北京", "省会城市")),
            "occupation_type": rng.choice(["工薪", "个体", "自由职业", "小微业主"], size=n, p=[0.58, 0.18, 0.18, 0.06]),
            "customer_segment": rng.choice(["新客", "复借", "优质", "风险关注"], size=n, p=[0.26, 0.45, 0.20, 0.09]),
            "risk_level_current": rng.choice(["A", "B", "C", "D"], size=n, p=[0.18, 0.42, 0.30, 0.10]),
            "sensitive_flag": rng.random(n) < 0.025,
            "blacklist_flag": rng.random(n) < 0.006,
        }
    )


def make_loans(
    config: dict[str, int],
    customers: pd.DataFrame,
    rng: np.random.Generator,
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
) -> pd.DataFrame:
    n = config["loans"]
    due_dates = random_dates(rng, start_date + pd.Timedelta(days=30), end_date, n)
    amount = rng.lognormal(mean=9.0, sigma=0.72, size=n).clip(1_000, 120_000).round(2)
    loan = pd.DataFrame(
        {
            "loan_id": [f"L{i:08d}" for i in range(n)],
            "customer_id": rng.choice(customers["customer_id"].to_numpy(), size=n),
            "product_code": rng.choice([p[0] for p in PRODUCTS], size=n, p=[0.52, 0.33, 0.15]),
            "channel_code": rng.choice([c[0] for c in CHANNELS], size=n, p=[0.55, 0.30, 0.15]),
            "loan_amount": amount,
            "loan_term": rng.choice([3, 6, 9, 12, 18, 24], size=n, p=[0.12, 0.28, 0.16, 0.26, 0.12, 0.06]),
            "interest_rate": rng.uniform(0.096, 0.19, size=n).round(4),
            "loan_status": rng.choice(["NORMAL", "OVERDUE", "SETTLED"], size=n, p=[0.58, 0.32, 0.10]),
            "first_due_date": due_dates.dt.date,
        }
    )
    loan["disburse_time"] = pd.to_datetime(loan["first_due_date"]) - pd.to_timedelta(rng.integers(30, 540, n), unit="D")
    loan["mob"] = ((end_date - pd.to_datetime(loan["disburse_time"])).dt.days // 30).clip(lower=0)
    loan["vintage_month"] = pd.to_datetime(loan["disburse_time"]).dt.strftime("%Y-%m")
    return loan


def make_cases(config: dict[str, int], loans: pd.DataFrame, rng: np.random.Generator, end_date: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame]:
    n = config["cases"]
    chosen = loans.sample(n=n, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)
    recent_flag = rng.random(n) < 0.36
    case_dates = random_dates(rng, end_date - pd.Timedelta(days=180), end_date - pd.Timedelta(days=31), n)
    case_dates.loc[recent_flag] = random_dates(rng, end_date - pd.Timedelta(days=29), end_date, recent_flag.sum()).to_numpy()
    line_probs = np.array([0.16, 0.33, 0.13, 0.18, 0.20])
    line_ids = rng.choice([x[0] for x in LINES], size=n, p=line_probs)
    line_df = pd.DataFrame(LINES, columns=["line_id", "vendor_id", "line_name", "region", "line_type", "dpd_bucket_scope", "capacity_limit"])
    case = pd.DataFrame(
        {
            "case_id": [f"CASE{i:08d}" for i in range(n)],
            "loan_id": chosen["loan_id"],
            "customer_id": chosen["customer_id"],
            "case_create_time": case_dates,
            "case_type": rng.choice(["M1_COLLECTION", "M2_COLLECTION", "HIGH_RISK"], size=n, p=[0.70, 0.22, 0.08]),
            "initial_dpd_bucket": rng.choice(["M1", "M2", "M3+"], size=n, p=[0.70, 0.22, 0.08]),
            "initial_outstanding_amount": (chosen["loan_amount"].to_numpy() * rng.uniform(0.35, 1.05, n)).round(2),
            "current_line_id": line_ids,
            "protect_flag": rng.random(n) < 0.018,
            "sensitive_flag": rng.random(n) < 0.025,
            "complaint_flag": False,
        }
    ).merge(line_df[["line_id", "vendor_id"]], left_on="current_line_id", right_on="line_id", how="left")
    case = case.drop(columns=["line_id"]).rename(columns={"vendor_id": "current_vendor_id"})
    recent_mask = pd.to_datetime(case["case_create_time"]) >= end_date - pd.Timedelta(days=29)
    high_recent = recent_mask & (rng.random(n) < 0.34)
    high_base = (~recent_mask) & (rng.random(n) < 0.26)
    case["balance_segment"] = np.where(high_recent | high_base | (case["initial_outstanding_amount"] >= 35_000), "HIGH", "NORMAL")
    mapping = pd.DataFrame(
        {
            "mapping_id": [f"MAP{i:08d}" for i in range(n)],
            "case_id": case["case_id"],
            "loan_id": case["loan_id"],
            "customer_id": case["customer_id"],
            "mapping_start_date": pd.to_datetime(case["case_create_time"]).dt.date,
            "mapping_end_date": pd.NaT,
            "main_loan_flag": True,
        }
    )
    return case.drop(columns=["loan_id"]), mapping


def make_repayment(loans: pd.DataFrame, mapping: pd.DataFrame, cases: pd.DataFrame, rng: np.random.Generator, end_date: pd.Timestamp) -> dict[str, pd.DataFrame]:
    n = len(loans)
    plan = pd.DataFrame(
        {
            "plan_id": [f"PLAN{i:08d}" for i in range(n)],
            "loan_id": loans["loan_id"],
            "customer_id": loans["customer_id"],
            "period_no": 1,
            "due_date": loans["first_due_date"],
            "due_principal": (loans["loan_amount"] * rng.uniform(0.06, 0.16, n)).round(2),
        }
    )
    plan["due_interest"] = (plan["due_principal"] * rng.uniform(0.006, 0.018, n)).round(2)
    plan["due_fee"] = (plan["due_principal"] * rng.uniform(0.0, 0.004, n)).round(2)
    plan["due_amount"] = (plan["due_principal"] + plan["due_interest"] + plan["due_fee"]).round(2)
    plan["plan_status"] = "DUE"

    case_map = mapping.merge(cases[["case_id", "initial_dpd_bucket", "case_create_time"]], on="case_id", how="left")
    plan = plan.merge(case_map[["loan_id", "initial_dpd_bucket", "case_create_time"]], on="loan_id", how="left")
    due_ts = pd.to_datetime(plan["due_date"])
    recent = due_ts >= end_date - pd.Timedelta(days=29)
    m1 = plan["initial_dpd_bucket"].fillna("M1").eq("M1")
    prob = np.where(m1 & recent, 0.20, np.where(m1, 0.186, 0.27))
    prob = np.where(plan["initial_dpd_bucket"].isna(), 0.30, prob)
    paid = rng.random(len(plan)) < prob
    repay = plan.loc[paid, ["plan_id", "loan_id", "customer_id", "due_date", "due_amount"]].copy().reset_index(drop=True)
    repay["repay_id"] = [f"RP{i:08d}" for i in range(len(repay))]
    repay["repay_time"] = pd.to_datetime(repay["due_date"]) + pd.to_timedelta(rng.integers(0, 8, len(repay)), unit="D")
    repay["repay_amount"] = (repay["due_amount"] * rng.uniform(0.92, 1.0, len(repay))).round(2)
    repay["repay_channel"] = rng.choice(["APP", "BANK", "WITHHOLD"], size=len(repay), p=[0.56, 0.22, 0.22])
    repay["repay_status"] = "SUCCESS"
    repay = repay[["repay_id", "plan_id", "loan_id", "customer_id", "repay_time", "repay_amount", "repay_channel", "repay_status"]]
    plan = plan.drop(columns=["initial_dpd_bucket", "case_create_time"])
    return {"ods_repayment_plan": plan, "ods_repayment_detail": repay}


def make_actions(
    config: dict[str, int],
    cases: pd.DataFrame,
    collectors: pd.DataFrame,
    rng: np.random.Generator,
    end_date: pd.Timestamp,
) -> dict[str, pd.DataFrame]:
    n = config["actions"]
    sampled = cases.sample(n=n, replace=True, random_state=int(rng.integers(0, 1_000_000))).reset_index(drop=True)
    action_dates = random_dates(rng, end_date - pd.Timedelta(days=180), end_date, n)
    recent = action_dates >= end_date - pd.Timedelta(days=29)
    collector_by_line = {k: v["collector_id"].to_numpy() for k, v in collectors.groupby("line_id")}
    collector_ids = [rng.choice(collector_by_line[line_id]) for line_id in sampled["current_line_id"]]

    ai_share = np.where(recent, 0.18, 0.30)
    sms_share = 0.20
    draw = rng.random(n)
    action_type = np.where(draw < ai_share, "AI_OUTBOUND", np.where(draw < ai_share + sms_share, "SMS", "CALL"))
    vendor_b_recent = sampled["current_vendor_id"].eq("V_B").to_numpy() & recent.to_numpy()
    connect_prob = np.where(vendor_b_recent, 0.28, np.where(sampled["current_vendor_id"].eq("V_B").to_numpy(), 0.34, 0.36))
    connected = rng.random(n) < connect_prob
    ptp_prob = np.where(recent, 0.17, 0.22)
    ptp = connected & (rng.random(n) < ptp_prob)
    fulfilled = ptp & (rng.random(n) < np.where(recent, 0.44, 0.51))
    template = np.where(action_type == "SMS", rng.choice(["TPL_NORMAL", "TPL_RISK_NOTICE", "TPL_REMIND"], size=n, p=[0.55, 0.20, 0.25]), None)

    action = pd.DataFrame(
        {
            "action_id": [f"ACT{i:09d}" for i in range(n)],
            "case_id": sampled["case_id"],
            "customer_id": sampled["customer_id"],
            "vendor_id": sampled["current_vendor_id"],
            "line_id": sampled["current_line_id"],
            "collector_id": collector_ids,
            "action_time": action_dates + pd.to_timedelta(rng.integers(8, 21, n), unit="h"),
            "action_type": action_type,
            "template_id": template,
            "connected_flag": connected,
            "ptp_flag": ptp,
            "ptp_fulfilled_flag": fulfilled,
            "ai_outbound_flag": action_type == "AI_OUTBOUND",
        }
    )
    call_actions = action[action["action_type"].isin(["CALL", "AI_OUTBOUND"])].sample(
        n=min(len(action[action["action_type"].isin(["CALL", "AI_OUTBOUND"])]), max(1, n // 3)),
        random_state=int(rng.integers(0, 1_000_000)),
    )
    call_record = pd.DataFrame(
        {
            "call_id": [f"CALL{i:08d}" for i in range(len(call_actions))],
            "action_id": call_actions["action_id"].to_numpy(),
            "case_id": call_actions["case_id"].to_numpy(),
            "call_start_time": call_actions["action_time"].to_numpy(),
            "duration_seconds": rng.integers(0, 360, len(call_actions)),
            "recording_uri": [f"recording://synthetic/{i:08d}" for i in range(len(call_actions))],
            "transcript_masked": "已脱敏通话摘要",
        }
    )
    sms = action[action["action_type"].eq("SMS")].copy().reset_index(drop=True)
    sms_log = pd.DataFrame(
        {
            "message_id": [f"MSG{i:08d}" for i in range(len(sms))],
            "action_id": sms["action_id"],
            "case_id": sms["case_id"],
            "customer_id": sms["customer_id"],
            "template_id": sms["template_id"],
            "send_time": sms["action_time"],
            "send_status": rng.choice(["SUCCESS", "FAILED"], size=len(sms), p=[0.985, 0.015]),
        }
    )
    return {"ods_collection_action": action, "ods_call_record": call_record, "ods_sms_send_log": sms_log}


def make_other_ods(
    cases: pd.DataFrame,
    customers: pd.DataFrame,
    actions: pd.DataFrame,
    sms_log: pd.DataFrame,
    rng: np.random.Generator,
    end_date: pd.Timestamp,
) -> dict[str, pd.DataFrame]:
    case_count = len(cases)
    flow = pd.DataFrame(
        {
            "flow_id": [f"FLOW{i:08d}" for i in range(case_count)],
            "case_id": cases["case_id"],
            "from_status": "NEW",
            "to_status": "ASSIGNED",
            "flow_time": pd.to_datetime(cases["case_create_time"]) + pd.to_timedelta(1, unit="h"),
            "strategy_id": "S_ASSIGN_BASE",
        }
    )
    collectors_by_line = actions.groupby("case_id")["collector_id"].first()
    decision = cases[["case_id", "customer_id", "current_vendor_id", "current_line_id", "case_create_time"]].copy()
    decision["decision_id"] = [f"DEC{i:08d}" for i in range(case_count)]
    decision["collector_id"] = decision["case_id"].map(collectors_by_line).fillna(actions["collector_id"].iloc[0])
    decision["strategy_id"] = "S_ASSIGN_BASE"
    decision["decision_time"] = pd.to_datetime(decision["case_create_time"])
    decision["decision_reason"] = "synthetic_m1_assignment"
    decision = decision.rename(columns={"current_vendor_id": "vendor_id", "current_line_id": "line_id"})
    decision = decision[["decision_id", "case_id", "customer_id", "vendor_id", "line_id", "collector_id", "strategy_id", "decision_time", "decision_reason"]]

    score_n = min(len(customers), max(5_000, len(customers) // 2))
    score_customers = customers.sample(n=score_n, random_state=int(rng.integers(0, 1_000_000)))
    score = pd.DataFrame(
        {
            "score_id": [f"SCORE{i:08d}" for i in range(score_n)],
            "customer_id": score_customers["customer_id"].to_numpy(),
            "score_date": (end_date - pd.to_timedelta(rng.integers(0, 180, score_n), unit="D")).date,
            "postloan_c_score": rng.normal(620, 70, score_n).clip(300, 850).round(1),
        }
    )
    score["score_level"] = pd.cut(score["postloan_c_score"], bins=[0, 560, 640, 720, 900], labels=["D", "C", "B", "A"]).astype(str)

    note_actions = actions.sample(n=min(len(actions), max(10_000, len(actions) // 5)), random_state=int(rng.integers(0, 1_000_000)))
    note = pd.DataFrame(
        {
            "note_id": [f"NOTE{i:08d}" for i in range(len(note_actions))],
            "case_id": note_actions["case_id"].to_numpy(),
            "collector_id": note_actions["collector_id"].to_numpy(),
            "note_time": note_actions["action_time"].to_numpy(),
            "note_type": rng.choice(["CONTACT", "PTP", "NO_ANSWER"], size=len(note_actions), p=[0.42, 0.18, 0.40]),
            "note_text_masked": "已脱敏催记内容",
        }
    )

    recent_cases = pd.to_datetime(cases["case_create_time"]) >= end_date - pd.Timedelta(days=29)
    base_cases = cases.loc[~recent_cases]
    current_cases = cases.loc[recent_cases]
    base_n = int(len(base_cases) * 0.08)
    recent_n = int(len(current_cases) * 0.03)
    reduction_cases = pd.concat(
        [
            base_cases.sample(n=max(1, base_n), random_state=int(rng.integers(0, 1_000_000))),
            current_cases.sample(n=max(1, recent_n), random_state=int(rng.integers(0, 1_000_000))),
        ],
        ignore_index=True,
    )
    reduction = pd.DataFrame(
        {
            "reduction_id": [f"RED{i:08d}" for i in range(len(reduction_cases))],
            "case_id": reduction_cases["case_id"],
            "customer_id": reduction_cases["customer_id"],
            "apply_time": pd.to_datetime(reduction_cases["case_create_time"]) + pd.to_timedelta(rng.integers(1, 20, len(reduction_cases)), unit="D"),
            "apply_amount": (reduction_cases["initial_outstanding_amount"] * rng.uniform(0.04, 0.18, len(reduction_cases))).round(2),
            "approval_status": rng.choice(["APPROVED", "REJECTED"], size=len(reduction_cases), p=[0.72, 0.28]),
        }
    )
    reduction["approved_amount"] = np.where(reduction["approval_status"].eq("APPROVED"), reduction["apply_amount"] * rng.uniform(0.55, 1.0, len(reduction)), 0).round(2)

    risk_sms = sms_log[sms_log["template_id"].eq("TPL_RISK_NOTICE")]
    normal_sms = sms_log[~sms_log["template_id"].eq("TPL_RISK_NOTICE")]
    risk_n = max(1, int(len(risk_sms) * 0.012))
    normal_n = max(1, int(len(normal_sms) * 0.004))
    complaint_source = pd.concat(
        [
            risk_sms.sample(n=min(len(risk_sms), risk_n), random_state=int(rng.integers(0, 1_000_000))),
            normal_sms.sample(n=min(len(normal_sms), normal_n), random_state=int(rng.integers(0, 1_000_000))),
        ],
        ignore_index=True,
    ).merge(actions[["action_id", "vendor_id", "collector_id"]], on="action_id", how="left")
    complaint = pd.DataFrame(
        {
            "complaint_id": [f"CMP{i:08d}" for i in range(len(complaint_source))],
            "case_id": complaint_source["case_id"],
            "customer_id": complaint_source["customer_id"],
            "vendor_id": complaint_source["vendor_id"],
            "collector_id": complaint_source["collector_id"],
            "template_id": complaint_source["template_id"],
            "complaint_time": pd.to_datetime(complaint_source["send_time"]) + pd.to_timedelta(rng.integers(1, 72, len(complaint_source)), unit="h"),
            "complaint_type": "短信话术",
            "complaint_level": rng.choice(["LOW", "MEDIUM", "HIGH"], size=len(complaint_source), p=[0.70, 0.25, 0.05]),
        }
    )
    return {
        "ods_case_flow": flow,
        "ods_assignment_decision_log": decision,
        "ods_postloan_c_score": score,
        "ods_collection_note": note,
        "ods_reduction_application": reduction,
        "ods_complaint": complaint,
    }


def make_snapshots(
    loans: pd.DataFrame,
    cases: pd.DataFrame,
    mapping: pd.DataFrame,
    collectors: pd.DataFrame,
    rng: np.random.Generator,
    end_date: pd.Timestamp,
) -> dict[str, pd.DataFrame]:
    dates = pd.date_range(end_date - pd.Timedelta(days=59), end_date, freq="D")
    loan_frames = []
    case_frames = []
    customer_frames = []
    collector_by_line = {k: v["collector_id"].to_numpy() for k, v in collectors.groupby("line_id")}
    for stat_date in dates:
        loan_sample = loans.sample(n=min(len(loans), 4_000), random_state=int(rng.integers(0, 1_000_000))).copy()
        loan_sample["stat_date"] = stat_date.date()
        loan_sample["dpd"] = (stat_date - pd.to_datetime(loan_sample["first_due_date"])).dt.days.clip(lower=0)
        loan_sample["dpd_bucket"] = pd.cut(loan_sample["dpd"], bins=[-1, 0, 30, 60, 9999], labels=["CURRENT", "M1", "M2", "M3+"]).astype(str)
        loan_sample["outstanding_amount"] = (loan_sample["loan_amount"] * rng.uniform(0.25, 0.95, len(loan_sample))).round(2)
        loan_frames.append(loan_sample[["stat_date", "loan_id", "customer_id", "dpd", "dpd_bucket", "outstanding_amount", "loan_status"]])

        active = cases[pd.to_datetime(cases["case_create_time"]).dt.date <= stat_date.date()].copy()
        if len(active) > 0:
            active["stat_date"] = stat_date.date()
            active["vendor_id"] = active["current_vendor_id"]
            active["line_id"] = active["current_line_id"]
            active["collector_id"] = [rng.choice(collector_by_line[line_id]) for line_id in active["line_id"]]
            active["case_status"] = "ASSIGNED"
            active["dpd_bucket"] = active["initial_dpd_bucket"]
            active["outstanding_amount"] = active["initial_outstanding_amount"]
            case_frames.append(active[["stat_date", "case_id", "customer_id", "vendor_id", "line_id", "collector_id", "case_status", "dpd_bucket", "outstanding_amount"]])

            cust = (
                active.groupby("customer_id")
                .agg(active_case_count=("case_id", "nunique"), total_outstanding_amount=("initial_outstanding_amount", "sum"))
                .reset_index()
            )
            cust["stat_date"] = stat_date.date()
            cust["active_loan_count"] = cust["customer_id"].map(mapping.groupby("customer_id")["loan_id"].nunique()).fillna(1).astype(int)
            cust["max_dpd"] = rng.integers(1, 90, len(cust))
            cust["risk_level"] = rng.choice(["A", "B", "C", "D"], size=len(cust), p=[0.15, 0.38, 0.35, 0.12])
            customer_frames.append(cust[["stat_date", "customer_id", "active_loan_count", "active_case_count", "total_outstanding_amount", "max_dpd", "risk_level"]])
    return {
        "ods_loan_daily_snapshot": pd.concat(loan_frames, ignore_index=True),
        "ods_case_daily_snapshot": pd.concat(case_frames, ignore_index=True),
        "ods_customer_daily_snapshot": pd.concat(customer_frames, ignore_index=True),
    }


def write_raw_secure(customers: pd.DataFrame, rng: np.random.Generator, output_format: str) -> None:
    raw = pd.DataFrame(
        {
            "customer_id": customers["customer_id"],
            "customer_name": [f"测试客户{i:08d}" for i in range(len(customers))],
            "id_no": [f"110101{rng.integers(19600101, 20060101)}{rng.integers(1000, 9999)}" for _ in range(len(customers))],
            "mobile_no": [f"13{rng.integers(0, 10)}{rng.integers(0, 100000000):08d}" for _ in range(len(customers))],
            "bank_card_no": [f"6222{rng.integers(0, 10**15):015d}" for _ in range(len(customers))],
            "address": [f"合成地址{i:08d}号" for i in range(len(customers))],
        }
    )
    write_df(raw, "raw_secure", "raw_customer_pii", output_format)


def main() -> int:
    args = build_parser().parse_args()
    sync_metadata_and_schemas()
    config = SCALE_CONFIG[args.scale]
    rng = np.random.default_rng(args.seed)
    end_date = pd.Timestamp(date.today())
    start_date = end_date - pd.DateOffset(months=args.months)

    dims = make_static_dims(config, rng, end_date)
    customers = make_customers(config, rng)
    loans = make_loans(config, customers, rng, start_date, end_date)
    cases, mapping = make_cases(config, loans, rng, end_date)
    repayment = make_repayment(loans, mapping, cases, rng, end_date)
    actions = make_actions(config, cases, dims["dim_collector"], rng, end_date)
    other_ods = make_other_ods(cases, customers, actions["ods_collection_action"], actions["ods_sms_send_log"], rng, end_date)
    snapshots = make_snapshots(loans, cases, mapping, dims["dim_collector"], rng, end_date)
    cases.loc[cases["case_id"].isin(other_ods["ods_complaint"]["case_id"]), "complaint_flag"] = True

    dim_tables = {
        **dims,
        "dim_customer": customers,
        "dim_loan": loans,
        "dim_case": cases,
        "dim_case_loan_mapping": mapping,
    }
    ods_tables = {**repayment, **snapshots, **actions, **other_ods}

    for table, df in dim_tables.items():
        write_df(df, "dim", table, args.output_format)
    for table, df in ods_tables.items():
        write_df(df, "ods", table, args.output_format)
    if args.with_raw:
        write_raw_secure(customers, rng, args.output_format)

    print(f"generated dim_tables={len(dim_tables)} ods_tables={len(ods_tables)} scale={args.scale} format={args.output_format}")
    print(f"customers={len(customers)} loans={len(loans)} cases={len(cases)} actions={len(actions['ods_collection_action'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
