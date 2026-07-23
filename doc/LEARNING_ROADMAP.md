# VideoCraft Learning Roadmap

This is how the learning is structured. The idea is that every version teaches one major engineering skill. By the end, you'll know not only how to build the project but also why each technology exists and where it fits.

## Version 0 — AI Infrastructure Foundation (Week 1)
**Goal:** Build the backend foundation that can execute long-running AI jobs.

**Build:**
- Express API
- PostgreSQL
- Prisma
- Redis
- BullMQ
- Docker
- File Uploads
- R2/S3 Storage
- Worker Service

**Learn:**
- **Backend:** Express architecture, Middleware, Request lifecycle, REST APIs, Error handling, Validation (Zod)
- **Database:** PostgreSQL, Prisma ORM, Transactions, Indexing, Relations
- **Queue:** Redis, BullMQ, Workers, Delayed jobs, Retry, Dead Letter Queue
- **Infrastructure:** Docker, Docker Compose, Environment variables, File storage
- **Concepts:** Async processing, Job queues, Background workers, Idempotency, Retry mechanism, Logging, File uploads

**Test:**
Upload Image -> Create Job -> Queue -> Worker -> Storage -> Status Complete

## Version 1 — AI Planning Engine (Week 2)
**Goal:** Teach AI to understand user intent.

**Build:**
- Planner Agent

**Learn:**
- **LLM Concepts:** Prompt Engineering, Context Engineering, System Prompt, User Prompt, Temperature, Top P
- **AI:** Structured Output, JSON Mode, Function Calling Basics
- **Libraries:** LiteLLM, OpenAI SDK, Anthropic SDK, Gemini SDK, Zod
- **Concepts:** Prompt Templates, Prompt Chaining, Output Validation, JSON Schema, AI Reasoning

**Test:**
Input -> Planner -> Structured JSON

## Version 2 — Workflow Engine (Week 3)
**Goal:** Replace if/else with AI workflows.

**Build:**
Planner -> Storyboard -> Prompt Optimizer -> Router

**Learn:**
- **LangGraph ⭐:** Nodes, Edges, State, Graph, Conditional Edge, Loop, Checkpoint
- **AI:** Agent Architecture, Workflow Design, State Machines
- **Libraries:** LangGraph, LiteLLM
- **Concepts:** DAG, Graph Execution, Agent State, Workflow Engine, Sequential Execution, Parallel Execution

**Test:**
Different prompts create different execution graphs.

## Version 3 — Tool Calling (Week 4)
**Goal:** AI decides which tool to use.

**Build:**
Tool Registry (Video, Image, Voice, Search, Website, PDF)

**Learn:**
- **LangChain:** Tools, Tool Calling, Tool Registry
- **MCP ⭐:** MCP Server, MCP Client, Tool Discovery
- **Concepts:** Function Calling, Dynamic Routing, Agent Tool Selection, External Tools

**Test:**
- Poster Request -> Only Poster Tool
- Video Request -> Only Video Tool
- Mixed Request -> Multiple Tools

## Version 4 — Video Generation (Week 5)
**Goal:** Generate complete AI videos.

**Learn:**
- **Video:** Storyboards, Scene Planning, Camera Motion, Prompt Splitting, FFmpeg, Merge, Render
- **Audio:** Captions
- **Libraries:** FFmpeg, Video API
- **Concepts:** Parallel Generation, Rendering Pipeline, Video Stitching

**Test:**
Generate a 60-second AI advertisement.

## Version 5 — Audio AI (Week 6)
**Goal:** Complete audio generation.

**Build:**
Voice, Music, Effects

**Learn:**
- **Audio:** TTS, Voice Cloning, Music Generation, Audio Mixing
- **Libraries:** ElevenLabs, Whisper, Suno, MusicGen
- **Concepts:** Speech Synthesis, Voice Clone, Audio Pipeline, Lip Sync

**Test:**
Generate Video + Voice + Music + Captions

