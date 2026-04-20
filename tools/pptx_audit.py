#!/usr/bin/env python3
"""pptx_audit.py - Structural audit for PPTX templates.

Extracts per-template attributes to surface inconsistencies that can feed
template standardization (Phase 3):
  - slide size (cx, cy) in EMU and inches
  - slide master count + first master name
  - theme name + theme file count
  - major/minor font scheme (latin)
  - accent1 color (if solid)

Usage:
    python3 pptx_audit.py                   # scan all skills/*/assets/*.pptx, print CSV
    python3 pptx_audit.py <file.pptx>       # audit a single file
    python3 pptx_audit.py --out audit.csv   # write CSV to file
"""
from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from pathlib import Path

from lxml import etree

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"

P_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

EMU_PER_INCH = 914400


def _safe_parse(data: bytes) -> etree._Element | None:
    try:
        return etree.fromstring(data)
    except etree.XMLSyntaxError:
        return None


def _get_slide_size(zf: zipfile.ZipFile) -> tuple[int, int]:
    if "ppt/presentation.xml" not in zf.namelist():
        return (0, 0)
    root = _safe_parse(zf.read("ppt/presentation.xml"))
    if root is None:
        return (0, 0)
    sz = root.find(f"{{{P_NS}}}sldSz")
    if sz is None:
        return (0, 0)
    return int(sz.get("cx", 0)), int(sz.get("cy", 0))


def _get_theme_info(zf: zipfile.ZipFile) -> tuple[str, str, str, str]:
    theme_files = [n for n in zf.namelist() if n.startswith("ppt/theme/theme")]
    if not theme_files:
        return ("", "", "", "")
    root = _safe_parse(zf.read(sorted(theme_files)[0]))
    if root is None:
        return ("", "", "", "")
    name = root.get("name", "") or ""
    font_scheme = root.find(f".//{{{A_NS}}}fontScheme")
    major = minor = ""
    if font_scheme is not None:
        major_el = font_scheme.find(f".//{{{A_NS}}}majorFont/{{{A_NS}}}latin")
        minor_el = font_scheme.find(f".//{{{A_NS}}}minorFont/{{{A_NS}}}latin")
        if major_el is not None:
            major = major_el.get("typeface", "") or ""
        if minor_el is not None:
            minor = minor_el.get("typeface", "") or ""
    # Accent1 color (only srgbClr is captured; complex schemes left blank)
    accent1 = ""
    a1 = root.find(f".//{{{A_NS}}}clrScheme/{{{A_NS}}}accent1/{{{A_NS}}}srgbClr")
    if a1 is not None:
        accent1 = a1.get("val", "") or ""
    return (name, major, minor, accent1)


def _get_master_count(zf: zipfile.ZipFile) -> int:
    return sum(1 for n in zf.namelist()
               if n.startswith("ppt/slideMasters/slideMaster") and n.endswith(".xml"))


def audit(path: Path) -> dict:
    row = {
        "skill": path.parent.parent.name,
        "template": path.name,
        "slide_cx": 0,
        "slide_cy": 0,
        "slide_inches": "",
        "master_count": 0,
        "theme_count": 0,
        "theme_name": "",
        "major_font": "",
        "minor_font": "",
        "accent1": "",
    }
    try:
        with zipfile.ZipFile(path, "r") as zf:
            cx, cy = _get_slide_size(zf)
            row["slide_cx"] = cx
            row["slide_cy"] = cy
            if cx and cy:
                row["slide_inches"] = f"{cx / EMU_PER_INCH:.3f}x{cy / EMU_PER_INCH:.3f}"
            row["master_count"] = _get_master_count(zf)
            row["theme_count"] = sum(
                1 for n in zf.namelist()
                if n.startswith("ppt/theme/theme") and n.endswith(".xml")
            )
            theme_name, major, minor, accent1 = _get_theme_info(zf)
            row["theme_name"] = theme_name
            row["major_font"] = major
            row["minor_font"] = minor
            row["accent1"] = accent1
    except (zipfile.BadZipFile, OSError) as exc:
        row["error"] = str(exc)
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pptx_audit.py")
    parser.add_argument("path", nargs="?", help=".pptx file to audit (default: scan all)")
    parser.add_argument("--out", help="write CSV to this path instead of stdout")
    args = parser.parse_args(argv)

    if args.path:
        rows = [audit(Path(args.path))]
    else:
        templates = sorted(SKILLS_DIR.glob("*/assets/*.pptx"))
        rows = [audit(t) for t in templates]

    fieldnames = [
        "skill", "template", "slide_cx", "slide_cy", "slide_inches",
        "master_count", "theme_count", "theme_name",
        "major_font", "minor_font", "accent1",
    ]

    def write(stream) -> None:
        writer = csv.DictWriter(stream, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    if args.out:
        out_path = Path(args.out).expanduser()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", newline="", encoding="utf-8") as f:
            write(f)
        print(f"wrote {len(rows)} rows -> {out_path}")
    else:
        write(sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main())
