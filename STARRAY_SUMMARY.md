# Starray Summary

Date: 2026-02-17

## Goal
Build a CLI-first "Starray" where the user talks to a single visible **Analyst** agent, while hidden specialist agents (planning, architecture, implementation, testing, security, etc.) coordinate behind the scenes.

## Core Product Direction
- Do **not** fork Codex as the primary base.
- Do **not** build everything from scratch.
- Use a **hybrid approach**:
  - orchestration framework for multi-agent flow,
  - custom thin domain layer for roles/policies/handoffs,
  - provider abstraction for model portability.

## Recommended Starting Stack
- **LangGraph**: multi-agent orchestration, stateful workflows, handoffs/loops, checkpointing.
- **LiteLLM** (or similar): provider abstraction/routing for OpenAI, Anthropic, Gemini.
- **CLI framework**: Typer (Python) or oclif (TypeScript).
- **Single user-facing persona**: Analyst.

## Why This vs Alternatives

### From scratch
- Too much plumbing cost (state, retries, tool routing, persistence, approvals).

### Forking Codex
- Useful source of ideas, but different product constraints.
- Better to borrow patterns than inherit architecture.

### Framework-led approach
- Faster path to MVP while preserving custom workflow control.

## Proposed MVP (2-3 weeks)
1. CLI conversation loop with Analyst only.
2. Internal agent graph:
   - Analyst -> Planner -> Architect -> Implementer -> Tester -> Security -> Analyst
3. Shared project state/memory and a basic task board.
4. Tool boundary with approval gates (filesystem/git/test commands).
5. Provider-switch config:
   - provider=openai|anthropic|google
   - model=<model_name>
6. End-to-end demo: "build feature from prompt" in one repository.

## How This Differs from Codex/Claude Agent
- Encodes **your SDLC** and governance (not vendor defaults).
- Uses explicit role contracts and auditable handoffs.
- Keeps one consistent front persona (Analyst).
- Supports provider portability and per-task model routing.
- Enforces deterministic quality/security gates.
- Stores organization-specific standards and process memory.
- Integrates deeply with your internal toolchain and policies.

## Build vs Buy Guidance
- If solo/small team optimizing for speed: Codex/Claude Agent alone is often enough.
- If team/org needs repeatable, auditable, policy-driven delivery + model flexibility: custom Starray is worth it.

## Suggested Next Step
Scaffold a starter repo with:
1. baseline architecture,
2. agent contracts,
3. provider adapter interface,
4. first working Analyst-led CLI loop.

## References Mentioned
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph multi-agent guide: https://langchain-ai.github.io/langgraph/how-tos/multi-agent-network-functional/
- OpenAI Codex CLI repo: https://github.com/openai/codex
- Anthropic tool use overview: https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview
- Gemini function calling docs: https://ai.google.dev/gemini-api/docs/function-calling
- MCP spec: https://modelcontextprotocol.io/specification/2024-11-05/index
