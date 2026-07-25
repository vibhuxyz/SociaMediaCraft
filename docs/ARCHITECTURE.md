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