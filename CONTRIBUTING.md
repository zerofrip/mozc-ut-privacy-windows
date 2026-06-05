# Contributing

Thank you for contributing to Mozc UT Privacy Edition.

## Project Model

This repository is an **orchestration project**, not a Mozc fork. We vendor upstream sources as git submodules and apply minimal patches from `patches/`.

**Do not** make large changes directly in `vendor/mozc/` or `vendor/merge-ut-dictionaries/`. Instead:

1. Create a patch in `patches/mozc/` or `patches/merge-ut/`
2. Document the rationale in your pull request
3. Keep patches small and focused

## Development Workflow

```bash
git clone --recursive https://github.com/mozc-ut-privacy/mozc-ut-privacy-windows.git
cd mozc-ut-privacy-windows
python scripts/checkout_vendor.py
python scripts/apply_patches.py
```

### Creating Patches

After making changes in a vendor tree:

```bash
cd vendor/mozc
git diff > ../../patches/mozc/0003-my-change.patch
```

Verify the patch applies cleanly to a fresh upstream checkout before submitting.

### Updating the License Manifest

When adding a new dependency or dictionary source:

1. Add an entry to `licenses/manifest.yaml`
2. Add the full license text to `licenses/`
3. Run `python scripts/generate_licenses.py --check`

## Upstream Sync Policy

- Upstream Mozc and merge-ut-dictionaries are synced automatically on the 1st of each month (UTC).
- Manual sync: `python scripts/sync_upstream.py`
- SHAs are pinned in `upstream.lock` for reproducible builds.

## Pull Request Guidelines

- One logical change per PR
- Include a clear description of what and why
- Verify patches apply to the current upstream SHA
- Do not add telemetry, analytics, or network calls to the IME
- Update documentation if behavior changes

## Code Style

- **Python**: Follow PEP 8; use type hints for new scripts
- **PowerShell**: Use `$ErrorActionPreference = 'Stop'`
- **C++**: C++20, WinHTTP for networking, no external dependencies in the updater

## Reporting Issues

- Build failures: Include the full CI log and `upstream.lock` contents
- Dictionary issues: Specify which UT sources are affected
- Security issues: See [SECURITY.md](SECURITY.md)
