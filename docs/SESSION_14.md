## Session 13: Omni AI Platform: Session Architecture & Refactoring Decisions

## Overview
This document tracks the significant architectural shifts and decisions made during the current development session to restructure the Omni AI Platform into a more efficient, robust, and adaptive system.

## 1. Prompt Ownership & Generation Pipeline
**Previous Architecture:** The `Worker` was responsible for building the prompt by concatenating strings from the `CreativePlan` and orchestrating the AI generation process.
**New Architecture:** The `AI Engine` now wholly owns the generation logic, while the `Worker` merely acts as a thin dispatch layer, and the `Orchestrator` owns workflow state. 

*   **Decision Made:** The Prompt Builder was moved inside the AI Engine. A new `PromptOptimizer` was introduced to sit between the raw assembly and the provider adapters.
*   **Why:** 
    *   It centralizes AI logic within the AI Engine, making it easier to swap providers (e.g., Flux → GPT Image → Imagen) without changing the Worker or Orchestrator logic.
    *   It prevents token waste by deduplicating and enriching prompts using reusable assets (e.g. expanding character details, environments, action sequences, composition rules, lighting, emotional intent, and provider-specific negative prompts) rather than simple string concatenation.

## 2. Project Context Store & Dependency Invariant
**Previous Architecture:** Project state was embedded entirely inside every RabbitMQ prompt message (leading to massive data repetition for 50+ shot videos) and lacked strict prerequisites before dispatching jobs.
**New Architecture:** We implemented a centralized, Redis-backed `ProjectContext` store. 

*   **Decision Made:** The Orchestrator extracts fields (characters, environment, brand, art direction, etc.) from the production plan and stores them in Redis (`POST /store-context`). 
*   **Why:** It dramatically reduces message payload size. Every generation job only needs a `job_id_parent` to fetch its context.
*   **Invariant Gate Added:** The Orchestrator now strictly enforces an invariant: `Generate Plan → Store Context → Verify Context Stored (`GET /api/v1/context-status/{job_id}`) → Dispatch Jobs`. If context storage fails or goes missing, the orchestrator aborts *before* spamming the message queue, preventing cascaded worker failures.

## 3. Advanced Generation Scheduler & Failover
**Previous Architecture:** The AI Engine attempted to generate assets directly, lacking robust retries and alternative provider handling.
**New Architecture:** A new `Generation Scheduler` module was built into the AI Engine.

*   **Decision Made:** Implemented an asynchronous scheduler that applies exponential backoff and tracks successive provider failures. If the primary provider (e.g. Flux Pro) exhausts its retry limits, the scheduler automatically failovers to a secondary provider (e.g. SDXL) or lower tier (e.g. Flux Schnell). 
*   **Why:** Increases fault tolerance. Provider exhaustion now returns HTTP 503 instead of 500, enabling the Worker to negatively acknowledge (NACK) messages without treating them as catastrophic system failures.

## 4. Adaptive Orchestration via the Workflow Registry
**Previous Architecture:** A static Directed Acyclic Graph (DAG) using LangGraph where every project, regardless of complexity, ran a massive suite of ~25 LLM agents.
**New Architecture:** The architecture transitioned to declarative **Adaptive Orchestration**.

*   **Decision Made:** We updated the `AgentRegistry` to support declarative `runs_when` conditions. We also refactored the workflow graph to maintain a comprehensive "superset" graph where agents evaluate their own conditions and instantly skip execution (returning an empty dict) if their criteria aren't met.
*   **Why:** A 10-second B-roll clip shouldn't invoke a Story Architect, Dialogue Writer, and Brand Identity agent. 
    *   **Workflow matching:** Different workflows (Advertisement, Short Film, Product Showcase, Talking Avatar) define their own implicit pipelines via conditions.
    *   *Example:* The `Story Architect` checks `runs_when=lambda state: state.get("classifier_plan").get("project_type") in ["short film", "cinematic scene"]`. 

## 5. Merging & Specializing Audio/Voice Agents
**Previous Architecture:** Disjointed agents for `Music`, `Sound Design`, `Dialogue`, `Narration`, and `Voice`.
**New Architecture:** 
*   **Merged Audio Director:** Replaced `Music Director` and `Sound Design Director` with a single `audio_director_node` (and unified `AudioPlan` schema). It decides stock music, foley, ambient audio, and sound effects in one LLM pass.
*   **Re-structured Voice Pipeline:** The `Voice Director` was scaled back to only act as a decision-maker (determining *if* dialogue, narration, or captions are needed, and *who* speaks). The actual scriptwriting was spun back out into conditionally executed `dialogue_writer_node` and `narration_writer_node` agents that only run if the Voice Director flags them as necessary.
*   **Why:** Consolidates LLM calls where tasks overlap (music vs sound design) while maintaining strict modularity for computationally expensive tasks like script generation.
