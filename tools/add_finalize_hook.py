#!/usr/bin/env python3
"""add_finalize_hook.py - Insert a LibreOffice-roundtrip post-save hook into
every ``skills/*/scripts/fill_*.py``.

What it adds:
  * a self-contained helper ``_finalize_pptx(path)`` that runs ``soffice
    --headless --convert-to pptx`` and gracefully skips if LibreOffice is
    missing or times out. Leaves the original file untouched on failure.
  * a call to ``_finalize_pptx(<output>)`` immediately after the
    ``prs.save(<output>)`` line.

Safe to run multiple times: files that already contain ``_finalize_pptx`` are
skipped. Use ``--dry-run`` to preview and ``--revert`` to strip the hook.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"


HELPER = '''

def _finalize_pptx(path):
    """LibreOffice roundtrip to normalize OOXML so PowerPoint stops asking for repair.

    No-op if soffice is unavailable or the conversion fails; the original file
    is preserved. Added by tools/add_finalize_hook.py.
    """
    import os, shutil, subprocess, tempfile, glob
    candidates = [
        os.environ.get("SOFFICE_BIN"),
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/opt/homebrew/bin/soffice",
        "/usr/local/bin/soffice",
        "/usr/bin/soffice",
        shutil.which("soffice"),
        shutil.which("libreoffice"),
    ]
    soffice = next((c for c in candidates if c and os.path.exists(c)), None)
    if not soffice:
        return
    try:
        with tempfile.TemporaryDirectory(prefix="pptx_rt_") as tmp:
            subprocess.run(
                [soffice, f"-env:UserInstallation=file://{tmp}/prof",
                 "--headless", "--convert-to", "pptx",
                 "--outdir", tmp, str(path)],
                timeout=120, capture_output=True, check=True,
            )
            found = glob.glob(os.path.join(tmp, "*.pptx"))
            if found:
                shutil.move(found[0], str(path))
    except Exception:
        pass

'''.lstrip("\n")

HELPER_MARKER = "def _finalize_pptx("

SAVE_RE = re.compile(
    r"""^(?P<indent>\s*)(?P<prefix>prs\.save|presentation\.save)\((?P<arg>[^)]*)\)(?P<suffix>.*)$""",
    re.MULTILINE,
)

CALL_TEMPLATE = "{indent}_finalize_pptx({arg})\n"


def patch_file(path: Path, *, dry_run: bool) -> str:
    text = path.read_text(encoding="utf-8")
    if HELPER_MARKER in text:
        return "already_hooked"

    match = SAVE_RE.search(text)
    if not match:
        return "no_save_call"

    # Find the last match (some files save at multiple spots; hook the final one).
    matches = list(SAVE_RE.finditer(text))
    last = matches[-1]
    indent = last.group("indent")
    arg = last.group("arg").strip()

    call_line = CALL_TEMPLATE.format(indent=indent, arg=arg)
    insertion_point = last.end()
    # Skip over the trailing newline so insertion appears on the next line.
    if insertion_point < len(text) and text[insertion_point] == "\n":
        insertion_point += 1
    new_text = text[:insertion_point] + call_line + text[insertion_point:]

    # Insert the helper function right after the final top-level import. This
    # avoids NameError cases where `if __name__ == "__main__": main()` sits on
    # one line (so matching before it is fragile) and keeps the helper loaded
    # before main() executes.
    import_re = re.compile(r"^(?:from\s+\S+\s+import\s+.*|import\s+.*)$",
                           re.MULTILINE)
    last_import = None
    for m in import_re.finditer(new_text):
        last_import = m
    if last_import:
        pos = last_import.end()
        # advance past trailing newline
        if pos < len(new_text) and new_text[pos] == "\n":
            pos += 1
        new_text = new_text[:pos] + "\n" + HELPER + new_text[pos:]
    else:
        # no imports — prepend
        new_text = HELPER + new_text

    if dry_run:
        return "would_patch"
    path.write_text(new_text, encoding="utf-8")
    return "patched"


def revert_file(path: Path, *, dry_run: bool) -> str:
    text = path.read_text(encoding="utf-8")
    if HELPER_MARKER not in text:
        return "not_hooked"
    # Remove the helper block (from HELPER_MARKER up to matching blank line after pass)
    # Simpler: drop the exact HELPER block.
    new_text = text.replace(HELPER, "")
    # Remove inserted call lines.
    new_text = re.sub(r"^[ \t]*_finalize_pptx\([^)]*\)\s*\n", "", new_text, flags=re.MULTILINE)
    if dry_run:
        return "would_revert"
    path.write_text(new_text, encoding="utf-8")
    return "reverted"


def iter_targets(only: list[str] | None) -> list[Path]:
    all_ = sorted(SKILLS_DIR.glob("*/scripts/fill_*.py"))
    if not only:
        return all_
    allowed = set(only)
    return [p for p in all_ if p.parent.parent.name in allowed]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="add_finalize_hook.py")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--revert", action="store_true", help="strip the hook from all files")
    parser.add_argument("--only", help="comma-separated list of skill names to patch")
    args = parser.parse_args(argv)

    only = [s.strip() for s in args.only.split(",")] if args.only else None
    targets = iter_targets(only)
    if not targets:
        print("no fill_*.py found")
        return 1

    fn = revert_file if args.revert else patch_file
    counts: dict[str, int] = {}
    for t in targets:
        status = fn(t, dry_run=args.dry_run)
        counts[status] = counts.get(status, 0) + 1
        print(f"[{status}] {t.relative_to(REPO)}")

    print(f"\nSummary: {counts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
