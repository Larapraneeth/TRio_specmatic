# TRIO Agentic AI – Specmatic Contract Testing

## Overview

This repository demonstrates contract testing and API resiliency testing for the TRIO Agentic AI backend using Specmatic V3.

The goal of this project is to ensure that the OpenAPI specification remains the single source of truth for the API and that all implemented endpoints comply with the published contract.

## Features

* OpenAPI 3.0.3 Contract
* Specmatic V3 Configuration
* Contract Testing
* Schema Resiliency Testing
* GitHub Actions CI Integration
* FastAPI Backend
* Local Ollama-powered AI Agents
* Voice (TTS/STT) APIs
* Conversation Management APIs

---

## API Endpoints

### Health

```http
GET /health
```

Returns service health and version information.

### Agents

```http
GET /api/agents/list
```

Returns available AI agents.

### System Information

```http
GET /api/system/info
```

Returns runtime and model status.

### Conversations

```http
GET    /api/conversations/
POST   /api/conversations/
GET    /api/conversations/{cid}
PATCH  /api/conversations/{cid}/title
```

Provides conversation management functionality.

### Chat

```http
POST /api/chat/
```

Routes user requests through the TRIO agent manager.

### Voice

```http
POST /api/voice/speak
POST /api/voice/transcribe
```

Provides text-to-speech and speech-to-text capabilities.

---

## Project Structure

```text
trio-specmatic/
│
├── backend/
│   ├── api/
│   ├── agents/
│   ├── core/
│   ├── memory/
│   └── voice/
│
├── examples/
│
├── reports/
│
├── .github/workflows/
│
├── trio_api.yaml
├── specmatic.yaml
└── README.md
```

---

## Running the Backend

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Backend

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Verify

```bash
http://localhost:8000/docs
```

---

## Running Contract Tests

```bash
docker run --rm \
-v "${PWD}:/usr/src/app" \
-w /usr/src/app \
specmatic/specmatic test trio_api.yaml \
--testBaseURL=http://host.docker.internal:8000
```

---

## Running Resiliency Tests

```bash
docker run --rm \
-v "${PWD}:/usr/src/app" \
-w /usr/src/app \
specmatic/specmatic test trio_api.yaml \
--testBaseURL=http://host.docker.internal:8000
```

Resiliency tests automatically generate negative scenarios to validate schema enforcement and request validation.

---

## Specmatic Test Mode

AI-backed endpoints such as:

```text
POST /api/chat/
POST /api/voice/speak
```

can take longer due to model inference.

To ensure deterministic and fast CI execution, a dedicated test mode was introduced:

```bash
SPECMATIC_TEST=true
```

When enabled:

* Chat endpoint returns a mock response.
* Voice endpoint returns mock WAV content.
* Contract and resiliency tests execute without waiting for model inference.

---

## Continuous Integration

GitHub Actions automatically runs:

* Contract Tests
* Resiliency Tests

on every push and pull request.

Workflow location:

```text
.github/workflows/CI.yml
```

---

## Results

### Achievements

* Migrated to Specmatic V3
* Added OpenAPI examples
* Added Contract Testing
* Added Schema Resiliency Testing
* Added GitHub Actions CI
* Removed endpoint exclusions
* Included Chat and Voice APIs in testing
* Achieved 87% API Coverage

---

## Tech Stack

* FastAPI
* Python 3.11
* Ollama
* Specmatic V3
* Docker
* GitHub Actions
* OpenAPI 3.0.3

---

## Author

**Lara Praneeth Kondeti**

B.Tech Computer Science Engineering
Indian Institute of Information Technology (IIIT) Surat
