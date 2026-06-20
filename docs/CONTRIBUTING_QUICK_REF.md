# LangChain Contributor Quick Reference

## Package setup

```bash
cd libs/<package>     # e.g. libs/core
uv sync --all-groups  # install dev + test deps
```

## Common commands

```bash
# Run unit tests (no network)
make test

# Lint
make lint

# Format
make format

# Type check
uv run --group lint mypy .
```

## PR title format

```
type(scope): description starting with lowercase
```

Examples:
```
feat(core): add `astream_events` v2 support
fix(openai): handle empty `tool_calls` in response
docs(anthropic): update `claude-opus-4-8` examples
```

Valid types: `feat` `fix` `docs` `chore` `refactor` `test` `ci` `perf`

The scope is **required** — use the package name (e.g. `core`, `openai`,
`anthropic`, `langchain`).

## Adding a new parameter to a public method

New parameters must be **keyword-only** to avoid breaking positional callers:

```python
def my_method(
    self,
    input: str,
    *,
    new_option: bool = False,  # keyword-only
) -> str: ...
```

## Testing checklist

- [ ] Unit test added in `tests/unit_tests/`
- [ ] Test fails before the fix, passes after
- [ ] No real network calls in unit tests (use mocks)
- [ ] Integration test added in `tests/integration_tests/` if relevant
