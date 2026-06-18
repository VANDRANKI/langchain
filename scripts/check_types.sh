#!/usr/bin/env bash
# Run mypy on all partner packages and core libraries.
# Reports failures at the end so all packages are checked even if one fails.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

failed=()

run_mypy() {
  local dir="$1"
  local pkg="$2"
  printf "Checking %-45s ... " "$pkg"
  if (cd "$dir" && uv run --group lint mypy "$pkg" --no-error-summary 2>&1) > /tmp/mypy_out 2>&1; then
    echo "OK"
  else
    echo "FAIL"
    tail -5 /tmp/mypy_out | sed 's/^/  /'
    failed+=("$pkg")
  fi
}

# Core libraries
run_mypy "$ROOT/libs/core"       "langchain_core"
run_mypy "$ROOT/libs/langchain_v1" "langchain"

# Partner integrations
for partner_dir in "$ROOT"/libs/partners/*/; do
  pkg=$(basename "$partner_dir" | tr '-' '_')
  if [[ -d "$partner_dir/langchain_$pkg" ]]; then
    run_mypy "$partner_dir" "langchain_$pkg"
  fi
done

echo
if [[ ${#failed[@]} -gt 0 ]]; then
  echo "Type check FAILED for:"
  for p in "${failed[@]}"; do
    echo "  - $p"
  done
  exit 1
fi
echo "All type checks passed."
