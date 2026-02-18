# Starray

Phase 0 baseline scaffold for a CLI-first Starray.

## Install

```bash
pipx install starray
starray --version
```

If you prefer source install:

```bash
git clone <repo-url>
cd starray
pyenv install 3.13.12 --skip-existing
pyenv local 3.13.12
python -m venv .venv
source .venv/bin/activate
pip install -e .
starray
starray status
starray chat --message "hello"
starray --session-id <session_id>
starray chat --session-id <session_id>
```

## Python Version
- Required: `3.13.12`
- Supported range: `>=3.13,<3.14` (LangGraph dependency compatibility)

## Session Resume
- When chat exits, the CLI prints `Session saved: <session_id>`.
- Resume a session with:
  - `starray --session-id <session_id>` (interactive default)
  - `starray chat --session-id <session_id>`

## Interactive Commands
- `/status`: show active provider/model.
- `/session`: show current session id.
- `/help`: show available chat commands.
- `exit` or `quit`: save and exit.

## Release
- CI runs on pushes/PRs via `.github/workflows/ci.yml`.
- Publishing runs on tags like `v0.1.1` via `.github/workflows/publish.yml`.
- PyPI publishing uses repository secret `PYPI_API_TOKEN`.
- A helper installer script is available at `scripts/install.sh`.

## Layout
- `src/starray/`: CLI, config, logging, session primitives
- `configs/starray.toml`: provider/model configuration
- `docs/`: architecture notes and ADRs
- `tests/`: baseline tests
