#!/usr/bin/env python3
"""Build and integrate merge-ut-dictionaries into the Mozc vendor tree."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MOZC_ROOT = REPO_ROOT / "vendor" / "mozc"
MERGE_UT_ROOT = REPO_ROOT / "vendor" / "merge-ut-dictionaries"
MERGE_DIR = MERGE_UT_ROOT / "src" / "merge"
DICT_TARGET = MOZC_ROOT / "src" / "data" / "dictionary_oss" / "dictionary10.txt"


def count_dictionary_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with open(path, encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def parse_enabled_sources(make_sh: Path) -> list[str]:
    enabled = []
    pattern = re.compile(r'^([a-z_]+)="true"')
    with open(make_sh, encoding="utf-8") as handle:
        for line in handle:
            match = pattern.match(line.strip())
            if match:
                enabled.append(match.group(1))
    return enabled


def main() -> int:
    if not MOZC_ROOT.exists():
        print(f"ERROR: Mozc vendor tree not found: {MOZC_ROOT}", file=sys.stderr)
        return 1
    if not MERGE_DIR.exists():
        print(f"ERROR: merge-ut directory not found: {MERGE_DIR}", file=sys.stderr)
        return 1

    env = os.environ.copy()
    env["MOZC_ROOT"] = str(MOZC_ROOT)

    print("Building UT dictionary...")
    make_sh = MERGE_DIR / "make.sh"
    shells = ["bash", "sh"] if sys.platform == "win32" else ["bash"]
    last_error: Exception | None = None
    for shell in shells:
        try:
            subprocess.run(
                [shell, str(make_sh)],
                cwd=MERGE_DIR,
                env=env,
                check=True,
            )
            break
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            last_error = exc
    else:
        raise RuntimeError("Failed to run make.sh") from last_error

    ut_output = MERGE_DIR / "mozcdic-ut.txt"
    if not ut_output.exists():
        print(f"ERROR: Dictionary build failed; missing {ut_output}", file=sys.stderr)
        return 1

    line_count = count_dictionary_lines(ut_output)
    if line_count == 0:
        print("ERROR: Generated dictionary is empty.", file=sys.stderr)
        return 1

    shutil.copy2(ut_output, DICT_TARGET)
    print(f"Integrated {line_count} UT dictionary entries into {DICT_TARGET}")

    metadata_dir = REPO_ROOT / "generated"
    metadata_dir.mkdir(parents=True, exist_ok=True)
    metadata_file = metadata_dir / "dictionary_metadata.txt"
    enabled = parse_enabled_sources(MERGE_DIR / "make.sh")
    metadata_file.write_text(
        "\n".join([
            f"entry_count={line_count}",
            f"enabled_sources={','.join(enabled)}",
        ]) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
