#!/usr/bin/env bash
# Run `make lint` in every package that has a Makefile.
# Useful after changing langchain-core to surface downstream type errors.
# Usage: ./scripts/lint_all.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
FAILED=()

for makefile in "$ROOT"/libs/*/Makefile "$ROOT"/libs/partners/*/Makefile; do
  dir=$(dirname "$makefile")
  pkg=$(basename "$dir")
  echo "==> Linting $pkg"
  if ! make -C "$dir" lint --no-print-directory; then
    FAILED+=("$pkg")
  fi
done

if [ ${#FAILED[@]} -gt 0 ]; then
  echo ""
  echo "FAILED packages:"
  for p in "${FAILED[@]}"; do
    echo "  - $p"
  done
  exit 1
fi

echo ""
echo "All packages passed lint."