## Version 6 — Memory + RAG (Week 7)
**Goal:** AI remembers everything.

**Learn:**
- **RAG ⭐⭐⭐⭐⭐:** Embeddings, Chunking, Retrieval, Similarity Search
- **Memory:** Short-term Memory, Long-term Memory, Semantic Search
- **Libraries:** LangChain Retrieval, pgvector
- **Concepts:** Vector Database, Embedding Models, Semantic Search, Context Retrieval, Brand Memory

**Test:**
Ask: "Create another ad for Nike." -> AI remembers previous campaigns.

## Version 7 — Multimodal AI (Week 8)
**Goal:** Understand all inputs.

**Learn:**
- **Vision:** OCR, Image Captioning, Vision Models
- **Audio:** Speech Recognition
- **Video:** Scene Understanding
- **Libraries:** Whisper, OCR, FaceFusion
- **Concepts:** Multimodal AI, Image Understanding, Audio Understanding, Video Understanding

**Test:**
Upload Logo, Website, Brand PDF -> AI automatically extracts information.

## Version 8 — Reflection & Evaluation
**Goal:** AI critiques itself.

**Learn:**
- **Reflection:** Self Reflection, AI Critic, Prompt Improvement
- **Evaluation:** LLM as Judge, Quality Score, Hallucination Detection
- **Libraries:** LangGraph, LangSmith
- **Concepts:** Reflection Loop, AI Evaluation, Retry Strategy, Prompt Optimization

**Test:**
Bad prompt -> Bad output -> Critic -> Improved prompt -> Better output

## Version 9 — Production AI
**Goal:** Scale to production.

**Learn:**
- **Backend:** Scaling, API Gateway, Rate Limiting
- **Infrastructure:** Kubernetes, Kafka, OpenTelemetry, Prometheus, Grafana
- **Concepts:** Distributed Systems, Autoscaling, Observability, Tracing, Metrics, Logging, Monitoring

**Test:**
Run hundreds or thousands of concurrent jobs and verify:
- Workers recover from failures.
- Queues drain correctly.
- Metrics and traces show system health.
- Autoscaling handles increased load.

## Complete Learning Roadmap

| Version | Main Topic | Libraries | Core Concepts |
|---|---|---|---|
| V0 | Backend Infrastructure | Express, Prisma, BullMQ, Redis, Docker | APIs, Queues, Workers, Idempotency |
| V1 | AI Planning | LiteLLM, OpenAI, Zod | Prompt Engineering, Structured Outputs, Context Engineering |
| V2 | Agent Workflows | LangGraph | State, DAGs, Agent Orchestration, Conditional Flows |
| V3 | Tool Calling | LangChain, MCP | Function Calling, Tool Registry, Dynamic Routing |
| V4 | Video Generation | FFmpeg, Video Providers | Storyboards, Parallel Rendering, Video Pipelines |
| V5 | Audio Generation | ElevenLabs, Whisper, MusicGen | TTS, Voice Cloning, Music, Audio Pipelines |
| V6 | Memory & RAG | pgvector, LangChain Retrieval | Embeddings, Semantic Search, Long-Term Memory |
| V7 | Multimodal AI | Vision Models, Whisper, FaceFusion | Image, Audio, Video Understanding |
| V8 | Reflection & Evaluation | LangGraph, LangSmith | AI Critique, Evaluation, Retry Loops |
| V9 | Production AI | Kubernetes, Kafka, OpenTelemetry | Scaling, Observability, Distributed Systems |

### By the end of this roadmap
You'll have practical experience across four major domains:
- **Backend Engineering:** Express, PostgreSQL, Redis, BullMQ, Docker, distributed workers.
- **Applied AI:** Prompt engineering, context engineering, agent workflows, tool calling, RAG, memory, reflection, evaluation.
- **Multimodal AI:** Image, video, voice, music, captions, face swap, media processing.
- **Production Systems:** Kubernetes, Kafka, observability, scaling, monitoring, and resilient AI infrastructure.
