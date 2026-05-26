"""Tests for llm_scorer — all LLM calls are mocked, no network required."""

from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from riskops.engines.qc.llm_scorer import (
    DIMENSIONS,
    _fallback_score,
    merge_with_keyword_scan,
    score_with_llm,
)


# ---------------------------------------------------------------------------
# _fallback_score
# ---------------------------------------------------------------------------


def test_fallback_score_has_all_dimensions() -> None:
    result = _fallback_score()
    dims = result["dimensions"]
    dim_names = [name for name, _ in DIMENSIONS]
    assert set(dims.keys()) == set(dim_names)


def test_fallback_score_all_seventy() -> None:
    result = _fallback_score()
    assert all(v == 70 for v in result["dimensions"].values())


def test_fallback_score_flagged() -> None:
    result = _fallback_score()
    assert result["_fallback"] is True
    assert result["supervisor_review_required"] is False


# ---------------------------------------------------------------------------
# merge_with_keyword_scan
# ---------------------------------------------------------------------------

_BASE_LLM = {
    "dimensions": {name: 85 for name, _ in DIMENSIONS},
    "overall_compliance_score": 85,
    "supervisor_review_required": False,
    "suggested_alternative": None,
    "risk_summary": "无明显风险",
}


def test_merge_clean_keyword_preserves_llm_scores() -> None:
    keyword_result = {"violation_count": 0, "violations": [], "risk_level": "clean"}
    merged = merge_with_keyword_scan(dict(_BASE_LLM), keyword_result)

    assert merged["overall_compliance_score"] == 85
    assert merged["dimensions"]["合规红线"] == 85
    assert merged["keyword_risk_level"] == "clean"


def test_merge_one_violation_lowers_red_line() -> None:
    keyword_result = {
        "violation_count": 1,
        "violations": [{"category": "威胁恐吓", "keyword": "起诉你", "position": 0}],
        "risk_level": "medium",
    }
    merged = merge_with_keyword_scan(dict(_BASE_LLM), keyword_result)

    # 1 violation → red_line_score = max(0, 20 - 1*10) = 10
    assert merged["dimensions"]["合规红线"] == 10
    # 投诉风险 上调到 max(85, 60+10) — LLM score of 85 is already higher
    assert merged["dimensions"]["投诉风险"] >= 70
    assert merged["supervisor_review_required"] is True


def test_merge_two_violations_red_line_zero() -> None:
    keyword_result = {
        "violation_count": 2,
        "violations": [],
        "risk_level": "medium",
    }
    merged = merge_with_keyword_scan(dict(_BASE_LLM), keyword_result)

    # 2 violations → red_line_score = max(0, 20 - 2*10) = 0
    assert merged["dimensions"]["合规红线"] == 0


def test_merge_high_keyword_caps_overall_score() -> None:
    keyword_result = {"violation_count": 3, "violations": [], "risk_level": "high"}
    merged = merge_with_keyword_scan(dict(_BASE_LLM), keyword_result)

    assert merged["overall_compliance_score"] <= 30


def test_merge_medium_keyword_caps_overall_at_65() -> None:
    keyword_result = {"violation_count": 1, "violations": [], "risk_level": "medium"}
    merged = merge_with_keyword_scan(dict(_BASE_LLM), keyword_result)

    assert merged["overall_compliance_score"] <= 65


def test_merge_propagates_keyword_violations_list() -> None:
    violations = [{"category": "威胁恐吓", "keyword": "起诉你", "position": 5}]
    keyword_result = {"violation_count": 1, "violations": violations, "risk_level": "medium"}
    merged = merge_with_keyword_scan(dict(_BASE_LLM), keyword_result)

    assert merged["keyword_violations"] == violations


# ---------------------------------------------------------------------------
# score_with_llm — mocked HTTP
# ---------------------------------------------------------------------------

_VALID_LLM_RESPONSE = {
    "choices": [
        {
            "message": {
                "content": json.dumps(
                    {
                        "dimensions": {name: 80 for name, _ in DIMENSIONS},
                        "overall_compliance_score": 80,
                        "supervisor_review_required": False,
                        "suggested_alternative": None,
                        "risk_summary": "合规",
                    }
                )
            }
        }
    ]
}


def _make_mock_response(payload: dict) -> MagicMock:
    body = json.dumps(payload).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_score_with_llm_parses_valid_response() -> None:
    with patch("urllib.request.urlopen", return_value=_make_mock_response(_VALID_LLM_RESPONSE)):
        result = score_with_llm("请按时还款。", api_key="sk-fake")

    assert result["overall_compliance_score"] == 80
    assert result.get("_fallback") is None or result.get("_fallback") is False


def test_score_with_llm_strips_markdown_code_block() -> None:
    inner = json.dumps(
        {
            "dimensions": {name: 75 for name, _ in DIMENSIONS},
            "overall_compliance_score": 75,
            "supervisor_review_required": False,
            "suggested_alternative": None,
            "risk_summary": "ok",
        }
    )
    wrapped = f"```json\n{inner}\n```"
    payload = {"choices": [{"message": {"content": wrapped}}]}

    with patch("urllib.request.urlopen", return_value=_make_mock_response(payload)):
        result = score_with_llm("请按时还款。", api_key="sk-fake")

    assert result["overall_compliance_score"] == 75


def test_score_with_llm_falls_back_on_network_error() -> None:
    import urllib.error

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("timeout")):
        result = score_with_llm("测试文本。", api_key="sk-fake")

    assert result["_fallback"] is True
    assert result["overall_compliance_score"] == 70


def test_score_with_llm_falls_back_on_bad_json() -> None:
    bad_payload = {"choices": [{"message": {"content": "not json {"}}]}
    with patch("urllib.request.urlopen", return_value=_make_mock_response(bad_payload)):
        result = score_with_llm("测试文本。", api_key="sk-fake")

    assert result["_fallback"] is True


# ---------------------------------------------------------------------------
# scan_text_with_llm integration (mocked at llm_scorer level)
# ---------------------------------------------------------------------------


def test_scan_text_with_llm_merges_keyword_result() -> None:
    from riskops.engines.qc.compliance_scanner import scan_text_with_llm

    with patch(
        "riskops.engines.qc.llm_scorer.score_with_llm",
        return_value={
            "dimensions": {name: 85 for name, _ in DIMENSIONS},
            "overall_compliance_score": 85,
            "supervisor_review_required": False,
            "suggested_alternative": None,
            "risk_summary": "合规",
        },
    ):
        result = scan_text_with_llm("我是法院，起诉你。", api_key="sk-fake")

    # keyword scan should find violations → red-line must be forced down
    assert result["dimensions"]["合规红线"] < 85
    assert result["supervisor_review_required"] is True
    assert len(result["keyword_violations"]) >= 2


def test_scan_text_with_llm_clean_text_preserves_scores() -> None:
    from riskops.engines.qc.compliance_scanner import scan_text_with_llm

    with patch(
        "riskops.engines.qc.llm_scorer.score_with_llm",
        return_value={
            "dimensions": {name: 90 for name, _ in DIMENSIONS},
            "overall_compliance_score": 90,
            "supervisor_review_required": False,
            "suggested_alternative": None,
            "risk_summary": "无风险",
        },
    ):
        result = scan_text_with_llm("您好，请问您方便还款吗？", api_key="sk-fake")

    assert result["overall_compliance_score"] == 90
    assert result["keyword_risk_level"] == "clean"
    assert result["keyword_violations"] == []
