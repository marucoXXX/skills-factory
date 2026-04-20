#!/usr/bin/env python3
"""extract_sample_data.py - Extract first JSON code-block from a SKILL.md into
``references/sample_data.json`` so smoke_test_all.py can drive the skill.

Usage:
    python3 tools/extract_sample_data.py <skill-dir>
    python3 tools/extract_sample_data.py --all      # scan skills missing sample_data.json
    python3 tools/extract_sample_data.py --all --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

NON_PPTX = {"strategy-report-agent", "issue-tree", "nttdata-pptx",
            "merge-pptxv2", "merge-pptxv3", "_common"}

CODE_BLOCK = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)


def find_first_valid_json(text: str) -> dict | list | None:
    for m in CODE_BLOCK.finditer(text):
        block = m.group(1).strip()
        # Strip leading "// ..." style comments that sometimes appear
        block = re.sub(r"^//.*?$", "", block, flags=re.MULTILINE)
        try:
            return json.loads(block)
        except json.JSONDecodeError:
            continue
    return None


def process_skill(skill_dir: Path, *, dry_run: bool, overwrite: bool) -> str:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "no_skill_md"
    target = skill_dir / "references" / "sample_data.json"
    if target.exists() and not overwrite:
        return "exists"
    data = find_first_valid_json(skill_md.read_text(encoding="utf-8"))
    if data is None:
        return "no_valid_json"
    if dry_run:
        return f"would_write ({type(data).__name__})"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return f"wrote ({type(data).__name__})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="extract_sample_data.py")
    parser.add_argument("skill_dir", nargs="?")
    parser.add_argument("--all", action="store_true",
                        help="scan all skills missing sample_data.json")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overwrite", action="store_true",
                        help="replace existing sample_data.json files")
    args = parser.parse_args(argv)

    if args.skill_dir:
        targets = [Path(args.skill_dir)]
    elif args.all:
        targets = []
        for p in sorted(SKILLS_DIR.iterdir()):
            if not p.is_dir() or p.name in NON_PPTX:
                continue
            if not (p / "SKILL.md").exists():
                continue
            if (p / "references" / "sample_data.json").exists() and not args.overwrite:
                continue
            targets.append(p)
    else:
        parser.print_usage(sys.stderr)
        return 2

    for t in targets:
        status = process_skill(t, dry_run=args.dry_run, overwrite=args.overwrite)
        print(f"[{t.name}] {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
