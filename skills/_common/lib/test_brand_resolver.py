"""brand_resolver Phase 0 (agnostic 化) のテスト。

実行: ``python -m pytest skills/_common/lib/test_brand_resolver.py``

テスト対象:
- ``_discover_brands`` の動的検出（ディレクトリ追加に追従）
- ``_validate_brand_id`` の D1 命名規則（`^[a-z][a-z0-9_]{1,23}$`）
- ``is_brand_supported_by_skill`` の SKILL.md frontmatter 解釈
- ``resolve_brand_with_fallback`` の warning + stella fallback
"""

from __future__ import annotations

import os
import warnings

import pytest

from skills._common.lib.brand_resolver import (
    DEFAULT_BRAND,
    _discover_brands,
    _read_supported_brands,
    _validate_brand_id,
    is_brand_supported_by_skill,
    resolve_brand,
    resolve_brand_with_fallback,
)


# ---- _discover_brands ---------------------------------------------------


def test_discover_brands_existing_repo() -> None:
    found = _discover_brands()
    assert "stellar_aiz" in found
    assert "roleup" in found


def test_discover_brands_dynamic_addition(tmp_path) -> None:
    fake_brands = tmp_path / "brands"
    fake_brands.mkdir()
    for name in ("stellar_aiz", "roleup", "test_corp"):
        sub = fake_brands / name
        sub.mkdir()
        (sub / "theme.json").write_text("{}", encoding="utf-8")
    found = _discover_brands(str(fake_brands))
    assert found == ("roleup", "stellar_aiz", "test_corp")


def test_discover_brands_skips_invalid_dir_names(tmp_path) -> None:
    fake_brands = tmp_path / "brands"
    fake_brands.mkdir()
    # Valid brand
    (fake_brands / "stellar_aiz").mkdir()
    (fake_brands / "stellar_aiz" / "theme.json").write_text("{}", encoding="utf-8")
    # macOS metadata dir — should be silently skipped
    (fake_brands / ".DS_Store").mkdir()
    (fake_brands / ".DS_Store" / "theme.json").write_text("{}", encoding="utf-8")
    # Uppercase / kebab-case violates D1 — silently skipped
    (fake_brands / "Test-Corp").mkdir()
    (fake_brands / "Test-Corp" / "theme.json").write_text("{}", encoding="utf-8")
    found = _discover_brands(str(fake_brands))
    assert found == ("stellar_aiz",)


def test_discover_brands_requires_theme_json(tmp_path) -> None:
    fake_brands = tmp_path / "brands"
    fake_brands.mkdir()
    (fake_brands / "stellar_aiz").mkdir()
    (fake_brands / "stellar_aiz" / "theme.json").write_text("{}", encoding="utf-8")
    # roleup dir without theme.json — skipped
    (fake_brands / "roleup").mkdir()
    found = _discover_brands(str(fake_brands))
    assert found == ("stellar_aiz",)


# ---- _validate_brand_id -------------------------------------------------


@pytest.mark.parametrize("bad_id", ["Test-Corp", "1abc", "a", "ROLEUP", "ab-cd", ""])
def test_validate_brand_id_rejects_invalid(bad_id: str) -> None:
    with pytest.raises(ValueError):
        _validate_brand_id(bad_id)


@pytest.mark.parametrize("good_id", ["stellar_aiz", "roleup", "nttdata", "ab"])
def test_validate_brand_id_accepts_valid(good_id: str) -> None:
    _validate_brand_id(good_id)


def test_validate_brand_id_rejects_non_str() -> None:
    with pytest.raises(ValueError):
        _validate_brand_id(123)  # type: ignore[arg-type]


# ---- _read_supported_brands ---------------------------------------------


def test_read_supported_brands_no_frontmatter(tmp_path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("# A skill without frontmatter\n", encoding="utf-8")
    assert _read_supported_brands(str(skill_md)) == ("stellar_aiz",)


def test_read_supported_brands_inline_list(tmp_path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        "name: foo\n"
        "supported_brands: [stellar_aiz, roleup]\n"
        "---\n"
        "# Skill body\n",
        encoding="utf-8",
    )
    assert _read_supported_brands(str(skill_md)) == ("stellar_aiz", "roleup")


def test_read_supported_brands_quoted_items(tmp_path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text(
        "---\n"
        'supported_brands: ["stellar_aiz", \'roleup\']\n'
        "---\n",
        encoding="utf-8",
    )
    assert _read_supported_brands(str(skill_md)) == ("stellar_aiz", "roleup")


def test_read_supported_brands_field_absent_in_frontmatter(tmp_path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: foo\n---\n# body\n", encoding="utf-8")
    assert _read_supported_brands(str(skill_md)) == ("stellar_aiz",)


def test_read_supported_brands_missing_file(tmp_path) -> None:
    assert _read_supported_brands(str(tmp_path / "nonexistent.md")) == ("stellar_aiz",)


# ---- is_brand_supported_by_skill ----------------------------------------


def test_is_brand_supported_default_for_legacy_skill(tmp_path) -> None:
    (tmp_path / "SKILL.md").write_text("# legacy\n", encoding="utf-8")
    assert is_brand_supported_by_skill(str(tmp_path), "stellar_aiz") is True
    assert is_brand_supported_by_skill(str(tmp_path), "roleup") is False


def test_is_brand_supported_with_explicit_list(tmp_path) -> None:
    (tmp_path / "SKILL.md").write_text(
        "---\nsupported_brands: [stellar_aiz, roleup]\n---\n", encoding="utf-8"
    )
    assert is_brand_supported_by_skill(str(tmp_path), "stellar_aiz") is True
    assert is_brand_supported_by_skill(str(tmp_path), "roleup") is True


def test_is_brand_supported_validates_brand_id(tmp_path) -> None:
    (tmp_path / "SKILL.md").write_text("# legacy\n", encoding="utf-8")
    with pytest.raises(ValueError):
        is_brand_supported_by_skill(str(tmp_path), "Bad-Id")


# ---- resolve_brand validation -------------------------------------------


def test_resolve_brand_rejects_undiscoverable() -> None:
    with pytest.raises(ValueError) as excinfo:
        resolve_brand("nonexistent_brand")
    assert "not discovered" in str(excinfo.value)


def test_resolve_brand_rejects_invalid_id() -> None:
    with pytest.raises(ValueError):
        resolve_brand("Bad-Id")


# ---- resolve_brand_with_fallback ----------------------------------------


def test_resolve_brand_with_fallback_supported(tmp_path) -> None:
    # Fake skill that explicitly declares roleup support.
    # Real skills will get this frontmatter in Phase 1; until then this test
    # exercises the supported-path with a synthetic SKILL.md.
    (tmp_path / "SKILL.md").write_text(
        "---\nsupported_brands: [stellar_aiz, roleup]\n---\n# fake\n",
        encoding="utf-8",
    )
    theme, msg = resolve_brand_with_fallback("roleup", str(tmp_path))
    assert theme.id == "roleup"
    assert msg is None


def test_resolve_brand_with_fallback_unsupported_emits_warning(tmp_path) -> None:
    # Create a fake skill dir with SKILL.md declaring only stellar_aiz support
    (tmp_path / "SKILL.md").write_text(
        "---\nsupported_brands: [stellar_aiz]\n---\n# fake skill\n", encoding="utf-8"
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        theme, msg = resolve_brand_with_fallback("roleup", str(tmp_path))
    assert theme.id == DEFAULT_BRAND
    assert msg is not None
    assert "does not support brand 'roleup'" in msg
    assert any(issubclass(w.category, RuntimeWarning) for w in caught)
