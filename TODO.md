# VideoCraft - TODO List

## Current Phase: V3 — Tool Calling & External Systems

### 🚧 To Do (Upcoming)
- [ ] **V3.2:** Build LangGraph Workflow Engine (`graph.py`, `state.py`, `nodes.py`).
- [ ] Implement Agent Tool Calling for context extraction (e.g., Website Reader, PDF Reader) to gather facts before writing scripts.
- [ ] Set up LangGraph agent workflow to handle multi-step reasoning (Scripting -> Directing -> Tool Routing).

### ✅ Completed
- [x] **V3.1:** AI Engine Foundation (Universal LiteLLM Provider, Pydantic Settings, Structured Logging, Server Setup).
- [x] **V2:** Connected the Next.js/React frontend to the `/api/plan` endpoint.
- [x] **V2:** Built a UI to input a prompt and display the generated JSON Video Plan.
- [x] **V2:** Added PostgreSQL database tracking (Saved plans to DB so the frontend can poll/fetch them).
- [x] **V1:** Initialized `services/agents` Python microservice.
- [x] **V1:** Built Python `PlannerAgent` enforcing Pydantic schema with OpenAI Structured Outputs.
- [x] **V1:** Integrated Python consumer into RabbitMQ (`planning_queue`).
- [x] **V1:** Added `/api/plan` producer endpoint in Node.js API Gateway.
- [x] **V0:** Initialized Express API, RabbitMQ Worker, MinIO S3, and Postgres Database.
- [x] **V0:** Built End-to-End Task Queue and File Upload flows.
- [x] Set up Monorepo single-command boot with `concurrently`.

### 🚫 Blocked
- *None currently.*
