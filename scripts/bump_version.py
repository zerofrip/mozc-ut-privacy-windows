#!/usr/bin/env python3
"""Bump Mozc version constants after dictionary integration."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = REPO_ROOT / "vendor" / "mozc" / "src" / "version.bzl"


def read_version_values(content: str) -> dict[str, int]:
    values = {}
    for key in ("MAJOR", "MINOR", "BUILD_OSS", "ENGINE_VERSION", "DATA_VERSION"):
        match = re.search(rf"^{key} = (\d+)", content, re.MULTILINE)
        if not match:
            raise ValueError(f"Could not parse {key} from version.bzl")
        values[key] = int(match.group(1))
    return values


def replace_value(content: str, key: str, value: int) -> str:
    return re.sub(
        rf"^({key} = )\d+",
        rf"\g<1>{value}",
        content,
        count=1,
        flags=re.MULTILINE,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Bump Mozc version.bzl values.")
    parser.add_argument(
        "--engine-bump",
        action="store_true",
        help="Increment ENGINE_VERSION and reset DATA_VERSION to 0.",
    )
    parser.add_argument(
        "--data-bump",
        action="store_true",
        help="Increment DATA_VERSION only.",
    )
    parser.add_argument(
        "--build-bump",
        action="store_true",
        help="Increment BUILD_OSS (and BUILD).",
    )
    args = parser.parse_args()

    if not VERSION_FILE.exists():
        print(f"ERROR: {VERSION_FILE} not found", file=sys.stderr)
        return 1

    content = VERSION_FILE.read_text(encoding="utf-8")
    values = read_version_values(content)

    if args.engine_bump:
        values["ENGINE_VERSION"] += 1
        values["DATA_VERSION"] = 0
    if args.data_bump:
        values["DATA_VERSION"] += 1
    if args.build_bump:
        values["BUILD_OSS"] += 1

    content = replace_value(content, "ENGINE_VERSION", values["ENGINE_VERSION"])
    content = replace_value(content, "DATA_VERSION", values["DATA_VERSION"])
    content = replace_value(content, "BUILD_OSS", values["BUILD_OSS"])
    content = replace_value(content, "BUILD", values["BUILD_OSS"])

    VERSION_FILE.write_text(content, encoding="utf-8")
    print(
        "Updated version.bzl: "
        f"{values['MAJOR']}.{values['MINOR']}.{values['BUILD_OSS']}.100 "
        f"(engine={values['ENGINE_VERSION']}, data={values['DATA_VERSION']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
