# Production-Grade LangGraph Multi-Agent Architecture

A complete, wired-together reference implementation. Every file below is real,
runnable Python — not pseudocode — organized so you can copy the structure
directly into a repo.

---

## 1. Directory Structure

In VideoCraft, this maps to our `services/ai-engine/` directory as defined in `PROJECT_ROADMAP.md`:



> **Note:** The code examples below use a generic `project/` layout (`core/`, `graph/`). When implementing in VideoCraft, use the paths shown above (e.g., `workflow/state.py` instead of `core/state.py`).

---

## 2. Core State + Reducers (Point 3, 9, and Addition #1)

The single most common mistake: assuming `return {"story": story}` is enough.
That's true for **last-write-wins** fields. Fields that multiple agents touch
(logs, running scores, evidence lists) need an explicit reducer or they'll
silently overwrite each other.

```python
# core/state.py
from typing import Annotated, Optional
from operator import add
from typing_extensions import TypedDict
from agents.story.schema import StoryOutput
from agents.character.schema import CharacterOutput


def merge_scores(current: dict, new: dict) -> dict:
    """Custom reducer: shallow-merge score dicts instead of overwriting."""
    merged = dict(current or {})
    merged.update(new or {})
    return merged


class GraphState(TypedDict, total=False):
    # Last-write-wins — each agent owns its own section (Point 3)
    story: Optional[StoryOutput]
    character: Optional[CharacterOutput]

    # Append-only across every agent that logs (Addition #1)
    logs: Annotated[list[str], add]

    # Custom-merged — multiple validators can each score without
    # clobbering each other's keys (Addition #1)
    scores: Annotated[dict, merge_scores]

    # Loop-guard counters (Addition #8)
    story_retry_count: int
    thread_id: str
```

**Rule of thumb:** if only one agent ever writes a field, plain overwrite is
fine. The moment a second agent needs to touch it, it needs a reducer —
don't wait until the bug shows up in production.

---

## 3. Config vs Prompts — Kept Separate (Point 10, Addition #9, #10)

Prompts and model config change for different reasons and on different
schedules. Mixing them means a temperature tweak requires touching the same
file as a prompt rewrite, which makes diffs and rollbacks messy.

```python
# core/config.py
from pydantic import BaseModel
import os


class ModelConfig(BaseModel):
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    fallback_model: str | None = None


class Settings(BaseModel):
    env: str = os.getenv("APP_ENV", "development")

    story_model: ModelConfig = ModelConfig(
        model="claude-sonnet-4-6",
        temperature=0.8,
        max_tokens=3000,
        fallback_model="gpt-4o-mini",
    )
    validator_model: ModelConfig = ModelConfig(
        model="claude-haiku-4-5",  # cheap model for validation calls
        temperature=0.0,
        max_tokens=500,
    )

    postgres_dsn: str = os.getenv("CHECKPOINT_DB_URL", "")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "story-graph")


settings = Settings()
```

```python
# core/prompt_loader.py
from pathlib import Path
from functools import lru_cache

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@lru_cache(maxsize=32)
def load_prompt(name: str) -> str:
    """
    Loads a versioned prompt file, e.g. load_prompt("story_v3").
    Versioning in the filename means you can grep a run's trace for
    which prompt version produced it (Addition #9) — critical during
    an incident when someone asks "which prompt made this output?"
    """
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text()
```

```markdown
# prompts/story_v3.md
You are a story generation specialist. Given the context and retrieved
knowledge below, write a story with a clear title, 3-5 scenes, and an
ending that resolves the central tension.

Context:
{context}

Retrieved knowledge:
{knowledge}

Respond only with structured output matching the required schema.
```

---

## 4. Typed Schemas (Point 4)

```python
# agents/story/schema.py
from pydantic import BaseModel, Field


class Scene(BaseModel):
    heading: str
    description: str
    characters: list[str] = Field(default_factory=list)


class StoryOutput(BaseModel):
    title: str
    scenes: list[Scene]
    ending: str
    confidence: float = Field(ge=0.0, le=1.0)


class StoryInput(BaseModel):
    premise: str
    tone: str = "neutral"
    max_scenes: int = 5
```

Every agent takes a typed input and returns a typed output. No raw dicts
crossing a service boundary.

---

## 5. LLM Client Wrapper (Point 7)

Never call `OpenAI()` / `Anthropic()` inside a node or service directly.
One wrapper owns retries, fallback, streaming, and cost tracking.

