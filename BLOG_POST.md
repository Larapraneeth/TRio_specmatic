
I completed the full Specmatic Spec-First Engineering course hands-on — working through every lab (contract testing, mocking, API testing, coverage, backward compatibility, examples, resiliency, Arazzo workflow testing, async/Kafka testing, MCP auto-test, and coding agents) — before applying Specmatic independently to my own TRIO project in this repository

# From 87% Coverage and 7 Failing Resiliency Tests to 100% Coverage and 48 Passing Tests: Applying Specmatic Spec-First Engineering to an Agentic AI System

## Introduction

TRIO is an Agentic AI Assistant built using FastAPI, local LLMs, conversation memory, speech processing, and multi-agent routing.

While the application worked correctly during manual testing, I wanted stronger guarantees around API correctness, validation behaviour, contract compliance, and long-term maintainability.

To achieve this, I adopted Specmatic's Spec-First Engineering approach and made the OpenAPI specification the single source of truth for the entire API lifecycle.

Before applying Specmatic to TRIO, I completed the full Specmatic course and hands-on labs covering contract testing, mocking, coverage reporting, resiliency testing, backward compatibility testing, workflow testing, async testing, MCP testing, and coding agents.

I then independently applied these concepts to my own AI project.

---

## Initial State

The project already had a working FastAPI backend and OpenAPI specification.

The first contract test execution validated the happy path successfully.

However, once schema resiliency testing was enabled, several issues surfaced.

The initial results were:

* 39 Tests Executed
* 32 Successes
* 7 Failures
* 87% API Coverage

The failures were not caused by application crashes alone.

They were a combination of:

* Contract gaps
* Missing examples
* Validation schema mismatches
* Incomplete API documentation
* Untested AI and voice endpoints

---

## Problem 1: Missing Validation Documentation

Several endpoints correctly returned HTTP 422 validation errors when invalid requests were sent.

Examples included:

* Missing request body
* Null values
* Number instead of string
* Boolean instead of string

The application behaved correctly.

However, these 422 responses were not documented in the OpenAPI specification.

Specmatic therefore reported failures because the contract did not describe the actual behaviour of the API.

### Resolution

I updated the OpenAPI specification to include:

* ValidationErrorResponse schemas
* 422 response definitions
* Response examples

This aligned the contract with the implementation.

---

## Problem 2: Missing Request-Response Example Pairs

Some endpoints contained only partial examples.

Specmatic works best when requests and responses are paired using named examples.

I reviewed the specification and added complete request-response pairs across all endpoints.

This enabled additional automated testing scenarios and removed skipped coverage.

---

## Problem 3: Chat Endpoint Testing

The chat endpoint depends on an external LLM.

Initially, hardcoded responses were introduced to make tests deterministic.

After receiving review feedback, I replaced this approach with Specmatic's mocking capability.

Instead of bypassing application logic, the backend now communicates with a mocked LLM API during CI execution.

This allowed the full request flow to be tested while maintaining deterministic behaviour.

Benefits included:

* No hardcoded responses
* More realistic testing
* Better contract verification
* End-to-end validation

---

## Problem 4: Voice Endpoint Failures in CI

Locally, the voice endpoint worked correctly.

However, GitHub Actions repeatedly returned:

HTTP 503 Service Unavailable

during contract testing.

The root cause was environment-specific.

The CI runner lacked the required audio generation dependencies.

### Resolution

The CI workflow was enhanced to install:

* espeak
* espeak-ng
* libespeak1
* ffmpeg

The TTS fallback implementation was also improved to generate WAV files reliably in a headless environment.

After these changes, the voice endpoint successfully returned:

* HTTP 200 audio/wav
* HTTP 422 validation responses

during automated testing.

---

## Problem 5: GitHub Actions Integration

The project originally relied on local execution.

To ensure repeatability, I integrated Specmatic directly into GitHub Actions.

The CI pipeline now:

1. Builds the backend.
2. Starts a mocked LLM using Specmatic Stub.
3. Launches the FastAPI application.
4. Executes contract tests.
5. Executes schema resiliency tests.
6. Generates coverage reports.
7. Uploads HTML reports as build artifacts.

Every push and pull request now validates API behaviour automatically.

---

## Final Results

After all improvements:

100% API Coverage

100% Absolute Coverage

48 Tests Executed

48 Successes

0 Failures

0 Errors

0 WIP

Every documented endpoint is now validated through automated testing.

Both positive and negative scenarios are exercised.

The OpenAPI contract accurately reflects runtime behaviour.

---

## Key Lessons Learned

The most valuable lesson was understanding the distinction between implementation defects and contract defects.

Some failures were caused by code issues.

Others were caused by incomplete specifications.

Specmatic made both categories visible.

Contract testing ensured the API behaved as documented.

Schema resiliency testing ensured the API failed safely.

Mocking allowed deterministic testing of AI-dependent functionality.

Coverage reporting revealed gaps that manual testing would likely miss.

Most importantly, a single OpenAPI specification became the source of truth for:

* Development
* Mocking
* Testing
* Coverage Reporting
* Continuous Integration

This significantly improved confidence in the TRIO backend while reducing manual verification effort.

---

## Final Outcome

The project evolved from:

87% API Coverage

32/39 Passing Tests

to:

100% API Coverage

48/48 Passing Tests

through a combination of Spec-First Engineering, contract testing, resiliency testing, dependency mocking, and continuous integration.

