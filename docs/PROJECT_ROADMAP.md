# VideoCraft V3 — AI Director Brain (Pre-Production Studio)

> **Goal:** Build the intelligence layer of VideoCraft.  
> V3 is responsible for understanding the user's vision, collecting missing creative information, planning the entire production, and producing a complete cinematic blueprint.

---

## What V3 Does NOT Do

- Generate images
- Generate videos
- Generate voice
- Generate music
- Render videos

**Its only responsibility is planning.**

---

## Input & Output

| Input | Output |
|-------|--------|
| `User Prompt` + `Creative Brief` + `Brand Assets` | `CreativePlan.json` |

`CreativePlan.json` becomes the single source of truth for V4+ (Generation & Rendering).

---

## High-Level Architecture

````

                                                     USER
                                                      │
                                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React / Next.js)                              │
│──────────────────────────────────────────────────────────────────────────────│
│ • Create Project                                                            │
│ • Analyze Project                                                           │
│ • Fill Missing Information                                                  │
│ • Generate Project                                                          │
│                                                                              │
│ API Calls                                                                    │
│ POST /projects                                                               │
│ POST /projects/{id}/analyze                                                  │
│ POST /projects/{id}/finalize                                                 │
│                                                                              │
│ ◄──────────── SSE / WebSocket Progress Updates ─────────────►                │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                          │
│                                                                              │
│ Authentication • Credits • Validation • Rate Limit                           │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        PROJECT SERVICE                                       │
│                                                                              │
│ ✓ Create Project                                                             │
│ ✓ Create Job                                                                 │
│ ✓ Update Status                                                              │
└───────────────────┬───────────────────────────────┬──────────────────────────┘
                    │                               │
                    ▼                               ▼
            PostgreSQL                      RabbitMQ
      Projects • Jobs • Status         planning_queue
                                                │
                                                ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                  ORCHESTRATOR SERVICE (Node.js)                              │
│──────────────────────────────────────────────────────────────────────────────│
│ ✓ Consume Queue                                                              │
│ ✓ Decide Workflow                                                            │
│ ✓ Retry Failed Jobs                                                          │
│ ✓ Dispatch Worker                                                            │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    WORKER SERVICE (Node.js)                                  │
│──────────────────────────────────────────────────────────────────────────────│
│ ✓ Load Project                                                               │
│ ✓ Build AI Context                                                           │
│ ✓ Call Python AI Engine                                                      │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
═══════════════════════════════════════════════════════════════════════════════════════
                           PYTHON AI ENGINE
═══════════════════════════════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────────────────────────┐
│ KNOWLEDGE LAYER                                                              │
│──────────────────────────────────────────────────────────────────────────────│
│ Knowledge & Research Agent                                                   │
│ • Brand Guidelines                                                           │
│ • Previous Campaigns                                                         │
│ • Brand Assets                                                               │
│ • Template Rules                                                             │
│ • Localization                                                               │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ DIRECTOR LAYER                                                               │
│──────────────────────────────────────────────────────────────────────────────│
│ Director Agent                                                               │
│ Overall Creative Decision Maker                                              │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ ANALYSIS LAYER                                                               │
│──────────────────────────────────────────────────────────────────────────────│
│ Intent Classifier                                                            │
│ Requirement Analyzer                                                         │
│ Brief Validator                                                              │
│ Missing Information Detector                                                 │
│ Importance Scorer                                                            │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
═══════════════════════════════════════════════════════════════════════════════════════
                         DECISION ENGINE
═══════════════════════════════════════════════════════════════════════════════════════

                     Is information complete?
                               │
                 ┌─────────────┴──────────────┐
                 │                            │
                 ▼                            ▼
          AI Can Infer                  Need User Input
                 │                            │
                 ▼                            ▼
      Intelligent Defaults         Clarification Agent
                                           │
                                           ▼
                                  Dynamic Question Builder
                                           │
                                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ Missing Information Payload                                                  │
│──────────────────────────────────────────────────────────────────────────────│
│ Story                                                                       │
│   ○ Generate with AI                                                        │
│   ○ I'll write it                                                           │
│                                                                              │
│ Script                                                                      │
│   ○ Generate with AI                                                        │
│   ○ I'll write it                                                           │
│                                                                              │
│ Voice                                                                       │
│   ○ AI                                                                      │
│   ○ Upload                                                                  │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
                          Return To Worker Service
                                      │
                                      ▼
                              Redis Pub/Sub
                                      │
                                      ▼
                           SSE / WebSocket Event
                                      │
                                      ▼
                                  Frontend
                                      │
                                      ▼
                         User Completes Information
                                      │
                       POST /projects/{id}/finalize
                                      │
                                      ▼
                         Worker Resumes AI Pipeline