```python
# core/llm_client.py
import litellm
from core.config import ModelConfig


class LLMClient:
    """
    Single chokepoint for every model call in the system.
    Swap providers, add logging, or add cost tracking here —
    once — instead of in every agent.
    """

    def __init__(self, cost_tracker=None, logger=None):
        self._cost_tracker = cost_tracker
        self._logger = logger

    async def complete(
        self,
        prompt: str,
        config: ModelConfig,
        response_model: type | None = None,
    ):
        try:
            response = await litellm.acompletion(
                model=config.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        except Exception as e:
            if config.fallback_model:
                if self._logger:
                    self._logger.warning(
                        f"{config.model} failed ({e}); falling back to "
                        f"{config.fallback_model}"
                    )
                response = await litellm.acompletion(
                    model=config.fallback_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                )
            else:
                raise

        if self._cost_tracker:
            self._cost_tracker.record(response)

        content = response.choices[0].message.content

        if response_model:
            return response_model.model_validate_json(content)
        return content

    async def stream(self, prompt: str, config: ModelConfig):
        """
        Streaming pass-through (Addition #7). If you wrap this again
        inside service.execute() without forwarding chunks, streaming
        silently stops working three layers up in the UI. Keep this
        generator undisturbed all the way to the node boundary.
        """
        async for chunk in await litellm.acompletion(
            model=config.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=config.temperature,
            stream=True,
        ):
            yield chunk.choices[0].delta.content or ""
```

---

## 6. Middleware Stack (Point 12)

```python
# core/middleware.py
import time
import asyncio
import logging
from functools import wraps

logger = logging.getLogger("agent.middleware")


def with_middleware(timeout_s: float = 30.0):
    """
    Wraps any async callable with logging, timeout, and latency tracking.
    The agent code underneath never knows this exists (Point 12).
    """
    def decorator(fn):
        @wraps(fn)
        async def wrapped(*args, **kwargs):
            start = time.monotonic()
            logger.info(f"[start] {fn.__qualname__}")
            try:
                result = await asyncio.wait_for(
                    fn(*args, **kwargs), timeout=timeout_s
                )
                elapsed = time.monotonic() - start
                logger.info(f"[done] {fn.__qualname__} in {elapsed:.2f}s")
                return result
            except asyncio.TimeoutError:
                logger.error(f"[timeout] {fn.__qualname__} > {timeout_s}s")
                raise
            except Exception as e:
                elapsed = time.monotonic() - start
                logger.error(
                    f"[error] {fn.__qualname__} after {elapsed:.2f}s: {e}"
                )
                raise
        return wrapped
    return decorator
```

Retry itself is intentionally **not** here — that's handled by LangGraph's
own `RetryPolicy` at the node level (Section 10), so retries are visible in
the graph's execution trace instead of hidden inside a decorator.

---

## 7. Retriever Service (Point 11)

```python
# core/retriever.py
class RetrieverService:
    """Shared by every agent that needs knowledge grounding."""

    def __init__(self, vector_store, reranker=None):
        self._store = vector_store
        self._reranker = reranker

    async def retrieve(self, query: str, k: int = 8) -> str:
        docs = await self._store.similarity_search(query, k=k)
        if self._reranker:
            docs = await self._reranker.rerank(query, docs)
        compressed = self._compress(docs)
        return self._format(compressed)

    def _compress(self, docs, max_tokens: int = 1500):
        # Trim/summarize to fit budget — real implementation would
        # use token counting, not len()
        return docs[:5]

    def _format(self, docs) -> str:
        return "\n\n".join(f"- {d.page_content}" for d in docs)
```

---

## 8. Dependency Injection Container (Point 5)

```python
# core/container.py
from dataclasses import dataclass
from core.llm_client import LLMClient
from core.retriever import RetrieverService
from core.config import settings


@dataclass
class Container:
    """
    Built once at startup, passed into every service. Nothing inside
    a service ever does `OpenAI()` or `VectorStore()` itself — makes
    swapping a mock in for tests trivial (see tests/test_story_service.py).
    """
    llm: LLMClient
    retriever: RetrieverService


def build_container() -> Container:
    from vector_store import get_vector_store  # your actual store
    return Container(
        llm=LLMClient(),
        retriever=RetrieverService(vector_store=get_vector_store()),
    )
```

---

## 9. Base Agent — Template Method Pattern (Point 6)

