# Releasing

PULQ is published to **PyPI** and documentation is built on **Read the Docs** when you merge to `main` with an updated version (see [Release on Main Merge](https://github.com/vadim-schultz/pulq/blob/main/.github/workflows/release.yml)).

## Release checklist

1. Bump `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` for that version.
3. Merge to `main`.

The **Release on Main Merge** workflow will:

- Read the version from `pyproject.toml`.
- Skip if git tag `v<version>` already exists (avoids duplicate releases).
- Otherwise: create and push the tag, build the sdist/wheel, publish to PyPI, and create a GitHub release.

Read the Docs is connected to the GitHub repository; new tags/releases trigger a documentation build automatically when your [Read the Docs project](https://readthedocs.org/projects/pulq/) is configured with the default GitHub integration.

## PyPI trusted publishing

Publishing uses [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) (OIDC from GitHub Actions). No long-lived PyPI token is stored in GitHub secrets.

Configure **both** workflows that call `pypa/gh-action-pypi-publish` (otherwise manual or fallback runs will fail with auth errors):

1. Open PyPI: **Your project** → **pulq** → **Publishing** → **Add a new pending publisher** (or manage existing publishers).
2. For each workflow file, add a publisher:

   | Field | Value |
   | ----- | ----- |
   | **PyPI Project Name** | `pulq` |
   | **Owner** | `vadim-schultz` |
   | **Repository name** | `pulq` |
   | **Workflow name** | `release.yml` **or** `publish.yml` |
   | **Environment name** | *(leave empty unless you use a GitHub Environment)* |

3. Save. Repeat for the other workflow name if you use both.

The **Release on Main Merge** workflow (`.github/workflows/release.yml`) needs `release.yml` registered. The **Manual PyPI Publish** workflow (`.github/workflows/publish.yml`) needs `publish.yml` registered if you run it (including when it is triggered by a published GitHub release).

### GitHub Actions permissions

Both workflows set `permissions: id-token: write` for OIDC. The release workflow also sets `contents: write` so it can push tags and create releases.

## Manual PyPI publish

Use **Actions** → **Manual PyPI Publish** → **Run workflow**. Optionally enable **Skip PyPI upload** to only build artifacts locally in the job log (dry run).

## Version and docs metadata

- Package version: `pyproject.toml` → `[project].version`.
- Sphinx `release` in `docs/conf.py` is maintained separately; align it with the package version when you cut a release so on-site docs match PyPI.