═══════════════════════════════════════════════════════════════════════════════════════
                    CREATIVE PLANNING PIPELINE
═══════════════════════════════════════════════════════════════════════════════════════

Campaign Strategy
        │
Audience & Localization
        │
Brand Identity
        │
Casting Director
        │
Character Designer
        │
Environment Designer
        │
Art Director
        │
Story Architect
        │
Screenplay Writer
        │
Dialogue Writer
        │
Narration Writer
        │
Voice Director
        │
Music Director
        │
Sound Design Director
        │
Storyboard Director
        │
Cinematography Director
        │
Shot Planner
        │
Prompt Engineering
        │
Asset Planner
        │
Quality Review
        │
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ Production Plan Builder                                                     │
│──────────────────────────────────────────────────────────────────────────────│
│ Generates CreativePlan.json                                                 │
└─────────────────────────────────────┬────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    WORKER SERVICE (Node.js)                                  │
│──────────────────────────────────────────────────────────────────────────────│
│ ✓ Save PostgreSQL                                                           │
│ ✓ Publish Redis Events                                                      │
│ ✓ Queue Generation Job                                                      │
│ ✓ Update Status                                                             │
└───────────────┬────────────────────────────┬─────────────────────────────────┘
                │                            │
                ▼                            ▼
          PostgreSQL                 RabbitMQ (Generation)
                │
                ▼
          Redis Pub/Sub
                │
                ▼
       SSE / WebSocket
                │
                ▼
           FRONTEND

````
---

## V3.1 — AI Engine Foundation

**Goal:** Create the AI service.

**Build:**
- Python project structure
- Virtual environments
- Logging
- LiteLLM integration
- LangGraph setup
- Configuration management
- Provider abstraction
- Environment variables
- Server (`server.py`)

**Output:** AI Engine Running

**Tech Stack:**
- Python (AsyncIO, Typing, Dataclasses, Error handling, Dependency Injection)
- LiteLLM (OpenAI, Gemini, Open Source Models, HuggingFace)
- Model routing, Retry, Streaming, Cost tracking

---

## V3.2 — Workflow Foundation

**Goal:** Build the LangGraph workflow engine.

**Build:**
- `graph.py` — StateGraph definition
- `state.py` — Shared state schema
- `nodes.py` — Node implementations
- `router.py` — Conditional edge routing
- `checkpoints.py` — Persistence & checkpointing

**Learn:**
- Graph construction
- Retry logic
- Conditional routing
- Checkpointing
- Interrupt handling

---

## V3.3 — Shared State

**Goal:** Every agent shares one state object. Every node updates only its section.

**Flow:**
```
Prompt → Director → Classifier → Requirements → Characters → Story → CreativePlan
```

**Shared `VideoState` / `CreativeState`:**

| Field | Owner |
|-------|-------|
| `prompt` | User |
| `project_type` | Classifier |
| `requirements` | Requirement Analyzer |
| `missing_information` | Missing Info Detector |
| `clarification_questions` | Clarification Agent |
| `clarification_answers` | User |
| `director_plan` | Director Agent |
| `campaign_strategy` | Campaign Strategy Agent |
| `audience_localization` | Audience & Localization Agent |
| `brand_identity` | Brand Identity Agent |
| `casting` | Casting Director |
| `character_sheet` | Character Designer |
| `environment_sheet` | Environment Designer |
| `style_sheet` / `art_direction` | Art Director |
| `emotion_plan` | Emotion Analyzer |
| `story` | Story Architect |
| `screenplay` | Screenplay Writer |
| `dialogue` | Dialogue Writer |
| `narration` | Narration Writer |
| `voice_plan` | Voice Director |
| `music_plan` | Music Director |
| `sound_design` | Sound Design Director |
| `storyboard` | Storyboard Director |
| `camera_plan` | Cinematography Director |
| `shot_plan` | Shot Planner |
| `prompt_pack` | Prompt Engineering Agent |
| `asset_plan` | Asset Planner |
| `quality_report` | Quality Review Agent |
| `production_plan` / `creative_plan` | Production Plan Builder |

