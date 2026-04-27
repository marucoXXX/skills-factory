#!/usr/bin/env python3
"""Render the final Markdown report from synthesis_output.json using report-template.md.

Handles schema variations defensively:
- `status` values: normalizes common synonyms (covered → complete, etc.)
- `verification_issues[]` field names: supports both canonical schema
  (id/category/issue/current_hypothesis/verification_method/priority) and
  the aliased form (issue/rationale/related_findings).

Usage:
    python3 render_report.py <synthesis_json> <template_md> <output_md>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


STATUS_ALIASES = {
    "complete": {"complete", "done", "full", "yes", "ok", "取得済", "取得済み", "✓", "covered"},
    "partial": {"partial", "part", "一部", "△", "limited"},
    "missing": {"missing", "none", "no", "✗", "x", "未取得", "n/a"},
}

PRIORITY_ALIASES = {
    "high": {"high", "高", "H"},
    "medium": {"medium", "中", "M"},
    "low": {"low", "低", "L"},
}

CATEGORY_FALLBACK = "未分類"


def normalize_status(raw: str) -> str:
    """Map any status synonym to canonical value (complete/partial/missing).

    Unknown values pass through for visibility (downstream may still display them).
    """
    if not raw:
        return ""
    lower = str(raw).strip().lower()
    for canonical, aliases in STATUS_ALIASES.items():
        if lower in (a.lower() for a in aliases):
            return canonical
    return lower


def normalize_priority(raw: str) -> str:
    if not raw:
        return ""
    lower = str(raw).strip().lower()
    for canonical, aliases in PRIORITY_ALIASES.items():
        if lower in (a.lower() for a in aliases):
            return canonical
    return lower


def fmt_findings_index_entry(f: dict) -> str:
    return (
        f"- **{f['id']}** (`{f['agent']}` / `{f['metric']}` / `confidence: {f['confidence']}`): "
        f"{f['value']}  \n  出典: {f['source']}"
    )


def fmt_evidence_list(refs: list, index: list) -> str:
    if not refs:
        return "- （根拠finding未指定）"
    id_to_f = {f["id"]: f for f in index}
    lines = []
    for r in refs:
        f = id_to_f.get(r)
        if f:
            lines.append(f"- **{r}**: {f['value']} _(confidence: {f['confidence']}, source: {f['source']})_")
        else:
            lines.append(f"- **{r}**: (not found in index)")
    return "\n".join(lines)


def fmt_reality_check(items: list, index: list) -> str:
    if not items:
        return "- 齟齬は検出されなかった"
    blocks = []
    for i, rc in enumerate(items, 1):
        refs_str = ", ".join(rc.get("evidence_refs", []))
        blocks.append(
            f"**齟齬 {i}**\n\n"
            f"- **Stated（発言）**: {rc.get('stated', '-')}\n"
            f"- **Revealed（行動）**: {rc.get('revealed', '-')}\n"
            f"- **Gap**: {rc.get('gap', '-')}\n"
            f"- **根拠 finding**: {refs_str}\n"
        )
    return "\n\n".join(blocks)


def fmt_data_availability_rows(matrix: dict) -> str:
    symbol_map = {"complete": "✓", "partial": "△", "missing": "✗"}
    rows = []
    for cat in matrix.get("categories", []):
        cat_name = cat.get("name", "")
        for item in cat.get("items", []):
            raw_status = item.get("status", "")
            canonical = normalize_status(raw_status)
            symbol = symbol_map.get(canonical, raw_status)
            label = item.get("label") or item.get("item") or ""
            source = item.get("source") or item.get("note") or ""
            rows.append(f"| {cat_name} | {label} | {symbol} | {source} |")
    return "\n".join(rows)


def count_statuses(matrix: dict) -> tuple[int, int, int]:
    complete = partial = missing = 0
    for cat in matrix.get("categories", []):
        for item in cat.get("items", []):
            canonical = normalize_status(item.get("status", ""))
            if canonical == "complete":
                complete += 1
            elif canonical == "partial":
                partial += 1
            elif canonical == "missing":
                missing += 1
    return complete, partial, missing


def _vrow_field(v: dict, canonical_key: str, alias_keys: list[str] = None) -> str:
    """Extract a verification issue field with alias fallback."""
    if canonical_key in v:
        return v[canonical_key]
    for k in alias_keys or []:
        if k in v:
            return v[k]
    return ""


def fmt_verification_rows(items: list) -> str:
    rows = []
    for i, v in enumerate(items, 1):
        vid = v.get("id") or f"V{i}"
        category = v.get("category") or CATEGORY_FALLBACK
        issue = v.get("issue", "")
        # Aliases: schema's current_hypothesis+verification_method may be combined in rationale
        current_hyp = _vrow_field(v, "current_hypothesis", ["rationale", "hypothesis"])
        verif = _vrow_field(v, "verification_method", ["verification", "method"])
        priority = normalize_priority(v.get("priority", ""))
        rows.append(
            f"| {vid} | {category} | {issue} | {current_hyp} | {verif} | {priority} |"
        )
    return "\n".join(rows)


def fmt_exec_findings(findings: list) -> str:
    lines = []
    for f in findings:
        refs = ", ".join(f.get("evidence_refs", []))
        lines.append(
            f"### [{f.get('category','')}] {f.get('heading','')}\n\n"
            f"{f.get('detail','')}\n\n"
            f"_根拠: {refs}_"
        )
    return "\n\n".join(lines)


def fmt_sources_appendix(index: list) -> str:
    seen = {}
    for f in index:
        src = f.get("source", "")
        stype = f.get("source_type", "")
        key = (stype, src)
        seen[key] = seen.get(key, 0) + 1
    lines = []
    for (stype, src), n in sorted(seen.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{stype}` / {src} （{n}件のfindingで参照）")
    return "\n".join(lines)


def fmt_all_findings_index(index: list) -> str:
    return "\n".join(fmt_findings_index_entry(f) for f in index)


def fmt_company_overview(index: list) -> str:
    keys_of_interest = {
        "establishment",
        "capital_history",
        "employee_count",
        "management",
        "group_structure",
        "fiscal_year",
        "business_description",
        "business_segments",
    }
    lines = []
    for f in index:
        if f.get("confidence") != "high":
            continue
        if f.get("metric") in keys_of_interest:
            lines.append(f"- **{f.get('metric')}**: {f.get('value')}  \n  _出典: {f.get('source')}_")
    if not lines:
        return "- （確定情報として分類できる finding が見つかりませんでした）"
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print("usage: render_report.py <synthesis_json> <template_md> <output_md>", file=sys.stderr)
        return 2

    synthesis = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    template = Path(argv[2]).read_text(encoding="utf-8")
    out_path = Path(argv[3])

    index = synthesis["all_findings_index"]
    hyp = synthesis["strategy_hypotheses"]
    stats = synthesis["triangulation_stats"]
    c, p, m = count_statuses(synthesis["data_availability_matrix"])

    replacements = {
        "{TARGET_COMPANY}": synthesis["target_company"],
        "{SYNTHESIZED_AT}": synthesis["synthesized_at"],
        "{INDUSTRY}": synthesis["industry"],
        "{RESEARCH_PURPOSE}": synthesis["research_purpose"],
        "{DEPTH_MODE}": synthesis.get("depth_mode", "基本/標準"),

        "{EXECUTIVE_SUMMARY_MAIN_MESSAGE}": synthesis["executive_summary"]["main_message"],
        "{EXECUTIVE_SUMMARY_FINDINGS_BULLETS}": fmt_exec_findings(
            synthesis["executive_summary"]["findings"]
        ),

        "{COMPANY_OVERVIEW_ITEMS}": fmt_company_overview(index),

        "{AGENTS_INVOKED_LIST}": synthesis.get("agents_invoked_markdown") or (
            "- Financial Signals Agent ✓\n"
            "- Strategic Signals Agent ✓\n"
            "- Corporate Registry Agent ✓\n"
            "- Talent & Organization Agent ✓\n"
            "- Industry Context Agent ✓\n"
            "- Synthesis Agent ✓"
        ),
        "{CONFIDENCE_HIGH_COUNT}": str(stats.get("high_confidence", 0)),
        "{CONFIDENCE_MEDIUM_COUNT}": str(stats.get("medium_confidence", 0)),
        "{CONFIDENCE_LOW_COUNT}": str(stats.get("low_confidence", 0)),
        "{TOTAL_FINDINGS_COUNT}": str(stats.get("total_findings", 0)),
        "{TRIANGULATION_RATE}": f"{stats.get('triangulation_rate', 0):.0%}",

        "{WTP_CONFIDENCE}": hyp["where_to_play"].get("confidence", ""),
        "{WHERE_TO_PLAY_HYPOTHESIS}": hyp["where_to_play"].get("hypothesis", ""),
        "{WHERE_TO_PLAY_EVIDENCE}": fmt_evidence_list(hyp["where_to_play"].get("evidence_refs", []), index),

        "{HTW_CONFIDENCE}": hyp["how_to_win"].get("confidence", ""),
        "{HOW_TO_WIN_HYPOTHESIS}": hyp["how_to_win"].get("hypothesis", ""),
        "{HOW_TO_WIN_EVIDENCE}": fmt_evidence_list(hyp["how_to_win"].get("evidence_refs", []), index),

        "{CAP_CONFIDENCE}": hyp["capability_resource"].get("confidence", ""),
        "{CAPABILITY_RESOURCE_HYPOTHESIS}": hyp["capability_resource"].get("hypothesis", ""),
        "{CAPABILITY_RESOURCE_EVIDENCE}": fmt_evidence_list(hyp["capability_resource"].get("evidence_refs", []), index),

        "{ASP_CONFIDENCE}": hyp["aspiration_trajectory"].get("confidence", ""),
        "{ASPIRATION_TRAJECTORY_HYPOTHESIS}": hyp["aspiration_trajectory"].get("hypothesis", ""),
        "{ASPIRATION_TRAJECTORY_EVIDENCE}": fmt_evidence_list(hyp["aspiration_trajectory"].get("evidence_refs", []), index),

        "{REALITY_CHECK_ITEMS}": fmt_reality_check(hyp.get("reality_check", []), index),

        "{DATA_AVAILABILITY_TABLE_ROWS}": fmt_data_availability_rows(synthesis["data_availability_matrix"]),
        "{COMPLETE_COUNT}": str(c),
        "{PARTIAL_COUNT}": str(p),
        "{MISSING_COUNT}": str(m),

        "{VERIFICATION_ISSUES_TABLE_ROWS}": fmt_verification_rows(synthesis["verification_issues"]),

        "{SOURCES_APPENDIX}": fmt_sources_appendix(index),
        "{ALL_FINDINGS_INDEX}": fmt_all_findings_index(index),

        "{SYNTHESIS_OUTPUT_PATH}": str(Path(argv[1]).resolve()),
        "{MASTER_OUTPUT_PATH}": str(Path(argv[1]).resolve().parent / "master_output.json"),
    }

    rendered = template
    for k, v in replacements.items():
        rendered = rendered.replace(k, v)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"wrote {out_path} ({len(rendered)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
