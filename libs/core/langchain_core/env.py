"""Utilities for inspecting the LangChain runtime environment.

The primary export is :func:`get_runtime_environment`, which returns a
dictionary of version and platform information.  The result is cached with
:func:`functools.lru_cache` so that repeated calls are cheap.

This information is typically attached to LangSmith traces and API requests
so that the LangChain team can diagnose version-specific issues.
"""

import platform
from functools import lru_cache

from langchain_core import __version__


@lru_cache(maxsize=1)
def get_runtime_environment() -> dict[str, str]:
    """Return a snapshot of the current LangChain runtime environment.

    The returned dictionary is suitable for attaching to LangSmith traces or
    API request headers.  The result is computed once and then cached for the
    lifetime of the process, so this function is safe to call in hot paths.

    Returns:
        A dictionary with the following keys:

        * ``"library"`` — always ``"langchain-core"``.
        * ``"library_version"`` — the installed version of ``langchain-core``.
        * ``"platform"`` — a human-readable string describing the OS and
          hardware (e.g. ``"macOS-14.4-arm64-arm-64bit"``).
        * ``"runtime"`` — always ``"python"``.
        * ``"runtime_version"`` — the Python version string (e.g. ``"3.12.3"``).
    """
    return {
        "library_version": __version__,
        "library": "langchain-core",
        "platform": platform.platform(),
        "runtime": "python",
        "runtime_version": platform.python_version(),
    }
