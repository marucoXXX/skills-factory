"""Extract a single-slide rollup template from the official rollup style guide.

Usage:
  python3 tools/extract_rollup_template.py \\
      --source work/rollup_official_templates/standard_format_vF_20250928.pptx \\
      --slide-index 3 \\
      --output skills/customer-profile-pptx/assets/rollup/customer-profile-template.pptx \\
      --layout-name "rollup-2col"

What this does:
  1. Open the official multi-slide rollup style guide pptx.
  2. Extract one selected slide (--slide-index, 1-based).
  3. Strip sample text content from text shapes (so fill_*.py writes into a
     clean placeholder).
  4. Rename shapes to match Pilot 3 fill_*.py conventions:
       - Sample text shape "テキスト プレースホルダー 4" (14pt key message)
         → "Title 1" (SHAPE_MAIN_MESSAGE).
       - Sample text shape "テキスト プレースホルダー 5" (12pt subtitle)
         → "Text Placeholder 2" (SHAPE_CHART_TITLE). For 2-column layouts,
         the right-side instance is renamed "Text Placeholder 2 Right".
       - Sample text shape "テキスト プレースホルダー 3" (6pt source)
         → "Source 3" (Phase 4 fill 側で参照予定).
       - "タイトル 3" (22pt sample title) is removed entirely (fill uses
         "Title 1" for the Main Message slot).
  5. Decoration shapes (object 8 separators, 正方形/長方形 N panels) are
     preserved as-is.
  6. Output the result as a 1-slide pptx.

Design notes:
  - Operates at the OOXML level (zipfile + ElementTree) to avoid python-pptx
     re-serializing and changing layout coordinates.
  - Preserves slideMaster, slideLayouts, theme, and font fallbacks from the
     official template.
  - Output passes tools/check_template_invariants.py.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"a": NS_A, "p": NS_P, "r": NS_R}

# Register namespaces so ElementTree writes them with the conventional prefix.
ET.register_namespace("a", NS_A)
ET.register_namespace("p", NS_P)
ET.register_namespace("r", NS_R)

# Mapping: official-template shape name → rollup-template shape name.
# A "second occurrence" of the same source name (sub-panel on the right) gets
# the suffix; the first occurrence wins the bare rename.
SHAPE_RENAME = {
    "テキスト プレースホルダー 4": ["Title 1"],
    "テキスト プレースホルダー 5": ["Text Placeholder 2", "Text Placeholder 2 Right"],
    "テキスト プレースホルダー 3": ["Source 3"],
}

# Source shape names that should be removed entirely (sample 22pt title).
SHAPES_TO_REMOVE = {"タイトル 3"}


def extract_slide(src_pptx: Path, dst_pptx: Path, slide_idx: int) -> None:
    """Copy `src_pptx` to `dst_pptx`, keeping only slide `slide_idx` (1-based)."""
    if not src_pptx.exists():
        raise FileNotFoundError(f"source pptx not found: {src_pptx}")

    tmp_root = Path(tempfile.mkdtemp(prefix="rollup_extract_"))
    src_dir = tmp_root / "src"
    src_dir.mkdir()
    with zipfile.ZipFile(src_pptx, "r") as z:
        z.extractall(src_dir)

    # Determine total slide count.
    slides_dir = src_dir / "ppt" / "slides"
    all_slides = sorted(
        [p for p in slides_dir.iterdir() if p.name.startswith("slide") and p.suffix == ".xml"],
        key=lambda p: int(p.stem.replace("slide", "")),
    )
    if slide_idx < 1 or slide_idx > len(all_slides):
        raise ValueError(f"--slide-index {slide_idx} out of range (1..{len(all_slides)})")

    keep_slide = all_slides[slide_idx - 1]
    keep_rels = slides_dir / "_rels" / f"{keep_slide.name}.rels"

    # Load presentation.xml + .rels to rebuild a single-slide deck.
    pres_xml = src_dir / "ppt" / "presentation.xml"
    pres_rels = src_dir / "ppt" / "_rels" / "presentation.xml.rels"

    pres_tree = ET.parse(pres_xml)
    pres_root = pres_tree.getroot()
    sld_id_lst = pres_root.find("p:sldIdLst", NS)

    rels_tree = ET.parse(pres_rels)
    rels_root = rels_tree.getroot()
    rels_ns = "http://schemas.openxmlformats.org/package/2006/relationships"

    # Find rId of the slide we want to keep.
    keep_target = f"slides/{keep_slide.name}"
    keep_rid = None
    drop_rids = []
    for rel in list(rels_root):
        target = rel.attrib.get("Target", "")
        rtype = rel.attrib.get("Type", "")
        if "/relationships/slide" not in rtype:
            continue
        if not rtype.endswith("/slide"):
            # /slideMaster, /slideLayout etc — keep
            continue
        if target.endswith(keep_slide.name):
            keep_rid = rel.attrib["Id"]
        else:
            drop_rids.append(rel.attrib["Id"])
            rels_root.remove(rel)

    if keep_rid is None:
        raise RuntimeError(f"could not find rId for {keep_slide.name} in presentation rels")

    # Drop other slides from sldIdLst.
    for sld in list(sld_id_lst):
        rid = sld.attrib.get(f"{{{NS_R}}}id")
        if rid in drop_rids:
            sld_id_lst.remove(sld)

    pres_tree.write(pres_xml, xml_declaration=True, encoding="UTF-8")
    rels_tree.write(pres_rels, xml_declaration=True, encoding="UTF-8")

    # Delete other slide files + their rels.
    for sld in all_slides:
        if sld.name == keep_slide.name:
            continue
        sld.unlink()
        sld_rels = slides_dir / "_rels" / f"{sld.name}.rels"
        if sld_rels.exists():
            sld_rels.unlink()

    # Update [Content_Types].xml to drop the removed slide entries.
    ct_path = src_dir / "[Content_Types].xml"
    ct_tree = ET.parse(ct_path)
    ct_root = ct_tree.getroot()
    for ov in list(ct_root):
        part_name = ov.attrib.get("PartName", "")
        if part_name.startswith("/ppt/slides/") and part_name.endswith(".xml"):
            if not part_name.endswith(keep_slide.name):
                ct_root.remove(ov)
    ct_tree.write(ct_path, xml_declaration=True, encoding="UTF-8")

    # Re-zip into dst_pptx.
    if dst_pptx.exists():
        dst_pptx.unlink()
    dst_pptx.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst_pptx, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(src_dir):
            for f in files:
                full = Path(root) / f
                arc = full.relative_to(src_dir)
                z.write(full, arc.as_posix())

    shutil.rmtree(tmp_root)


def rename_and_clean_shapes(pptx_path: Path) -> dict:
    """Open the (already 1-slide) pptx, rename shapes, blank sample text.

    Returns a dict of {old_name: new_name(s)} for verification.
    """
    tmp_root = Path(tempfile.mkdtemp(prefix="rollup_rename_"))
    work = tmp_root / "work"
    work.mkdir()
    with zipfile.ZipFile(pptx_path, "r") as z:
        z.extractall(work)

    slide_xml = work / "ppt" / "slides" / "slide1.xml"
    if not slide_xml.exists():
        # The single slide may not be slide1.xml after extraction; pick any.
        slide_files = list((work / "ppt" / "slides").glob("slide*.xml"))
        if len(slide_files) != 1:
            raise RuntimeError(f"expected exactly 1 slide, found {len(slide_files)}")
        slide_xml = slide_files[0]

    tree = ET.parse(slide_xml)
    root = tree.getroot()
    sp_tree = root.find("p:cSld/p:spTree", NS)

    rename_log: dict[str, list[str]] = {}
    rename_counters: dict[str, int] = {}

    # Pass 1: identify shapes to remove and shapes to rename.
    to_remove = []
    for sp in list(sp_tree.findall("p:sp", NS)):
        cnv = sp.find("p:nvSpPr/p:cNvPr", NS)
        if cnv is None:
            continue
        name = cnv.attrib.get("name", "")
        if name in SHAPES_TO_REMOVE:
            to_remove.append(sp)
            rename_log.setdefault(name, []).append("(removed)")
            continue
        if name in SHAPE_RENAME:
            new_names = SHAPE_RENAME[name]
            idx = rename_counters.get(name, 0)
            new_name = new_names[idx] if idx < len(new_names) else f"{new_names[-1]} ({idx+1})"
            rename_counters[name] = idx + 1
            cnv.attrib["name"] = new_name
            rename_log.setdefault(name, []).append(new_name)

            # Blank the sample text on renamed shapes (so fill_*.py overwrites cleanly).
            tx_body = sp.find("p:txBody", NS)
            if tx_body is not None:
                _blank_text_body(tx_body)

    # Pass 2: remove sample 22pt title shape.
    for sp in to_remove:
        sp_tree.remove(sp)

    # Pass 3: blank sample text on long decoration paragraphs (e.g. the
    # 「【PPT作成時の留意点】」inside 正方形/長方形 1).
    for sp in sp_tree.findall("p:sp", NS):
        cnv = sp.find("p:nvSpPr/p:cNvPr", NS)
        if cnv is None:
            continue
        name = cnv.attrib.get("name", "")
        if name.startswith("正方形/長方形") or name.startswith("Rectangle"):
            tx_body = sp.find("p:txBody", NS)
            if tx_body is not None:
                # Decoration panels — blank the embedded sample text.
                _blank_text_body(tx_body)

    tree.write(slide_xml, xml_declaration=True, encoding="UTF-8")

    # Re-zip back to pptx_path.
    pptx_path.unlink()
    with zipfile.ZipFile(pptx_path, "w", zipfile.ZIP_DEFLATED) as z:
        for r, _, files in os.walk(work):
            for f in files:
                full = Path(r) / f
                arc = full.relative_to(work)
                z.write(full, arc.as_posix())

    shutil.rmtree(tmp_root)
    return rename_log


def _blank_text_body(tx_body: ET.Element) -> None:
    """Replace all <a:t> text content in a txBody with empty string.

    Preserves <a:rPr>, <a:pPr>, paragraph structure (so the placeholder retains
    its font/size/color), but removes the sample text.
    """
    for t in tx_body.findall(".//a:t", NS):
        t.text = ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, type=Path, help="path to standard_format_vF_20250928.pptx")
    parser.add_argument("--slide-index", required=True, type=int, help="1-based slide index to extract")
    parser.add_argument("--output", required=True, type=Path, help="path to write extracted single-slide pptx")
    parser.add_argument("--layout-name", default="", help="optional human label, written to stderr only")
    args = parser.parse_args()

    print(f"Extracting slide {args.slide_index} from {args.source}", file=sys.stderr)
    extract_slide(args.source, args.output, args.slide_index)
    print(f"  Wrote {args.output} (single-slide)", file=sys.stderr)

    log = rename_and_clean_shapes(args.output)
    print("Shape rename log:", file=sys.stderr)
    for old, news in sorted(log.items()):
        print(f"  '{old}' → {news}", file=sys.stderr)

    print(f"Done: {args.output} ({args.layout_name})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
