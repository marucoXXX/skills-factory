#!/usr/bin/env python3
"""validate_pptx.py - Static OOXML integrity checker for .pptx files.

Checks:
  1. ZIP integrity (testzip + duplicate arcname)
  2. [Content_Types].xml coverage (Default extension + Override partname)
  3. All *.rels Target references resolve to real parts (normalized paths)
  4. ppt/charts/_rels/chartN.xml.rels reference chain (xlsx / image / colors / style)
  5. Every *.xml is parseable by lxml

Usage:
    python3 validate_pptx.py <file.pptx> [--json] [--verbose]
    python3 validate_pptx.py --template-scan   # scan all skills/*/assets/*.pptx

Exit codes:
    0 = ok
    1 = validation failures found
    2 = usage / IO error
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

# Reuse constants from merge_pptx_v2.
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills" / "merge-pptxv2" / "scripts"))
try:
    from merge_pptx_v2 import EXT_CONTENT_TYPES, NSMAP, PART_CONTENT_TYPES, read_zip
except ImportError as exc:  # pragma: no cover - defensive
    print(f"error: cannot import merge_pptx_v2: {exc}", file=sys.stderr)
    sys.exit(2)

from lxml import etree

CT_NS = NSMAP["ct"]
REL_NS = NSMAP["rel"]


@dataclass
class ValidationResult:
    path: str
    ok: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=dict)

    def err(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "ok": self.ok,
            "errors": self.errors,
            "warnings": self.warnings,
            "stats": self.stats,
        }


def _resolve_rels_target(rels_path: str, target: str) -> str:
    """Resolve a rels Target (relative) to a package-root-relative path.

    Note: top-level ``_rels/.rels`` describes the package root itself; LibreOffice
    emits Targets like ``../customXml/item1.xml`` for these which resolve outside
    the root under strict path semantics. PowerPoint tolerates this, so we strip
    any leading ``../`` segments that escape the root and treat the remainder as
    package-relative.
    """
    if target.startswith("/"):
        return target.lstrip("/")
    rels_dir = os.path.dirname(rels_path)
    part_dir = os.path.dirname(rels_dir)  # strip trailing /_rels
    joined = os.path.join(part_dir, target) if part_dir else target
    resolved = os.path.normpath(joined).replace("\\", "/")
    # Strip leading ../ that would escape the package root.
    while resolved.startswith("../"):
        resolved = resolved[3:]
    return resolved


def _check_zip_integrity(path: Path, result: ValidationResult) -> zipfile.ZipFile | None:
    try:
        zf = zipfile.ZipFile(path, "r")
    except zipfile.BadZipFile as exc:
        result.err(f"zip_corrupt: not a valid zip: {exc}")
        return None
    bad = zf.testzip()
    if bad is not None:
        result.err(f"zip_corrupt: CRC failure on {bad}")
    names = zf.namelist()
    seen: dict[str, int] = {}
    for n in names:
        seen[n] = seen.get(n, 0) + 1
    for n, c in seen.items():
        if c > 1:
            result.err(f"zip_duplicate: {n} appears {c} times")
    result.stats["file_count"] = len(names)
    return zf


def _check_content_types(zf: zipfile.ZipFile, names: list[str], result: ValidationResult) -> None:
    ct_name = "[Content_Types].xml"
    if ct_name not in names:
        result.err("content_type_missing: [Content_Types].xml not found")
        return
    try:
        root = etree.fromstring(zf.read(ct_name))
    except etree.XMLSyntaxError as exc:
        result.err(f"xml_parse: [Content_Types].xml: {exc}")
        return

    defaults: dict[str, str] = {}
    overrides: dict[str, str] = {}
    for el in root.findall(f"{{{CT_NS}}}Default"):
        defaults[el.get("Extension", "").lower()] = el.get("ContentType", "")
    for el in root.findall(f"{{{CT_NS}}}Override"):
        overrides[el.get("PartName", "")] = el.get("ContentType", "")

    # Verify coverage: every non-rels, non-CT file must have Default OR Override
    for n in names:
        if n == ct_name:
            continue
        partname = "/" + n
        if partname in overrides:
            continue
        ext = os.path.splitext(n)[1].lstrip(".").lower()
        if ext and ext in defaults:
            continue
        if n.endswith(".rels"):
            # rels typically covered by Default rels entry
            if "rels" in defaults:
                continue
        result.err(f"content_type_missing: no Default/Override for {n}")

    # Verify Override partnames reference real parts
    for partname in overrides:
        inner = partname.lstrip("/")
        if inner not in names:
            result.err(f"content_type_dangling: Override points to missing part {partname}")

    result.stats["ct_defaults"] = len(defaults)
    result.stats["ct_overrides"] = len(overrides)


def _check_rels(zf: zipfile.ZipFile, names: list[str], result: ValidationResult) -> None:
    rels_files = [n for n in names if n.endswith(".rels")]
    result.stats["rels_count"] = len(rels_files)
    for rels_path in rels_files:
        try:
            root = etree.fromstring(zf.read(rels_path))
        except etree.XMLSyntaxError as exc:
            result.err(f"xml_parse: {rels_path}: {exc}")
            continue
        for rel in root.findall(f"{{{REL_NS}}}Relationship"):
            target = rel.get("Target", "")
            mode = rel.get("TargetMode", "")
            if mode == "External":
                continue
            if not target:
                result.err(f"rels_dangling: {rels_path} has empty Target")
                continue
            resolved = _resolve_rels_target(rels_path, target)
            if resolved not in names:
                category = "chart_rels_broken" if "/charts/" in rels_path else "rels_dangling"
                result.err(f"{category}: {rels_path} -> {target} (resolved {resolved}) missing")


def _check_xml_parse(zf: zipfile.ZipFile, names: list[str], result: ValidationResult) -> None:
    xml_count = 0
    for n in names:
        if not (n.endswith(".xml") or n.endswith(".rels")):
            continue
        xml_count += 1
        try:
            etree.fromstring(zf.read(n))
        except etree.XMLSyntaxError as exc:
            result.err(f"xml_parse: {n}: {exc}")
    result.stats["xml_count"] = xml_count


def _check_chart_chains(zf: zipfile.ZipFile, names: list[str], result: ValidationResult) -> None:
    charts = [n for n in names if re.match(r"ppt/charts/chart\d+\.xml$", n)]
    result.stats["chart_count"] = len(charts)
    for chart in charts:
        rels = f"ppt/charts/_rels/{os.path.basename(chart)}.rels"
        if rels not in names:
            result.warn(f"chart_rels_missing: no rels for {chart}")


def validate(path: Path) -> ValidationResult:
    result = ValidationResult(path=str(path))
    zf = _check_zip_integrity(path, result)
    if zf is None:
        return result
    try:
        names = zf.namelist()
        _check_content_types(zf, names, result)
        _check_rels(zf, names, result)
        _check_xml_parse(zf, names, result)
        _check_chart_chains(zf, names, result)
    finally:
        zf.close()
    return result


def _print_human(result: ValidationResult, verbose: bool) -> None:
    tag = "OK  " if result.ok else "FAIL"
    print(f"[{tag}] {result.path}")
    for e in result.errors:
        print(f"  ERROR: {e}")
    if verbose or not result.ok:
        for w in result.warnings:
            print(f"  WARN:  {w}")
    if verbose:
        for k, v in result.stats.items():
            print(f"  stat   {k}: {v}")


def _scan_templates() -> int:
    skills_dir = REPO / "skills"
    templates = sorted(skills_dir.glob("*/assets/*.pptx"))
    any_fail = False
    results = []
    for t in templates:
        r = validate(t)
        results.append(r)
        if not r.ok:
            any_fail = True
        _print_human(r, verbose=False)
    print(f"\nScanned {len(templates)} templates; {sum(1 for r in results if not r.ok)} failed.")
    return 1 if any_fail else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="validate_pptx.py")
    parser.add_argument("path", nargs="?", help=".pptx file to validate")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--template-scan", action="store_true",
                        help="scan all skills/*/assets/*.pptx")
    args = parser.parse_args(argv)

    if args.template_scan:
        return _scan_templates()

    if not args.path:
        parser.print_usage(sys.stderr)
        return 2

    path = Path(args.path)
    if not path.exists():
        print(f"error: not found: {path}", file=sys.stderr)
        return 2

    result = validate(path)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        _print_human(result, args.verbose)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
