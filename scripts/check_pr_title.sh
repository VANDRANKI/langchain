#!/usr/bin/env bash
# check_pr_title.sh
#
# Validates that a PR title follows the Conventional Commits format required
# by this repository's CI title linter (.github/workflows/pr_lint.yml).
#
# Usage:
#   bash scripts/check_pr_title.sh "feat(openai): add streaming support"
#   bash scripts/check_pr_title.sh "$(gh pr view --json title -q .title)"
#
# Exit codes:
#   0  title is valid
#   1  title is invalid (details printed to stderr)

set -euo pipefail

PR_TITLE="${1:-}"

if [[ -z "$PR_TITLE" ]]; then
  echo "Usage: $0 <pr-title>" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Valid types (must match .github/workflows/pr_lint.yml)
# ---------------------------------------------------------------------------
VALID_TYPES="feat|fix|docs|refactor|test|chore|ci|perf|style|revert"

# ---------------------------------------------------------------------------
# Pattern: type(scope): description
#   - type must be one of the valid types above
#   - scope is required (non-empty, no whitespace)
#   - description must start immediately after ": " with at least one character
# ---------------------------------------------------------------------------
PATTERN="^(${VALID_TYPES})\([a-zA-Z0-9_/-]+\): .+$"

if echo "$PR_TITLE" | grep -qE "$PATTERN"; then
  echo "PR title is valid: $PR_TITLE"
  exit 0
fi

# ---------------------------------------------------------------------------
# Diagnosis: give a specific error message for common mistakes
# ---------------------------------------------------------------------------
echo "ERROR: PR title does not match required format." >&2
echo "" >&2
echo "  Required: type(scope): description" >&2
echo "" >&2
echo "  Valid types: $(echo "$VALID_TYPES" | tr '|' ' ')" >&2
echo "" >&2
echo "  Examples of valid titles:" >&2
echo "    feat(openai): add streaming support for chat completions" >&2
echo "    fix(core): resolve type hinting issue in RunnableSequence" >&2
echo "    docs(anthropic): update Claude model references" >&2
echo "    chore(langchain): bump infrastructure dependencies" >&2
echo "    refactor(langchain-v1): extract base retriever to core" >&2
echo "" >&2
echo "  Common mistakes:" >&2
echo "    - Missing scope:      'feat: add feature'         (needs scope in parens)" >&2
echo "    - Wrong type:         'update(openai): ...'       (not in valid types list)" >&2
echo "    - Missing colon:      'feat(openai) add feature'  (needs ': ' after scope)" >&2
echo "    - Capital first word: 'feat(core): Add support'   (use lowercase unless proper noun)" >&2
echo "" >&2
echo "  Got: $PR_TITLE" >&2
exit 1
