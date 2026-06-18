# LangChain Development Guide

A quick reference for contributing to this Python monorepo.

## Monorepo Structure

Each package lives under `libs/` and has its own `pyproject.toml` and
`uv.lock`. Changes are **not** automatically shared across packages —
you must install and test each package independently.

```
libs/
  core/          # langchain-core  (base primitives)
  langchain/     # langchain-classic (legacy)
  langchain_v1/  # langchain (active)
  partners/      # Third-party integrations
  standard-tests/
  model-profiles/
```

## Setup

```bash
# From the root of the package you're working on, e.g. libs/core
cd libs/core
uv sync --all-groups
```

## Running Tests

```bash
# Unit tests (no network)
make test

# Single file
uv run --group test pytest tests/unit_tests/test_specific.py -v
```

## Linting and Formatting

```bash
make lint    # ruff check + mypy
make format  # ruff format
```

## PR Title Format

All PR titles **must** follow Conventional Commits with a scope:

```
feat(core): add retry-with-backoff to BaseLLM
fix(openai): handle rate-limit 429 in streaming calls
docs(anthropic): update model list to include claude-sonnet-4-6
chore(langchain): bump minimum pydantic to 2.6
```

Valid types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`, `ci`.
Scope is **required** — even for the top-level `langchain` package.

## Docstrings

Use Google-style docstrings. Types go in function signatures, **not**
in the docstring body. Use single backticks for inline code references
(`symbol`), not Sphinx double backticks.

```python
def invoke(self, input: str, *, stop: Optional[list[str]] = None) -> str:
    """Run the model on a single string input.

    Args:
        input: The prompt text to send to the model.
        stop: Optional list of stop sequences.

    Returns:
        The model's response string.
    """
```

## Model References

Always use the latest GA model IDs in docs and examples. Verify against
the provider's official documentation — do not rely on memorized names.

## Adding a New Partner

Beyond the code, update these files when adding a new partner package:

- `.github/ISSUE_TEMPLATE/*.yml`
- `.github/dependabot.yml`
- `.github/scripts/pr-labeler-config.json`
- `.github/workflows/check_diffs.yml`
- `.github/workflows/integration_tests.yml`
- `.github/workflows/pr_lint.yml` (add scope to allowed list)
