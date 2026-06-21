"""Utilities for printing system and LangChain package information.

Primarily useful for bug reports and debugging: running
``python -m langchain_core.sys_info`` (or calling :func:`print_sys_info`
directly) prints the OS, Python version, and the versions of every installed
``langchain*`` / ``langgraph*`` package and their direct dependencies.
"""

import pkgutil
import platform
import re
import sys
from collections.abc import Sequence
from importlib import metadata, util


def _get_sub_deps(packages: Sequence[str]) -> list[str]:
    """Collect the direct dependencies of a set of installed packages.

    For each package in *packages*, the function reads its distribution
    metadata to discover declared requirements and accumulates any dependency
    whose name is *not* already in *packages* (normalised to ``snake_case``
    with hyphens replaced by underscores).  This is a best-effort listing
    based on the ``Requires-Dist`` metadata entries; extras and environment
    markers are not evaluated.

    Args:
        packages: Names of the installed packages whose sub-dependencies
            should be discovered.  Hyphens and underscores are both accepted
            (e.g. ``"langchain-core"`` and ``"langchain_core"`` are treated
            identically).

    Returns:
        A sorted (case-insensitive) list of dependency names that are *not*
        already listed in *packages*.  The list contains each dependency at
        most once even if multiple packages in *packages* share it.
    """
    sub_deps = set()
    underscored_packages = {pkg.replace("-", "_") for pkg in packages}

    for pkg in packages:
        try:
            required = metadata.requires(pkg)
        except metadata.PackageNotFoundError:
            continue

        if not required:
            continue

        for req in required:
            # Extract package name (e.g., "httpx<1,>=0.23.0" -> "httpx")
            match = re.match(r"^([a-zA-Z0-9_.-]+)", req)
            if match:
                pkg_name = match.group(1)
                if pkg_name.replace("-", "_") not in underscored_packages:
                    sub_deps.add(pkg_name)

    return sorted(sub_deps, key=lambda x: x.lower())


def print_sys_info(*, additional_pkgs: Sequence[str] = ()) -> None:
    """Print a diagnostic summary of the environment to standard output.

    The output is structured into three sections:

    1. **System Information** - OS name, OS version, and Python version.
    2. **Package Information** - Installed versions of every ``langchain*``
       and ``langgraph*`` package found on ``sys.path``, plus any packages
       listed in *additional_pkgs*.  Key packages (``langchain_core``,
       ``langchain``, ``langchain_community``, ``langsmith``) are always
       shown first.
    3. **Other Dependencies** - Direct dependencies of the packages listed
       above that are not themselves in that list.

    Packages that are not installed are collected and printed in a separate
    "Optional packages not installed" section rather than silently omitted.

    Args:
        additional_pkgs: Extra package names to include in the diagnostic
            output alongside the auto-discovered ``langchain*``/``langgraph*``
            packages.  Useful when diagnosing issues with integration packages
            that do not follow the ``langchain`` naming convention.

    Example:
        ```python
        from langchain_core.sys_info import print_sys_info

        # Basic usage
        print_sys_info()

        # Include an extra package in the report
        print_sys_info(additional_pkgs=["openai", "tiktoken"])
        ```
    """
    # Packages that do not start with "langchain" prefix.
    other_langchain_packages = [
        "langsmith",
        "deepagents",
        "deepagents-cli",
    ]

    langchain_pkgs = [
        name for _, name, _ in pkgutil.iter_modules() if name.startswith("langchain")
    ]

    langgraph_pkgs = [
        name for _, name, _ in pkgutil.iter_modules() if name.startswith("langgraph")
    ]

    all_packages = sorted(
        set(
            langchain_pkgs
            + langgraph_pkgs
            + other_langchain_packages
            + list(additional_pkgs)
        )
    )

    # Always surface these packages to the top
    order_by = ["langchain_core", "langchain", "langchain_community", "langsmith"]

    for pkg in reversed(order_by):
        if pkg in all_packages:
            all_packages.remove(pkg)
            all_packages = [pkg, *list(all_packages)]

    system_info = {
        "OS": platform.system(),
        "OS Version": platform.version(),
        "Python Version": sys.version,
    }
    print()
    print("System Information")
    print("------------------")
    print("> OS: ", system_info["OS"])
    print("> OS Version: ", system_info["OS Version"])
    print("> Python Version: ", system_info["Python Version"])

    # Print out only langchain packages
    print()
    print("Package Information")
    print("-------------------")

    not_installed = []

    for pkg in all_packages:
        try:
            found_package = util.find_spec(pkg)
        except Exception:
            found_package = None
        if found_package is None:
            not_installed.append(pkg)
            continue

        # Package version
        try:
            package_version = metadata.version(pkg)
        except Exception:
            package_version = None

        # Print package with version
        if package_version is not None:
            print(f"> {pkg}: {package_version}")

    if not_installed:
        print()
        print("Optional packages not installed")
        print("-------------------------------")
        for pkg in not_installed:
            print(f"> {pkg}")

    sub_dependencies = _get_sub_deps(all_packages)

    if sub_dependencies:
        print()
        print("Other Dependencies")
        print("------------------")

        for dep in sub_dependencies:
            try:
                dep_version = metadata.version(dep)
            except Exception:
                dep_version = None

            if dep_version is not None:
                print(f"> {dep}: {dep_version}")


if __name__ == "__main__":
    print_sys_info()
