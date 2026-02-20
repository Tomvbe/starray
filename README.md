# Starray

Phase 0 baseline scaffold for a CLI-first StarRay.

## Install

```bash
pipx install --python 3.13 starray-cli
starray --version
starray init
```

To enable remote provider calls through LiteLLM:

```bash
pipx inject starray-cli "starray-cli[providers]"
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

## Config Resolution
Order of precedence:
1. `--config <path>`
2. `STARRAY_CONFIG` environment variable
3. `~/.config/starray/starray.toml` (or `$XDG_CONFIG_HOME/starray/starray.toml`)
4. `./configs/starray.toml` (repo-local fallback)

If no config exists, run `starray init`.

## Interactive Commands
- `/status`: show active provider/model.
- `/provider`: show provider/model fallback routing.
- `/session`: show current session id.
- `/help`: show available chat commands.
- `exit` or `quit`: save and exit.

## Release
- CI runs on pushes/PRs via `.github/workflows/ci.yml`.
- Publishing runs on tags like `v0.1.2` via `.github/workflows/publish.yml`.
- PyPI publishing uses repository secret `PYPI_API_TOKEN`.
- A helper installer script is available at `scripts/install.sh`.

## Layout
- `src/starray/`: CLI, config, logging, session primitives
- `configs/starray.toml`: provider/model configuration
- `docs/`: architecture notes and ADRs
- `tests/`: baseline tests
