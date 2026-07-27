# Session 11: AI Engine Model Upgrades & Motion Planning Architecture

## What We Did
1. **OpenRouter API Upgrades**: 
   - Replaced deprecated model endpoints (`gemini-1.5-flash`, `claude-3.5-sonnet`) with valid 2026 model IDs in `config/settings.py`.
   - Transitioned the entire stack to OpenRouter's 100% free models (`gemma-4-26b-a4b-it:free`, `nemotron-3-super-120b-a12b:free`, `gpt-oss-20b:free`) to bypass API 402 Insufficient Credit errors.
   - Hotfixed a bug in `universal_provider.py` where LiteLLM threw unhandled mapping exceptions on custom model IDs when attempting to calculate the cost.

2. **Graph Routing Bug Fix**:
   - Fixed a fatal routing bug in `workflow/graph.py` where the `route_after_clarification` edge mistakenly returned `END` and terminated the entire AI pipeline early if clarification questions were raised, completely bypassing the user prompt logic.

3. **Major Motion Planning Architecture Upgrade**:
   - Overhauled the prompt generation pipeline to align with modern Video Generation best practices (preventing physics hallucination).
   - Expanded the `Shot` schema to support action complexities, object interaction arrays, and a chronological `MicroAction` timeline array.
   - Built and injected **3 new Agents** directly between Shot Planning and Prompt Engineering:
     - `Action Complexity Analyzer`: Scores shots 1-10 based on physical complexity and dynamically splits complex shots into shorter sub-shots.
     - `Object Interaction Analyzer`: Detects risky hand-object interactions (e.g. human grasping a cup) to modulate complexity dynamically.
     - `Motion Planner`: Replaces abstract paragraphs with highly rigid chronological motion sequences (e.g., 0.0-0.5s: look_at_cup).
   - Completely rewrote the `Prompt Engineering` system constraints: dropped the 150-word minimum length limit, explicitly disabled excessive adjective padding, and enforced a rigorous block format (Subject, Environment, Camera, Lighting, Motion Sequence, Facial Expression, Object Interaction, Negative Constraints).
