
I completed the full Specmatic Spec-First Engineering course hands-on — working through every lab (contract testing, mocking, API testing, coverage, backward compatibility, examples, resiliency, Arazzo workflow testing, async/Kafka testing, MCP auto-test, and coding agents) — before applying Specmatic independently to my own TRIO project in this repository

# From 8 Failures to 16 Passing: Finding and Fixing Real Bugs in My AI Backend with Specmatic Schema Resiliency Testing

When I added executable contracts to **TRIO** — my agentic AI assistant — I expected
contract testing to confirm what I already believed: that my API worked. It did. But
the moment I turned on *schema resiliency testing*, the picture changed. Eight tests
failed. Working through those eight failures taught me to tell the difference between
a gap in my contract and a real bug in my code, and it ended with a clean run of
16 passing tests and a backend that fails safely. Here's the full story.

---

## The project

TRIO is an agentic AI assistant: a **FastAPI** backend with multiple specialized
agents, conversation memory (SQLite), voice (speech-to-text and text-to-speech), and
a React frontend. Its HTTP API covers health, agent listing, system info,
conversation CRUD, chat, and text-to-speech.

I used [Specmatic](https://specmatic.io) to make the OpenAPI specification
(`trio_api.yaml`) the single source of truth. Specmatic reads that one file to
contract-test the running backend, mock the API for frontend work, and run
resiliency tests — all from the same contract.

---

## Step 1 — The happy path passed (9/9)

My first contract-test run was clean. Specmatic sent one request per documented
endpoint and checked each real response against the contract:

```
Tests run: 9, Successes: 9, Failures: 0
```

Health, agents, system info, and the full conversation CRUD flow all matched the
spec. Satisfying — but a green happy-path run only proves one thing: that *valid*
requests work. It says nothing about what the API does when a client sends something
invalid. For an AI backend that takes unpredictable input, that's exactly where
production incidents come from.

---

## Step 2 — Turning on schema resiliency testing

Resiliency (generative) testing flips the question from "does a valid request
succeed?" to "does an *invalid* request fail *safely*?" Specmatic automatically
mutates each request — changing a string to a number, a string to a boolean, a
string to null, or omitting a required field entirely — and checks the backend
rejects each one gracefully with a 4xx instead of crashing with a 5xx.

I enabled it with the `SPECMATIC_GENERATIVE_TESTS` flag and pointed it at TRIO's
deterministic CRUD endpoints. (I excluded `/api/chat/` and `/api/voice/speak`,
because they depend on a local LLM and long-running inference, which makes generated
requests time out — testing them this way wasn't meaningful.)

```
docker run --rm -e SPECMATIC_GENERATIVE_TESTS=true \
  -v "${PWD}:/usr/src/app" specmatic/specmatic test trio_api.yaml \
  --testBaseURL=http://host.docker.internal:8000 \
  --filter="PATH!='/api/chat/,/api/voice/speak'"
```

The result:

```
Tests run: 16, Successes: 8, Failures: 8, Errors: 0
```

Eight failures. The interesting part wasn't the number — it was that they were
actually **two completely different problems** wearing the same red label.

---

## Step 3 — The key insight: two kinds of failure

### Category A — Contract gaps (7 of the 8 failures)

For `POST /api/conversations/` and `PATCH /api/conversations/{cid}/title`, Specmatic
sent invalid bodies — an omitted body, a `title` mutated to a number, a `title`
mutated to a boolean. My backend **correctly rejected all of them with 422
Unprocessable Entity**; FastAPI and Pydantic were already validating input properly.

But Specmatic still failed the test, with this message:

> "Received 422, but the specification does not contain a 4xx or default response,
> hence unable to verify this response."

This was the lightbulb moment. **The code was fine. The contract was incomplete.**
My spec only described the happy path — it documented the 200 responses but never
declared that these endpoints can also return a 422. So when the backend did the
right thing and returned 422, Specmatic had nothing in the contract to verify it
against, and treated it as an unexpected response.

A contract gap is fixed in the **spec**, not the code.

### Category B — A real bug (the 1 remaining failure)

One failure was genuinely different. When the `title` field was mutated to **null**,
the backend didn't return a clean 422 — it returned a **500**:

> "Expected 4xx status, but received 500"

This was a real defect. A null title slipped past validation, reached application
code, and threw an unhandled exception. The root cause was in the request model:

```python
class CreateConversationRequest(BaseModel):
    title: Optional[str] = "New Chat"
```

`Optional[str]` means "string **or** None" — so Pydantic *accepted* `null`, passed it
through, and the downstream code that expected a string blew up with a 500. Happy-path
testing would never have caught this, because no valid request sends a null title.

A code bug is fixed in the **implementation**, not the spec.

---

## Step 4 — The fixes

**Fix 1 — closing the contract gaps (Category A).**
I added a documented `422` response (backed by a `ValidationErrorResponse` schema) to
the create-conversation and update-title operations in `trio_api.yaml`. Now the
contract explicitly states these endpoints can return a 422 on invalid input, so
Specmatic can verify that behaviour instead of flagging it as unexpected. Seven
failures resolved — not by changing a single line of application code, but by making
the contract honestly describe what the API already does.

**Fix 2 — fixing the real bug (Category B).**
I tightened the request model so null is rejected at validation:

```python
# Before: null is accepted, then crashes downstream with a 500
title: Optional[str] = "New Chat"

# After: an omitted title still defaults to "New Chat",
# but an explicit null is now rejected at validation with a clean 422
title: str = "New Chat"
```

An omitted title still falls back to "New Chat", so normal usage is completely
unchanged — but a `null` title is now caught at the validation layer and returns a
422 instead of crashing the endpoint.

---

## Step 5 — All green (16/16)

I re-ran the exact same resiliency suite:

```
Tests run: 16, Successes: 16, Failures: 0, Errors: 0
```

Every mutation is now handled correctly. The invalid bodies return the documented
422, and the null-title case that used to throw a 500 now returns a clean 422. The
report is saved alongside the project.

---

## What I learned

The most valuable takeaway wasn't a Specmatic command or a config flag — it was a way
of reading failures. When a resiliency test goes red, the first question isn't "how do
I make it green?" — it's **"which layer does this belong to?"**

- If the backend already behaves correctly but the test still fails, it's usually a
  **contract gap** → document the real behaviour in the spec.
- If the backend genuinely mishandles the input (a 500, a crash, wrong status), it's a
  **code bug** → fix the implementation.

Happy-path contract testing confirms the API *works*. Schema resiliency testing
confirms it *fails safely* — and for any service that accepts untrusted input, that's
the difference between a clean 422 and a 3 a.m. production 500. Best of all, one
OpenAPI spec drove everything: the contract tests, the mock, and the resiliency tests,
with no duplicated effort and a single source of truth throughout.
