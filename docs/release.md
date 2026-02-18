# Release Playbook

## One-time Setup
1. Create a PyPI project named `starray`.
2. In GitHub repository settings, add secret `PYPI_API_TOKEN`.
3. Replace placeholder links in `pyproject.toml` `[project.urls]`.

## Per-Release Steps
1. Update `src/starray/__init__.py` version.
2. Update `pyproject.toml` version to match.
3. Update `CHANGELOG.md`.
4. Run locally:
   - `PYTHONPATH=src python -m unittest discover -s tests -q`
   - `PYTHONPATH=src python -m starray.cli --version`
5. Commit and merge to `main`.
6. Create and push tag: `vX.Y.Z`.
7. Verify GitHub Actions:
   - `CI` workflow passes.
   - `Publish` workflow uploads to PyPI.
8. Verify install in clean shell:
   - `pipx install starray`
   - `starray --version`

## Rollback
1. Yank bad release from PyPI.
2. Fix issue and publish a new patch release.
