# Contributor Development Reference

A practical reference for developing and testing LangChain integrations.

## Environment Setup

```bash
# From any package directory (e.g., libs/partners/openai/)
uv sync --all-groups

# Run unit tests
make test

# Lint and format
make lint
make format
```

## Package Structure

```
langchain/
├── libs/
│   ├── core/           # langchain-core: base abstractions
│   ├── langchain/      # langchain-classic (legacy)
│   ├── langchain_v1/   # Actively maintained langchain package
│   ├── partners/       # Third-party integrations
│   │   ├── openai/
│   │   ├── anthropic/
│   │   └── ...
│   ├── standard-tests/ # Shared integration test suite
│   └── model-profiles/ # Model configuration data
```

## Writing Tests

Unit tests must not make network calls:

```python
# tests/unit_tests/test_my_feature.py
import pytest
from unittest.mock import MagicMock, patch
from langchain_openai import ChatOpenAI

def test_chat_model_initialization() -> None:
    """Verify model initializes with expected defaults."""
    model = ChatOpenAI(api_key="test-key")
    assert model.model_name == "gpt-4o"  # or latest GA model
```

## Type Hints

All public functions must have complete type hints:

```python
from typing import Optional

def filter_messages(
    messages: list[dict[str, str]],
    *,
    role: Optional[str] = None,
    max_tokens: int = 4096,
) -> list[dict[str, str]]:
    """Filter a list of messages by role or token budget.

    Args:
        messages: List of message dicts with `role` and `content` keys.
        role: If provided, only messages with this role are returned.
        max_tokens: Maximum number of tokens to include in the result.

    Returns:
        Filtered list of messages.
    """
    if role is not None:
        messages = [m for m in messages if m["role"] == role]
    return messages
```

## PR Conventions

PR titles must follow Conventional Commits with a scope:

```
feat(openai): add support for structured output in `ChatOpenAI`
fix(core): resolve type error in `BaseChatModel.invoke`
docs(anthropic): update model ID references to latest GA release
```

Valid types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `perf`

## Model References

- Always use the latest GA model IDs in examples and docstrings
- Never hardcode preview/beta model identifiers
- Run `langchain-profiles refresh` to update model profile data

## Stable Interface Rule

**Never change positional argument order or remove parameters** from exported functions. For new parameters, always use keyword-only arguments with defaults:

```python
def my_function(
    existing_param: str,
    *,
    new_param: str = "default",  # keyword-only, backward compatible
) -> str:
    ...
```
