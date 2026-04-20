#!/usr/bin/env python3
"""Extract fact-check candidate claims from data_*.json files.

Usage:
  extract_claims.py --data-dir <dir> --scope high_risk|all|skip --out <path>

The script walks every JSON tree, collects leaf values that match known claim
patterns, and writes a claims.json that lists each claim with its JSONPath-like
locator. The actual web verification is the caller's job.

Claim types:
  numeric_value     Any leaf string/number with units (%, 億円, 兆円, 人, 年間)
  numeric_share     Leaf containing "シェア" or "market share" plus a %
  numeric_money     金額単位を含むリーフ
  date              YYYY, YYYY年, YYYY/MM, YYYY-MM-DD, etc.
  proper_noun       株式会社〜 / 〜Corporation / 〜Inc. / 〜Co., Ltd.
  text_assertion    (scope=all only) 10+ char text values with 。or period
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterator

NUMBER_UNIT_RE = re.compile(
    r"(?:[\-+]?\d[\d,\.]*)\s*(?:%|％|億円|兆円|千億円|百万円|万円|人|件|年|ヵ月|か月|倍|pt|pts|bps)"
)
DATE_RE = re.compile(
    r"\b(?:19|20)\d{2}(?:\s*年|/\d{1,2}(?:/\d{1,2})?|-\d{2}(?:-\d{2})?)?\b"
)
PROPER_NOUN_RE = re.compile(
    r"(?:株式会社[\u3040-\u30ff\u4e00-\u9fffA-Za-z0-9]+"
    r"|[A-Z][A-Za-z0-9&\-\s]{2,}(?:Corporation|Corp\.?|Inc\.?|Co\.,?\s*Ltd\.?|Ltd\.?|Group|Holdings?))"
)
SHARE_RE = re.compile(r"(?:シェア|市場シェア|market\s*share)", re.IGNORECASE)


def iter_leaves(node, path: str) -> Iterator[tuple[str, object]]:
    if isinstance(node, dict):
        for k, v in node.items():
            yield from iter_leaves(v, f"{path}.{k}" if path else f"$.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from iter_leaves(v, f"{path}[{i}]")
    else:
        yield path, node


def classify_claim(value: str, scope: str) -> list[str]:
    types: list[str] = []
    if SHARE_RE.search(value) and NUMBER_UNIT_RE.search(value):
        types.append("numeric_share")
    if NUMBER_UNIT_RE.search(value):
        types.append("numeric_value")
    if DATE_RE.search(value):
        types.append("date")
    if PROPER_NOUN_RE.search(value):
        types.append("proper_noun")
    if scope == "all" and len(value) >= 10 and re.search(r"[。．.]", value):
        if not types:
            types.append("text_assertion")
    return types


def extract_from_file(path: Path, scope: str) -> list[dict]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"warn: skip {path.name}: {e}", file=sys.stderr)
        return []

    claims: list[dict] = []
    for json_path, leaf in iter_leaves(doc, ""):
        if leaf is None:
            continue
        if not isinstance(leaf, (str, int, float)):
            continue
        text = str(leaf)
        if len(text) < 2:
            continue
        types = classify_claim(text, scope)
        if not types:
            continue
        primary_type = types[0]
        if scope == "high_risk" and primary_type == "text_assertion":
            continue
        claims.append(
            {
                "data_file": path.name,
                "json_path": json_path,
                "claim_text": text,
                "claim_type": primary_type,
                "all_types": types,
            }
        )
    return claims


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument(
        "--scope", required=True, choices=["high_risk", "all", "skip"]
    )
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data_dir = Path(args.data_dir).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.scope == "skip":
        out.write_text(
            json.dumps({"scope": "skip", "claims": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"scope=skip, wrote empty claims -> {out}")
        return

    if not data_dir.is_dir():
        raise SystemExit(f"data-dir not found: {data_dir}")

    all_claims: list[dict] = []
    for path in sorted(data_dir.glob("data_*.json")):
        file_claims = extract_from_file(path, args.scope)
        for idx, claim in enumerate(file_claims):
            claim["claim_id"] = f"{path.stem}_{idx:03d}"
        all_claims.extend(file_claims)

    out.write_text(
        json.dumps(
            {"scope": args.scope, "claims": all_claims},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"extracted {len(all_claims)} claims -> {out}")


if __name__ == "__main__":
    main()
