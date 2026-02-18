# Architecture (Phase 0)

## Purpose
Phase 0 provides the baseline scaffolding for a Starray CLI:
- load structured configuration,
- start a CLI process,
- persist chat sessions,
- log each turn.

## Initial Components
- `starray.cli`: user entry point (`status`, `chat`).
- `starray.config`: loads and validates app configuration.
- `starray.session`: session creation, append-turn, save/load JSON state.
- `starray.logging_utils`: per-session file logger.

## Data Layout
- `configs/starray.toml`: provider and role model mapping.
- `.starray/sessions/*.json`: serialized session transcripts.
- `.starray/logs/*.log`: per-session operational logs.

## Constraints in Phase 0
- Only one visible persona (Analyst).
- No real provider calls yet.
- No agent graph orchestration yet.
- Runtime targets Python `3.13.12` (`>=3.13,<3.14`) for LangGraph compatibility.

## Next Phases
- Phase 1: provider abstraction + real model calls.
- Phase 2: multi-agent orchestration graph.
- Phase 3+: tool safety, governance, and reliability hardening.
