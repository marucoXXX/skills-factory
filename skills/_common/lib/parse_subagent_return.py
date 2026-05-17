"""parse_subagent_return — research-subagent の return value を頑健に dict に変換する helper。

ISSUE-009 で観測された wrapper bloat（前置き説明文 / マークダウン code fence /
末尾 ``Sources:`` / 二重 JSON 出力）を吸収し、orchestrator 側で
``parsed = json.loads(result)`` を直接呼ぶ代わりに本 helper を介すことで、
subagent 出力の小揺らぎで親側がクラッシュしないようにする。

使い方::

    from skills._common.lib.parse_subagent_return import parse_subagent_return
    parsed = parse_subagent_return(result)

抽出ロジック:
    1) そのまま ``json.loads`` を試す（subagent が規約遵守できている場合は最速）
    2) マークダウン code fence (```json ... ``` / ``` ... ```) を除去して再試行
    3) 最初に出現する均衡の取れた ``{...}`` ブロックを抽出して再試行
       （二重 JSON 出力時は最初の 1 つを優先）
    4) すべて失敗したら ``ValueError`` を上げる（原文 head/tail 付き）
"""

from __future__ import annotations

import json
import re
from typing import Any


_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE)


def _strip_code_fences(s: str) -> str:
    m = _FENCE_RE.search(s)
    if m:
        return m.group(1)
    return s


def _extract_first_json_object(s: str) -> str:
    """最初に出現する均衡の取れた ``{...}`` ブロックを返す。

    文字列リテラル内の ``{`` ``}`` とエスケープされた ``"`` を考慮する。
    二重 JSON 出力（``{...}{...}``）の場合は最初のオブジェクトのみ返す。
    """
    depth = 0
    start = -1
    in_str = False
    escape = False
    for i, ch in enumerate(s):
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            continue
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start >= 0:
                    return s[start : i + 1]
    raise ValueError("no balanced { ... } block found")


def parse_subagent_return(raw: str) -> dict[str, Any]:
    """research-subagent return value を dict に変換する。

    Args:
        raw: subagent から返る生の文字列。

    Returns:
        パース済みの dict。

    Raises:
        TypeError: ``raw`` が ``str`` ではない。
        ValueError: どの抽出戦略でも JSON object を取り出せなかった。
            メッセージには原文先頭/末尾 200 字を含める。
    """
    if not isinstance(raw, str):
        raise TypeError(
            f"parse_subagent_return expects str, got {type(raw).__name__}"
        )

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    stripped = _strip_code_fences(raw).strip()
    if stripped and stripped != raw.strip():
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    try:
        block = _extract_first_json_object(stripped)
        return json.loads(block)
    except (ValueError, json.JSONDecodeError) as e:
        head = raw[:200].replace("\n", " ")
        tail = raw[-200:].replace("\n", " ")
        raise ValueError(
            "parse_subagent_return: failed to extract a valid JSON object "
            f"from subagent return value (length={len(raw)}). "
            f"Head: {head!r} | Tail: {tail!r}"
        ) from e
