# Type Safety in LangChain

LangChain enforces strict type checking via mypy. This guide documents the
type patterns used across the codebase and the common errors contributors
encounter when adding new components.

## Running Type Checks

```bash
# Check a single package
cd libs/partners/openai
uv run --group lint mypy langchain_openai

# Check langchain-core
cd libs/core
uv run --group lint mypy langchain_core

# Check all packages with the lint-all script
bash scripts/lint_all.sh
```

## Pydantic v2 Patterns

All LangChain components inherit from Pydantic v2 `BaseModel` (via
`langchain_core.pydantic_v1` compatibility shim where needed, but new code
should use native Pydantic v2).

### Field Declarations

```python
from typing import Optional
from pydantic import BaseModel, Field, model_validator

class MyChatModel(BaseChatModel):
    # Required field — no default
    model_name: str = Field(..., description="Name of the model to use.")

    # Optional with default
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

    # Optional that may be None
    api_key: Optional[str] = Field(default=None, alias="openai_api_key")

    # Computed/private field (excluded from schema)
    _client: Any = PrivateAttr(default=None)

    @model_validator(mode="after")
    def initialize_client(self) -> "MyChatModel":
        """Build the provider client after all fields are validated."""
        self._client = MyProviderClient(api_key=self.api_key or "")
        return self
```

### Python Version Compatibility

LangChain targets Python 3.9+. Use `Optional[X]` — not `X | None` — for
nullable types. The `|` union syntax only works in Python 3.10+:

```python
# Correct (Python 3.9 compatible)
def get_model(name: Optional[str] = None) -> Optional[BaseChatModel]: ...

# Wrong — fails in Python 3.9
def get_model(name: str | None = None) -> BaseChatModel | None: ...
```

### Return Types on Public Methods

All public methods must have explicit return type annotations:

```python
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult

def _generate(
    self,
    messages: list[BaseMessage],
    stop: Optional[list[str]] = None,
    run_manager: Optional[CallbackManagerForLLMRun] = None,
    **kwargs: Any,
) -> ChatResult:
    response = self._client.complete(messages=[m.content for m in messages])
    return ChatResult(
        generations=[ChatGeneration(message=AIMessage(content=response.text))]
    )
```

## Common mypy Errors and Fixes

### Error: `Returning Any from function declared to return X`

This usually means a dict access or third-party SDK call returns `Any`.
Cast explicitly:

```python
from typing import cast

# SDK returns Any
raw = provider_client.complete(prompt)
text = cast(str, raw["choices"][0]["message"]["content"])
```

### Error: `Incompatible types in assignment`

Usually a mutable default in a Pydantic model. Use `Field(default_factory=list)`:

```python
# Wrong
stop_sequences: list[str] = []  # mutable default — mypy and Pydantic warn

# Correct
stop_sequences: list[str] = Field(default_factory=list)
```

### Error: `Cannot determine type of ...`

Happens when `__all__` in an `__init__.py` references a name that mypy
can't find due to a missing re-export. Add `from module import X as X`
(with the explicit `as X`) to mark the re-export:

```python
# In __init__.py
from langchain_openai.chat_models import ChatOpenAI as ChatOpenAI  # explicit re-export
```

## Writing Stubs for External SDKs

If a provider SDK has no type stubs, create a minimal `py.typed` stub in
the partner package's `types-*` directory:

```python
# libs/partners/myprovider/langchain_myprovider/py.typed
# (empty file — signals to mypy that this package is typed)
```

Then add the stubs directory to `mypy.ini`:

```ini
[mypy-myprovider.*]
ignore_missing_imports = True
```
