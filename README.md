# TRIO + Specmatic: Spec-First Engineering, Contract Testing & Resiliency Testing

## Overview

TRIO is an Agentic AI Assistant built using FastAPI, local LLMs (Ollama), conversation memory, speech-to-text, text-to-speech, and a React frontend.

As part of this project, I applied Specmatic's Spec-First Engineering approach by making the OpenAPI specification the single source of truth for development, testing, mocking, and CI validation.

The repository demonstrates:

* OpenAPI-driven development
* Contract Testing
* Schema Resiliency Testing
* API Coverage Reporting
* Specmatic Mocking
* GitHub Actions CI Integration
* LLM Dependency Virtualization
* End-to-End Validation of AI and Voice APIs

---

## Specmatic Learning Journey

Before applying Specmatic to TRIO, I completed the full Specmatic Spec-First Engineering course and worked through all hands-on labs, including:

* Contract Testing
* API Mocking
* API Coverage Reporting
* Backward Compatibility Testing
* Schema Resiliency Testing
* Example-driven Testing
* Arazzo Workflow Testing
* Async / Kafka Testing
* MCP Auto Testing
* Coding Agents

The knowledge gained from these labs was then applied independently to this repository.

---

## Architecture

TRIO consists of:

* FastAPI Backend
* Multi-Agent Routing System
* SQLite Conversation Memory
* Ollama Local LLM Integration
* Speech-to-Text Module
* Text-to-Speech Module
* React Frontend

---

## Specmatic Implementation

### OpenAPI Specification

The OpenAPI specification (`trio_api.yaml`) acts as the single source of truth.

Covered APIs:

* GET /health
* GET /api/agents/list
* GET /api/system/info
* GET /api/conversations/
* POST /api/conversations/
* GET /api/conversations/{cid}
* PATCH /api/conversations/{cid}/title
* POST /api/chat/
* POST /api/voice/speak

---

### Contract Testing

Specmatic validates all request and response structures against the OpenAPI specification.

Positive scenarios verify:

* Valid requests
* Response schemas
* Response codes
* Content types

---

### Schema Resiliency Testing

Specmatic automatically generates negative test cases by mutating requests.

Examples include:

* Missing request bodies
* Null values
* Number instead of string
* Boolean instead of string
* Invalid nested object structures

The API is verified to return safe 4xx responses rather than failing with 5xx errors.

---

### Mocking LLM Dependencies

Instead of hardcoding LLM responses, Specmatic Stub is used to mock the Ollama API during CI execution.

Benefits:

* Deterministic tests
* Faster execution
* No dependency on local models
* Stable CI pipelines

---

### GitHub Actions CI

The project automatically runs:

* Contract Tests
* Resiliency Tests
* Coverage Reports

on every push and pull request.

---

## Final Results

### Coverage

100% API Coverage

100% Absolute Coverage

### Test Results

Tests Run: 48

Successes: 48

Failures: 0

Errors: 0

WIP: 0

---

## Key Improvements Identified Through Testing

Specmatic helped identify:

* Missing validation response documentation
* Missing request-response example pairs
* Uncovered negative test scenarios
* CI-only TTS execution issues
* Contract completeness gaps

These issues were resolved through updates to the OpenAPI specification, API implementation, and CI pipeline.

---

## Repository

https://github.com/Larapraneeth/TRio_specmatic

---

## Technologies Used

* Python
* FastAPI
* SQLite
* Ollama
* Specmatic
* OpenAPI 3.0.3
* GitHub Actions
* Docker
* Speech Processing Tools
