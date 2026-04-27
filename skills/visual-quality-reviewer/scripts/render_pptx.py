#!/usr/bin/env python3
"""Render a PPTX file to per-slide PNG images via LibreOffice + pdftoppm.

Usage:
  render_pptx.py --pptx <path> --out-dir <dir> [--dpi 200]

Output:
  <out-dir>/page_01.png, page_02.png, ...
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def which_or_die(cmd: str) -> str:
    path = shutil.which(cmd)
    if not path:
        raise SystemExit(f"required command not found on PATH: {cmd}")
    return path


def pptx_to_pdf(pptx: Path, work: Path) -> Path:
    soffice = which_or_die("soffice")
    work.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(work),
            str(pptx),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    pdf = work / (pptx.stem + ".pdf")
    if not pdf.exists():
        raise SystemExit(f"LibreOffice did not produce PDF: {pdf}")
    return pdf


def pdf_to_pngs(pdf: Path, out_dir: Path, dpi: int) -> list[Path]:
    pdftoppm = which_or_die("pdftoppm")
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = out_dir / "page"
    subprocess.run(
        [
            pdftoppm,
            "-png",
            "-r",
            str(dpi),
            str(pdf),
            str(prefix),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    pages = sorted(out_dir.glob("page-*.png"))
    renamed: list[Path] = []
    for p in pages:
        num = p.stem.rsplit("-", 1)[-1]
        dst = out_dir / f"page_{int(num):02d}.png"
        p.rename(dst)
        renamed.append(dst)
    return renamed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pptx", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()

    pptx = Path(args.pptx).expanduser().resolve()
    out_dir = Path(args.out_dir).expanduser().resolve()
    if not pptx.exists():
        raise SystemExit(f"pptx not found: {pptx}")

    work = out_dir / "_pdf"
    pdf = pptx_to_pdf(pptx, work)
    pages = pdf_to_pngs(pdf, out_dir, args.dpi)
    shutil.rmtree(work, ignore_errors=True)

    print(f"rendered {len(pages)} pages to {out_dir}")
    for p in pages:
        print(f"  {p.name}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(e.stderr.decode("utf-8", errors="replace") if e.stderr else "")
        raise SystemExit(e.returncode)
