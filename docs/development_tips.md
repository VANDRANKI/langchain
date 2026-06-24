# Development Tips

Practical notes for contributing to the LangChain Python monorepo.
For the full guide see the [Contributing Guide](https://docs.langchain.com/oss/python/contributing/overview).

## Workspace Setup

This monorepo uses `uv` workspaces. Each package under `libs/` has its own
`pyproject.toml` and `uv.lock`.

```bash
# Sync all dependency groups for the package you're working on
cd libs/core          # or libs/partners/openai, etc.
uv sync --all-groups

# Run unit tests (no network)
make test

# Lint and format
make lint
make format
```

## Dependency Groups

| Group | Purpose |
|-------|-----------------------------------|
| `test` | pytest and test fixtures |
| `lint` | ruff, mypy, and related tools |
| `typing` | mypy stubs for third-party libs |

Install only what you need: `uv sync --group test`.

## Partner Packages

- Each integration lives in `libs/partners/<name>/`.
- Standard tests live in `libs/standard-tests/` and must be run for any
  new integration that extends a base class.
- When adding a new partner, update all CI configuration files listed in
  the `CLAUDE.md` "Adding a new partner" section.

## Public API Stability

Before changing any function exported via `__init__.py`:

1. Check if adding the parameter as keyword-only (`*, new_param=default`)
   keeps existing callers working.
2. Warn in the docstring with a `!!! warning` MkDocs admonition if the
   change is experimental.
3. Never move a required positional argument.

## Docstring Format

Use Google style with type hints in the function signature, not the docstring:

```python
def my_func(x: int, *, flag: bool = False) -> str:
    """One-line summary.

    Args:
        x: Description of x.
        flag: Description of flag.

    Returns:
        Description of return value.

    Raises:
        ValueError: When x is negative.
    """
```

Do NOT use Sphinx double-backtick (` ``code`` `). Use single backticks.

## PR Conventions

Titles must follow `type(scope): description` with a scope — e.g.:
- `fix(core): resolve type error in vector store`
- `feat(openai): add streaming tool call support`

Start the description after the colon with a **lowercase** letter unless
the first word is a proper noun or a named entity in backticks.

## Model References

Always use the latest GA model ID when writing docstring examples —
never hardcode preview or deprecated identifiers. Verify current IDs
against the provider's official docs before writing or updating examples.
