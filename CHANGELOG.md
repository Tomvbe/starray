# Changelog

All notable changes to this project are documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]
### Added
- Added `ModelProvider` abstraction with LiteLLM adapters and deterministic local fallback provider.
- Added `AnalystRuntime` with provider/model fallback routing and provider summary output.
- Added `starray provider` CLI command and `/provider` interactive chat command.
- Added provider optional dependency extra (`starray-cli[providers]`) for LiteLLM support.
- Added `tests/test_analyst.py` coverage for fallback behavior and route summaries.

### Changed
- Extended config schema with provider fallbacks, role fallback models, timeout, and temperature settings.
- Updated chat responses to call the provider runtime and log provider/model fallback metadata.
- Updated default and checked-in config templates with Phase 1 provider routing fields.
- Updated docs to describe provider routing, LiteLLM setup, and `/provider` command usage.
- Updated CLI intro text to reflect Phase 1 provider abstraction readiness.

### Fixed
- Ensured chat remains functional without remote SDKs by automatically falling back to local provider behavior.

## [0.1.2] - 2026-02-18
### Added
- `starray init` command to bootstrap user config at `~/.config/starray/starray.toml` (or XDG path).
- Config resolution order support: CLI flag, env var, user config, repo fallback.
- Tests for CLI config resolution and init bootstrap.

### Changed
- `status` output now shows the active config path.
- Install script now targets package name `starray-cli` and prefers Python 3.13 for pipx install/upgrade.
- Documentation now clearly distinguishes package name (`starray-cli`) from executable (`starray`).

### Fixed
- Global pipx installs now work outside the repo without requiring `configs/starray.toml` in the current directory.
- Missing config error now includes actionable next step (`starray init`).

## [0.1.1] - 2026-02-18
### Added
- Phase 0 CLI scaffold (`status`, `chat`, session persistence, logs).
- Config loader and baseline project structure.
- Python runtime pinning for LangGraph compatibility (`>=3.13,<3.14`).
- Interactive CLI styling, session resume hints, and slash commands.
- Release scaffolding (`--version`, CI workflow, publish workflow, install script).