```python
# core/base_agent.py
from abc import ABC, abstractmethod
from core.container import Container
from core.middleware import with_middleware


class ValidationError(Exception):
    def __init__(self, feedback: str):
        self.feedback = feedback
        super().__init__(feedback)


class BaseAgent(ABC):
    """
    Every agent follows: load context -> retrieve -> prompt -> LLM
    -> validate -> map -> return. Only build_prompt(), validate(),
    and map_output() differ per agent (Point 6).

    Retries here handle VALIDATION failures — re-prompting with the
    validator's feedback appended — which is a distinct path from
    LangGraph's node-level RetryPolicy, which handles infra failures
    like timeouts/rate limits (Addition #3). Don't conflate the two.
    """

    max_validation_retries: int = 2

    def __init__(self, container: Container):
        self.llm = container.llm
        self.retriever = container.retriever

    @abstractmethod
    def build_prompt(self, context: dict, knowledge: str, feedback: str = "") -> str:
        ...

    @abstractmethod
    def response_model(self) -> type:
        ...

    @abstractmethod
    def validate(self, output) -> None:
        """Raise ValidationError(feedback) if invalid."""
        ...

    @abstractmethod
    def map_output(self, output) -> dict:
        """Convert typed LLM output into a GraphState partial-update dict."""
        ...

    def load_context(self, state: dict) -> dict:
        return {"state": state}

    def retrieval_query(self, context: dict) -> str:
        return context.get("query", "")

    @with_middleware(timeout_s=30.0)
    async def execute(self, state: dict) -> dict:
        context = self.load_context(state)
        knowledge = await self.retriever.retrieve(self.retrieval_query(context))

        feedback = ""
        last_error = None
        for attempt in range(self.max_validation_retries + 1):
            prompt = self.build_prompt(context, knowledge, feedback)
            output = await self.llm.complete(
                prompt, self.model_config(), response_model=self.response_model()
            )
            try:
                self.validate(output)
                return self.map_output(output)
            except ValidationError as e:
                last_error = e
                feedback = e.feedback  # fed back into the next prompt

        raise last_error

    @abstractmethod
    def model_config(self):
        ...
```

---

## 10. The Story Agent (all six files, wired to the base class)

```python
# agents/story/schema.py
# (shown above in Section 4 — reused here)
```

```python
# agents/story/prompt.py
from core.prompt_loader import load_prompt


def build(context: dict, knowledge: str, feedback: str = "") -> str:
    template = load_prompt("story_v3")
    prompt = template.format(context=context["state"].get("premise", ""), knowledge=knowledge)
    if feedback:
        prompt += f"\n\nYour previous attempt had an issue: {feedback}\nPlease fix it."
    return prompt
```

```python
# agents/story/validator.py
from core.base_agent import ValidationError
from agents.story.schema import StoryOutput


def validate(output: StoryOutput) -> None:
    if len(output.scenes) < 2:
        raise ValidationError("Story needs at least 2 scenes.")
    if output.confidence < 0.4:
        raise ValidationError(
            "Confidence too low — reconsider the premise interpretation."
        )
    if not output.ending.strip():
        raise ValidationError("Ending is missing or empty.")
```

```python
# agents/story/mapper.py
from agents.story.schema import StoryOutput


def to_state(output: StoryOutput) -> dict:
    """LLM output -> GraphState partial update. Never mutate state directly (Point 3)."""
    return {
        "story": output,
        "logs": [f"story agent produced '{output.title}' with {len(output.scenes)} scenes"],
        "scores": {"story_confidence": output.confidence},
    }
```

```python
# agents/story/service.py
from core.base_agent import BaseAgent
from core.config import settings
from agents.story.schema import StoryOutput
from agents.story import prompt as prompt_mod
from agents.story import validator as validator_mod
from agents.story import mapper as mapper_mod


class StoryService(BaseAgent):
    def build_prompt(self, context, knowledge, feedback=""):
        return prompt_mod.build(context, knowledge, feedback)

    def response_model(self):
        return StoryOutput

    def validate(self, output):
        validator_mod.validate(output)

    def map_output(self, output):
        return mapper_mod.to_state(output)

    def model_config(self):
        return settings.story_model

    def retrieval_query(self, context):
        return context["state"].get("premise", "")
```