---

## V3.4 — Director Agent

**Responsibility:** Understand the user's creative vision.

**Output:**
- `genre`
- `purpose`
- `target_audience`
- `tone`
- `duration`
- `style`
- `references`

---

## V3.5 — Intent / Project Classifier

**Responsibility:** Determine what the user is creating.

**Project Types:**
- Story Film
- Commercial
- Travel Reel
- Product Advertisement
- Documentary
- Real Estate
- Wedding
- Music Video
- Animation
- Fashion

> Different project types trigger different planning flows.

---

## V3.6 — Requirement Analyzer

**Responsibility:** Extract everything already known from the user prompt.

**Example:**
| Input | Output |
|-------|--------|
| *"Crowded train station. Golden hour. Two people hug."* | **Known:** characters: 2, location: train station, time: golden hour, action: hug |
| | **Missing:** appearance, clothing, camera |

---

## V3.7 — Brief Validator

**Responsibility:** Check for critical errors before planning begins.

**Checks:**
- Missing product info
- Invalid duration
- Missing template
- Invalid input
- Conflicting requests

---

## V3.8 — Missing Information Detector

**Responsibility:** Compare required information with available information.

**Example:**
| Question | Answer |
|----------|--------|
| Need Character? | YES |
| Need Camera? | YES |
| Need Story? | NO |

---

## V3.9 — Importance Scorer

**Responsibility:** Not every missing field needs user input.

**Example:**
| Missing | Impact | Action |
|---------|--------|--------|
| Eye Color | Low | Use defaults |
| Character Appearance | Very High | Ask user |

---

## V3.10 — Clarification Agent

**Responsibility:** Generate dynamic interview questions instead of fixed forms.

**Questions adapt by project type:**

| Project Type | Sample Questions |
|--------------|------------------|
| **Story Project** | 👥 Characters, 🌍 Environment, 🎬 Style, 📷 Camera, 🎵 Audio |
| **Product Advertisement** | 📦 Product, 🎨 Branding, 🎯 Audience, 🎬 Style |
| **Travel Video** | 🌍 Destination, ☀ Weather, 🎥 Activities, 📷 Camera Style |

**Additional checks:**
- Which country is this advertisement for?
- Should the actors be Indian or international?
- Voice language preference?
- CTA requirements?

---

## V3.11 — Knowledge & Research Agent *(New)*

**Responsibility:** Gather context before creative planning when needed.

**Actions:**
- If user uploads brand guidelines → parse and apply
- If user provides a logo → extract colors and placement rules
- If user mentions an existing campaign → maintain consistency
- If user chooses a template → load best practices and predefined shot structures
- If user specifies a country → apply localization defaults

---

## V3.12 — Campaign Strategy Agent

**Responsibility:** Define the strategic backbone of the creative.

**Output:**
- **Goal:** Brand awareness / Conversion / Engagement
- **Primary Emotion:** Luxury / Joy / Trust / Excitement
- **Call To Action:** Buy Now / Learn More / Subscribe
- **Message:** Core campaign message (e.g., *"Confidence attracts."*)

---

## V3.13 — Audience & Localization Agent

**Responsibility:** Ensure cultural and regional relevance.

**Output:**
- `country`
- `language`
- `accent`
- `culture`
- `festival` (if applicable)
- `legal_rules` (e.g., Meta Safe, regional compliance)

> **Extremely important** for global campaigns.

---

## V3.14 — Brand Identity Agent

**Responsibility:** Lock brand consistency across all assets.

**Output:**
- `brand_personality` (Luxury, Elegant, Premium)
- `color_palette`
- `typography`
- `logo_rules`
- `product_placement_rules`
- `tagline`

---

## V3.15 — Casting Director

**Responsibility:** Define who appears in the production.

**Output (per character):**
- `gender`
- `ethnicity` / `nationality`
- `age`
- `archetype` (Luxury CEO, Fashion Model, etc.)
- `build` / `physique`

**Future:** Can recommend AI avatars or digital humans.

---

## V3.16 — Character Designer

**Responsibility:** Creates reusable Character Sheets.

**Output:**
```yaml
characters:
  - name: ""
    gender: ""
    age: ""
    appearance:
      face: ""
      hair: ""
      eyes: ""
      build: ""
    clothing:
      outfit_1: ""
      outfit_2: ""
    accessories: []
    expressions: []
    poses: []
    reference_images: []
```

