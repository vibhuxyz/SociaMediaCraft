# Session 02: Initializing V0 Backend Infrastructure
**Date:** 2026-07-23

## Goal of the Session
Initialize the V0 backend infrastructure (RabbitMQ, MinIO, Postgres, Express API Gateway, Worker Service) to execute long-running AI jobs asynchronously.

## What We Built
* Initialized a Bun-based Monorepo structure (`packages`, `apps`, `services`).
* Configured and booted up a complete Docker Compose cluster with Postgres 15, RabbitMQ, and MinIO (S3 compatible object storage).
* Created the `api-gateway` Express server in TypeScript with endpoints for job submission and file uploads.
* Created the `worker` service that listens to the `ai_jobs` RabbitMQ queue.
* Developed an auto-initialization script `init-s3.ts` that safely provisions MinIO buckets on API boot if they don't exist.
* Designed the base `Prisma` PostgreSQL schema tracking Jobs and Users.

## Engineering Decisions Made
* **DECISION-003 (Package Manager):** Switched from NPM to Bun for workspaces and package management for faster dependency resolution.
* **DECISION-004 (Queue):** Decided to use RabbitMQ instead of BullMQ/Redis for the V0 implementation to better prepare for standard message broker concepts.
* **DECISION-005 (Storage):** Swapped out direct S3 usage for a local MinIO container to ensure the entire V0 stack can run and be developed 100% locally offline.

## Next Session Plan
* **V1 (AI Planning Engine):** Integrate LiteLLM with structured outputs to build the Planner Agent that will intercept these jobs and output a structured plan before moving down the pipeline.
