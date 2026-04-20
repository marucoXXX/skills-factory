#!/usr/bin/env python3
"""fix_template_rels.py - Remove dangling relationships and Content-Types entries
from a .pptx template.

Templates authored in PowerPoint can leave behind ``*.rels`` entries that point
to OLE objects or media files that were later deleted from the package. PowerPoint
itself tolerates these (with "修復が必要"), but downstream python-pptx work and
merge-pptxv2 surfaces the brokenness.

This tool rewrites the zip in place (or to --out), dropping any Relationship
whose Target does not resolve to an existing part, and any Content-Types Override
whose PartName does not exist.

Usage:
    python3 tools/fix_template_rels.py <in.pptx> [--out <out.pptx>] [--dry-run]
    python3 tools/fix_template_rels.py --all   # fix every template validation has flagged
"""
from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import zipfile
from pathlib import Path

from lxml import etree

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from validate_pptx import validate, _resolve_rels_target  # noqa: E402

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

# Relationship types that are allowed to be "orphan" in the content XML
# (they represent package-level or structural links that don't appear as
# rId references inside the content).
ORPHAN_SAFE_TYPES = frozenset({
    "slideLayout", "slideMaster", "theme", "notesSlide", "notesMaster",
    "handoutMaster", "tags", "commentAuthors", "comments", "hyperlink",
    "customXml", "customXmlProps", "printerSettings", "presProps",
    "viewProps", "tableStyles", "package",
    # Coauthoring / revision tracking links that PowerPoint manages itself
    "revisionInfo", "changesInfo",
    # notesSlide's rels point back to its parent slide; that backref is valid
    "slide",
})


def _rel_type_leaf(type_url: str) -> str:
    return type_url.rsplit("/", 1)[-1] if type_url else ""


def _collect_content_rids(content_xml_bytes: bytes) -> set[str]:
    """Return the set of rIds referenced anywhere in a content XML part."""
    try:
        root = etree.fromstring(content_xml_bytes)
    except etree.XMLSyntaxError:
        return set()
    used: set[str] = set()
    targets = {f"{{{R_NS}}}id", f"{{{R_NS}}}embed", f"{{{R_NS}}}link"}
    for el in root.iter():
        for attr, val in el.attrib.items():
            if attr in targets and val:
                used.add(val)
    return used


def _xml_bytes(root: etree._Element) -> bytes:
    return etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)


