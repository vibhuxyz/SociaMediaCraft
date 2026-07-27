"""
Project Context Store
=====================
A thin Redis wrapper that lets the orchestrator write a rich ProjectContext
once per job (Fix #2), and lets the AI Engine resolve it on every shot
without embedding the same data in every queue message.

Usage
-----
  # Orchestrator side (TypeScript calls our Python HTTP endpoint, or
  # the worker service calls store_context via a small REST shim):
  await store_context(job_id, project_context_dict)

  # AI Engine side (inside each generation node):
  ctx = await load_context(job_id)
  char = resolve_character(ctx, "char_001")
"""

import json
import logging
from typing import Any, Optional

import redis.asyncio as aioredis

from config.settings import settings

logger = logging.getLogger("ai-engine.context_store")

_redis: Optional[aioredis.Redis] = None


def _context_key(job_id: str) -> str:
    return f"job:{job_id}:project_context"


async def _get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = await aioredis.from_url(
            settings.REDIS_URL, encoding="utf-8", decode_responses=True
        )
    return _redis


# ---------------------------------------------------------------------------
# Write (called once per job, by the orchestrator / Python shim endpoint)
# ---------------------------------------------------------------------------

async def store_context(job_id: str, context: dict[str, Any], ttl_seconds: int = 86400) -> None:
    """Persist the full ProjectContext for *job_id*.

    TTL defaults to 24 hours — enough for any generation run while keeping
    Redis clean automatically.
    """
    r = await _get_redis()
    await r.set(_context_key(job_id), json.dumps(context), ex=ttl_seconds)
    logger.info(f"[ContextStore] Stored context for job {job_id!r} (TTL={ttl_seconds}s)")


# ---------------------------------------------------------------------------
# Read (called by each generation node inside the AI Engine)
# ---------------------------------------------------------------------------

async def load_context(job_id: str) -> dict[str, Any]:
    """Load the ProjectContext for *job_id* from Redis.

    Raises RuntimeError if the context has not been stored yet (the worker
    must call store_context before dispatching generation jobs).
    """
    r = await _get_redis()
    raw = await r.get(_context_key(job_id))
    if raw is None:
        raise RuntimeError(
            f"[ContextStore] No context found for job {job_id!r}. "
            "Did the orchestrator call store_context before dispatching?"
        )
    return json.loads(raw)


async def context_exists(job_id: str) -> bool:
    """Return True if the ProjectContext for *job_id* is present in Redis.

    Used by the orchestrator's invariant gate: it calls the AI Engine's
    /api/v1/context-status/{job_id} endpoint which calls this function to
    confirm the key was actually written before dispatching any jobs.
    """
    r = await _get_redis()
    result = await r.exists(_context_key(job_id))
    exists = result > 0
    logger.info(
        f"[ContextStore] context_exists({job_id!r}) → {exists}"
        f"  (key={_context_key(job_id)!r})"
    )
    return exists


# ---------------------------------------------------------------------------
# Resolvers (helpers used by the prompt builder)
# ---------------------------------------------------------------------------

def resolve_character(ctx: dict, character_id: str) -> Optional[dict]:
    """Return the character sheet for *character_id*, or None."""
    for char in ctx.get("characters", []):
        if char.get("character_id") == character_id:
            return char
    return None


def resolve_environment(ctx: dict, environment_id: str) -> Optional[dict]:
    """Return the environment sheet for *environment_id*, or None."""
    for env in ctx.get("environments", []):
        if env.get("environment_id") == environment_id:
            return env
    return None


def resolve_brand(ctx: dict) -> dict:
    """Return the brand guide from context (always present)."""
    return ctx.get("brand", {})


def resolve_art_direction(ctx: dict) -> dict:
    """Return the shared art-direction / camera rules."""
    return ctx.get("art_direction", {})
