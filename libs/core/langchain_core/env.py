"""Utilities for querying the LangChain runtime environment.

The primary public API is :func:`get_runtime_environment`, which returns a
fixed snapshot of the Python interpreter and ``langchain-core`` version that
was captured the first time the function was called.  Subsequent calls return
the cached result without re-inspecting the interpreter.
"""

import platform
from functools import lru_cache

from langchain_core import __version__


@lru_cache(maxsize=1)
def get_runtime_environment() -> dict[str, str]:
    """Return a snapshot of the current LangChain runtime environment.

    The result is computed once and cached for the lifetime of the process
    (via :func:`functools.lru_cache`).  This makes repeated calls cheap and
    guarantees that all callers in the same process see identical values.

    Returns:
        A dictionary with the following string keys:

        - ``"library"``: always ``"langchain-core"``.
        - ``"library_version"``: the installed version of ``langchain-core``
          (e.g. ``"0.3.0"``).
        - ``"platform"``: a human-readable platform identifier returned by
          :func:`platform.platform` (e.g.
          ``"Linux-5.15.0-x86_64-with-glibc2.35"``).
        - ``"runtime"``: always ``"python"``.
        - ``"runtime_version"``: the Python interpreter version string returned
          by :func:`platform.python_version` (e.g. ``"3.11.7"``).

    Example:
        ```python
        from langchain_core.env import get_runtime_environment

        info = get_runtime_environment()
        print(info["library_version"])  # e.g. "0.3.0"
        print(info["runtime_version"])  # e.g. "3.11.7"
        ```
    """
    return {
        "library_version": __version__,
        "library": "langchain-core",
        "platform": platform.platform(),
        "runtime": "python",
        "runtime_version": platform.python_version(),
    }