def fix_pptx(src: Path, dst: Path | None = None, *, dry_run: bool = False,
             remove_orphans: bool = False) -> dict:
    """Return {removed_rels, removed_orphans, removed_overrides}."""
    dst = dst or src
    with zipfile.ZipFile(src, "r") as zf:
        contents = {n: zf.read(n) for n in zf.namelist()}

    real_parts = set(contents.keys())
    removed_rels: list[tuple[str, str, str]] = []
    removed_orphans: list[tuple[str, str, str, str]] = []
    # Process all .rels files
    for name in list(contents.keys()):
        if not name.endswith(".rels"):
            continue
        try:
            root = etree.fromstring(contents[name])
        except etree.XMLSyntaxError:
            continue
        changed = False

        # Pre-compute orphan check for slide/slideLayout/slideMaster parts
        used_rids: set[str] | None = None
        if remove_orphans:
            # rels_path like "ppt/slides/_rels/slide1.xml.rels" -> "ppt/slides/slide1.xml"
            content_path = name.replace("/_rels/", "/").removesuffix(".rels")
            if content_path in contents:
                used_rids = _collect_content_rids(contents[content_path])

        for rel in list(root.findall(f"{{{REL_NS}}}Relationship")):
            target = rel.get("Target", "")
            mode = rel.get("TargetMode", "")
            if mode == "External" or not target:
                continue
            resolved = _resolve_rels_target(name, target)
            # Case 1: target does not exist → always remove
            if resolved not in real_parts:
                removed_rels.append((name, rel.get("Id", ""), target))
                root.remove(rel)
                changed = True
                continue
            # Case 2: target exists but rId is never used in content → remove only if opted in
            if remove_orphans and used_rids is not None:
                rid = rel.get("Id", "")
                rtype = _rel_type_leaf(rel.get("Type", ""))
                if rid not in used_rids and rtype not in ORPHAN_SAFE_TYPES:
                    removed_orphans.append((name, rid, rtype, target))
                    root.remove(rel)
                    changed = True
        if changed:
            contents[name] = _xml_bytes(root)

    # Process [Content_Types].xml: drop Override pointing to missing parts
    removed_overrides: list[str] = []
    ct_name = "[Content_Types].xml"
    if ct_name in contents:
        try:
            ct_root = etree.fromstring(contents[ct_name])
            changed = False
            for el in list(ct_root.findall(f"{{{CT_NS}}}Override")):
                partname = el.get("PartName", "")
                inner = partname.lstrip("/")
                if inner and inner not in real_parts:
                    removed_overrides.append(partname)
                    ct_root.remove(el)
                    changed = True
            if changed:
                contents[ct_name] = _xml_bytes(ct_root)
        except etree.XMLSyntaxError:
            pass

    if dry_run:
        return {"removed_rels": removed_rels, "removed_orphans": removed_orphans,
                "removed_overrides": removed_overrides, "dry_run": True}

    # Write out
    if dst == src:
        backup = src.with_suffix(src.suffix + ".bak")
        if not backup.exists():
            shutil.copy2(src, backup)
    dst.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as out:
        for name in sorted(contents.keys()):
            out.writestr(name, contents[name])
    dst.write_bytes(buf.getvalue())

    return {"removed_rels": removed_rels, "removed_orphans": removed_orphans,
            "removed_overrides": removed_overrides, "dry_run": False,
            "output": str(dst)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fix_template_rels.py")
    parser.add_argument("path", nargs="?")
    parser.add_argument("--out")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--all", action="store_true",
                        help="scan skills/*/assets/*.pptx and fix any that have dangling refs")
    parser.add_argument("--remove-orphans", action="store_true",
                        help="also remove orphan rels whose target exists but rId is unused"
                             " (excludes safe structural types like slideLayout/theme/tags)")
    args = parser.parse_args(argv)

    targets: list[Path]
    if args.all:
        templates = sorted((REPO / "skills").glob("*/assets/*.pptx"))
        if args.remove_orphans:
            # --remove-orphans applies to every template (not just the broken ones)
            targets = templates
            print(f"scanning {len(templates)} templates for orphan rels")
        else:
            broken = [t for t in templates if not validate(t).ok]
            if not broken:
                print("no broken templates found")
                return 0
            targets = broken
            print(f"fixing {len(broken)} broken template(s)")
    elif args.path:
        targets = [Path(args.path)]
    else:
        parser.print_usage(sys.stderr)
        return 2

    any_fail = False
    for t in targets:
        dst = Path(args.out) if (args.out and not args.all) else t
        try:
            info = fix_pptx(t, dst, dry_run=args.dry_run,
                            remove_orphans=args.remove_orphans)
        except (zipfile.BadZipFile, OSError) as exc:
            print(f"[FAIL] {t}: {exc}")
            any_fail = True
            continue
        n_rels = len(info["removed_rels"])
        n_orph = len(info.get("removed_orphans", []))
        n_ov = len(info["removed_overrides"])
        if n_rels + n_orph + n_ov == 0:
            continue  # nothing to do, silent
        action = "would remove" if info.get("dry_run") else "removed"
        print(f"[{t.name}] {action} {n_rels} rels, {n_orph} orphans, {n_ov} overrides")
        for rels_file, rid, tgt in info["removed_rels"]:
            print(f"    rels:    {rels_file}  {rid}  -> {tgt}")
        for rels_file, rid, rtype, tgt in info.get("removed_orphans", []):
            print(f"    orphan:  {rels_file}  {rid}  ({rtype}) -> {tgt}")
        for o in info["removed_overrides"]:
            print(f"    ct:      {o}")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
