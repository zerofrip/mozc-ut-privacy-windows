#!/usr/bin/env python3
"""Compute the release version string for builds."""

from __future__ import annotations

import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LOCK_FILE = REPO_ROOT / "upstream.lock"


def parse_lock() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in LOCK_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def read_version_bzl(mozc_sha: str) -> tuple[int, int, int]:
    local_file = REPO_ROOT / "vendor" / "mozc" / "src" / "version.bzl"
    if local_file.exists():
        content = local_file.read_text(encoding="utf-8")
    else:
        url = (
            "https://raw.githubusercontent.com/google/mozc/"
            f"{mozc_sha}/src/version.bzl"
        )
        with urllib.request.urlopen(url, timeout=60) as response:
            content = response.read().decode("utf-8")

    major = int(re.search(r"^MAJOR = (\d+)", content, re.MULTILINE).group(1))
    minor = int(re.search(r"^MINOR = (\d+)", content, re.MULTILINE).group(1))
    build = int(re.search(r"^BUILD_OSS = (\d+)", content, re.MULTILINE).group(1))
    return major, minor, build


def main() -> int:
    lock = parse_lock()
    major, minor, build = read_version_bzl(lock["mozc"])
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    print(f"{major}.{minor}.{build}.{date_str}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
