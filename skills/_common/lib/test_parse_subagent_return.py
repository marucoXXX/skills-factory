"""parse_subagent_return の挙動テスト。

実行: ``python -m pytest skills/_common/lib/test_parse_subagent_return.py``
"""

from __future__ import annotations

import json

import pytest

from skills._common.lib.parse_subagent_return import parse_subagent_return


CLEAN = '{"topic_id":"data_04_market_environment","data":{"value":1.45,"unit":"兆円"}}'


def test_clean_json_passes_through() -> None:
    parsed = parse_subagent_return(CLEAN)
    assert parsed["topic_id"] == "data_04_market_environment"
    assert parsed["data"]["value"] == 1.45


def test_strips_leading_prose() -> None:
    raw = (
        "Based on my comprehensive web research, I have gathered the "
        "following data:\n\n" + CLEAN
    )
    assert parse_subagent_return(raw) == json.loads(CLEAN)


def test_strips_markdown_code_fence_with_json_lang() -> None:
    raw = "```json\n" + CLEAN + "\n```"
    assert parse_subagent_return(raw) == json.loads(CLEAN)


def test_strips_markdown_code_fence_without_lang() -> None:
    raw = "```\n" + CLEAN + "\n```"
    assert parse_subagent_return(raw) == json.loads(CLEAN)


def test_strips_trailing_sources_section() -> None:
    raw = CLEAN + "\n\nSources:\n- https://example.com/a\n- https://example.com/b"
    assert parse_subagent_return(raw) == json.loads(CLEAN)


def test_double_json_returns_first_object() -> None:
    second = '{"topic_id":"data_05_other","data":{}}'
    raw = CLEAN + "\n\n" + second
    parsed = parse_subagent_return(raw)
    assert parsed["topic_id"] == "data_04_market_environment"


def test_handles_braces_inside_string_literals() -> None:
    raw = '{"note":"contains } brace and { brace inside","value":1}'
    parsed = parse_subagent_return(raw)
    assert parsed["note"] == "contains } brace and { brace inside"
    assert parsed["value"] == 1


def test_handles_escaped_quote_inside_string() -> None:
    raw = '{"quote":"he said \\"hi\\"","ok":true}'
    parsed = parse_subagent_return(raw)
    assert parsed["quote"] == 'he said "hi"'
    assert parsed["ok"] is True


def test_combined_prose_fence_and_trailing_sources() -> None:
    raw = (
        "Sure! Here is the data:\n\n```json\n"
        + CLEAN
        + "\n```\n\nSources:\n- https://example.com"
    )
    assert parse_subagent_return(raw) == json.loads(CLEAN)


def test_raises_on_no_json_object() -> None:
    with pytest.raises(ValueError) as excinfo:
        parse_subagent_return("no json here, just prose and a stray ] bracket")
    assert "subagent return value" in str(excinfo.value)


def test_raises_on_non_string_input() -> None:
    with pytest.raises(TypeError):
        parse_subagent_return({"already": "dict"})  # type: ignore[arg-type]


def test_error_message_includes_head_and_tail() -> None:
    raw = "garbage prefix " * 30 + "garbage suffix " * 30
    with pytest.raises(ValueError) as excinfo:
        parse_subagent_return(raw)
    msg = str(excinfo.value)
    assert "Head:" in msg
    assert "Tail:" in msg
