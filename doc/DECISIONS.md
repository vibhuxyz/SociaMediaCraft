# Architecture Decisions Record (ADR)

## 1. Core Architecture
- **Decision**: Split the platform into three layers (Infrastructure, Agent Platform, AI Studio).
- **Rationale**: Increases modularity. Allows selling the infrastructure or agent platform as separate B2B products while using the AI Studio as a flagship showcase.

## 2. Model Routing & Abstraction
- **Decision**: Never call OpenAI (or any provider) directly from the frontend or agent logic. Use a Unified API Layer (LiteLLM / Custom Model Router).
- **Rationale**: Prevents vendor lock-in, enables the self-healing fallback mechanism, and centralizes cost tracking and policy enforcement.

## 3. Agent Orchestration
- **Decision**: Use LangGraph for multi-agent workflows.
- **Rationale**: Provides stateful, observable, and graph-based execution of agents. Essential for the "Reviewer -> Self Healing -> Retry" loop.

## 4. Tech Stack Selection
- **Applied AI Layer**: Python (for all core AI, agents, LangGraph, LLM routing).
- **Backend / Full Stack**: Express (Node.js) for the web application API, user management, and orchestration.
- **Frontend Web App**: React, Tailwind CSS, shadcn/ui, React Flow (for visual pipeline).
- **State & Queue**: Redis, RabbitMQ/Kafka, Temporal/BullMQ for long-running multimodal generation tasks.
- **Database**: PostgreSQL (relational), Qdrant (vector storage for RAG).
- **Observability**: LangSmith (agent tracing), OpenTelemetry, Sentry, Grafana.

## 5. Tool Integration
- **Decision**: Use Model Context Protocol (MCP).
- **Rationale**: Standardizes tool consumption without writing custom integrations for every third-party service (Slack, Jira, Github).
