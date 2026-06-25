# Partner Integration Development Checklist

Use this checklist when adding a new partner integration to the LangChain monorepo.

## Setup

- [ ] Create `libs/partners/<provider>/` directory
- [ ] Initialize `pyproject.toml` following an existing partner as template
- [ ] Add `uv.lock` by running `uv lock` in the partner directory
- [ ] Create `langchain_<provider>/` package with `__init__.py`

## Implementation

- [ ] Implement `ChatModel` subclass if applicable
- [ ] Implement `Embeddings` subclass if applicable
- [ ] All public methods have complete type annotations
- [ ] All public classes/methods have Google-style docstrings with `Args:` and `Returns:`
- [ ] Use latest GA model IDs in examples (verify against provider docs)
- [ ] New parameters use keyword-only arguments: `*, new_param: str = "default"`
- [ ] No use of `eval()`, `exec()`, or `pickle` on user input
- [ ] Proper exception handling (no bare `except:`)

## Testing

- [ ] Unit tests in `libs/partners/<provider>/tests/unit_tests/`
- [ ] Integration tests in `libs/partners/<provider>/tests/integration_tests/`
- [ ] Tests mirror the source code file structure
- [ ] All new features have tests that fail when the feature is broken
- [ ] Mock/fixtures used for all external API calls in unit tests
- [ ] Standard tests from `langchain-standard-tests` are applied

## CI / Infrastructure

- [ ] Added to `.github/ISSUE_TEMPLATE/*.yml` package dropdown
- [ ] Added to `.github/dependabot.yml`
- [ ] Added to `.github/scripts/pr-labeler-config.json`
- [ ] Added allowed scope to `.github/workflows/pr_lint.yml`
- [ ] Added to `.github/workflows/check_diffs.yml`
- [ ] Added to `.github/workflows/integration_tests.yml`

## Documentation

- [ ] Docstrings reference latest GA model IDs
- [ ] No Sphinx-style double-backtick formatting (use single backticks)
- [ ] README covers installation, quick start, and authentication
- [ ] American English spelling throughout

## PR Conventions

- [ ] PR title format: `feat(<provider>): add <Provider> integration`
- [ ] PR description explains the *why* and references any upstream docs
- [ ] No line number references in PR description (they go stale)

## Common Pitfalls

| Issue | Fix |
|---|---|
| Breaking existing signature | Use keyword-only args for new params |
| Stale model references | Check provider docs before committing |
| Flaky integration test | Mock the API call; use VCR or similar |
| Missing `uv.lock` | Run `uv lock` in the partner directory |
| Wrong docstring style | Use Google-style, not Sphinx/NumPy |