---

## V3.17 — Environment Designer

**Responsibility:** Build the world where the story lives.

**Output:**
```yaml
environment:
  location: ""
  country: ""
  city: ""
  architecture: ""
  season: ""
  weather: ""
  lighting: ""
  time_of_day: ""
  furniture: ""
  luxury_assets: []
```

---

## V3.18 — Art Director (Style Designer)

**Responsibility:** Creates the overall visual language.

**Output:**
```yaml
art_direction:
  visual_style: ""        # e.g., Apple Style, Tom Ford Style
  camera: ""
  lens: ""
  film_stock: ""
  color_grading: ""
  aspect_ratio: ""
  fps: ""
  mood: ""                # e.g., Luxury, Minimalism, Warm Gold
```

---

## V3.19 — Emotion Analyzer

**Responsibility:** Creates emotional progression across the narrative.

**Output:**
```yaml
emotion_plan:
  opening: ""
  middle: ""
  ending: ""
  primary: ""
  secondary: ""
```

---

## V3.20 — Story Architect

**Responsibility:** Creates narrative structure.

**Output:**
- Beginning
- Middle
- Ending
- Conflict
- Resolution
- Scene Summary

> Expands one sentence into a professional commercial story.

---

## V3.21 — Screenplay Writer

**Responsibility:** Writes every scene professionally.

**Output:**
- Scene-by-scene breakdown
- Scene descriptions
- Action lines
- Professional formatting

---

## V3.22 — Dialogue Writer

**Responsibility:** Creates natural dialogue.

**Rules:**
- Natural, culturally appropriate dialogue
- Or **no dialogue** if the project demands it (e.g., luxury ads)

---

## V3.23 — Narration Writer

**Responsibility:** Creates professional ad narration / voiceover script.

**Output:**
- Narration text per scene
- Timing markers
- Tone indicators

---

## V3.24 — Voice Director

**Responsibility:** Plan the voiceover production.

**Output:**
```yaml
voice_plan:
  provider: "ElevenLabs"  # or other
  gender: ""
  accent: ""
  emotion: ""
  energy: ""              # Low / Medium / High
  pace: ""                # Slow / Medium / Fast
```

---

## V3.25 — Music Director

**Responsibility:** Plan the musical score.

**Output:**
```yaml
music_plan:
  genre: ""               # e.g., Luxury Commercial
  tempo: ""               # e.g., 72 BPM
  mood: ""                # e.g., Elegant
  instruments:
    - strings
    - piano
    - synth
  ending_build: true/false
```

---

## V3.26 — Sound Design Director

**Responsibility:** Plan all non-music audio.

**Output:**
```yaml
sound_design:
  ambient: []             # Room tone, wind
  foley: []               # Footsteps, fabric, glass
  sfx: []                 # Perfume spray, door, specific actions
```

---

## V3.27 — Storyboard Director

**Responsibility:** Break screenplay into visual scenes.

**Output:**
- Scene 1, Scene 2, Scene 3...
- Visual descriptions per scene
- Key frames

---

## V3.28 — Cinematography Director

**Responsibility:** Convert scenes into filmmaking language.

**Output:**
```yaml
camera_plan:
  camera: ""
  lens: ""
  movement: ""
  lighting: ""
  composition: ""
  focus: ""
  depth: ""
  transitions: ""
```

---

## V3.29 — Shot Planner

**Responsibility:** Expand every storyboard scene into executable shots.

**Example:**
```yaml
shots:
  - shot_id: 1
    duration: "6s"
    camera: "Slow Dolly"
    lens: "50mm"
    lighting: "Golden Hour"
    composition: "Rule of Thirds"
    transition: "Cut"
```

---

## V3.30 — Prompt Engineering Agent *(New — Critical)*

**Responsibility:** Convert creative ideas into optimized prompts for each generation model.

**Adapts creative intent per provider:**

| Asset Type | Target Format |
|------------|---------------|
| Image Prompt | FLUX format |
| Video Prompt | Veo format |
| Voice Prompt | ElevenLabs format |
| Music Prompt | Music API format |

> Different models perform best with different prompt structures. This agent adapts accordingly.

---

## V3.31 — Asset Planner *(New)*

**Responsibility:** Calculate exact asset requirements for V4.

