#!/usr/bin/env python3
"""smoke_test_all.py - Generate each skill's PPTX with its sample data, then validate.

Runs every skill that ships a ``references/sample_data.json`` fixture using its
``scripts/fill_*.py`` script (standard CLI: ``--data --template --output``),
then runs the produced .pptx through ``validate_pptx.py`` to surface
"修復が必要" precursors.

Outputs:
  - work/smoke/<skill>.pptx          (generated artifacts)
  - work/smoke_result.csv            (summary: skill, status, error_category, notes)
  - work/smoke_result.json           (full structured results)

Usage:
    python3 tools/smoke_test_all.py
    python3 tools/smoke_test_all.py --only customer-profile-pptx,section-divider-pptx
    python3 tools/smoke_test_all.py --merge-with v2
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
import traceback
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
WORK_DIR = REPO / "work" / "smoke"

sys.path.insert(0, str(REPO / "tools"))
from validate_pptx import validate  # noqa: E402


NON_PPTX_SKILLS = {
    "strategy-report-agent",
    "issue-tree",
    "nttdata-pptx",
    "merge-pptxv2",
    "merge-pptxv3",
    "_common",
}

# Skills whose fill_*.py uses a non-standard CLI. The value is a list of
# extra args to append (template paths get resolved here).
EXTRA_CLI_ARGS = {
    "conceptual-pptx": lambda skill_dir: [
        "--template3", str(skill_dir / "assets" / "Conceptual3.pptx"),
        "--template5", str(skill_dir / "assets" / "Conceptual5.pptx"),
    ],
}

# Skills that use a non-standard --template arg (omit the default --template flag)
SKIP_TEMPLATE_FLAG = {"conceptual-pptx"}


@dataclass
class SkillResult:
    skill: str
    status: str = "pending"     # pending | no_fixture | runtime_error | validate_fail | ok
    error_category: str = ""     # xml_parse | rels_dangling | content_type_missing | chart_rels_broken | zip_corrupt | runtime_error | template_missing
    output_pptx: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    note: str = ""


def discover_skills() -> list[str]:
    return sorted(
        p.name for p in SKILLS_DIR.iterdir()
        if p.is_dir() and p.name not in NON_PPTX_SKILLS and (p / "SKILL.md").exists()
    )


def find_fixture(skill: str) -> tuple[Path | None, Path | None, Path | None]:
    """Return (sample_data.json, template.pptx, fill_script) or None for missing parts."""
    skill_dir = SKILLS_DIR / skill
    sample = skill_dir / "references" / "sample_data.json"
    sample = sample if sample.exists() else None

    templates = sorted((skill_dir / "assets").glob("*.pptx")) if (skill_dir / "assets").exists() else []
    template = templates[0] if templates else None

    scripts = sorted((skill_dir / "scripts").glob("fill_*.py")) if (skill_dir / "scripts").exists() else []
    script = scripts[0] if scripts else None

    return sample, template, script


def categorize_errors(errors: list[str]) -> str:
    for e in errors:
        head = e.split(":", 1)[0]
        if head in {"xml_parse", "rels_dangling", "content_type_missing",
                    "content_type_dangling", "chart_rels_broken", "zip_corrupt",
                    "zip_duplicate"}:
            return head
    return "unknown"


def run_skill(skill: str) -> SkillResult:
    result = SkillResult(skill=skill)
    sample, template, script = find_fixture(skill)

    if script is None or template is None:
        result.status = "no_fixture"
        result.note = (
            f"script={'y' if script else 'n'} template={'y' if template else 'n'}"
        )
        return result
    if sample is None:
        result.status = "no_fixture"
        result.note = "no sample_data.json"
        return result

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    out_pptx = WORK_DIR / f"{skill}.pptx"
    if out_pptx.exists():
        out_pptx.unlink()

    cmd = [sys.executable, str(script), "--data", str(sample)]
    if skill not in SKIP_TEMPLATE_FLAG:
        cmd += ["--template", str(template)]
    if skill in EXTRA_CLI_ARGS:
        cmd += EXTRA_CLI_ARGS[skill](SKILLS_DIR / skill)
    cmd += ["--output", str(out_pptx)]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        result.status = "runtime_error"
        result.error_category = "runtime_error"
        result.note = "timeout after 180s"
        return result

    if proc.returncode != 0:
        result.status = "runtime_error"
        result.error_category = "runtime_error"
        result.note = (proc.stderr or proc.stdout or "").strip().splitlines()[-1:][:1]
        result.note = result.note[0] if result.note else f"exit {proc.returncode}"
        return result

    if not out_pptx.exists():
        result.status = "runtime_error"
        result.error_category = "runtime_error"
        result.note = "script exited 0 but no output file"
        return result

    result.output_pptx = str(out_pptx)
    v = validate(out_pptx)
    result.errors = v.errors
    result.warnings = v.warnings
    if v.ok:
        result.status = "ok"
    else:
        result.status = "validate_fail"
        result.error_category = categorize_errors(v.errors)
    return result


def try_merge_pair(results: list[SkillResult], variant: str) -> list[dict]:
    """Merge successful skill outputs pairwise and validate the result."""
    oks = [r for r in results if r.status == "ok" and r.output_pptx]
    if len(oks) < 2:
        return []

    script_map = {
        "v2": SKILLS_DIR / "merge-pptxv2" / "scripts" / "merge_pptx_v2.py",
        "v3": SKILLS_DIR / "merge-pptxv3" / "scripts" / "merge_pptx_v3.py",
    }
    merge_script = script_map.get(variant)
    if merge_script is None or not merge_script.exists():
        return [{"skill_a": "-", "skill_b": "-", "status": "skipped",
                 "note": f"{variant} not available"}]

    pairs = [(oks[0], oks[1])]
    if len(oks) >= 4:
        pairs.append((oks[2], oks[3]))

    results_out = []
    for a, b in pairs:
        out = WORK_DIR / f"_merge_{variant}_{a.skill}+{b.skill}.pptx"
        if out.exists():
            out.unlink()
        cmd = [sys.executable, str(merge_script), str(out), a.output_pptx, b.output_pptx]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        row = {"variant": variant, "skill_a": a.skill, "skill_b": b.skill, "output": str(out)}
        if proc.returncode != 0 or not out.exists():
            row["status"] = "merge_error"
            row["note"] = (proc.stderr or proc.stdout).strip().splitlines()[-1:][:1]
            row["note"] = row["note"][0] if row["note"] else f"exit {proc.returncode}"
        else:
            v = validate(out)
            row["status"] = "ok" if v.ok else "validate_fail"
            row["errors"] = v.errors
            row["warnings"] = v.warnings
        results_out.append(row)
    return results_out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="smoke_test_all.py")
    parser.add_argument("--only", help="comma-separated skill names to run")
    parser.add_argument("--merge-with", choices=["v2", "v3"],
                        help="also run pairwise merge smoke test")
    parser.add_argument("--csv-out", default=str(REPO / "work" / "smoke_result.csv"))
    parser.add_argument("--json-out", default=str(REPO / "work" / "smoke_result.json"))
    args = parser.parse_args(argv)

    if args.only:
        skills = [s.strip() for s in args.only.split(",") if s.strip()]
    else:
        skills = discover_skills()

    results: list[SkillResult] = []
    for s in skills:
        try:
            r = run_skill(s)
        except Exception as exc:
            r = SkillResult(skill=s, status="runtime_error",
                            error_category="runtime_error",
                            note=f"{type(exc).__name__}: {exc}")
            traceback.print_exc()
        tag_map = {"ok": "OK  ", "validate_fail": "FAIL", "no_fixture": "SKIP",
                   "runtime_error": "ERR ", "pending": "PEND"}
        tag = tag_map.get(r.status, r.status)
        suffix = f"  ({r.error_category})" if r.error_category else ""
        note = f"  # {r.note}" if r.note else ""
        print(f"[{tag}] {s}{suffix}{note}")
        if r.errors:
            for e in r.errors[:3]:
                print(f"        {e}")
            if len(r.errors) > 3:
                print(f"        ... ({len(r.errors) - 3} more)")
        results.append(r)

    # Summary
    counts = {"ok": 0, "validate_fail": 0, "no_fixture": 0, "runtime_error": 0}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    print(f"\nSummary: {counts}")

    # Merge smoke
    merge_rows: list[dict] = []
    if args.merge_with:
        print(f"\n=== Merge smoke test ({args.merge_with}) ===")
        merge_rows = try_merge_pair(results, args.merge_with)
        for row in merge_rows:
            print(f"  [{row['status']}] {row.get('skill_a')} + {row.get('skill_b')}"
                  f"  {row.get('note', '')}")

    # Write CSV
    csv_out = Path(args.csv_out)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["skill", "status", "error_category", "output", "note", "error_count"])
        for r in results:
            w.writerow([r.skill, r.status, r.error_category, r.output_pptx,
                       r.note, len(r.errors)])
    print(f"\nwrote {csv_out}")

    # Write JSON
    json_out = Path(args.json_out)
    with json_out.open("w", encoding="utf-8") as f:
        payload = {
            "summary": counts,
            "skills": [r.__dict__ for r in results],
            "merge": merge_rows,
        }
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"wrote {json_out}")

    # Exit non-zero if anything failed
    return 0 if counts["validate_fail"] == 0 and counts["runtime_error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
