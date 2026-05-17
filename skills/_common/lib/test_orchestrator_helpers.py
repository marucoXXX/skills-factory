"""orchestrator_helpers (ISSUE-010 Phase 1 iii) のテスト。

実行: ``python -m pytest skills/_common/lib/test_orchestrator_helpers.py``

テスト対象:
- ``resolve_fill_brand_with_warning`` の supported / unsupported 分岐、buffer 追記、warnings.warn
- ``append_brand_warnings_to_merge_file`` の新規作成 / 既存 read+append / 空 brand_warnings の no-op
"""

from __future__ import annotations

import json
import os
import warnings

import pytest

from skills._common.lib.orchestrator_helpers import (
    append_brand_warnings_to_merge_file,
    resolve_fill_brand_with_warning,
)


# ---- resolve_fill_brand_with_warning -----------------------------------


def _make_skill_md(skill_dir, supported_brands_inline):
    """Helper: create a minimal SKILL.md with the given supported_brands list."""
    skill_md = skill_dir / "SKILL.md"
    if supported_brands_inline is None:
        # legacy SKILL.md (no frontmatter)
        skill_md.write_text("# Test skill (no frontmatter)\n", encoding="utf-8")
    else:
        skill_md.write_text(
            "---\n"
            "name: test-skill\n"
            f"supported_brands: {supported_brands_inline}\n"
            "---\n"
            "# Body\n",
            encoding="utf-8",
        )


def test_resolve_supported_brand_returns_unchanged(tmp_path) -> None:
    skill = tmp_path / "test_skill"
    skill.mkdir()
    _make_skill_md(skill, "[stellar_aiz, roleup]")
    buf: list = []

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = resolve_fill_brand_with_warning(str(skill), "roleup", buf)

    assert result == "roleup"
    assert buf == []
    assert caught == []


def test_resolve_default_brand_short_circuits(tmp_path) -> None:
    """When scope_brand == stellar_aiz, the helper returns it directly without
    even reading the SKILL.md (skill_dir can be a non-existent path)."""
    bogus_dir = str(tmp_path / "does_not_exist")
    buf: list = []

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = resolve_fill_brand_with_warning(bogus_dir, "stellar_aiz", buf)

    assert result == "stellar_aiz"
    assert buf == []
    assert caught == []


def test_resolve_unsupported_falls_back_and_appends(tmp_path) -> None:
    skill = tmp_path / "swot_pptx"
    skill.mkdir()
    _make_skill_md(skill, "[stellar_aiz]")
    buf: list = []

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = resolve_fill_brand_with_warning(str(skill), "roleup", buf)

    assert result == "stellar_aiz"
    assert len(buf) == 1
    assert buf[0]["slide_index"] == -1
    assert buf[0]["type"] == "brand_fallback"
    assert "swot_pptx" in buf[0]["message"]
    assert "roleup" in buf[0]["message"]
    assert "stellar_aiz" in buf[0]["message"]
    # warnings.warn fired exactly once with RuntimeWarning
    assert len(caught) == 1
    assert issubclass(caught[0].category, RuntimeWarning)


def test_resolve_unsupported_legacy_skill_md(tmp_path) -> None:
    """SKILL.md without frontmatter is treated as supporting stellar_aiz only."""
    skill = tmp_path / "legacy_skill"
    skill.mkdir()
    _make_skill_md(skill, None)  # no frontmatter
    buf: list = []

    result = resolve_fill_brand_with_warning(str(skill), "roleup", buf)

    assert result == "stellar_aiz"
    assert len(buf) == 1
    assert buf[0]["type"] == "brand_fallback"


def test_resolve_accumulates_warnings_across_calls(tmp_path) -> None:
    skill_a = tmp_path / "skill_a"
    skill_a.mkdir()
    _make_skill_md(skill_a, "[stellar_aiz]")
    skill_b = tmp_path / "skill_b"
    skill_b.mkdir()
    _make_skill_md(skill_b, "[stellar_aiz, roleup]")
    skill_c = tmp_path / "skill_c"
    skill_c.mkdir()
    _make_skill_md(skill_c, "[stellar_aiz]")

    buf: list = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert resolve_fill_brand_with_warning(str(skill_a), "roleup", buf) == "stellar_aiz"
        assert resolve_fill_brand_with_warning(str(skill_b), "roleup", buf) == "roleup"
        assert resolve_fill_brand_with_warning(str(skill_c), "roleup", buf) == "stellar_aiz"

    assert len(buf) == 2
    assert all(w["type"] == "brand_fallback" for w in buf)
    assert "skill_a" in buf[0]["message"]
    assert "skill_c" in buf[1]["message"]


# ---- append_brand_warnings_to_merge_file ----------------------------------


def test_append_no_op_when_empty(tmp_path) -> None:
    """When brand_warnings is empty, the file is left untouched (must not be
    created if it didn't exist, must not be re-written if it did)."""
    p = tmp_path / "merge_warnings.json"
    append_brand_warnings_to_merge_file(str(p), [])
    assert not p.exists()

    p.write_text(
        json.dumps([{"slide_index": 3, "type": "section_divider_position", "message": "x"}]),
        encoding="utf-8",
    )
    mtime_before = p.stat().st_mtime
    append_brand_warnings_to_merge_file(str(p), [])
    assert p.stat().st_mtime == mtime_before


def test_append_creates_file_when_missing(tmp_path) -> None:
    p = tmp_path / "merge_warnings.json"
    bw = [{"slide_index": -1, "type": "brand_fallback", "message": "foo"}]
    append_brand_warnings_to_merge_file(str(p), bw)
    assert p.exists()
    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded == bw


def test_append_preserves_existing_section_divider(tmp_path) -> None:
    """When merge-pptxv2 has already written its own warnings, brand_fallback
    entries are appended after (preserves merge-pptxv2's content)."""
    p = tmp_path / "merge_warnings.json"
    sd = {"slide_index": 5, "type": "section_divider_position",
          "message": "section divider not on odd slide"}
    p.write_text(json.dumps([sd], ensure_ascii=False, indent=2), encoding="utf-8")

    bw = [
        {"slide_index": -1, "type": "brand_fallback", "message": "skill 'a' falls back"},
        {"slide_index": -1, "type": "brand_fallback", "message": "skill 'b' falls back"},
    ]
    append_brand_warnings_to_merge_file(str(p), bw)

    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert len(loaded) == 3
    assert loaded[0] == sd
    assert loaded[1] == bw[0]
    assert loaded[2] == bw[1]


def test_append_handles_corrupt_existing_file(tmp_path) -> None:
    """If the existing merge_warnings.json is malformed (not valid JSON or
    not a list), the append silently treats it as empty and writes the new
    brand_warnings only — never crashes the orchestrator."""
    p = tmp_path / "merge_warnings.json"
    p.write_text("garbage not json", encoding="utf-8")

    bw = [{"slide_index": -1, "type": "brand_fallback", "message": "x"}]
    append_brand_warnings_to_merge_file(str(p), bw)

    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded == bw


def test_append_roundtrip_readable_by_python_json(tmp_path) -> None:
    """Sanity check: the written file is valid JSON parseable as list of dicts."""
    p = tmp_path / "merge_warnings.json"
    bw = [{"slide_index": -1, "type": "brand_fallback",
           "message": "日本語メッセージ含む — 'skill_x'"}]
    append_brand_warnings_to_merge_file(str(p), bw)
    loaded = json.loads(p.read_text(encoding="utf-8"))
    assert loaded == bw
    # ensure_ascii=False で日本語がそのまま書かれる
    assert "日本語" in p.read_text(encoding="utf-8")
