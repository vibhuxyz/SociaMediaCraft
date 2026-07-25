# Session 03: The Agentic V2 Pipeline & Redis Event Streaming
**Date**: 2026-07-23

## Goal of the Session
Prove the end-to-end "Agentic" architecture (V2) where a Python AI Engine streams real-time progress events directly to the React frontend while generating a structured production plan via OpenAI.

## What We Built
- **V2 Node.js SSE Server**: Set up Server-Sent Events (SSE) to forward Redis Pub/Sub events directly to the frontend.
- **Python Redis Emitter**: Built a `RedisEventEmitter` in Python to stream real-time typed events (`job.{jobId}.progress`, `job.{jobId}.warning`).
- **OpenAI Integration**: Implemented a real LLM call using `OpenAIProvider` to generate a strict Pydantic `ProductionPlan`.
- **Frontend V2 Stream**: Connected the React UI to the SSE endpoint to render beautifully animated progress updates and the final JSON payload.

## What I Implemented Myself
- Guided the architectural shift to a typed event bus (`job.{jobId}.{type}`).
- Caught the bug where the Node SSE server wasn't listening to the new typed Redis channels.

## New Concepts Learned
- **Server-Sent Events (SSE)**: A lightweight alternative to WebSockets for one-way streaming from server to client.
- **Redis pSubscribe**: Using wildcard pattern matching to subscribe to dynamic Redis channels.
- **Pydantic Validation Errors**: Why LLMs fail at strict JSON parsing if not prompted securely.
- **OpenAI Structured Outputs**: How to inject JSON schemas into the system prompt to guarantee 100% adherence to a Pydantic model.

## Production Concepts Discussed
- **Decoupled Architecture**: Keeping progress streaming out of the main API Gateway to prevent overwhelming the core service with long-lived SSE connections.
- **Event-Driven Lifecycles**: The Node Worker owns the true `CompletedEvent`, while Python only emits `ProgressEvent` steps.

## Engineering Decisions Made
- **Typed Event Bus**: Shifted from a single `job_events` channel to a dynamically typed bus (`job.{jobId}.progress`) for finer-grained subscriptions.
- **OpenAI API Fallback**: Used JSON injection with `json_object` mode because the local SDK was `v1.3.5`, rather than dealing with the friction of environment upgrades right now.

## Trade-offs Considered
- Using `pSubscribe` in Node vs dedicated channels. We used `pSubscribe` to let the UI easily listen to all events for a single job without opening multiple subscriptions.

## Problems Encountered
1. Node processes getting stuck on ports 8080 and 6001 (`EADDRINUSE`).
2. Python's events missing from the UI because SSE wasn't listening to the new wildcard channel.
3. TypeScript compiler bug (`ChannelModel` vs `Connection`) in `@types/amqplib`.
4. Pydantic validation failures from OpenAI making up its own JSON keys.
5. UI "Processing..." bug where React expected `evt.message` but Python sent `evt.step`.
6. Premature SSE disconnection because Python fired a `CompletedEvent` at 85%.

## How We Solved Them
1. Killed the stray processes using `lsof -t -i :PORT | xargs kill -9`.
2. Updated Node.js SSE to use `pSubscribe("job.*.*")`.
3. Bypassed the TS bug by explicitly typing `connection: any` and `msg: any`.
4. Injected the `ProductionPlan` JSON schema directly into the OpenAI System Prompt and set `temperature=0.2`.
5. Renamed `step` to `message` in the Python `ProgressEvent` schema.
6. Removed the `CompletedEvent` from Python, letting the Node Worker emit it when S3 upload finishes.

## Code Review Summary
The event flow is extremely clean. The architecture follows a true microservice paradigm:
`React -> API Gateway -> RabbitMQ -> Python Engine -> Redis (Progress) -> Node Worker (Upload/DB) -> React (Complete)`.

## Mistakes I Made
- Overlooked the Node.js SSE subscription channel when redesigning the Python event emitter payload.

## Things I Should Remember
- Whenever changing a contract (like an event channel name), always check *both* the publisher and the subscriber.
- LLMs are not psychic. If you want strict JSON, you must provide the exact schema.

## Homework Before Next Session
- Review the generated `ProductionPlan` JSON to see if the AI Director's output makes logical sense for a video generation pipeline.

## Next Session Plan
- Begin Phase 4/5 integration: Taking the generated JSON `ProductionPlan` and actually passing the individual scenes/prompts to the image and video generators (e.g., Runway, Flux).