```python
# agents/story/node.py
"""LangGraph integration ONLY. Nothing else lives here (Point 2)."""
from core.container import Container
from agents.story.service import StoryService


def make_story_node(container: Container):
    service = StoryService(container)

    async def node(state: dict) -> dict:
        return await service.execute(state)

    return node
```

Notice `node.py` never imports `prompt.py`, `validator.py`, or `mapper.py` —
it only knows `service.execute()` exists. That's the whole point of Point 2.

---

## 11. Node-Level RetryPolicy + Loop Guards (Addition #3, #8)

```python
# graph/build.py
from langgraph.graph import StateGraph, END
from langgraph.pregel import RetryPolicy
from langgraph.checkpoint.postgres import PostgresSaver
from litellm.exceptions import RateLimitError, Timeout

from core.state import GraphState
from core.container import build_container
from agents.story.node import make_story_node
from graph.director import route_after_story


def build_graph():
    container = build_container()
    graph = StateGraph(GraphState)

    graph.add_node(
        "story",
        make_story_node(container),
        retry=RetryPolicy(
            max_attempts=3,
            # Only retry INFRA failures here — validation failures are
            # already handled inside BaseAgent.execute() with feedback
            # injection, which is a different failure mode (Addition #3).
            retry_on=lambda e: isinstance(e, (RateLimitError, Timeout)),
        ),
    )

    graph.set_entry_point("story")
    graph.add_conditional_edges("story", route_after_story)

    # Loop guard (Addition #8): recursion_limit is set at invoke-time
    # (see main.py), and story_retry_count in state caps any agent
    # that can re-trigger itself or a peer.

    checkpointer = PostgresSaver.from_conn_string(
        __import__("core.config", fromlist=["settings"]).settings.postgres_dsn
    )
    return graph.compile(checkpointer=checkpointer)
```

```python
# graph/director.py
"""
Director owns ONLY routing decisions — who runs next, retry-or-not,
stop-or-continue. No prompts, no validation, no business rules live
here (Point 13).
"""
from langgraph.graph import END


def route_after_story(state: dict) -> str:
    retries = state.get("story_retry_count", 0)
    if retries >= 3:
        return END  # loop guard — stop escalating (Addition #8)

    scores = state.get("scores", {})
    if scores.get("story_confidence", 1.0) < 0.5:
        return "story"  # low confidence -> re-run

    return "character"  # hand off to the next specialist
```

---

## 12. Human-in-the-Loop via `interrupt()` (Addition #4)

Decide **early** where approval gates live — retrofitting this after five
agents exist means touching every validator.

```python
# agents/story/node.py (extended with an approval gate)
from langgraph.types import interrupt
from core.container import Container
from agents.story.service import StoryService


def make_story_node(container: Container):
    service = StoryService(container)

    async def node(state: dict) -> dict:
        result = await service.execute(state)

        if result["scores"]["story_confidence"] < 0.6:
            decision = interrupt({
                "question": "Low-confidence story — approve, edit, or reject?",
                "story": result["story"].model_dump(),
            })
            if decision == "reject":
                result["logs"] = ["story rejected by human reviewer"]
                result["story"] = None

        return result

    return node
```

Resuming after an interrupt (from your API layer or `main.py`):

```python
# main.py (resume flow)
from langgraph.types import Command

# First call pauses at interrupt() and returns the interrupt payload
config = {"configurable": {"thread_id": "story-42"}}
result = await graph.ainvoke({"premise": "a lighthouse keeper finds a letter"}, config=config)

# ... show result["__interrupt__"] to a human, get their decision ...

# Resume with their decision
result = await graph.ainvoke(Command(resume="approve"), config=config)
```

This only works because a checkpointer is attached (Section 11) — without
it, `interrupt()` has nowhere to persist the paused state.

---

## 13. Checkpointer + `thread_id` Strategy (Addition #5)

```python
# core/config.py already defines postgres_dsn.
# Decide thread_id strategy explicitly — don't leave it implicit:
#
#   thread_id = f"user:{user_id}:story:{story_draft_id}"
#
# This determines the granularity of resumability. Per-draft is usually
# right for creative-writing tools: a user can walk away and resume a
# specific draft days later without state bleeding across drafts.
```

