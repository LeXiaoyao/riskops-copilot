"""Render M1 metadata documents."""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render metadata-driven docs.")
    parser.add_argument("target", choices=["all", "data_dict", "privacy", "keys", "lineage", "metrics", "metric_lineage"])
    return parser


def load_yaml(name: str) -> Any:
    return yaml.safe_load((ROOT / "metadata" / name).read_text(encoding="utf-8"))


def write_doc(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def render_data_dict() -> None:
    tables = load_yaml("tables.yaml")
    columns = load_yaml("columns.yaml")
    by_table: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for col in columns:
        by_table[col["table_name"]].append(col)

    lines = ["# 数据字典", "", "> 由 `metadata/tables.yaml` 和 `metadata/columns.yaml` 自动渲染。", ""]
    for layer in ["DIM", "ODS", "DWD", "DWS", "ADS"]:
        lines.extend([f"## {layer} 层", ""])
        for table in [t for t in tables if t["layer"] == layer]:
            lines.extend(
                [
                    f"### {table['table_name']}",
                    f"- 中文名：{table['table_name_cn']}",
                    f"- 主题域：{table['domain']}",
                    f"- 粒度：{table['grain']}",
                    f"- 主键：{table['primary_key']}",
                    f"- 说明：{table['description']}",
                    "- 字段：",
                ]
            )
            for col in by_table[table["table_name"]]:
                nullable = "可空" if col["nullable"] else "非空"
                pk = "，主键" if col["is_primary_key"] else ""
                lines.append(
                    f"  - `{col['column_name']}`：{col['column_name_cn']}，{col['data_type']}，{nullable}{pk}，隐私 {col['privacy_level']}"
                )
            lines.append("")
    write_doc(DOCS / "data_dictionary.md", "\n".join(lines))


def render_privacy() -> None:
    policy = load_yaml("privacy_policy.yaml")
    lines = ["# 隐私分级策略", "", "> 由 `metadata/privacy_policy.yaml` 自动渲染。", ""]
    for level in policy["levels"]:
        lines.extend(
            [
                f"## {level['level']} · {level['name']}",
                f"- DWD/DWS/ADS：{'允许' if level['warehouse_allowed'] else '禁止'}",
                f"- 报告：{'允许' if level['report_allowed'] else '禁止'}",
                f"- LLM 上下文：{'允许' if level['llm_allowed'] else '禁止'}",
                f"- 示例字段：{', '.join(level['examples'])}",
                "",
            ]
        )
    lines.append("## 强制规则")
    for rule in policy["rules"]:
        lines.append(f"- {rule}")
    write_doc(DOCS / "privacy_policy.md", "\n".join(lines))


def render_keys() -> None:
    relationships = load_yaml("key_relationships.yaml")["relationships"]
    lines = ["# 主键关系", "", "> 由 `metadata/key_relationships.yaml` 自动渲染。", ""]
    for item in relationships:
        via = f"，经 `{item['via']}`" if item.get("via") else ""
        lines.append(f"- `{item['from']}` → `{item['to']}`：{item['cardinality']}{via}")
    write_doc(DOCS / "key_relationships.md", "\n".join(lines))


def render_lineage() -> None:
    lineage = load_yaml("metric_lineage.yaml")
    lines = [
        "# 数据血缘",
        "",
        "> M1 仅记录血缘占位，不实现 M2 指标计算引擎。",
        "",
        f"- 阶段：{lineage['phase']}",
        f"- 范围：{lineage['scope']}",
        "",
    ]
    for metric in lineage["metrics"]:
        lines.extend(
            [
                f"## {metric['metric_code']}",
                f"- 中文名：{metric['metric_name_cn']}",
                f"- ADS：{metric['ads_table']}",
                f"- DWS：{', '.join(metric['dws_tables'])}",
                f"- DWD：{', '.join(metric['dwd_tables'])}",
                f"- ODS：{', '.join(metric['ods_tables'])}",
                "",
            ]
        )
    write_doc(DOCS / "data_lineage.md", "\n".join(lines))


def render_metrics() -> None:
    metrics = load_yaml("metric_dictionary.yaml")
    by_domain: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in metrics:
        by_domain[item["business_domain"]].append(item)

    lines = ["# 指标字典", "", "> 由 `metadata/metric_dictionary.yaml` 自动渲染。", ""]
    for domain in ["postloan", "collection", "compliance", "roi"]:
        if domain not in by_domain:
            continue
        lines.extend([f"## {domain}", ""])
        for metric in by_domain[domain]:
            lines.extend(
                [
                    f"### {metric['metric_code']}",
                    f"- 中文名：{metric['metric_name_cn']}",
                    f"- 类型：{metric['metric_type']}",
                    f"- 分子：{metric['numerator']}",
                    f"- 分母：{metric['denominator']}",
                    f"- 公式：`{metric['formula']}`",
                    f"- 粒度：{', '.join(metric['grain'])}",
                    f"- 来源表：{', '.join(metric['source_tables'])}",
                    f"- 过滤条件：`{metric['filter_condition']}`",
                    f"- Owner：{metric['owner']}",
                    f"- 刷新频率：{metric['refresh_frequency']}",
                    f"- 版本：{metric['version']}",
                    f"- 优先级：{metric['priority']}",
                    f"- 说明：{metric['notes']}",
                    "- 变更记录：",
                ]
            )
            for change in metric["change_log"]:
                lines.append(f"  - {change['date']}：{change['change']}")
            lines.append("")
    write_doc(DOCS / "metric_dictionary.md", "\n".join(lines))


def render_metric_lineage() -> None:
    lineage = load_yaml("metric_lineage.yaml")
    lines = [
        "# 指标血缘",
        "",
        "> 由 `metadata/metric_lineage.yaml` 自动渲染。",
        "",
        f"- 阶段：{lineage['phase']}",
        f"- 范围：{lineage['scope']}",
        "",
    ]
    for metric in lineage["metrics"]:
        lines.extend(
            [
                f"## {metric['metric_code']}",
                f"- 中文名：{metric['metric_name_cn']}",
                f"- ADS：{metric['ads_table']}",
                f"- DWS：{', '.join(metric['dws_tables']) if metric['dws_tables'] else '无'}",
                f"- DWD：{', '.join(metric['dwd_tables']) if metric['dwd_tables'] else '无'}",
                f"- ODS：{', '.join(metric['ods_tables']) if metric['ods_tables'] else '无'}",
                "",
            ]
        )
    write_doc(DOCS / "metric_lineage.md", "\n".join(lines))


def main() -> int:
    args = build_parser().parse_args()
    renderers = {
        "data_dict": render_data_dict,
        "privacy": render_privacy,
        "keys": render_keys,
        "lineage": render_lineage,
        "metrics": render_metrics,
        "metric_lineage": render_metric_lineage,
    }
    if args.target == "all":
        for renderer in renderers.values():
            renderer()
    else:
        renderers[args.target]()
        if args.target == "data_dict":
            render_lineage()
    print(f"rendered target={args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
