#!/usr/bin/env python3
"""Prepare vendored sources for a release build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "scripts"


def run(script: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / script)], check=True)


def main() -> int:
    run("checkout_vendor.py")
    run("apply_patches.py")
    run("integrate_dictionary.py")
    run("generate_licenses.py")
    subprocess.run(
        [sys.executable, str(SCRIPTS / "bump_version.py"), "--data-bump", "--build-bump"],
        check=True,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
