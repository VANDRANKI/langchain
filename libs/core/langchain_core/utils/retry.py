"""Retry utilities for LangChain runnable invocations.

Provides helpers for implementing exponential backoff on transient
errors from LLM providers and tools.
"""

from __future__ import annotations

import asyncio
import time
from typing import Callable, TypeVar, Optional

T = TypeVar("T")


def with_retry(
    func: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Call *func*, retrying on specified exceptions with exponential backoff.

    Args:
        func: Zero-argument callable to execute.
        max_attempts: Maximum number of total attempts (including the first).
        base_delay: Initial delay between retries in seconds.
        max_delay: Upper bound on retry delay in seconds.
        exceptions: Exception types that trigger a retry.

    Returns:
        The return value of *func* on success.

    Raises:
        The last exception raised by *func* if all attempts fail.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as exc:
            last_exc = exc
            if attempt < max_attempts - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]


async def async_with_retry(
    func: Callable[[], "asyncio.Coroutine[None, None, T]"],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> T:
    """Async variant of :func:`with_retry`.

    Args:
        func: Zero-argument async callable (coroutine function) to execute.
        max_attempts: Maximum number of total attempts.
        base_delay: Initial delay between retries in seconds.
        max_delay: Upper bound on retry delay in seconds.
        exceptions: Exception types that trigger a retry.

    Returns:
        The return value of *func* on success.

    Raises:
        The last exception raised by *func* if all attempts fail.
    """
    last_exc: Optional[Exception] = None
    for attempt in range(max_attempts):
        try:
            return await func()
        except exceptions as exc:
            last_exc = exc
            if attempt < max_attempts - 1:
                delay = min(base_delay * (2 ** attempt), max_delay)
                await asyncio.sleep(delay)
    raise last_exc  # type: ignore[misc]
