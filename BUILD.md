# Build Guide

This document describes how to build Mozc UT Privacy Edition locally on Windows.

## Prerequisites

- Windows 10 1809+ (x64 or ARM64)
- Visual Studio 2022 with Windows 11 SDK and MSVC build tools
- Python 3.12+
- .NET 6+ SDK
- [Bazelisk](https://github.com/bazelbuild/bazelisk)
- CMake 3.20+ (for the updater)
- Git

## Clone and Prepare

```cmd
git clone --recursive https://github.com/mozc-ut-privacy/mozc-ut-privacy-windows.git
cd mozc-ut-privacy-windows
pip install -r requirements.txt
python scripts\checkout_vendor.py
python scripts\apply_patches.py
python scripts\integrate_dictionary.py
python scripts\generate_licenses.py
python scripts\bump_version.py --data-bump --build-bump
```

Or run the combined prepare step:

```cmd
python scripts\prepare_build.py
```

## Build the IME

### x64

```cmd
powershell -File scripts\build_windows.ps1 -Architecture x64
```

### ARM64

```cmd
powershell -File scripts\build_windows.ps1 -Architecture arm64
```

Output MSI: `vendor\mozc\src\bazel-bin\win32\installer\MozcUTPrivacy64.msi`

## Build the Updater

```cmd
cmake -S updater -B updater\build -G "Visual Studio 17 2022" -A x64
cmake --build updater\build --config Release
```

## Package Portable ZIP

```cmd
powershell -File scripts\package_portable.ps1 -Version 3.33.6133.20250601 -Architecture x64 -OutputDir dist
```

## Dictionary Integration

The dictionary merge pipeline:

1. Clones pre-built UT dictionary repositories (jawiki, sudachidict, etc.)
2. Concatenates them into `mozcdic-ut.txt`
3. Deduplicates against the local Mozc tree via `merge_dictionaries.py --mozc-root`
4. Downloads the Japanese Wikipedia title index for cost tuning (build-time only)
5. Writes the result to `vendor/mozc/src/data/dictionary_oss/dictionary10.txt`

To regenerate from latest upstream dictionary sources, edit `vendor/merge-ut-dictionaries/src/merge/make.sh` and uncomment `generate_latest="true"`. This requires substantial disk space (~4+ GB for Wikipedia XML).

## Code Signing

Set these environment variables before running `scripts\sign_artifacts.ps1`:

| Variable | Description |
|----------|-------------|
| `WINDOWS_CODE_SIGNING_CERT_BASE64` | Base64-encoded PFX certificate |
| `WINDOWS_CODE_SIGNING_CERT_PASSWORD` | PFX password |
| `WINDOWS_CODE_SIGNING_TIMESTAMP_URL` | RFC 3161 timestamp server URL |

Signing is optional. CI skips signing when secrets are not configured.

## Evaluation Test

If the Mozc dictionary evaluation test fails after adding UT entries, update `vendor/mozc/src/data/dictionary_oss/evaluation.tsv`:

```cmd
cd vendor\mozc\src
bazelisk test //data/dictionary_oss:evaluation --test_output=errors
```

Follow Mozc's evaluation update procedure to regenerate the expected results.

## Release Process

Releases are automated via GitHub Actions:

1. **Monthly sync** (`monthly-sync.yml`) — Fetches latest upstream on the 1st of each month (UTC), updates `upstream.lock`, and creates a version tag if upstream changed.
2. **Build and release** (`build-release.yml`) — Triggered by tag push; builds x64 and ARM64, packages artifacts, generates checksums and release notes, and publishes a GitHub Release.

Manual release:

```cmd
git tag v3.33.6133.20250601
git push origin v3.33.6133.20250601
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Disk space exhausted during Qt build | Delete `vendor/mozc/src/third_party/qt_src` after `build_qt.py` (done automatically in CI) |
| `git apply` fails | Reset vendor submodules: `python scripts/checkout_vendor.py` then re-apply |
| Dictionary merge network errors | Ensure CI runner has internet access; check Wikimedia and GitHub availability |
| ARM64 build fails | Install ARM64 MSVC tools and build Qt for ARM64 |
