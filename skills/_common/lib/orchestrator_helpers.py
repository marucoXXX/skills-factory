"""Orchestrator helpers for skills_factory v0.4 (ISSUE-010 Phase 1).

Provides two helpers used by orchestrator agents (market-overview-agent /
strategy-report-agent / company-deepdive-agent / business-deepdive-agent /
smallcap-strategy-research / comparison-synthesis-agent etc.) to apply the
`brand_fallback` warning flow (D4) without each agent reimplementing the same
logic.

Usage in an orchestrator:

    import sys, os
    sys.path.insert(0, os.path.join(REPO_ROOT, "skills/_common/lib"))
    from orchestrator_helpers import (
        resolve_fill_brand_with_warning,
        append_brand_warnings_to_merge_file,
    )

    brand_warnings = []
    for entry in fill_targets:
        fill_brand = resolve_fill_brand_with_warning(
            entry.skill_dir, scope_brand, brand_warnings
        )
        subprocess.run([
            "python", entry.fill_script, "--brand", fill_brand, ...
        ])

    # ... merge-pptxv2 runs and writes merge_warnings.json ...
    append_brand_warnings_to_merge_file(
        os.path.join(output_dir, "merge_warnings.json"), brand_warnings
    )

Why a buffer + post-merge append? merge-pptxv2's `write_merge_warnings()`
writes `merge_warnings.json` in `"w"` mode and overwrites any pre-existing
content. Pre-merge writes by the orchestrator would be silently dropped, so
we hold brand-fallback warnings in memory and append them after merge.
"""
from __future__ import annotations

import json
import os
import warnings
from typing import List, Optional

# Dual-import: orchestrators inject `_common/lib/` into sys.path and import
# helpers as bare modules (`from orchestrator_helpers import ...`); pytest
# imports the same module under its full package path. Try the package-style
# absolute import first, then fall back to the bare-name path injection used
# at runtime.
try:
    from skills._common.lib.brand_resolver import (
        DEFAULT_BRAND,
        is_brand_supported_by_skill,
    )
except ModuleNotFoundError:
    from brand_resolver import DEFAULT_BRAND, is_brand_supported_by_skill


def resolve_fill_brand_with_warning(
    skill_dir: str,
    scope_brand: str,
    warnings_buffer: List[dict],
) -> str:
    """Resolve the brand to pass to a fill script, recording a warning when needed.

    Returns the brand id string suitable for `--brand <id>`. When the skill
    declares support for `scope_brand` (or `scope_brand` already equals
    `DEFAULT_BRAND`), returns `scope_brand` unchanged. Otherwise emits a
    `RuntimeWarning`, appends a `brand_fallback` entry to `warnings_buffer`,
    and returns `DEFAULT_BRAND`.

    The warning entry schema (per orchestrator_contract.md §4.4):

        {"slide_index": -1, "type": "brand_fallback", "message": "<msg>"}

    `slide_index = -1` means "deck-level" (not tied to any slide).

    Args:
        skill_dir: Absolute path to the skill directory (containing SKILL.md
                   with the `supported_brands` frontmatter).
        scope_brand: Brand id requested by the user (typically
                     `scope.json.brand`).
        warnings_buffer: A list the caller owns; this function appends to it
                         as a side effect. The caller passes it to
                         `append_brand_warnings_to_merge_file` after merge.

    Returns:
        The brand id string to pass to the fill script's `--brand` argument.
    """
    if scope_brand == DEFAULT_BRAND:
        return scope_brand
    if is_brand_supported_by_skill(skill_dir, scope_brand):
        return scope_brand

    skill_name = os.path.basename(skill_dir.rstrip(os.sep))
    msg = (
        f"skill {skill_name!r} does not support brand {scope_brand!r}; "
        f"falling back to {DEFAULT_BRAND!r}"
    )
    warnings.warn(msg, RuntimeWarning, stacklevel=2)
    warnings_buffer.append(
        {"slide_index": -1, "type": "brand_fallback", "message": msg}
    )
    return DEFAULT_BRAND


def append_brand_warnings_to_merge_file(
    merge_warnings_path: str,
    brand_warnings: List[dict],
) -> None:
    """Append brand-fallback warnings to merge_warnings.json after merge.

    Reads `merge_warnings.json` (created by merge-pptxv2 with the deck's own
    validation warnings), appends `brand_warnings`, and writes the merged list
    back. No-op when `brand_warnings` is empty (file is left untouched, which
    matters for byte-stable regression tests).

    Args:
        merge_warnings_path: Absolute path to `merge_warnings.json`. The file
                             may already exist (created by merge-pptxv2) or
                             be missing (the orchestrator skipped merge); both
                             are handled.
        brand_warnings: List of warning dicts (typically populated by
                        `resolve_fill_brand_with_warning`). Each entry should
                        follow the §2 schema:
                        `{"slide_index": int, "type": str, "message": str}`.
    """
    if not brand_warnings:
        return

    existing: List[dict] = []
    if os.path.exists(merge_warnings_path):
        with open(merge_warnings_path, encoding="utf-8") as f:
            try:
                loaded = json.load(f)
            except json.JSONDecodeError:
                loaded = []
            if isinstance(loaded, list):
                existing = loaded

    existing.extend(brand_warnings)

    with open(merge_warnings_path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
        f.write("\n")
