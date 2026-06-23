# TRIO × Specmatic — Spec-Driven Contract & Resiliency Testing

This repository adds **executable contracts** to the **TRIO Agentic AI** backend
(FastAPI) using [Specmatic](https://specmatic.io). The OpenAPI specification
`trio_api.yaml` is the single source of truth for TRIO's HTTP API. Specmatic uses
it to **contract-test** the running backend, to **mock** the API for frontend
development, and to run **schema resiliency** tests that probe the API's negative
space.

> Built for the Specmatic Spec-First Engineering challenge.

---

## Repository layout

```
trio-specmatic/
├── backend/                 # Full runnable TRIO backend (FastAPI)
│   ├── main.py              # App entry point (uvicorn main:app)
│   ├── requirements.txt
│   ├── api/                 # Route handlers (chat, voice, agents, system, conversations)
│   ├── agents/              # The specialized AI agents
│   ├── core/                # Agent manager / orchestration
│   ├── memory/              # SQLite conversation store
│   └── voice/               # Speech-to-text / text-to-speech
├── trio_api.yaml            # OpenAPI 3.0 spec (the executable contract)
├── specmatic.yaml           # Specmatic configuration
├── examples/                # External examples (Specmatic JSON request/response pairs)
├── reports/
│   ├── contract/index.html  # Saved happy-path contract test report
│   └── resiliency/index.html# Saved schema resiliency test report
├── RESILIENCY_LEARNINGS.md  # Findings & fixes from schema resiliency testing
├── BLOG_POST.md             # Write-up of the resiliency journey (8 failures -> all pass)
└── README.md
```

---

## Prerequisites

- Python 3.11+
- Docker Desktop (for Specmatic)
- (Optional) Ollama running locally, for the `/api/chat` and `/api/system/info`
  endpoints to return live model data

---

## 1. Run the TRIO backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Verify: open http://localhost:8000/health → `{"status":"online","version":"2.0.0"}`

---

## 2. Contract-test the backend against the spec

From the repository root, in a second terminal (backend still running):

```bash
docker run --rm -v "${PWD}:/usr/src/app" specmatic/specmatic test --testBaseURL=http://host.docker.internal:8000
```

Specmatic sends a request to each endpoint described in `trio_api.yaml` and checks
the real response against the contract. Result: 9/9 happy-path scenarios pass.

### Inline examples (matched names)

Per Specmatic convention, every request example and its response example share the
same name, so together they form one named contract test — for example
`CREATE_CONVERSATION_SUCCESS` appears under both the request body and the 200
response of `POST /api/conversations/`.

### External examples

The same scenarios are also provided as external JSON files under `examples/`, in
Specmatic's `http-request` / `http-response` format.

---

## 3. Mock the API from the same contract

```bash
docker run --rm -p 9000:9000 -v "${PWD}:/usr/src/app" specmatic/specmatic stub --port 9000
```

A frontend (or curl) can then call e.g. `http://localhost:9000/api/agents/list`
and get a valid, contract-shaped response with no backend running.

---

## 4. Schema resiliency tests

Generative testing mutates requests (wrong types, missing fields, nulls) and checks
the backend fails safely with a 4xx instead of crashing with a 5xx. The chat and
voice endpoints are excluded because they depend on a local LLM and long-running
inference.

```bash
docker run --rm -e SPECMATIC_GENERATIVE_TESTS=true -v "${PWD}:/usr/src/app" specmatic/specmatic test trio_api.yaml --testBaseURL=http://host.docker.internal:8000 --filter="PATH!='/api/chat/,/api/voice/speak'"
```

This run originally surfaced 8 failures — 7 contract gaps (undocumented 422s) and
1 real bug (a null title returned 500 instead of 422). Both were fixed; the suite
now passes 16/16. Full write-up in `RESILIENCY_LEARNINGS.md` and `BLOG_POST.md`,
report in `reports/resiliency/`.

---

## Notes & honest caveats

- **`/api/chat/`** returns LLM-generated text (non-deterministic). The contract
  validates response *structure*, not exact content — the correct way to
  contract-test an AI endpoint.
- **`/api/conversations/{cid}` (GET)** automated test targets the deterministic
  404 path; the 200 found-path is state-dependent and is demonstrated live via the
  create → get flow.
- **`/api/voice/*`** deals with binary audio; `/speak` validates the `audio/wav`
  response type.

## Cleanup

```powershell
docker ps -aq | ForEach-Object { docker rm -f $_ }   # PowerShell
```
