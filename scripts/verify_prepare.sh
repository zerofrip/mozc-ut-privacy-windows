#!/usr/bin/env bash
# Verify the pre-build pipeline (vendor checkout through dictionary merge).
# Run on Linux/macOS/WSL before attempting a full Windows build.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${REPO_ROOT}"

echo "==> Checking Python dependencies"
python3 -c "import jaconv" 2>/dev/null || pip install jaconv

echo "==> Running prepare_build.py"
python3 scripts/prepare_build.py

echo "==> Verifying outputs"
test -s vendor/mozc/src/data/dictionary_oss/dictionary10.txt
test -s vendor/mozc/src/data/installer/LICENSES.txt
test -s vendor/mozc/src/data/installer/THIRD_PARTY_LICENSES.txt
test -s vendor/mozc/src/data/installer/CREDITS.txt

LINES=$(wc -l < vendor/mozc/src/data/dictionary_oss/dictionary10.txt)
echo "Dictionary entries: ${LINES}"
echo "Prepare pipeline OK. Continue with scripts/build_windows.ps1 on Windows."
