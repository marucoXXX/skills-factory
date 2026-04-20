#!/usr/bin/env python3
"""Collect slide metadata (file name, skill, data JSON) into a single context.json.

Input:
  --merge-order   Path to merge_order.json. Expected shape:
                  {"entries": [{"slide_number": 1, "file_name": "slide_01_exec.pptx",
                                 "skill_name": "executive-summary-pptx",
                                 "data_file": "data_01_exec.json"}, ...]}
                  Minimal accepted shape: a list of the same entry objects.
  --data-dir      Directory containing data_NN_*.json files.
  --out           Output path for context.json.

Output JSON shape:
  {"slides": {"1": {"file_name": "...", "skill_name": "...",
                     "data_file": "...", "data_preview": {...}}, ...}}

data_preview is the parsed JSON truncated to the top-level keys + first nested
level of scalars, capped at 2KB to keep the review prompt tight.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


PREVIEW_BYTES_CAP = 2048


def load_merge_order(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "entries" in data:
        return list(data["entries"])
    if isinstance(data, list):
        return list(data)
    raise SystemExit(f"unexpected merge_order shape: {path}")


def truncate_preview(value):
    text = json.dumps(value, ensure_ascii=False)
    if len(text.encode("utf-8")) <= PREVIEW_BYTES_CAP:
        return value
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if isinstance(v, (dict, list)):
                out[k] = f"<{type(v).__name__} omitted>"
            else:
                out[k] = v
        return out
    if isinstance(value, list):
        return value[:3] + ([f"<+{len(value) - 3} more>"] if len(value) > 3 else [])
    return value


def load_data_preview(data_dir: Path, data_file: str | None) -> dict | None:
    if not data_file:
        return None
    candidate = data_dir / data_file
    if not candidate.exists():
        return {"_error": f"data file not found: {data_file}"}
    try:
        value = json.loads(candidate.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"_error": f"invalid JSON: {e}"}
    return truncate_preview(value)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--merge-order", required=True)
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    merge_order = Path(args.merge_order).expanduser().resolve()
    data_dir = Path(args.data_dir).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()

    entries = load_merge_order(merge_order)
    slides: dict[str, dict] = {}
    for entry in entries:
        num = entry.get("slide_number")
        if num is None:
            continue
        slides[str(num)] = {
            "file_name": entry.get("file_name"),
            "skill_name": entry.get("skill_name"),
            "data_file": entry.get("data_file"),
            "data_preview": load_data_preview(data_dir, entry.get("data_file")),
        }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"slides": slides}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"context written -> {out} ({len(slides)} slides)")


if __name__ == "__main__":
    main()
