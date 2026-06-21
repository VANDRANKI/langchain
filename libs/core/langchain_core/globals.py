"""Global values and configuration that apply to all of LangChain.

This module owns three process-wide settings:

- **verbose**: When ``True``, LangChain components emit extra informational
  output (e.g. full prompts and responses) to aid with debugging.
- **debug**: When ``True``, even more granular trace information is emitted.
  Setting ``debug=True`` also implies ``verbose=True`` in most components.
- **llm_cache**: An optional :class:`~langchain_core.caches.BaseCache` instance
  used to cache LLM responses.  When ``None`` caching is disabled.

Always use the public :func:`get_*` / :func:`set_*` accessors rather than
touching the module-level ``_verbose``, ``_debug``, and ``_llm_cache``
variables directly.  Direct access can produce subtle, hard-to-reproduce bugs
when multiple threads or libraries share the same interpreter process.
See https://github.com/langchain-ai/langchain/pull/11311#issuecomment-1743780004
for the full explanation.
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
    """Set the process-wide ``verbose`` flag.

    When ``verbose`` is ``True``, LangChain components print extra information
    such as full prompts and model responses.  This is useful during
    development and debugging but is typically disabled in production.

    Args:
        value: ``True`` to enable verbose output; ``False`` to disable it.

    Example:
        ```python
        from langchain_core.globals import set_verbose, get_verbose

        set_verbose(True)
        assert get_verbose() is True
        ```
    """
    global _verbose  # noqa: PLW0603
    _verbose = value


def get_verbose() -> bool:
    """Return the current value of the process-wide ``verbose`` flag.

    Returns:
        ``True`` if verbose output is enabled, ``False`` otherwise.

    Example:
        ```python
        from langchain_core.globals import get_verbose

        if get_verbose():
            print("Verbose mode is on")
        ```
    """
    return _verbose


def set_debug(value: bool) -> None:  # noqa: FBT001
    """Set the process-wide ``debug`` flag.

    When ``debug`` is ``True``, LangChain components emit fine-grained trace
    information in addition to the output controlled by ``verbose``.  In most
    components, enabling ``debug`` also enables ``verbose`` behaviour.

    Args:
        value: ``True`` to enable debug output; ``False`` to disable it.

    Example:
        ```python
        from langchain_core.globals import set_debug, get_debug

        set_debug(True)
        assert get_debug() is True
        ```
    """
    global _debug  # noqa: PLW0603
    _debug = value


def get_debug() -> bool:
    """Return the current value of the process-wide ``debug`` flag.

    Returns:
        ``True`` if debug output is enabled, ``False`` otherwise.

    Example:
        ```python
        from langchain_core.globals import get_debug

        if get_debug():
            print("Debug mode is on")
        ```
    """
    return _debug


def set_llm_cache(value: Optional["BaseCache"]) -> None:
    """Set (or clear) the process-wide LLM response cache.

    When a cache is installed, LangChain language-model wrappers check it
    before making a network request and store new responses in it after
    receiving them.  Passing ``None`` disables caching entirely.

    Args:
        value: A :class:`~langchain_core.caches.BaseCache` instance to use as
            the global LLM cache, or ``None`` to disable caching.

    Example:
        ```python
        from langchain_core.globals import set_llm_cache
        from langchain_core.caches import InMemoryCache

        set_llm_cache(InMemoryCache())
        # ... later, to disable caching:
        set_llm_cache(None)
        ```
    """
    global _llm_cache  # noqa: PLW0603
    _llm_cache = value


def get_llm_cache() -> Optional["BaseCache"]:
    """Return the currently configured process-wide LLM response cache.

    Returns:
        The active :class:`~langchain_core.caches.BaseCache` instance, or
        ``None`` if no cache has been configured.

    Example:
        ```python
        from langchain_core.globals import get_llm_cache

        cache = get_llm_cache()
        if cache is None:
            print("LLM caching is disabled")
        ```
    """
    return _llm_cache
