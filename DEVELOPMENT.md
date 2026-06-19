# Development Guide

This document is the quick-start reference for contributors to the LangChain Python monorepo.

## Monorepo Structure

```
langchain/
├── libs/
│   ├── core/             # langchain-core — base abstractions and primitives
│   ├── langchain/        # langchain-classic (legacy, no new features)
│   ├── langchain_v1/     # Actively maintained langchain package
│   ├── partners/         # Third-party integrations (openai, anthropic, ollama, …)
│   ├── text-splitters/   # Document chunking utilities
│   ├── standard-tests/   # Shared test suite for integrations
│   └── model-profiles/   # Model capability/pricing profiles
└── .github/              # CI/CD workflows and PR templates
```

Each package under `libs/` is **independently versioned** with its own `pyproject.toml` and `uv.lock`.

## Quick Start

### 1. Install dependencies

This monorepo uses [`uv`](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install all dependency groups (test, lint, typing, dev)
uv sync --all-groups

# Or install a specific group only
uv sync --group test
```

When working on a specific package, `cd` into its directory and run the same command:

```bash
cd libs/partners/openai
uv sync --all-groups
```

### 2. Run tests

```bash
# From any package directory that has a Makefile:
make test

# Or invoke pytest directly
uv run --group test pytest tests/unit_tests/ -x --tb=short

# Run a specific test file
uv run --group test pytest tests/unit_tests/test_specific.py -v
```

Unit tests must not make network calls. Integration tests live in `tests/integration_tests/`.

### 3. Lint

```bash
make lint

# Or run individual tools:
uv run --group lint ruff check .
uv run --group lint mypy .
```

### 4. Format

```bash
make format

# Or directly:
uv run --group lint ruff format .
```

Black-compatible formatting is enforced in CI. Always format before committing.

## Code Style Rules

### Stable public interfaces

Never change function signatures, argument positions, or names for exported/public methods without a deprecation plan. Before modifying any public API:

- Check if the function/class is exported in `__init__.py`.
- Add new parameters as keyword-only with a default: `*, new_param: str = "default"`
- Mark experimental features with docstring admonitions.

Ask: *Would this change break someone's code if they used it last week?*

### Error handling

Never use a bare `except:` clause — always catch a specific exception type:

```python
# Bad
try:
    result = do_thing()
except:
    pass

# Good
try:
    result = do_thing()
except ValueError as err:
    msg = f"Failed to do thing: {err}"
    raise RuntimeError(msg) from err
```

Use a `msg` variable for error messages, not f-strings directly in `raise`.

### Docstrings

Use Google-style docstrings. Types go in function signatures, **not** in docstrings.

```python
def send_email(to: str, msg: str, *, priority: str = "normal") -> bool:
    """Send an email to a recipient with specified priority.

    Args:
        to: The email address of the recipient.
        msg: The message body to send.
        priority: Email priority level.

    Returns:
        `True` if email was sent successfully, `False` otherwise.

    Raises:
        InvalidEmailError: If the email address format is invalid.
    """
```

**Do not** use Sphinx double-backtick formatting (` ``code`` `). Use single backticks (`` `code` ``) for all inline code references in docstrings and comments.

### Type hints

All Python code must include type hints and return types. Use keyword-only arguments for new parameters on public APIs.

## PR Title Format

All PR titles must follow [Conventional Commits](https://www.conventionalcommits.org/) with a mandatory scope:

```
type(scope): description
```

Valid types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`, `perf`

Examples:

```
feat(openai): add streaming support for chat completions
fix(core): resolve type hinting issue in RunnableSequence
docs(anthropic): update model reference to Claude 3.7 Sonnet
chore(langchain): update infrastructure dependencies
```

The scope is **not optional** — PRs without a scope are rejected by the title linter.

- Start the description after `type(scope):` with a lowercase letter, unless the first word is a proper noun or a named entity.
- Wrap class/function/variable names in backticks.

## Adding a New Partner Package

When adding a new partner integration, update **all** of these files:

1. `.github/ISSUE_TEMPLATE/*.yml` — add to package dropdown
2. `.github/dependabot.yml` — add dependency update entry
3. `.github/scripts/pr-labeler-config.json` — add file rule and scope-to-label mapping
4. `.github/workflows/_release.yml` — add API key secrets if needed
5. `.github/workflows/auto-label-by-package.yml` — add package label
6. `.github/workflows/check_diffs.yml` — add to change detection
7. `.github/workflows/integration_tests.yml` — add integration test config
8. `.github/workflows/pr_lint.yml` — add to allowed scopes

Missing any of these is the most common reason partner PRs need multiple review rounds.

## Model References

Always use the latest generally available (GA) model IDs in docstrings and examples. Verify against the provider's official documentation before writing — model IDs go stale quickly.

Changing a `model=` default parameter value in code may constitute a **breaking change** — treat it as a public API change.