**Example Output:**
```yaml
asset_plan:
  images: 18
  video_clips: 18
  narration: 1
  music_tracks: 1
  sound_fx: 8
  thumbnail: 1
  poster: 1
```

---

## V3.32 — Quality Review Agent *(New)*

**Responsibility:** Final gate before V4. Checks everything.

**Validation Checklist:**
- [ ] Story consistency
- [ ] Character consistency
- [ ] Timeline continuity
- [ ] Brand consistency
- [ ] Missing assets
- [ ] Prompt completeness
- [ ] Audio coverage
- [ ] Rendering readiness

> Only if everything passes does it produce `CreativePlan.json`.

---

## V3.33 — Production Plan Builder

**Responsibility:** Merge every agent's output into a single validated document.

**Actions:**
- Aggregate all agent outputs
- Validate using Pydantic
- Generate `CreativePlan.json`

---

## Final Output: `CreativePlan.json`

```json
{
  "metadata": {},
  "project": {},
  "project_type": "",
  "director": {},
  "campaign_strategy": {},
  "audience_localization": {},
  "brand_identity": {},
  "casting": {},
  "requirements": {},
  "characters": {},
  "environment": {},
  "art_direction": {},
  "style": {},
  "emotion": {},
  "story": {},
  "screenplay": {},
  "dialogue": {},
  "narration": {},
  "voice_plan": {},
  "music_plan": {},
  "sound_design": {},
  "storyboard": [],
  "camera": {},
  "cinematography": {},
  "shots": [],
  "shot_list": {},
  "prompt_pack": {},
  "asset_plan": {},
  "timeline": {},
  "rendering_rules": {},
  "quality_report": {},
  "production_plan": {}
}
```

---

## Folder Structure

```
services/
└── ai-engine/
    ├── server.py
    │
    ├── workflow/
    │   ├── graph.py
    │   ├── state.py
    │   ├── nodes.py
    │   ├── router.py
    │   └── checkpoints.py
    │
    ├── agents/
    │   ├── director/
    │   ├── classifier/
    │   ├── requirement_analyzer/
    │   ├── brief_validator/
    │   ├── missing_info_detector/
    │   ├── importance_scorer/
    │   ├── clarification/
    │   ├── knowledge_research/          # NEW
    │   ├── campaign_strategy/           # NEW
    │   ├── audience_localization/       # NEW
    │   ├── brand_identity/              # NEW
    │   ├── casting_director/            # NEW
    │   ├── character_designer/
    │   ├── environment_designer/
    │   ├── art_director/                # (was style_designer)
    │   ├── emotion/
    │   ├── story_architect/
    │   ├── screenplay/
    │   ├── dialogue_writer/             # NEW
    │   ├── narration_writer/            # NEW
    │   ├── voice_director/              # NEW
    │   ├── music_director/              # NEW
    │   ├── sound_design/                # NEW
    │   ├── storyboard/
    │   ├── cinematography/
    │   ├── shot_planner/
    │   ├── prompt_engineering/          # NEW
    │   ├── asset_planner/               # NEW
    │   └── quality_review/              # NEW
    │
    ├── prompts/
    │
    ├── providers/
    │   └── llm/
    │
    ├── schemas/
    │
    ├── knowledge/
    │   ├── cameras/
    │   ├── lenses/
    │   ├── lighting/
    │   ├── composition/
    │   ├── styles/
    │   ├── emotions/
    │   └── filmmaking/
    │
    ├── config/
    ├── utils/
    └── tests/
```

---

## What You'll Learn

### Python
- Project structure
- Virtual environments
- AsyncIO
- Typing
- Dataclasses
- Logging
- Error handling
- Dependency Injection

### LangGraph
- StateGraph
- Nodes
- Edges
- Conditional Edges
- Retry
- Interrupt
- Checkpointing
- State Management

### LiteLLM
- OpenAI, Gemini, Open Source Models, HuggingFace
- Model routing
- Retry
- Streaming
- Cost tracking

### Pydantic
- BaseModel
- Nested Models
- Validation
- Serialization
- Enums
- Field Validators

### Prompt Engineering
- System Prompts
- Role Prompting
- Structured Outputs
- JSON Outputs
- Prompt Templates

### AI System Design
- Multi-Agent Systems
- AI Orchestration
- Intent Classification
- Requirement Extraction
- Decision Making
- Production Planning
- Structured State Management
- Brand Consistency
- Localization
- Quality Assurance