```python
# main.py
import asyncio
from graph.build import build_graph
from agents.story.schema import StoryInput


async def main():
    graph = build_graph()
    config = {
        "configurable": {"thread_id": "user:123:story:draft-7"},
        "recursion_limit": 15,  # explicit loop guard (Addition #8)
    }
    result = await graph.ainvoke(
        {"premise": "a lighthouse keeper finds a letter with no sender"},
        config=config,
    )
    print(result["story"])


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 14. Command for Combined Routing + State Update (Addition #2)

Use sparingly — only when an agent genuinely knows better than the director
who should run next (e.g., a validator that detects a completely different
failure mode). Overusing this from inside agents erodes Point 13.

```python
from langgraph.types import Command


async def node(state: dict) -> Command:
    result = await service.execute(state)
    if result["story"] is None:
        return Command(update=result, goto="human_review")
    return Command(update=result, goto="character")
```

---

## 15. Testing via Dependency Injection (Point 5, tying it together)

```python
# tests/test_story_service.py
import pytest
from unittest.mock import AsyncMock
from core.container import Container
from agents.story.service import StoryService
from agents.story.schema import StoryOutput, Scene


@pytest.mark.asyncio
async def test_story_service_maps_output_correctly():
    fake_llm = AsyncMock()
    fake_llm.complete.return_value = StoryOutput(
        title="The Letter",
        scenes=[Scene(heading="Arrival", description="..."), Scene(heading="Discovery", description="...")],
        ending="He finally opens it.",
        confidence=0.9,
    )
    fake_retriever = AsyncMock()
    fake_retriever.retrieve.return_value = "some retrieved knowledge"

    container = Container(llm=fake_llm, retriever=fake_retriever)
    service = StoryService(container)

    result = await service.execute({"premise": "a lighthouse keeper finds a letter"})

    assert result["story"].title == "The Letter"
    assert result["scores"]["story_confidence"] == 0.9
    fake_llm.complete.assert_awaited_once()
```

No network call, no real LLM, no vector store — because nothing in
`StoryService` reaches for a global client. That's the entire payoff of
Point 5.

---

## 16. Streaming Pass-Through (Addition #7)

If you need token-level streaming to a UI, it has to survive every layer
unbuffered:

```python
# agents/story/node.py (streaming variant)
async def stream_node(state: dict):
    async for chunk in service.stream(state):  # service.stream, not service.execute
        yield chunk
```

```python
# core/base_agent.py — add alongside execute()
async def stream(self, state: dict):
    context = self.load_context(state)
    knowledge = await self.retriever.retrieve(self.retrieval_query(context))
    prompt = self.build_prompt(context, knowledge)
    async for chunk in self.llm.stream(prompt, self.model_config()):
        yield chunk
```

Test this path explicitly — it's the one addition on this list that looks
fine in a demo and breaks silently the first time someone wraps it in one
more decorator "just for logging."

---

## 17. Opaque Node vs Subgraph-Per-Step (Addition #6)

Two legitimate choices, pick one deliberately per agent rather than
defaulting to opaque because it's less code:

| | Opaque node (`node.py -> service.execute()`) | Subgraph per pipeline step |
|---|---|---|
| Graph trace granularity | One node in LangSmith trace | Each of load/retrieve/prompt/llm/validate visible separately |
| Per-step checkpointing | No — all or nothing | Yes — resume mid-pipeline |
| Per-step retry | No — retry re-runs the whole service | Yes — retry just the failed step |
| Complexity | Low | Higher — more edges, more state |

Use subgraphs when a single step (e.g., a slow retrieval call) is expensive
enough that retrying the whole pipeline on its failure is wasteful. Use
opaque nodes for cheap, fast agents where the extra graph machinery isn't
worth the trace noise.

---

## 18. Summary Checklist

- [ ] State reducers explicit for every field touched by >1 agent
- [ ] `node.py` imports nothing but `service`
- [ ] Every agent: `load_context → retrieve → prompt → llm → validate → map`
- [ ] All LLM calls go through `LLMClient`, never a raw provider SDK
- [ ] Prompts externalized + versioned in `/prompts`, config separate in `core/config.py`
- [ ] `RetryPolicy` for infra errors; feedback-loop retry for validation errors — not conflated
- [ ] Checkpointer attached, `thread_id` strategy decided explicitly
- [ ] `interrupt()` gates placed deliberately, not retrofitted
- [ ] `recursion_limit` set at invoke time; retry counters in state
- [ ] Director (`graph/director.py`) contains zero prompts/validation/business rules
- [ ] Services tested via DI mocks — zero real network calls in unit tests
- [ ] Streaming path tested end-to-end if the UI needs it
