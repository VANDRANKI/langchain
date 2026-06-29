#!/usr/bin/env python3
"""Verify structural compliance of partner packages in libs/partners/.

Checks that every partner directory has:
  - pyproject.toml
  - A tests/ or tests/unit_tests/ subdirectory
  - A Python package directory matching the folder name pattern

Usage:
    python scripts/check_partner_structure.py
    python scripts/check_partner_structure.py --partner openai
    python scripts/check_partner_structure.py --strict
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PARTNERS_DIR = Path("libs/partners")

REQUIRED_TOP_LEVEL = {"pyproject.toml"}
TEST_DIR_OPTIONS = {"tests", "tests/unit_tests", "tests/integration_tests"}


def check_partner(partner_dir: Path) -> list[str]:
    """Return list of structural issues for a single partner directory."""
    issues: list[str] = []

    for required in REQUIRED_TOP_LEVEL:
        if not (partner_dir / required).exists():
            issues.append(f"Missing {required}")

    has_tests = any((partner_dir / t).is_dir() for t in TEST_DIR_OPTIONS)
    if not has_tests:
        issues.append("Missing tests directory (tests/ or tests/unit_tests/)")

    # Expect a source package directory (e.g. langchain_openai/ for openai)
    pkg_name = f"langchain_{partner_dir.name.replace('-', '_')}"
    pkg_dir = partner_dir / pkg_name
    if not pkg_dir.is_dir():
        # Some partners use a different naming convention — soft warning only
        issues.append(f"Expected package directory '{pkg_name}' not found (may use different name)")

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--partner", metavar="NAME",
        help="Check only this partner (e.g. openai, anthropic)",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Treat naming warnings as errors",
    )
    args = parser.parse_args(argv)

    if not PARTNERS_DIR.exists():
        print(f"ERROR: {PARTNERS_DIR} does not exist.", file=sys.stderr)
        return 1

    if args.partner:
        targets = [PARTNERS_DIR / args.partner]
    else:
        targets = sorted(d for d in PARTNERS_DIR.iterdir() if d.is_dir())

    all_issues: dict[str, list[str]] = {}
    for partner_dir in targets:
        issues = check_partner(partner_dir)
        if issues:
            all_issues[partner_dir.name] = issues

    if all_issues:
        print(f"Structural issues found in {len(all_issues)} partner(s):\n")
        for name, issues in sorted(all_issues.items()):
            for issue in issues:
                print(f"  {name}: {issue}")
        return 1

    checked = len(targets)
    print(f"All {checked} partner package(s) passed structural checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
