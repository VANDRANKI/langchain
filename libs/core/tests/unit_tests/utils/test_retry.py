"""Unit tests for langchain_core.utils.retry."""

import asyncio
import pytest
from unittest.mock import MagicMock


def test_with_retry_succeeds_first_try():
    from langchain_core.utils.retry import with_retry

    func = MagicMock(return_value=42)
    result = with_retry(func, max_attempts=3)
    assert result == 42
    func.assert_called_once()


def test_with_retry_succeeds_on_second_attempt():
    from langchain_core.utils.retry import with_retry

    call_count = {"n": 0}

    def func():
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise ValueError("transient")
        return "ok"

    result = with_retry(func, max_attempts=3, base_delay=0.0, exceptions=(ValueError,))
    assert result == "ok"
    assert call_count["n"] == 2


def test_with_retry_raises_after_max_attempts():
    from langchain_core.utils.retry import with_retry

    func = MagicMock(side_effect=RuntimeError("persistent"))
    with pytest.raises(RuntimeError, match="persistent"):
        with_retry(func, max_attempts=3, base_delay=0.0, exceptions=(RuntimeError,))
    assert func.call_count == 3


def test_with_retry_does_not_retry_non_matching_exception():
    from langchain_core.utils.retry import with_retry

    func = MagicMock(side_effect=TypeError("wrong type"))
    with pytest.raises(TypeError):
        with_retry(func, max_attempts=3, base_delay=0.0, exceptions=(ValueError,))
    func.assert_called_once()


@pytest.mark.asyncio
async def test_async_with_retry_succeeds():
    from langchain_core.utils.retry import async_with_retry

    call_count = {"n": 0}

    async def func():
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise ValueError("transient")
        return "ok"

    result = await async_with_retry(func, max_attempts=3, base_delay=0.0, exceptions=(ValueError,))
    assert result == "ok"
    assert call_count["n"] == 2
