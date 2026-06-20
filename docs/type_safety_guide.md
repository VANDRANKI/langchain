# Type Safety in LangChain

This guide explains the conventions and tools used to maintain type safety
across the LangChain monorepo.

## Why type safety matters

LangChain exposes a large public API across multiple packages. Strong type
annotations allow:

- Catching breaking changes early with `mypy` in CI.
- IDE autocompletion for end users.
- Self-documenting function signatures that reduce the need for prose docs.

## Required annotation patterns

### Public functions

All public functions **must** include type hints for every parameter and the
return type:

```python
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage


def invoke_with_retry(
    llm: BaseChatModel,
    messages: list[BaseMessage],
    *,
    max_retries: int = 3,
    timeout: float = 30.0,
) -> BaseMessage:
    """Invoke a chat model with automatic retry on transient errors.

    Args:
        llm: The chat model to invoke.
        messages: Ordered list of messages to pass to the model.
        max_retries: Maximum number of retry attempts before raising.
        timeout: Per-attempt timeout in seconds.

    Returns:
        The model's response message.

    Raises:
        langchain_core.exceptions.LangChainException: If all retries fail.
    """
    ...
```

### New parameters on existing public methods

New parameters **must** be keyword-only to avoid positional-argument breakage:

```python
# Good: keyword-only, with a default that preserves existing behavior
def chain_invoke(
    self,
    input: dict,
    config: dict | None = None,
    *,
    return_only_outputs: bool = False,   # new param
) -> dict:
    ...

# Bad: positional param that changes existing callers
def chain_invoke(self, input: dict, config: dict | None = None,
                 return_only_outputs: bool = False) -> dict:
    ...
```

## Running mypy

```bash
cd libs/core          # or the package you changed
uv run --group lint mypy .
```

Mypy must pass with zero errors before a PR is merged.

## Common type errors and fixes

### `error: Argument 1 to "X" has incompatible type`

Usually caused by passing a concrete type where a base class is expected, or
vice versa. Check the expected type in the function signature and cast or
adapt the input.

### `error: Item "None" of "Optional[X]" has no attribute "Y"`

Guard optional values before use:

```python
if result is not None:
    value = result.some_attr
```

### `error: Missing return statement`

Every branch of a function must return a value (or raise). Add `raise
NotImplementedError("unreachable")` as a sentinel for provably-unreachable
branches.
