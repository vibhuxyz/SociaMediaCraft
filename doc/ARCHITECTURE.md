# Architecture

This document tracks the architecture of VideoCraft across all engineering milestones (V0 -> V9).

We are using a Node.js, TypeScript, and Express.js stack with a BullMQ-based task orchestration layer, gradually transitioning to LangGraph for multi-agent workflows.

## Final Repository Structure (Target)

```text
omni-ai-platform
│
├── apps/
│   ├── web/           (Frontend - Later)
│   └── admin/
│
├── services/
│   ├── api-gateway/   (Express.js, Zod validation, Auth)
│   ├── worker/        (RabbitMQ workers processing AI jobs)
│   └── orchestrator/  (LangGraph + RabbitMQ workflow engine)
│
├── packages/
│   ├── database/      (Prisma, PostgreSQL schema, pgvector)
│   ├── agents/        (Planner, Research, Memory, Timeline, etc.)
│   ├── tools/         (MCP tools, Video, Image, Audio generation)
│   ├── multimodal/    (FFmpeg, Vision processing, OCR, Whisper)
│   └── shared/        (Types, Config, Logger)
│
├── infrastructure/
│   ├── docker/        (Dockerfiles, docker-compose.yml)
│   └── k8s/           (Kubernetes manifests - Later)
│
├── docs/
└── README.md
```

## Core Technologies
- **API:** Node.js, TypeScript, Express.js
- **Validation:** Zod
- **Database:** PostgreSQL with pgvector (via Prisma ORM)
- **Queues:** Redis, BullMQ
- **AI/LLM Routing:** LiteLLM
- **Agent Orchestration:** LangGraph, LangChain (where useful), MCP
- **Media Processing:** FFmpeg, FaceFusion, Whisper
- **Storage:** Cloudflare R2 / AWS S3
- **Observability:** LangSmith (for AI evaluation/tracing), OpenTelemetry (for production infrastructure)

## The Flow
1. **API Gateway:** Receives jobs (e.g. generate a campaign) and performs input validation.
2. **Queueing:** Pushes jobs into BullMQ.
3. **Workflow Orchestrator:** Dequeues jobs and triggers LangGraph state machines.
4. **Agents:** Hierarchical LangGraph agents (Planner -> Creative Director -> Storyboard, etc.) determine necessary tools.
5. **Tool Router:** Specific external tools and APIs are called (ElevenLabs, Runway, Suno, etc.).
6. **Media Assembly:** Resulting pieces are passed to the Timeline Builder and merged via FFmpeg.
7. **Critic/Evaluation:** Agents evaluate the output; retries if necessary.
8. **Final Storage:** Rendered artifacts uploaded to R2/S3. DB is updated with final metadata.
