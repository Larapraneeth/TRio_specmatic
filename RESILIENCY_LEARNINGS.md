# Schema Resiliency Testing — Learnings

Specmatic's schema resiliency (generative) testing mutates each request — wrong
types, missing required fields, null values — and checks that the backend rejects
invalid input gracefully (4xx) instead of crashing (5xx). It tests the *negative
space* of the contract, surfacing issues the happy-path contract test cannot.

## How it was run

The `/api/chat/` and `/api/voice/speak` endpoints were excluded because they depend
on a local LLM (Ollama) and long-running inference, which made generative requests
time out. Resiliency testing was run against the deterministic CRUD endpoints:

```powershell
docker run --rm -e SPECMATIC_GENERATIVE_TESTS=true `
  -v "${PWD}:/usr/src/app" specmatic/specmatic test trio_api.yaml `
  --testBaseURL=http://host.docker.internal:8000 `
  --filter="PATH!='/api/chat/,/api/voice/speak'"
```

The HTML report is saved to `reports/resiliency/`.

## Results summary

- Tests run: 16
- Successes: 8
- Failures: 8
- Errors: 0

The 8 failures are not test-harness problems — they are genuine findings about how
the backend and the contract handle invalid input.

## Issues surfaced (learnings)

### 1. Contract gap: no documented 4xx response for invalid input

For `POST /api/conversations/` and `PATCH /api/conversations/{cid}/title`, when
Specmatic sent invalid bodies (omitted body, `title` mutated to a number or
boolean), the backend correctly rejected them with **422 Unprocessable Entity**
(FastAPI/Pydantic validation). However, Specmatic reported:

> "Received 422, but the specification does not contain a 4xx or default response,
> hence unable to verify this response."

**Learning:** The implementation validates input correctly, but the *contract*
did not document the 4xx behaviour. Generative testing exposed that the spec was
incomplete — it only described the happy path. The fix is to add a 422 (or generic
4xx) response definition to these operations so the contract fully describes the
API's real, safe behaviour. This is a concrete example of contract testing
improving the spec itself, not just the code.

### 2. Real bug: null title causes a 500 instead of a 422

For `POST /api/conversations/` with `title` mutated from string to **null**,
the backend returned:

> "Expected 4xx status, but received 500"

**Learning:** Unlike the other invalid inputs (which were cleanly rejected with
422), a `null` title is not handled gracefully — it reaches application code and
throws an unhandled error, producing a 500. This is a genuine resiliency defect
that only surfaced through generative mutation testing. The fix is to make the
`title` field validation explicitly reject null (e.g. tighten the Pydantic model),
so the endpoint returns a 422 instead of crashing.

## Why this matters

These two findings are exactly the value of schema resiliency testing:
- It revealed that the **contract was incomplete** (no documented error responses).
- It revealed a **real input-handling bug** (null title → 500) that happy-path
  testing would never catch.

For an AI backend exposed to unpredictable client input, verifying the negative
space — not just that valid requests succeed, but that invalid ones fail safely —
is essential to prevent production 500s.

## Follow-up actions

1. Add `422`/`4xx` response definitions to the contract for the conversation
   create and title-update operations (documents the real validated behaviour).
2. Fix the null-title handling so `POST /api/conversations/` returns 422, not 500.
3. Re-run resiliency tests to confirm all mutations are handled gracefully.