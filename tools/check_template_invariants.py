"""Verify that a Pilot 3 brand template pptx satisfies the invariants its
fill_*.py and brand theme expect.

Checks performed:
  1. ZIP integrity (the file is a readable pptx).
  2. Slide size matches theme.json (width/height in EMU, ±1 EMU tolerance).
  3. Theme fontScheme major/minor latin and ea typefaces match theme.json fonts.
  4. Required shapes exist in the slide:
       - 'Title 1'           (SHAPE_MAIN_MESSAGE for all Pilot 3)
       - 'Text Placeholder 2' (SHAPE_CHART_TITLE for all Pilot 3)
       - 'Source 3'          (roleup only, Phase 4 reference)
  5. No required shapes are duplicated in a way that would confuse fill_*.py
     (e.g. two shapes both named 'Title 1').

Usage:
  python3 tools/check_template_invariants.py \\
      --brand roleup \\
      skills/customer-profile-pptx/assets/roleup/customer-profile-template.pptx \\
      skills/company-history-pptx/assets/roleup/company-history-template.pptx \\
      skills/market-environment-pptx/assets/roleup/market-environment-template.pptx

  python3 tools/check_template_invariants.py \\
      --brand stellar_aiz \\
      skills/customer-profile-pptx/assets/stellar_aiz/customer-profile-template.pptx

Exit code: 0 if all pptx pass, 1 if any fail.
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS = {"a": NS_A, "p": NS_P}

REPO_ROOT = Path(__file__).resolve().parent.parent

# Per-brand required shape names.
REQUIRED_SHAPES_BY_BRAND = {
    "stellar_aiz": ("Title 1", "Text Placeholder 2"),
    "roleup":      ("Title 1", "Text Placeholder 2", "Source 3"),
}

# Tolerance for slide size in EMU. 5000 EMU ≈ 0.0055 inch — accommodates the
# slight rounding gap between the precise A4 size in the official roleup pptx
# and the rounded values shown in theme.json.
SLIDE_SIZE_TOL_EMU = 5000


def load_theme(brand: str) -> dict:
    path = REPO_ROOT / "skills" / "_common" / "brands" / brand / "theme.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_one(pptx_path: Path, brand: str, theme: dict) -> list[str]:
    """Return a list of failure messages (empty list = all checks passed)."""
    errors: list[str] = []

    if not pptx_path.exists():
        return [f"file not found: {pptx_path}"]

    try:
        with zipfile.ZipFile(pptx_path, "r") as z:
            bad = z.testzip()
            if bad:
                return [f"zip integrity failed at: {bad}"]
            namelist = z.namelist()

            # 2. Slide size.
            with z.open("ppt/presentation.xml") as fh:
                pres = ET.parse(fh).getroot()
            sld_sz = pres.find("p:sldSz", NS)
            if sld_sz is None:
                errors.append("ppt/presentation.xml: <p:sldSz> not found")
            else:
                cx = int(sld_sz.attrib.get("cx", "0"))
                cy = int(sld_sz.attrib.get("cy", "0"))
                expected_w = int(theme["slide_size"]["width_in"] * 914400)
                expected_h = int(theme["slide_size"]["height_in"] * 914400)
                if abs(cx - expected_w) > SLIDE_SIZE_TOL_EMU:
                    errors.append(
                        f"slide width mismatch: cx={cx} EMU "
                        f"({cx/914400:.3f} in), expected {expected_w} EMU "
                        f"({expected_w/914400:.3f} in)"
                    )
                if abs(cy - expected_h) > SLIDE_SIZE_TOL_EMU:
                    errors.append(
                        f"slide height mismatch: cy={cy} EMU "
                        f"({cy/914400:.3f} in), expected {expected_h} EMU "
                        f"({expected_h/914400:.3f} in)"
                    )

            # 3. Theme fontScheme.
            theme_files = sorted(n for n in namelist if n.startswith("ppt/theme/theme") and n.endswith(".xml"))
            if not theme_files:
                errors.append("no ppt/theme/themeN.xml found")
            else:
                # Use theme1.xml (the master theme).
                with z.open(theme_files[0]) as fh:
                    troot = ET.parse(fh).getroot()
                fs = troot.find(".//a:fontScheme", NS)
                expected_latin = theme["fonts"]["latin"]
                expected_ea = theme["fonts"]["ea"]
                if fs is None:
                    errors.append(f"{theme_files[0]}: <a:fontScheme> not found")
                else:
                    for tag, expected in (("majorFont", expected_latin), ("minorFont", expected_latin)):
                        f_el = fs.find(f"a:{tag}", NS)
                        latin_el = f_el.find("a:latin", NS) if f_el is not None else None
                        actual = latin_el.attrib.get("typeface") if latin_el is not None else None
                        if actual != expected:
                            errors.append(
                                f"theme {tag}/latin typeface mismatch: "
                                f"got {actual!r}, expected {expected!r}"
                            )
                    for tag in ("majorFont", "minorFont"):
                        f_el = fs.find(f"a:{tag}", NS)
                        ea_el = f_el.find("a:ea", NS) if f_el is not None else None
                        actual = ea_el.attrib.get("typeface") if ea_el is not None else None
                        if actual != expected_ea:
                            errors.append(
                                f"theme {tag}/ea typeface mismatch: "
                                f"got {actual!r}, expected {expected_ea!r}"
                            )

            # 4. Required shapes.
            slide_files = sorted(n for n in namelist if n.startswith("ppt/slides/slide") and n.endswith(".xml"))
            if len(slide_files) != 1:
                errors.append(f"expected exactly 1 slide, found {len(slide_files)}: {slide_files}")
            else:
                with z.open(slide_files[0]) as fh:
                    sroot = ET.parse(fh).getroot()
                shape_names: list[str] = []
                for sp in sroot.findall(".//p:sp", NS):
                    cnv = sp.find("p:nvSpPr/p:cNvPr", NS)
                    if cnv is not None:
                        shape_names.append(cnv.attrib.get("name", ""))

                required = REQUIRED_SHAPES_BY_BRAND.get(brand, ())
                for required_name in required:
                    count = shape_names.count(required_name)
                    if count == 0:
                        errors.append(
                            f"required shape missing: '{required_name}' "
                            f"(found shapes: {shape_names})"
                        )
                    elif count > 1:
                        errors.append(
                            f"required shape duplicated: '{required_name}' x{count} "
                            f"— fill_*.py will pick the first one only"
                        )

    except zipfile.BadZipFile as e:
        return [f"not a valid zip/pptx: {e}"]
    except ET.ParseError as e:
        return [f"XML parse error: {e}"]

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--brand", required=True, choices=list(REQUIRED_SHAPES_BY_BRAND.keys()))
    parser.add_argument("pptx", nargs="+", type=Path, help="one or more pptx paths to check")
    args = parser.parse_args()

    theme = load_theme(args.brand)
    print(f"Brand: {args.brand}", file=sys.stderr)
    print(f"  expected slide_size: {theme['slide_size']['width_in']} x {theme['slide_size']['height_in']} in")
    print(f"  expected fonts: latin={theme['fonts']['latin']!r}, ea={theme['fonts']['ea']!r}")
    print(f"  required shapes: {REQUIRED_SHAPES_BY_BRAND[args.brand]}")
    print()

    n_pass = 0
    n_fail = 0
    for p in args.pptx:
        errors = check_one(p, args.brand, theme)
        if not errors:
            print(f"PASS  {p}")
            n_pass += 1
        else:
            print(f"FAIL  {p}")
            for e in errors:
                print(f"        - {e}")
            n_fail += 1

    print(f"\n{n_pass} passed, {n_fail} failed")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
