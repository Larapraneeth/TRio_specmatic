# TRIO × Specmatic — Spec-Driven Contract Testing

This project adds **executable contracts** to the [TRIO Agentic AI](.) backend using
[Specmatic](https://specmatic.io). The OpenAPI specification `trio_api.yaml` is the
single source of truth for TRIO's HTTP API. Specmatic reads it to:

1. **Contract test** the running TRIO backend — verify the real API matches the spec.
2. **Mock** the API — let the React frontend run without the backend.

> Built as part of the Specmatic Spec-First Engineering challenge.
> TRIO's source code is NOT modified — Specmatic tests it over HTTP from the outside.

---

## What's in here

| File             | Purpose                                                        |
|------------------|----------------------------------------------------------------|
| `trio_api.yaml`  | OpenAPI 3.0 spec for the TRIO backend (the executable contract) |
| `specmatic.yaml` | Specmatic configuration                                        |
| `README.md`      | This file                                                      |

## API surface described by the contract

| Method | Path                              | Notes                                  |
|--------|-----------------------------------|----------------------------------------|
| GET    | `/health`                         | Liveness check                         |
| GET    | `/api/agents/list`                | The 8 agents TRIO exposes              |
| GET    | `/api/system/info`                | Runtime + Ollama status                |
| GET    | `/api/conversations/`             | List conversations                     |
| POST   | `/api/conversations/`             | Create a conversation                  |
| GET    | `/api/conversations/{cid}`        | Get conversation + messages (404 path) |
| PATCH  | `/api/conversations/{cid}/title`  | Rename a conversation                  |
| DELETE | `/api/conversations/{cid}`        | Delete a conversation                  |
| POST   | `/api/chat/`                      | Agent chat (shape-validated; LLM reply is non-deterministic) |
| POST   | `/api/voice/speak`                | Text-to-speech, returns WAV audio      |

---

## Prerequisites

- Docker Desktop running
- TRIO backend able to run locally on port 8000

---

## Part 1 — Contract test the real backend

**Step 1. Start the TRIO backend** (from your TRIO backend folder, in its venv):

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

Confirm it's up: open http://localhost:8000/health — you should see
`{"status":"online","version":"2.0.0"}`.

**Step 2. Run Specmatic contract tests** (from THIS folder, new terminal):

```powershell
docker run --rm --network host -v "${PWD}:/usr/src/app" specmatic/specmatic test --testBaseURL=http://localhost:8000
```

On Docker Desktop for Windows, if `--network host` does not reach the backend, use:

```powershell
docker run --rm -v "${PWD}:/usr/src/app" specmatic/specmatic test --testBaseURL=http://host.docker.internal:8000
```

Specmatic will hit each endpoint described in `trio_api.yaml` and check the real
responses match the contract. An HTML report is written to
`build/reports/specmatic/html/index.html`.

---

## Part 2 — Run a mock from the same contract

Spin up a mock server that serves spec-compliant responses without the real backend:

```powershell
docker run --rm -p 9000:9000 -v "${PWD}:/usr/src/app" specmatic/specmatic stub --port 9000
```

Then a frontend (or curl) can call e.g. `http://localhost:9000/api/agents/list`
and get a valid, contract-shaped response — no backend required. This is how the
React frontend can be developed in parallel with the backend.

---

## Part 3 — Generative / resiliency tests (optional, impressive)

Have Specmatic auto-generate many valid and invalid request variations and confirm
the backend handles them gracefully:

```powershell
docker run --rm --network host -e SPECMATIC_GENERATIVE_TESTS=true -v "${PWD}:/usr/src/app" specmatic/specmatic test --testBaseURL=http://localhost:8000
```

---

## Notes & honest caveats

- **`/api/chat/`** returns LLM-generated text, which is non-deterministic. The contract
  validates the response *structure* (fields and types), not exact content. This is the
  correct way to contract-test an AI endpoint.
- **`/api/voice/*`** deals with binary audio; `/transcribe` (multipart upload) is omitted
  from automated tests and `/speak` validates the audio response type.
- The cleanest end-to-end demo is the **conversations CRUD** flow
  (create → list → get → rename → delete), which is fully deterministic.

## Cleanup

```powershell
docker ps -aq | ForEach-Object { docker rm -f $_ }
```
