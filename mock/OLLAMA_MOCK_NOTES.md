# Ollama Mock Spec — Mapping to the Official Ollama OpenAPI

`mock/ollama_api.yaml` is used to run a Specmatic stub (mock) of the Ollama API so
TRIO's LLM-assisted endpoints can be tested end to end without a real model. It is a
**faithful subset** of the official Ollama OpenAPI specification:

https://github.com/ollama/ollama/blob/main/docs/openapi.yaml

## Component names and required fields — unchanged from official

The schema component names and their required properties are kept identical to the
official spec:

| Component         | Required fields (official & here) |
|-------------------|-----------------------------------|
| `GenerateRequest` | `model`                           |
| `GenerateResponse`| (none)                            |
| `ChatMessage`     | `role`, `content`                 |
| `ChatRequest`     | `model`, `messages`               |
| `ChatResponse`    | (none)                            |
| `ModelSummary`    | (none)                            |
| `ListResponse`    | (none)                            |
| `ModelOptions`    | (none)                            |

The `/api/tags` response is modelled with the official `ListResponse` (an object with
a `models` array of `ModelSummary`) — not a custom `TagsResponse`/`Model`.

## Intentional, scoped deviations (and why)

The only differences from the official spec are reductions and additions that Specmatic
permits for mocking, never renames or changed requirements:

1. **Endpoint subset.** Only the three endpoints TRIO actually calls are included:
   `/api/generate`, `/api/chat`, and `/api/tags`. The official spec contains many more
   (pull, push, create, delete, embed, ps, version, web search, etc.) which TRIO does
   not use, so they are omitted for clarity.

2. **Field subset.** Within the included schemas, fields TRIO does not depend on
   (e.g. `tools`, `think`, `logprobs`, `keep_alive`, streaming-only fields, timing
   metrics) are omitted. No remaining field has been renamed or had its type changed,
   and no required field has been added or removed relative to the official spec.

3. **Examples added.** Concrete `examples` were added to the requests and responses so
   Specmatic can serve deterministic mock responses. These are additive only.

These changes keep the mock small and focused on TRIO's usage while remaining
structurally consistent with the official Ollama contract.