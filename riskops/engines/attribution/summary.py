"""Markdown summary renderer for M3-B attribution."""

from __future__ import annotations


def render_markdown(results: list[dict[str, object]], warnings: list[str]) -> str:
    lines = ["# M1 D7 回收率下降归因摘要", ""]
    if not results:
        lines.extend(["## 1. 结论先行", "", "- 未产出归因结果：输入数据不足或目标异常不存在。", ""])
    else:
        top = results[0]
        lines.extend(
            [
                "## 1. 结论先行",
                "",
                f"- 主因：{top['dimension_name']}={top['dimension_value']}，贡献度 {float(top['contribution_score']):.2%}。",
                f"- 解释：{top['business_interpretation']}",
                "- 归因口径：基于 M1 D7 回款金额 / 到期应还金额，比较最近窗口与基线窗口。",
                "- 注意：贡献度为各维度切片的边际贡献，跨维度可能重叠，不可直接相加为整体下降的解释比例。",
                "",
                "## 2. Top 5 归因因素",
                "",
            ]
        )
        for item in results[:5]:
            lines.extend(
                [
                    f"### {item['contribution_rank']}. {item['dimension_name']}={item['dimension_value']}",
                    f"- 贡献度：{float(item['contribution_score']):.2%}",
                    f"- baseline：{float(item['baseline_value']):.2%}",
                    f"- recent：{float(item['recent_value']):.2%}",
                    f"- 业务解释：{item['business_interpretation']}",
                    f"- 建议动作：{item['recommended_action']}",
                    "",
                ]
            )
        lines.extend(["## 3. 每个因素的数据证据", ""])
        for item in results[:5]:
            lines.append(f"### {item['contribution_rank']}. {item['dimension_name']}={item['dimension_value']}")
            for evidence in item["evidence"]:
                if evidence["method"] == "segment_delta":
                    lines.append(
                        f"- 分组指标：{float(evidence['baseline_value']):.2%} → {float(evidence['recent_value']):.2%}，"
                        f"变化 {float(evidence['delta']):.2%}，recent 权重 {float(evidence['recent_weight']):.2%}。"
                    )
                else:
                    lines.append(
                        f"- {evidence['metric_name_cn']}：{float(evidence['baseline_value']):.2%} → "
                        f"{float(evidence['recent_value']):.2%}，变化 {float(evidence['delta']):.2%}。"
                    )
            lines.append("")
        lines.extend(
            [
                "## 4. 业务解释",
                "",
                "- 本次归因只使用数据拆解结果，不使用 LLM 生成未观测原因。",
                "- 贡献度来自分组回收率变化乘以 recent 窗口权重，过程指标作为证据链，不改变目标指标口径。",
                "",
                "## 5. 建议动作",
                "",
            ]
        )
        for item in results[:5]:
            lines.append(f"- {item['dimension_name']}={item['dimension_value']}：{item['recommended_action']}")
        lines.append("")

    lines.extend(["## 6. 数据局限", ""])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- 未发现字段缺失导致的降级。")
    lines.append("")
    return "\n".join(lines)
