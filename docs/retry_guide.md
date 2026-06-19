# Retry Guide

LangChain provides retry helpers in `langchain_core.utils.retry` for
wrapping LLM calls and tool invocations that may fail transiently.

## Basic usage

```python
from langchain_core.utils.retry import with_retry
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-5.4")

result = with_retry(
    lambda: llm.invoke("Hello"),
    max_attempts=3,
    base_delay=1.0,
)
```

## Async usage

```python
from langchain_core.utils.retry import async_with_retry

result = await async_with_retry(
    lambda: llm.ainvoke("Hello"),
    max_attempts=3,
    base_delay=1.0,
)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_attempts` | `3` | Total attempts including the first |
| `base_delay` | `1.0` | Initial retry delay in seconds |
| `max_delay` | `30.0` | Cap on retry delay |
| `exceptions` | `(Exception,)` | Exception types that trigger retry |

## Selecting which exceptions to retry

Only retry transient errors (rate limits, timeouts). Do not retry
authentication errors or invalid request errors:

```python
from langchain_core.utils.retry import with_retry

with_retry(
    lambda: llm.invoke(prompt),
    exceptions=(RateLimitError, TimeoutError),
)
```
