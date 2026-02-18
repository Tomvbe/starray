# Architecture (Phase 0)

## Purpose
Phase 0 provides the baseline scaffolding for an AI software factory CLI:
- load structured configuration,
- start a CLI process,
- persist chat sessions,
- log each turn.

## Initial Components
- `factory.cli`: user entry point (`status`, `chat`).
- `factory.config`: loads and validates app configuration.
- `factory.session`: session creation, append-turn, save/load JSON state.
- `factory.logging_utils`: per-session file logger.

## Data Layout
- `configs/factory.toml`: provider and role model mapping.
- `.factory/sessions/*.json`: serialized session transcripts.
- `.factory/logs/*.log`: per-session operational logs.

## Constraints in Phase 0
- Only one visible persona (Analyst).
- No real provider calls yet.
- No agent graph orchestration yet.
- Runtime targets Python `3.13.12` (`>=3.13,<3.14`) for LangGraph compatibility.

## Next Phases
- Phase 1: provider abstraction + real model calls.
- Phase 2: multi-agent orchestration graph.
- Phase 3+: tool safety, governance, and reliability hardening.
