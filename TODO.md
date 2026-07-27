# VideoCraft AI Platform - Development To-Do

## Current Phase: V3 — AI Director Brain

### ✅ Completed
- [x] **V3.1:** AI Engine Foundation (Server, LiteLLM, Logging, Project Structure).
- [x] **V3.2:** Workflow Foundation (LangGraph StateGraph, Nodes, Edges, Router).
- [x] **V3.3:** Shared State (Defined `CreativeState` in `state.py`).
- [x] **V3.4:** Director Agent (Extracts genre, purpose, tone, duration).
- [x] **V3.5:** Intent / Project Classifier (Determines if it's a Commercial, Story Film, etc. + Tool Calling).
- [x] **V3.6:** Requirement Analyzer (Extracts known visual/audio requirements from prompt).
- [x] **V3.7:** Brief Validator (Checks for critical errors before planning begins).
- [x] **V3.8:** Missing Information Detector (Flags missing info via parallel execution and reducers).
- [x] **V3.9:** Importance Scorer (Decides if missing fields actually need user input).
- [x] **V3.10:** Clarification Agent (Generates dynamic interview questions for the user).
- [x] **V3.11:** Knowledge & Research Agent (Parses brand guidelines, logos, previous campaigns).
- [x] **V3.12:** Campaign Strategy Agent (Defines goal, emotion, CTA, core message).
- [x] **V3.13:** Audience & Localization Agent (Defines country, language, accent, culture).
- [x] **V3.14:** Brand Identity Agent (Locks brand personality, colors, typography).
- [x] **V3.15:** Casting Director (Defines gender, ethnicity, age, archetype).
- [x] **V3.16:** Character Designer (Creates reusable character sheets).
- [x] **V3.17:** Environment Designer (Builds locations, architecture, weather).
- [x] **V3.18:** Art Director (Creates visual style, camera, film stock, color grading).
- [x] **V3.19:** Emotion Analyzer (Creates emotional progression).
- [x] **V3.20:** Story Architect (Creates narrative structure: beginning, middle, end).
- [x] **V3.21:** Screenplay Writer (Writes scene-by-scene breakdown and action lines).
- [x] **V3.22:** Dialogue Writer (Creates natural dialogue or specifies no dialogue).
- [x] **V3.23:** Narration Writer (Creates professional voiceover scripts).
- [x] **V3.24:** Voice Director (Plans voice provider, gender, accent, emotion, pace).
- [x] **V3.25:** Music Director (Plans genre, tempo, instruments, mood).
- [x] **V3.26:** Sound Design Director (Plans ambient, foley, and SFX).
- [x] **V3.27:** Storyboard Director (Breaks screenplay into visual scenes and keyframes).
- [x] **V3.28:** Cinematography Director (Plans camera movement, lighting, composition).
- [x] **V3.29:** Shot Planner (Expands scenes into executable shots).
- [x] **V3.30:** Prompt Engineering Agent (Converts intent into optimized prompts for FLUX, Veo, ElevenLabs).
- [x] **V3.31:** Asset Planner (Calculates exact asset requirements for rendering).
- [x] **V3.32:** Quality Review Agent (Final gate validation before V4).
- [x] **V3.33:** Production Plan Builder (Merges all output into `CreativePlan.json`).

### 🚧 To Do (Upcoming Sequence)
- [ ] **Human-in-the-Loop:** Add conditional graph pause/resume only when critical clarification questions are required.
- [x] **Phase 1 — Template Loader:** Create a `TemplateLoader` agent that loads the `.json` structural blueprint based on the user's requested template.
- [x] **Phase 2 — Director Refactor:** Modify the `Director` agent to *only* extract project metadata (Industry, Style, Country, Target Audience) without generating creative content.
- [x] **Phase 3 — Knowledge Selector:** Build a `KnowledgeSelector` agent that takes the Director's metadata and retrieves specific `.md` knowledge files into `CreativeState`.
- [x] **Phase 4 — Knowledge Base Setup:** Create the `knowledge/` directory structure containing domain expertise (advertising, cinematography, lighting, prompting, templates, presets, etc.).
- [x] **Phase 5 — Shared CreativeState Implementation:** Update `state.py` so all retrieved `.md` and `.json` knowledge is stored centrally in `CreativeState`.
- [x] **Phase 6 — Agent Parallelization & Refactor:** Refactor the LangGraph workflow to execute agents (Story Architect, Character Designer, Environment Designer, Cinematography Director, Prompt Engineer, etc.) in parallel or sequence based on the Template, utilizing only the specific portions of `CreativeState` relevant to their domain.

### ✅ Architectural & Logic Optimizations (Implemented)
- [x] **State Overwrite Protection:** Ensured `brand_name` and other critical fields are strictly protected in `CreativeState` from being nulled out.
- [x] **Requirements Merge Completeness:** Unified the `visual_requirements`, `audio_requirements`, and `clarification_answers` into a single canonical source of truth for downstream agents.
- [x] **Dynamic Validator Rules:** Un-hardcoded template rules (e.g. 30 seconds) so the `Rule Engine` dynamically extracts exact constraints from the `director_plan`.
- [x] **DAG Scheduler Refactor:** Parallelized the early analysis phase (`Director`, `Classifier`, `Visual`, `Audio`) and unblocked independent agents (e.g. `Music Director`) to minimize bottleneck latency.
- [x] **Screenplay Writer Optimization:** Enforced the `Screenplay Writer` to strictly format the scenes planned by the `Story Architect` (`dependencies=["story"]`) using a fast model, cutting its latency from ~16s down to ~2s.
- [x] **Plugin-Based Agent Registry:** Refactored graph building to use an explicit decorator-based registry (`@agent_registry.register`), eliminating brittle hardcoded node loops.
- [x] **Clarification Safeguards:** Banned boilerplate questions (legal, brand guidelines) and hard-capped the Clarification Agent to a maximum of 2 critical questions, alongside a generic "anything else" fallback.
- [x] **Analytics & Versioning Payload:** Injected `workflow_version`, `rule_version`, `prompt_versions`, and `analytics_summary` directly into the final `CreativePlan.json` metadata for tracing and debugging.

### ⚙️ AI Engine Model Routing
- Set `AI_ENGINE_USE_LLM=true` to call real models.
- Set `AI_ENGINE_MODEL` as the fallback model for all agents.
- Override per agent with env vars like `MODEL_DIRECTOR`, `MODEL_CLASSIFIER`, `MODEL_SCREENPLAY_WRITER`, `MODEL_PROMPT_ENGINEERING`, and `MODEL_QUALITY_REVIEW`.

### 🚀 Future Phases
- [ ] **V4:** Full-Stack Integration (FastAPI backend + Next.js frontend).
- [ ] **V5:** Generation & Rendering Engine.
- [x] **V2:** Connected the Next.js/React frontend to the `/api/plan` endpoint.
- [x] **V2:** Built a UI to input a prompt and display the generated JSON Video Plan.
- [x] **V2:** Added PostgreSQL database tracking (Saved plans to DB so the frontend can poll/fetch them).
- [x] **V1:** Initialized `services/agents` Python microservice.
- [x] **V1:** Added `/api/plan` producer endpoint in Node.js API Gateway.
- [x] **V0:** Initialized Express API, RabbitMQ Worker, MinIO S3, and Postgres Database.
- [x] **V0:** Built End-to-End Task Queue and File Upload flows.
- [x] Set up Monorepo single-command boot with `concurrently`.

### 🚫 Blocked
- *None currently.*
