# VideoCraft - TODO List

## Current Phase: V1 — AI Planning Engine (Week 2)

### 🚧 To Do (Upcoming)
- [ ] Initialize the `packages/agents` module.
- [ ] Install `openai` and `zod` for structured LLM interactions.
- [ ] Define the `Zod` schema for the Video Plan (e.g., Target Audience, Platform, Script, Mood).
- [ ] Build the `PlannerAgent` that forces the LLM to output the plan matching the Zod schema.
- [ ] Integrate the `PlannerAgent` into the API Gateway (`/api/plan` endpoint).
- [ ] **Test:** Send a vague prompt -> Receive a highly structured JSON plan.

### ✅ Completed
- [x] **V0:** Initialized Express API, RabbitMQ Worker, MinIO S3, and Postgres Database.
- [x] **V0:** Built End-to-End Task Queue and File Upload flows.
- [x] Set up Monorepo single-command boot with `concurrently`.

### 🚫 Blocked
- *None currently.*
