# AI Software Factory Roadmap

Date: 2026-02-18
Owner: Tom
Status: Draft v1

## Objective
Build a CLI-first AI software factory where the user interacts only with an Analyst persona while hidden specialist agents coordinate planning, architecture, implementation, testing, and security.

## Success Metrics (MVP)
- End-to-end feature delivery from prompts only in a real repository. The agents should ask regular feedback to the user. 
- >=90% of runs produce a valid plan + code diff + test report.
- Provider can be switched by config without code changes.
- All sensitive actions go through explicit approval gates.

## Phase 0 - Foundations (Week 1)
Goal: establish project skeleton, standards, and baseline execution path.

Scope:
1. Create repo structure (`src/`, `tests/`, `configs/`, `docs/`).
2. Define architecture decision record (ADR-001).
3. Add config system for provider/model/role mapping.
4. Add logging and session persistence primitives.

Deliverables:
- Initial project scaffolding.
- `docs/architecture.md` + `docs/adr/ADR-001.md`.
- Config file format and loader.

Acceptance Criteria:
- CLI starts and loads config.
- Session state can be saved and resumed.
- Logging captures each CLI turn.

## Phase 1 - Analyst CLI + Provider Abstraction (Week 1-2)
Goal: provide a usable single-agent conversation loop with pluggable models.

Scope:
1. Implement `factory chat` command (Typer).
2. Build `ModelProvider` interface (chat + structured output).
3. Add LiteLLM-based adapters for OpenAI/Anthropic/Gemini.
4. Add per-role model selection and fallback order.

Deliverables:
- Working Analyst CLI loop.
- Provider adapters and config-based routing.
- `/status`, `/provider` commands.

Acceptance Criteria:
- User can switch provider/model via config only.
- Graceful fallback when primary model fails.
- Structured response parsing works for Analyst outputs.

## Phase 2 - Multi-Agent Orchestration (Week 2-3)
Goal: wire specialist agents behind Analyst with deterministic flow.

Scope:
1. Implement agent contracts:
   - Analyst, Planner, Architect, Implementer, Tester, Security.
2. Implement LangGraph workflow:
   - Analyst -> Planner -> Architect -> Implementer -> Tester -> Security -> Analyst.
3. Define shared state schema and state transitions.
4. Add `/plan` command to inspect current workflow state.

Deliverables:
- Agent prompts/specs with versioning.
- Orchestration graph and state model.
- Workflow execution trace logs.

Acceptance Criteria:
- A single Analyst request triggers full graph traversal.
- Each agent returns schema-valid output.
- Analyst can summarize intermediate results coherently.

## Phase 3 - Tools, Safety, and Governance (Week 3-4)
Goal: execute repository actions safely with policy enforcement.

Scope:
1. Add tool wrappers (read/write files, search, test runner, git status/diff).
2. Add policy engine for allowed/blocked actions.
3. Add approval gates before write/exec/risky actions.
4. Add audit log for every tool call and approval event.

Deliverables:
- Tool execution layer.
- Policy + approval subsystem.
- Audit report format.

Acceptance Criteria:
- No write or command execution without passing policy checks.
- User can approve/deny gated actions in CLI.
- Complete action trail available for each run.

## Phase 4 - Quality and Reliability (Week 4-5)
Goal: make the system stable and testable.

Scope:
1. Add schema validation for every agent output.
2. Add retries/timeouts/circuit-breakers for model/tool failures.
3. Add unit tests for adapters, orchestration, and policy checks.
4. Add integration test for end-to-end feature generation.

Deliverables:
- Test suite and CI baseline.
- Reliability guardrails.
- Error handling and recovery strategy doc.

Acceptance Criteria:
- Automated tests pass in CI.
- Failed model/tool steps recover or fail clearly.
- End-to-end test succeeds on reference project.

## Phase 5 - MVP Release (Week 5)
Goal: release a usable v0.1 with clear docs and demo.

Scope:
1. Run a scripted demo in a sample repo.
2. Publish setup and usage docs.
3. Tag v0.1 release and changelog.

Deliverables:
- `README.md` with quickstart.
- Demo transcript + artifacts.
- Release notes.

Acceptance Criteria:
- New user can run first workflow in <=15 minutes.
- Demo consistently produces plan/design/code/test/security outputs.
- Known limitations documented.

## Post-MVP Backlog (Phase 6+)
1. CI/CD platform integrations (GitHub Actions, GitLab, Jenkins).
2. Long-term project memory and standards retrieval.
3. Multi-repo and parallel task queue support.
4. Cost/latency-aware model routing.
5. Team features: roles, permissions, approval policies.

## Risks and Mitigations
1. Prompt drift across providers.
- Mitigation: strict schemas, role-specific tests, provider regression suite.

2. Tool misuse or unsafe commands.
- Mitigation: explicit policy engine + approval gates + allowlists.

3. Cost blowups from multi-agent calls.
- Mitigation: token budgets per role, caching, adaptive routing.

4. State explosion in long sessions.
- Mitigation: summarization checkpoints + bounded memory windows.

## Immediate Next Actions
1. Scaffold baseline project structure.
2. Implement config loader and provider abstraction interfaces.
3. Build Analyst-only CLI loop.
4. Add first integration test for a mock provider.
