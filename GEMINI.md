# Gestia AI Business Assistant — Coding Agent Guide

## Prerequisites

Install dependencies (one-time):
```bash
agents-cli install
```

---

## Project Overview

This is an **ADK 2.0 multi-agent workflow** that acts as an AI Business Copilot.
The root workflow in `app/agent.py` orchestrates 7 nodes:

```
process_input → intent_classifier → route_intent → <domain_agent>
```

Domain agents: `sales_agent`, `product_agent`, `customer_agent`,
`analytics_agent`, `insights_agent`, `general_agent`, `out_of_scope_handler`.

**Critical rule:** The assistant is read-only. No tool, agent, or node may
ever create, update, or delete business data.

---

## Development Phases

### Phase 1: Understand Requirements
Read `README.md` for architecture context. Understand the tenant isolation
pattern (`business_id` via `ctx.state`) before modifying any tool or agent.

### Phase 2: Build and Implement
- Agent logic lives in `app/agents/`.
- Tool stubs live in `app/tools/` and delegate to `app/app_utils/services.py`.
- Shared schemas are in `app/app_utils/typing.py`.
- Shared prompts are in `app/app_utils/prompts.py`.
- Use `agents-cli playground` for interactive testing.

### Phase 3: The Evaluation Loop
Add eval cases in `eval/`. Run `agents-cli eval generate`, then
`agents-cli eval grade`. Iterate until satisfied.

### Phase 4: Pre-Deployment Tests
Run `uv run pytest tests/unit tests/integration`. Fix issues until all pass.

### Phase 5: Deploy
**Requires explicit human approval.** Run `agents-cli deploy` only after
user confirms.

---

## Development Commands

| Command | Purpose |
|---|---|
| `agents-cli playground` | Interactive local testing |
| `uv run pytest tests/unit tests/integration` | Run all tests |
| `agents-cli eval generate` | Run agent on eval dataset |
| `agents-cli eval grade` | Grade agent responses |
| `agents-cli eval compare` | Regression diff between two grade results |
| `agents-cli eval analyze` | Cluster failure modes |
| `agents-cli eval optimize` | Auto-tune agent prompts |
| `agents-cli lint` | Code quality check |
| `agents-cli deploy` | Deploy to dev (needs approval) |
| `agents-cli scaffold enhance` | Add deployment target or CI/CD |

---

## Architecture Rules (enforce these always)

### Tenant isolation
- `business_id` is always read from `ctx.state["business_id"]`.
- Every tool call **must** receive `business_id` as its first argument.
- Never hardcode a business_id in tools or agents.

### Read-only contract
- Tools only call `get_*` methods on `GestiaApiClient`.
- No tool may call create, update, or delete operations.
- Agent instructions must always include `SHARED_AGENT_INSTRUCTIONS` from `app/app_utils/prompts.py`.

### Response format
Every domain agent must produce responses in this structure:
1. **Respuesta directa** — direct, concise answer
2. **Contexto del negocio** — what it means for the business
3. **Recomendación accionable** — a concrete next step

### Replacing stubs with real API
When integrating the Gestia REST API:
- Only modify method bodies in `app/app_utils/services.py`.
- **Do not change** method signatures or return types — tools depend on them.
- Add JWT token handling via `security/` (do not store tokens in code).

---

## Operational Guidelines

- **Code preservation**: Only modify code directly targeted by the request.
- **NEVER change the model** (`gemini-2.5-flash`) unless explicitly asked.
- **Model 404 errors**: Fix `GOOGLE_CLOUD_LOCATION` (use `global`), not the model.
- **ADK tool imports**: Import the function, not the module.
- **Run Python with `uv`**: `uv run python script.py`.
- **Stop on repeated errors**: If the same error appears 3+ times, fix the root cause.

---

## Future Directories

| Directory | Purpose |
|---|---|
| `eval/` | Evaluation datasets and configs (`agents-cli eval`) |
| `security/` | JWT validation middleware for Gestia API auth |
| `hitl/` | Human-in-the-Loop approval hooks for sensitive recommendations |
