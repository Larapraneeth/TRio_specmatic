# Resiliency Testing Learnings – TRIO API

## Overview

As part of applying Specmatic's Spec-First Engineering approach to the TRIO Agentic AI Assistant, I enabled Schema Resiliency Testing to verify how the API behaves when clients send invalid or unexpected requests.

Unlike traditional happy-path testing, resiliency testing automatically generates negative test cases by mutating valid requests and validating that the API fails safely with appropriate 4xx responses instead of crashing or returning unexpected 5xx errors.

---

## Initial Results

The first resiliency test execution revealed several issues:

* Missing validation response documentation
* Missing request-response example pairs
* Contract gaps between implementation and specification
* Untested AI and voice endpoints
* CI-specific text-to-speech failures

Initial results:

```text
Tests Run: 39
Successes: 32
Failures: 7
Errors: 0

API Coverage: 87%
```

The failures were not all implementation bugs.

Some were caused by the OpenAPI specification not fully documenting the API behaviour.

---

## Issues Identified

### 1. Missing 422 Validation Responses

Several endpoints correctly returned:

```http
422 Unprocessable Entity
```

when invalid requests were submitted.

Examples included:

* Missing request body
* Null values
* Number instead of string
* Boolean instead of string

However, these validation responses were not documented in the OpenAPI specification.

As a result, Specmatic could not verify them and reported failures.

### Resolution

Added:

* ValidationErrorResponse schema
* 422 response definitions
* Validation examples

to all relevant endpoints.

---

## 2. Missing Example Pairs

Some operations did not contain complete request-response example pairs.

Specmatic uses paired examples to generate executable contract tests.

Missing examples reduced coverage and prevented some scenarios from executing.

### Resolution

Added examples for:

* GET_CONVERSATION_SUCCESS
* SPEAK_SUCCESS
* CHAT_SUCCESS
* CREATE_CONVERSATION_SUCCESS
* UPDATE_TITLE_SUCCESS

and ensured request and response examples were paired correctly.

---

## 3. Chat Endpoint Validation Testing

The chat endpoint relies on an external LLM.

To make testing deterministic and CI-friendly, Specmatic Stub was used to mock the Ollama API dependency.

This allowed the entire request flow to be exercised without requiring a live model.

Benefits:

* Deterministic execution
* Faster tests
* Improved coverage
* End-to-end validation

---

## 4. Voice Endpoint Failures in CI

The voice endpoint worked correctly on local machines but failed in GitHub Actions.

The endpoint returned:

```http
503 Service Unavailable
```

instead of:

```http
200 OK
Content-Type: audio/wav
```

Root cause:

* Missing audio dependencies in CI
* Headless environment limitations

### Resolution

Added CI dependencies:

* espeak
* espeak-ng
* libespeak1
* ffmpeg

Implemented a robust fallback audio generation mechanism compatible with headless runners.

After these changes, `/api/voice/speak` passed all contract and resiliency tests.

---

## Examples of Generated Resiliency Tests

Specmatic automatically generated negative scenarios such as:

### Chat Endpoint

```json
{
  "message": null
}
```

Expected:

```http
422 Unprocessable Entity
```

---

```json
{
  "message": false
}
```

Expected:

```http
422 Unprocessable Entity
```

---

```json
{
  "message": 123
}
```

Expected:

```http
422 Unprocessable Entity
```

---

### Voice Endpoint

```json
{
  "text": null
}
```

Expected:

```http
422 Unprocessable Entity
```

---

```json
{
  "text": true
}
```

Expected:

```http
422 Unprocessable Entity
```

---

```json
{
  "text": 845
}
```

Expected:

```http
422 Unprocessable Entity
```

---

## Final Results

After updating the specification, examples, CI pipeline, mocking strategy, and voice implementation:

```text
Tests Run: 48
Successes: 48
Failures: 0
Errors: 0
WIP: 0
```

Coverage:

```text
100% API Coverage
100% Absolute Coverage
```

All documented operations were successfully validated through both contract testing and schema resiliency testing.

---

## Key Learnings

### Contract Defects vs Implementation Defects

One of the most valuable lessons was learning to distinguish between:

**Contract Defects**

* Missing response documentation
* Missing examples
* Incomplete specifications

and

**Implementation Defects**

* Incorrect validation handling
* Environment-specific failures
* Dependency issues

Resiliency testing helped identify both categories quickly.

---

### Why Resiliency Testing Matters

Happy-path testing confirms that valid requests work.

Resiliency testing confirms that invalid requests fail safely.

For AI-powered systems that accept unpredictable user input, this provides significantly stronger confidence in API reliability.

---

## Outcome

The TRIO API evolved from:

```text
87% Coverage
32/39 Passing Tests
```

to:

```text
100% Coverage
48/48 Passing Tests
```

through Spec-First Engineering, executable contracts, schema resiliency testing, dependency mocking, and automated CI validation.
