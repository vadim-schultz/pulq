# Contributing

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

```bash
ruff check src tests examples benchmarks
ruff format src tests examples benchmarks
mypy src
pytest
```

## Docs

```bash
pip install -e ".[docs]"
sphinx-build -W -b html docs docs/_build
```

Pull requests should keep CI green (Ruff, Mypy, Pytest, Sphinx `-W`).

## Code coverage (Codecov)

CI uploads `coverage.xml` to [Codecov](https://codecov.io) on Python 3.12.

**Repository maintainers:** add a Codecov upload token so uploads are reliable (especially for private repos):

1. Sign in at [codecov.io](https://codecov.io) with GitHub and enable the `pulq` repository.
2. In GitHub: **Settings → Secrets and variables → Actions → New repository secret**
   - Name: `CODECOV_TOKEN`
   - Value: the token from Codecov’s project settings.
3. The workflow already passes `token: ${{ secrets.CODECOV_TOKEN }}`. After the secret exists, you may set `fail_ci_if_error: true` on the Codecov step in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) if you want upload failures to fail CI.

## Publishing to PyPI (trusted publishing)

Releases are built and published by [`.github/workflows/publish.yml`](.github/workflows/publish.yml) using [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC; no long-lived API token in the repo).

**One-time PyPI setup (account owner):**

1. Create a [PyPI](https://pypi.org) account, verify email, and enable **2FA** (required to publish).
2. **Account settings → Publishing → Add a new pending publisher**
   - **PyPI project name:** `pulq` (create the name if the project does not exist yet).
   - **Owner:** `vadim-schultz`
   - **Repository name:** `pulq`
   - **Workflow name:** `publish.yml`
   - **Environment name:** leave blank unless you use a GitHub Environment named in the workflow.
3. Save the pending publisher, then merge and push code so the workflow file exists on the default branch.

**Release:**

1. Tag: `git tag -a v0.1.0 -m "Release v0.1.0"` and `git push origin v0.1.0` (use the version in `pyproject.toml`).
2. On GitHub: **Releases → Draft a new release**, choose the tag, publish the release. The **Publish to PyPI** workflow runs and uploads the distribution.

For a dry run, use **Actions → Publish to PyPI → Run workflow** only after trusted publishing is configured on PyPI, or use [TestPyPI](https://test.pypi.org/) with a separate trusted publisher and workflow if you prefer.
