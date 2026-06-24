# TRIO × Specmatic — Spec-Driven Contract & Resiliency Testing

This repository applies [Specmatic](https://specmatic.io) to the **TRIO Agentic AI**
backend (FastAPI). The OpenAPI specification `trio_api.yaml` is the single source of
truth for TRIO's HTTP API. Specmatic uses it to **contract-test** the running backend
and to run **schema resiliency** tests, and a second spec (`mock/ollama_api.yaml`) is
used to run a **mock of the Ollama LLM** so the AI-assisted endpoints can be tested
end to end without a real model.

> Built for the Specmatic Spec-First Engineering challenge.

---

## Prerequisites

- **Python 3.11** (the backend targets 3.11)
- **Docker Desktop** (used to run Specmatic for testing and mocking)
- **Git**
- A TTS engine is optional — `/api/voice/speak` falls back to a valid silent WAV when
  no engine (Piper/espeak) is present, so the project runs anywhere.

---

## Repository layout

```
trio-specmatic/
├── backend/                  # Runnable TRIO backend (FastAPI)
│   ├── main.py               # App entry point
│   ├── requirements.txt
│   ├── api/ agents/ core/ memory/ voice/
├── trio_api.yaml             # OpenAPI 3.0 spec (the executable contract)
├── specmatic.yaml            # Specmatic V3 configuration
├── mock/
│   └── ollama_api.yaml       # Subset of the official Ollama spec, used as a mock
├── examples/                 # External request/response examples
├── reports/
│   ├── contract/             # Saved contract (happy-path) test report
│   └── resiliency/           # Saved schema-resiliency (generative) test report
├── .github/workflows/ci.yml  # CI: runs contract + resiliency tests on every push
├── RESILIENCY_LEARNINGS.md
├── BLOG_POST.md
└── README.md
```

---

## 1. Set up and run the backend

```bash
cd backend
python -m venv venv

# Windows (PowerShell):
venv\Scripts\Activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

The chat endpoint talks to an LLM at `OLLAMA_BASE_URL` (default
`http://localhost:11434`). For testing we point it at the Specmatic mock instead
(see step 2). Start the backend:

```bash
# Windows (PowerShell):
$env:OLLAMA_BASE_URL="http://localhost:8888"
# macOS / Linux:
export OLLAMA_BASE_URL=http://localhost:8888

uvicorn main:app --host 0.0.0.0 --port 8000
```

Verify: open http://localhost:8000/health → `{"status":"online", ...}`

---

## 2. Start the Ollama mock (virtualized LLM)

In a separate terminal, run Specmatic as a stub of the Ollama API using the spec in
`mock/`. This serves a fast, deterministic fake LLM on port 8888 so the chat flow can
be tested without a real model:

```bash
cd mock
docker run --rm -p 8888:8888 -v "${PWD}:/usr/src/app" specmatic/specmatic stub ollama_api.yaml --port 8888
```

With the backend started using `OLLAMA_BASE_URL=http://localhost:8888` (step 1), TRIO
now calls this mock instead of a real Ollama.

---

## 3. Run the contract tests (happy path)

From the repository root, with the backend and mock running:

```bash
docker run --rm -v "${PWD}:/usr/src/app" specmatic/specmatic test trio_api.yaml --testBaseURL=http://host.docker.internal:8000
```

> On Linux, use `--network host` and `--testBaseURL=http://localhost:8000`.

This runs one test per documented operation and verifies each response against the
contract. The HTML report is written to `build/reports/specmatic/test/html/` and a copy
is kept in `reports/contract/`.

---

## 4. Run the schema resiliency tests (generative)

Resiliency testing mutates each request (wrong types, missing fields, nulls) and checks
the backend rejects invalid input gracefully. Enable it with the
`SPECMATIC_GENERATIVE_TESTS` environment variable:

```bash
docker run --rm -e SPECMATIC_GENERATIVE_TESTS=true -v "${PWD}:/usr/src/app" specmatic/specmatic test trio_api.yaml --testBaseURL=http://host.docker.internal:8000
```

The report is kept in `reports/resiliency/`. Because this run includes the generated
negative tests, it is larger than the contract run — the two reports are therefore
distinct.

---

## 5. Continuous Integration

`.github/workflows/ci.yml` runs on every push and pull request. It:

1. Installs Python 3.11 and backend dependencies (plus espeak/ffmpeg for TTS).
2. Starts the Specmatic Ollama mock.
3. Starts the TRIO backend pointed at the mock.
4. Runs the **contract** tests and saves the contract report.
5. Runs the **resiliency** tests and saves the resiliency report.
6. Uploads both reports as separate build artifacts.

---

## Notes

- **`/api/chat/`** is tested end to end against the mocked Ollama, so its full pipeline
  (request handling → LLM call → response) is exercised without a real model and without
  hardcoding any response in application code.
- **`/api/voice/speak`** returns `audio/wav`. When no TTS engine is available it returns
  a valid silent WAV, so the endpoint behaves deterministically in every environment.
- **`/api/conversations/{cid}` (GET)** automated testing targets the deterministic 404
  path; the 200 found-path is exercised via the live create → get flow.
