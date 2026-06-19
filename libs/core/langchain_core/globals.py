"""Global configuration settings for LangChain.

This module exposes three process-wide settings that control diagnostic
output and LLM response caching:

* ``verbose`` — when ``True``, chains and agents log intermediate steps to
  ``stdout``.  Equivalent to passing ``verbose=True`` on individual objects,
  but applies globally.
* ``debug`` — when ``True``, enables more detailed internal logging than
  ``verbose``.  Intended for troubleshooting framework internals.
* ``llm_cache`` — a :class:`~langchain_core.caches.BaseCache` instance that
  stores LLM responses to avoid redundant API calls.  Set to ``None`` to
  disable caching.

Always use the getter/setter functions below rather than accessing the
module-level ``_verbose``, ``_debug``, and ``_llm_cache`` variables directly.
Direct access bypasses any future change-notification hooks and can produce
confusing behaviour when multiple LangChain sub-packages share the same
interpreter process.

See also: https://github.com/langchain-ai/langchain/pull/11311
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from langchain_core.caches import BaseCache


# DO NOT USE THESE VALUES DIRECTLY!
# Use them only via `get_<X>()` and `set_<X>()` below,
# or else your code may behave unexpectedly with other uses of these global settings:
# https://github.com/langchain-ai/langchain/pull/11311#issuecomment-1743780004
_verbose: bool = False
_debug: bool = False
_llm_cache: Optional["BaseCache"] = None


def set_verbose(value: bool) -> None:  # noqa: FBT001
    """Set a new value for the ``verbose`` global setting.

    When ``verbose`` is ``True``, most chains and agents will log the full
    input and output of each intermediate step to ``stdout``.  This mirrors
    the per-object ``verbose=True`` constructor argument but applies to all
    objects that respect the global flag.

    Args:
        value: ``True`` to enable verbose logging, ``False`` to disable it.
    """
    global _verbose  # noqa: PLW0603
    _verbose = value


def get_verbose() -> bool:
    """Return the current value of the ``verbose`` global setting.

    Returns:
        ``True`` if verbose logging is enabled, ``False`` otherwise.
    """
    return _verbose


def set_debug(value: bool) -> None:  # noqa: FBT001
    """Set a new value for the ``debug`` global setting.

    Debug mode enables more granular logging than ``verbose``.  It is intended
    for diagnosing issues inside the framework itself rather than for normal
    application development.

    Args:
        value: ``True`` to enable debug logging, ``False`` to disable it.
    """
    global _debug  # noqa: PLW0603
    _debug = value


def get_debug() -> bool:
    """Return the current value of the ``debug`` global setting.

    Returns:
        ``True`` if debug logging is enabled, ``False`` otherwise.
    """
    return _debug


def set_llm_cache(value: Optional["BaseCache"]) -> None:
    """Replace the global LLM cache with a new instance.

    The cache is consulted by LLM wrappers before making an API call.  If a
    matching response is found it is returned immediately; otherwise the API is
    called and the result is stored for future requests.

    Args:
        value: A :class:`~langchain_core.caches.BaseCache` implementation to
            use as the LLM cache.  Pass ``None`` to disable caching entirely.
    """
    global _llm_cache  # noqa: PLW0603
    _llm_cache = value


def get_llm_cache() -> Optional["BaseCache"]:
    """Return the currently active LLM cache.

    Returns:
        The active :class:`~langchain_core.caches.BaseCache` instance, or
        ``None`` if LLM caching is disabled.
    """
    return _llm_cache
