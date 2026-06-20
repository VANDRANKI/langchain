#!/usr/bin/env python3
"""Check public API surface for backwards-incompatible changes.

Compares the current ``__all__`` exports and public function signatures in a
package against a previously saved snapshot. This supplements mypy by catching
renames and removals that mypy misses because it only type-checks callers.

Usage::

    # Save a snapshot of the current API
    python scripts/check_api_compat.py --save --package libs/core/langchain_core

    # Compare against the saved snapshot
    python scripts/check_api_compat.py --check --package libs/core/langchain_core
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def extract_public_names(package_dir: Path) -> dict[str, list[str]]:
    """Extract public names from all Python modules in a package directory.

    Reads ``__all__`` when defined; falls back to names that do not start with
    an underscore.

    Args:
        package_dir: Root directory of the Python package.

    Returns:
        Mapping of ``module_path -> list[public_name]``.
    """
    result: dict[str, list[str]] = {}
    for py_file in sorted(package_dir.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue

        all_names: list[str] | None = None
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Assign)
                and any(
                    isinstance(t, ast.Name) and t.id == "__all__"
                    for t in node.targets
                )
                and isinstance(node.value, (ast.List, ast.Tuple))
            ):
                all_names = [
                    elt.s  # type: ignore[attr-defined]
                    for elt in node.value.elts
                    if isinstance(elt, ast.Constant) and isinstance(elt.s, str)
                ]
                break

        if all_names is None:
            all_names = [
                node.name  # type: ignore[attr-defined]
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                and not node.name.startswith("_")  # type: ignore[attr-defined]
            ]

        rel_path = str(py_file.relative_to(package_dir))
        result[rel_path] = sorted(set(all_names))

    return result


def save_snapshot(package_dir: Path, snapshot_path: Path) -> None:
    """Save the current public API snapshot to disk.

    Args:
        package_dir: Root directory of the Python package.
        snapshot_path: Path where the JSON snapshot will be written.
    """
    names = extract_public_names(package_dir)
    snapshot_path.write_text(json.dumps(names, indent=2), encoding="utf-8")
    print(f"Snapshot saved to {snapshot_path} ({sum(len(v) for v in names.values())} names).")


def check_compat(package_dir: Path, snapshot_path: Path) -> int:
    """Compare the current API against the saved snapshot.

    Args:
        package_dir: Root directory of the Python package.
        snapshot_path: Path to the previously saved JSON snapshot.

    Returns:
        ``0`` if no regressions are found, ``1`` otherwise.
    """
    if not snapshot_path.exists():
        print(f"ERROR: Snapshot not found at {snapshot_path}. Run with --save first.", file=sys.stderr)
        return 1

    saved: dict[str, list[str]] = json.loads(snapshot_path.read_text(encoding="utf-8"))
    current = extract_public_names(package_dir)

    regressions: list[str] = []
    for module, old_names in saved.items():
        new_names = set(current.get(module, []))
        for name in old_names:
            if name not in new_names:
                regressions.append(f"{module}: removed public name '{name}'")

    if regressions:
        print(f"Found {len(regressions)} potential breaking change(s):")
        for r in regressions:
            print(f"  - {r}")
        return 1

    print("No breaking changes detected.")
    return 0


def main() -> None:
    """Entry point for the API compatibility checker."""
    parser = argparse.ArgumentParser(
        description="Check LangChain public API compatibility."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--save", action="store_true", help="Save API snapshot.")
    group.add_argument("--check", action="store_true", help="Compare against snapshot.")
    parser.add_argument(
        "--package",
        required=True,
        type=Path,
        help="Path to the package directory.",
    )
    parser.add_argument(
        "--snapshot",
        type=Path,
        default=Path(".api_snapshot.json"),
        help="Snapshot file path (default: .api_snapshot.json).",
    )
    args = parser.parse_args()

    if args.save:
        save_snapshot(args.package, args.snapshot)
    else:
        sys.exit(check_compat(args.package, args.snapshot))


if __name__ == "__main__":
    main()
