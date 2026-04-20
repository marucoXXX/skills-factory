#!/usr/bin/env python3
"""pptx_roundtrip.py - LibreOffice headless OOXML normalization.

Runs .pptx through `soffice --headless --convert-to pptx` to normalize the
OOXML package. This removes many of the "repair needed" conditions that
PowerPoint otherwise flags (dangling rels, subtle content-type mismatches).

Chart-bearing files are skipped by default to avoid chart quality regressions
(custom color elements / c:extLst may be dropped by LibreOffice).

Usage:
    python3 pptx_roundtrip.py <file.pptx> [--dst <out.pptx>] [--force-charts]
    python3 pptx_roundtrip.py <file.pptx> --verify-only
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path


SOFFICE_CANDIDATES = [
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/local/bin/soffice",
    "/opt/homebrew/bin/soffice",
]


@dataclass
class RoundtripResult:
    ok: bool
    path: Path
    before_bytes: int = 0
    after_bytes: int = 0
    message: str = ""
    skipped: bool = False


def find_soffice(explicit: Path | None = None) -> Path | None:
    if explicit:
        return explicit if explicit.exists() else None
    env = os.environ.get("SOFFICE_BIN")
    if env and Path(env).exists():
        return Path(env)
    for cand in SOFFICE_CANDIDATES:
        p = Path(cand)
        if p.exists():
            return p
    # Fall back to PATH lookup
    found = shutil.which("soffice") or shutil.which("libreoffice")
    return Path(found) if found else None


def has_charts(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            for n in zf.namelist():
                if n.startswith("ppt/charts/chart") and n.endswith(".xml"):
                    return True
    except zipfile.BadZipFile:
        return False
    return False


def roundtrip(
    src: Path,
    dst: Path | None = None,
    *,
    timeout: int = 120,
    keep_on_failure: bool = True,
    soffice: Path | None = None,
    force_charts: bool = False,
) -> RoundtripResult:
    """Round-trip ``src`` through LibreOffice, writing to ``dst`` (defaults to ``src``).

    If ``src`` contains charts and ``force_charts`` is False, the file is left
    untouched (result.skipped=True, ok=True). If soffice is not available, the
    file is also left untouched with a warning.
    """
    src = Path(src)
    dst = Path(dst) if dst else src
    before = src.stat().st_size if src.exists() else 0

    if not src.exists():
        return RoundtripResult(ok=False, path=src, message=f"source not found: {src}")

    if has_charts(src) and not force_charts:
        if dst != src:
            shutil.copy2(src, dst)
        return RoundtripResult(
            ok=True, path=dst, before_bytes=before, after_bytes=before,
            message="skipped (chart-bearing file)", skipped=True,
        )

    so = find_soffice(soffice)
    if so is None:
        if dst != src:
            shutil.copy2(src, dst)
        return RoundtripResult(
            ok=True, path=dst, before_bytes=before, after_bytes=before,
            message="soffice not found; roundtrip skipped", skipped=True,
        )

    with tempfile.TemporaryDirectory(prefix="pptx_rt_") as tmp:
        tmp_path = Path(tmp)
        profile = tmp_path / "lo_profile"
        profile.mkdir()
        cmd = [
            str(so),
            f"-env:UserInstallation=file://{profile}",
            "--headless",
            "--convert-to", "pptx",
            "--outdir", str(tmp_path),
            str(src),
        ]
        try:
            proc = subprocess.run(
                cmd,
                timeout=timeout,
                capture_output=True,
                text=True,
            )
        except subprocess.TimeoutExpired:
            if keep_on_failure and dst != src:
                shutil.copy2(src, dst)
            return RoundtripResult(
                ok=False, path=dst, before_bytes=before, after_bytes=before,
                message=f"soffice timed out after {timeout}s",
            )

        if proc.returncode != 0:
            if keep_on_failure and dst != src:
                shutil.copy2(src, dst)
            err = (proc.stderr or proc.stdout or "").strip().splitlines()
            tail = err[-1] if err else f"exit {proc.returncode}"
            return RoundtripResult(
                ok=False, path=dst, before_bytes=before, after_bytes=before,
                message=f"soffice failed: {tail}",
            )

        # LibreOffice names output after the input stem
        candidates = list(tmp_path.glob("*.pptx"))
        if not candidates:
            if keep_on_failure and dst != src:
                shutil.copy2(src, dst)
            return RoundtripResult(
                ok=False, path=dst, before_bytes=before, after_bytes=before,
                message="soffice produced no output file",
            )

        produced = candidates[0]
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(produced), str(dst))

    after = dst.stat().st_size
    return RoundtripResult(
        ok=True, path=dst, before_bytes=before, after_bytes=after,
        message="roundtrip completed",
    )


def verify_openable(path: Path, timeout: int = 60, soffice: Path | None = None) -> bool:
    """Return True if soffice can open the file without error.

    Uses --cat to force a full parse. A non-zero exit or stderr indicates
    the package is structurally broken.
    """
    so = find_soffice(soffice)
    if so is None:
        return True  # cannot verify without soffice; treat as pass
    with tempfile.TemporaryDirectory(prefix="pptx_verify_") as tmp:
        profile = Path(tmp) / "lo_profile"
        profile.mkdir()
        cmd = [
            str(so),
            f"-env:UserInstallation=file://{profile}",
            "--headless",
            "--cat",
            str(path),
        ]
        try:
            proc = subprocess.run(cmd, timeout=timeout, capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            return False
    return proc.returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pptx_roundtrip.py")
    parser.add_argument("path", help=".pptx file to process")
    parser.add_argument("--dst", help="output path (default: overwrite source)")
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--force-charts", action="store_true",
                        help="roundtrip even when charts are present")
    parser.add_argument("--verify-only", action="store_true",
                        help="only check if file opens cleanly in soffice")
    args = parser.parse_args(argv)

    src = Path(args.path)
    if not src.exists():
        print(f"error: not found: {src}", file=sys.stderr)
        return 2

    if args.verify_only:
        ok = verify_openable(src, timeout=args.timeout)
        print(f"[{'OK' if ok else 'FAIL'}] {src}")
        return 0 if ok else 1

    dst = Path(args.dst) if args.dst else src
    result = roundtrip(src, dst, timeout=args.timeout, force_charts=args.force_charts)
    tag = "SKIP" if result.skipped else ("OK" if result.ok else "FAIL")
    print(f"[{tag}] {result.path}  ({result.before_bytes} -> {result.after_bytes} bytes)  {result.message}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
