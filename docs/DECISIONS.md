# Architectural Decisions Log

## 1. Universal AI Provider Pattern (LiteLLM)
**Date:** 2026-07-25
**Decision:** Use `litellm` alongside native clients (The "Escape Hatch" pattern) instead of hardcoding OpenAI/Anthropic SDKs everywhere.
**Why:** To prevent vendor lock-in, enable rapid switching between models, and provide unified tracking. Native clients are preserved for "day-one" features.

## 2. Fail-Fast Configuration (pydantic-settings)
**Date:** 2026-07-25
**Decision:** Use `BaseSettings` from `pydantic_settings` for all environment variables instead of `os.getenv`.
**Why:** Ensures the application crashes immediately on startup if a required API key or config is missing, preventing deep runtime crashes.
