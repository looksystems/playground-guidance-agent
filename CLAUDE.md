# CLAUDE.md - AI Assistant Guide for Pension Guidance Chat

This document provides comprehensive guidance for AI assistants (like Claude) working on this codebase.

## Project Overview

**Pension Guidance Chat** is an enterprise-grade AI agent that provides FCA-compliant pension guidance through an intuitive chat interface. Built with Test-Driven Development (TDD) and advanced agentic learning capabilities based on research papers (Generative Agents/Simulacra and Agent Hospital/MedAgent-Zero).

**Status**: ✅ Production Ready
- **Tests**: 417+ passing (214 backend, 203 frontend, 100% pass rate)
- **Documentation**: 8000+ lines across 63+ specification documents
- **Implementation**: November 2025

## Quick Reference

### Key Paths
- **Backend Source**: `src/guidance_agent/` (11,249 lines Python)
- **Frontend Source**: `frontend/app/` (8,469 lines Vue/TypeScript)
- **Backend Tests**: `tests/` (214 tests)
- **Frontend Tests**: `frontend/tests/` (203 tests)
- **Documentation**: `docs/` (8 comprehensive guides)
- **Specifications**: `specs/` (63 detailed specs, 700KB+)
- **Prompt Templates**: `src/guidance_agent/templates/` (20 Jinja2 templates)

### Key Commands
```bash
# Backend
uv sync                                    # Install dependencies
uv run uvicorn guidance_agent.api.main:app --reload  # Run backend
pytest                                     # Run all backend tests
pytest tests/api/                          # Run API tests (146)
pytest tests/templates/                    # Run template tests (40)

# Frontend
cd frontend && npm install                 # Install dependencies
npm run dev                               # Run dev server (port 3000)
npm test                                  # Run Playwright tests (83)
npm run test:e2e                          # Run E2E tests (99)

# Docker
docker-compose up -d postgres phoenix backend  # Start backend stack
docker-compose up -d                      # Start full stack
./scripts/deploy.sh                       # Production deployment
```

## Architecture Overview

### Tech Stack

**Frontend (Nuxt 3)**:
- Framework: Nuxt 3 (Vue 3 + TypeScript)
- UI: Nuxt UI 4, Tailwind CSS
- State: Pinia
- AI: Vercel AI SDK (SSE streaming)
- Testing: Playwright (E2E), Vitest (component)
- Charts: Chart.js, vue-chartjs

**Backend (FastAPI)**:
- Framework: FastAPI (async Python)
- ORM: SQLAlchemy + Alembic migrations
- Database: PostgreSQL + pgvector
- LLM: LiteLLM (multi-provider: OpenAI, Anthropic, AWS Bedrock, Azure, LM Studio, Ollama)
- Templates: Jinja2 (20 prompt templates)
- Observability: Arize Phoenix (LLM tracing)
- Validation: Pydantic v2
- Testing: Pytest, pytest-asyncio, httpx

**Infrastructure**:
- Containerization: Docker, Docker Compose
- Package Manager: uv (fast Python dependency manager)
- ASGI Server: Uvicorn
- Reverse Proxy: Nginx (production)

### System Architecture

```
┌─────────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│   Nuxt 3 Frontend   │ SSE  │   FastAPI Backend   │      │   PostgreSQL DB     │
│   (Port 3000)       │◄─────│   (Port 8000)       │◄─────│   + pgvector        │
│                     │      │                     │      │   (Port 5432)       │
│ • Customer Chat     │      │ • REST API          │      │                     │
│ • Admin Dashboard   │      │ • Advisor Agent     │      │ • 7 Core Models     │
│ • Analytics         │      │ • Customer Agent    │      │ • Vector Search     │
│ • Data Management   │      │ • Compliance Validation│   │ • Audit Logs        │
└─────────────────────┘      └─────────────────────┘      └─────────────────────┘
                                      │
                                      ├──────► LiteLLM (Multi-provider)
                                      │        • OpenAI GPT-4
                                      │        • Anthropic Claude
                                      │        • AWS Bedrock
                                      │        • Azure OpenAI
                                      │        • LM Studio (local)
                                      │        • Ollama (local)
                                      │
                                      └──────► Arize Phoenix (Port 6006)
                                               • LLM Tracing
                                               • Observability
                                               • Performance Monitoring
```

### Directory Structure

```
guidance-agent/
├── src/guidance_agent/          # Backend (11,249 lines Python)
│   ├── api/                     # FastAPI REST API
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── routers/             # API route handlers
│   │   │   ├── consultations.py    # Chat endpoints (SSE streaming)
│   │   │   ├── memories.py          # Memory CRUD
│   │   │   ├── cases.py             # Case CRUD
│   │   │   ├── rules.py             # Rule CRUD
│   │   │   ├── fca_knowledge.py     # FCA knowledge CRUD
│   │   │   ├── pension_knowledge.py # Pension knowledge CRUD
│   │   │   ├── customers.py         # Customer CRUD
│   │   │   └── settings.py          # System settings
│   │   └── dependencies.py      # Dependency injection (DB sessions)
│   │
│   ├── advisor/                 # Advisor Agent Implementation
│   │   ├── agent.py             # Main advisor agent logic
│   │   └── prompts.py           # Legacy prompts (migrated to Jinja2)
│   │
│   ├── compliance/              # FCA Compliance Validation
│   │   └── validator.py         # LLM-as-judge compliance validation
│   │
│   ├── core/                    # Core Infrastructure
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── config.py            # Environment configuration
│   │   ├── llm.py               # LiteLLM integration
│   │   └── embeddings.py        # Vector embeddings (1536 dims)
│   │
│   ├── customer/                # Customer Agent (Simulated)
│   │   ├── agent.py             # Customer simulation for testing
│   │   └── prompts.py           # Customer agent prompts
│   │
│   ├── environment/             # Virtual Environment Simulation
│   │   └── environment.py       # Training environment
│   │
│   ├── evaluation/              # Agent Evaluation System
│   │   └── evaluator.py         # Performance evaluation
│   │
│   ├── knowledge/               # Knowledge Base
│   │   ├── fca_knowledge.py     # FCA compliance knowledge
│   │   └── pension_knowledge.py # Pension domain knowledge (74KB)
│   │
│   ├── learning/                # Learning System
│   │   ├── case_based.py        # Case-based learning
│   │   ├── reflection.py        # Reflection generation
│   │   └── rule_learning.py     # Rule extraction & refinement
│   │
│   ├── models/                  # SQLAlchemy Models
│   │   ├── memory.py            # Memory stream (observations, reflections, plans)
│   │   ├── case.py              # Successful consultation cases
│   │   ├── rule.py              # Learned guidance principles
│   │   ├── consultation.py      # Session tracking
│   │   ├── fca_knowledge.py     # FCA compliance knowledge
│   │   ├── pension_knowledge.py # Domain knowledge
│   │   └── settings.py          # System settings (single-row)
│   │
│   ├── retrieval/               # RAG Retrieval System
│   │   └── retriever.py         # Multi-faceted context retrieval
│   │
│   └── templates/               # Jinja2 Prompt Templates (20 files)
│       ├── advisor/             # Advisor agent prompts
│       │   ├── system.jinja2            # System instructions
│       │   ├── guidance.jinja2          # Main guidance prompt
│       │   ├── guidance_reasoning.jinja2 # With chain-of-thought
│       │   ├── reflection.jinja2        # Reflection generation
│       │   └── rule_extraction.jinja2   # Rule learning
│       ├── compliance/          # Compliance validation
│       │   └── validation.jinja2        # FCA validation prompt
│       └── customer/            # Customer agent prompts
│           ├── system.jinja2            # Customer system prompt
│           └── message.jinja2           # Customer message generation
│
├── frontend/                    # Nuxt 3 Frontend (8,469 lines)
│   ├── app/
│   │   ├── components/          # Vue Components
│   │   │   ├── ChatMessage.vue      # Chat message display
│   │   │   ├── ChatInput.vue        # Message input
│   │   │   ├── ConsultationHistory.vue  # History list
│   │   │   ├── admin/               # Admin components
│   │   │   │   ├── DataTable.vue        # Generic CRUD table
│   │   │   │   ├── MemoryForm.vue       # Memory editor
│   │   │   │   ├── CaseForm.vue         # Case editor
│   │   │   │   ├── RuleForm.vue         # Rule editor
│   │   │   │   ├── SettingsForm.vue     # Settings editor
│   │   │   │   └── ComplianceDetails.vue # Validation reasoning display
│   │   │   └── forms/               # Form components
│   │   │
│   │   ├── pages/               # File-based Routing
│   │   │   ├── index.vue            # Customer chat interface
│   │   │   ├── history.vue          # Consultation history
│   │   │   └── admin/               # Admin dashboard
│   │   │       ├── index.vue            # Dashboard overview
│   │   │       ├── memories.vue         # Memory management
│   │   │       ├── cases.vue            # Case management
│   │   │       ├── rules.vue            # Rule management
│   │   │       ├── fca-knowledge.vue    # FCA knowledge
│   │   │       ├── pension-knowledge.vue # Pension knowledge
│   │   │       ├── customers.vue        # Customer management
│   │   │       ├── consultations.vue    # Consultation review
│   │   │       └── settings.vue         # System settings
│   │   │
│   │   ├── composables/         # Vue Composables
│   │   │   ├── useChat.ts           # Chat SSE streaming
│   │   │   ├── useConsultations.ts  # Consultation API
│   │   │   ├── useMemories.ts       # Memory CRUD
│   │   │   ├── useCases.ts          # Case CRUD
│   │   │   └── useSettings.ts       # Settings management
│   │   │
│   │   ├── stores/              # Pinia State Management
│   │   │   ├── chat.ts              # Chat state
│   │   │   └── admin.ts             # Admin state
│   │   │
│   │   └── utils/               # Utilities
│   │       └── api.ts               # API client
│   │
│   └── tests/                   # Playwright Tests (203 tests)
│       ├── chat.spec.ts             # Chat interface tests
│       ├── admin.spec.ts            # Admin dashboard tests
│       ├── accessibility.spec.ts    # WCAG 2.1 AA tests
│       ├── compliance-details.spec.ts # Validation reasoning tests (21)
│       └── e2e/                     # E2E test suites (99 tests)
│
├── tests/                       # Backend Tests (214 tests)
│   ├── api/                     # API Tests (146 tests)
│   │   ├── test_consultations.py    # Chat endpoints
│   │   ├── test_memories.py         # Memory CRUD
│   │   ├── test_cases.py            # Case CRUD
│   │   ├── test_rules.py            # Rule CRUD
│   │   ├── test_fca_knowledge.py    # FCA knowledge CRUD
│   │   ├── test_pension_knowledge.py # Pension knowledge CRUD
│   │   ├── test_customers.py        # Customer CRUD
│   │   └── test_settings.py         # Settings CRUD
│   │
│   ├── integration/             # Integration Tests (8 tests)
│   │   ├── test_advisor_flow.py     # End-to-end advisor flow
│   │   └── test_learning_cycle.py   # Learning system integration
│   │
│   ├── templates/               # Template Tests (40 tests)
│   │   └── test_template_rendering.py # All 20 Jinja2 templates
│   │
│   └── regression/              # Regression Tests (20 tests)
│       └── test_template_migration.py # Template migration validation
│
├── docs/                        # Documentation (8 guides)
│   ├── API_INTEGRATION.md           # Backend API guide
│   ├── DEPLOYMENT.md                # Production deployment (700+ lines)
│   ├── DOCKER_SETUP.md              # Container deployment
│   ├── TESTING.md                   # Testing guide
│   ├── EMBEDDING_DIMENSIONS.md      # Vector embedding config
│   └── PHASE*_SUMMARY.md            # Implementation phase summaries
│
├── specs/                       # Specifications (63 files, 700KB+)
│   ├── architecture.md              # System architecture (41KB)
│   ├── implementation-plan.md       # Implementation details (105KB)
│   ├── fca-compliance-manual.md     # Compliance guidelines (80KB)
│   ├── ui-ux-design-plan.md         # Design system
│   ├── validation-reasoning-display-plan.md # Compliance UI spec
│   └── JINJA_MIGRATION_COMPLETE.md  # Template migration report
│
├── scripts/                     # Utility Scripts
│   ├── bootstrap_all_knowledge.py   # Initialize knowledge base
│   ├── generate_seed_cases.py       # Generate seed cases
│   ├── train_advisor.py             # Training utility
│   └── deploy.sh                    # Deployment automation
│
├── alembic/                     # Database Migrations
│   ├── versions/                    # Migration scripts (3 migrations)
│   └── env.py                       # Alembic configuration
│
├── docker-compose.yml           # Multi-service orchestration
├── Dockerfile                   # Backend container
├── pyproject.toml               # Python dependencies (uv)
├── README.md                    # User-facing documentation
└── .env.example                 # Environment variables template
```

## Database Schema

### 7 Core Models (PostgreSQL + pgvector)

**1. Memory (Agent Memory Stream)**
- Stores observations, reflections, and plans
- Vector embeddings for similarity search
- Importance scoring (0-1) and temporal decay
- Fields: `id`, `agent_id`, `memory_type`, `content`, `embedding`, `importance`, `timestamp`, `metadata`

**2. Case (Successful Consultation Cases)**
- Task categorization for learning
- Customer situation + guidance provided
- Outcome tracking
- Vector similarity search
- Fields: `id`, `task_type`, `customer_situation`, `guidance_provided`, `outcome`, `embedding`, `confidence`, `created_at`

**3. Rule (Learned Guidance Principles)**
- Domain-specific learned rules
- Confidence scoring (0-1)
- Supporting evidence
- Refinement over time
- Fields: `id`, `domain`, `rule_text`, `confidence`, `evidence`, `embedding`, `last_used`, `created_at`

**4. Consultation (Session Tracking)**
- Full conversation history (JSONB)
- Outcome metrics
- Duration tracking
- Customer linkage
- Fields: `id`, `customer_id`, `conversation_history`, `start_time`, `end_time`, `outcome`, `compliance_scores`, `metadata`

**5. FCAKnowledge (FCA Compliance Knowledge)**
- Categorized compliance content
- Source tracking
- Vector search capability
- Fields: `id`, `category`, `content`, `source`, `embedding`, `created_at`, `updated_at`

**6. PensionKnowledge (Domain Knowledge, 74KB)**
- Category/subcategory structure
- Vector embeddings for RAG
- Fields: `id`, `category`, `subcategory`, `content`, `embedding`, `created_at`

**7. SystemSettings (Admin Configuration)**
- Single-row table (ID=1)
- AI model parameters
- Notification settings
- Compliance toggles
- Fields: `id`, `model_name`, `temperature`, `max_tokens`, `enable_compliance`, `enable_learning`, `notification_email`, `updated_at`

### Key Relationships
- `Consultation.customer_id` → `Customer.id`
- All models with `embedding` field use pgvector for similarity search
- All models have audit timestamps (`created_at`, `updated_at`)

## AI Agent System

### Advisor Agent (`src/guidance_agent/advisor/agent.py`)

**Core Capabilities**:
1. **Guidance Generation**: Provides FCA-compliant pension advice
2. **Context Retrieval**: Multi-faceted RAG from memories, cases, rules, FCA knowledge, pension knowledge
3. **Memory Management**: Stores observations, generates reflections and plans
4. **Case-Based Learning**: Learns from successful consultations
5. **Rule Learning**: Extracts and refines guidance principles
6. **Chain-of-Thought Reasoning**: Optional reasoning step before guidance (configurable)

**Prompt Templates** (Jinja2):
- `templates/advisor/system.jinja2`: System instructions
- `templates/advisor/guidance.jinja2`: Main guidance prompt
- `templates/advisor/guidance_reasoning.jinja2`: With chain-of-thought
- `templates/advisor/reflection.jinja2`: Reflection generation
- `templates/advisor/rule_extraction.jinja2`: Rule learning

**Key Methods**:
- `generate_guidance(message, context)`: Main guidance endpoint
- `store_observation(content)`: Add to memory stream
- `generate_reflection()`: Create strategic insights
- `learn_from_consultation(consultation)`: Extract cases and rules

### Customer Agent (`src/guidance_agent/customer/agent.py`)

**Purpose**: Simulated customer for testing and training

**Capabilities**:
1. Generate realistic customer messages
2. Simulate various pension scenarios
3. Provide feedback for agent evaluation

**Prompt Templates**:
- `templates/customer/system.jinja2`: Customer persona
- `templates/customer/message.jinja2`: Message generation

### Compliance Validation (`src/guidance_agent/compliance/validator.py`)

**LLM-as-Judge Validation**:
- Real-time FCA compliance checking
- Detailed reasoning and issue tracking
- Pass/fail determination
- Audit trail storage

**Prompt Template**:
- `templates/compliance/validation.jinja2`: Validation prompt

**Validation Output**:
```json
{
  "is_compliant": true/false,
  "score": 0.0-1.0,
  "reasoning": "Detailed LLM reasoning...",
  "issues_found": ["Issue 1", "Issue 2"],
  "timestamp": "2025-11-05T..."
}
```

### Retrieval System (`src/guidance_agent/retrieval/retriever.py`)

**Multi-Faceted RAG**:
1. **Memory Retrieval**: Recent observations + reflections (importance-weighted, temporal decay)
2. **Case Retrieval**: Similar consultation cases (vector similarity)
3. **Rule Retrieval**: Relevant learned rules (vector similarity)
4. **FCA Knowledge**: Compliance guidelines (vector similarity)
5. **Pension Knowledge**: Domain knowledge (vector similarity)

**Retrieval Strategy**:
- Recency: Temporal decay for memories
- Relevance: Vector similarity (cosine distance)
- Importance: Weighted scoring for memories

## Testing Strategy

### Backend Testing (214 tests, 100% pass rate)

**API Tests** (`tests/api/`, 146 tests):
- CRUD operations for all 7 data models
- SSE streaming endpoints
- Compliance validation
- Error handling
- Authentication & authorization

**Integration Tests** (`tests/integration/`, 8 tests):
- End-to-end advisor flow
- Learning cycle (observation → reflection → rule extraction)
- Multi-agent interaction

**Template Tests** (`tests/templates/`, 40 tests):
- All 20 Jinja2 templates
- Rendering with various contexts
- Edge cases and error handling

**Regression Tests** (`tests/regression/`, 20 tests):
- Template migration validation
- Backward compatibility
- Output consistency

**Running Backend Tests**:
```bash
pytest                          # All tests
pytest tests/api/               # API tests only (146)
pytest tests/integration/       # Integration tests (8)
pytest tests/templates/         # Template tests (40)
pytest tests/regression/        # Regression tests (20)
pytest --cov                    # With coverage
pytest -v -s                    # Verbose with output
pytest -k "test_name"           # Specific test
```

### Frontend Testing (203 tests, 100% pass rate)

**Component/Page Tests** (`frontend/tests/`, 83 tests):
- Chat interface components
- Admin dashboard components
- Form validation
- State management

**E2E Tests** (`frontend/tests/e2e/`, 99 tests):
- Full user workflows
- Multi-page interactions
- Data persistence
- Error scenarios

**Validation Reasoning Tests** (21 tests):
- Compliance details display
- Expandable reasoning UI
- Issues found rendering
- Pass/fail status

**Accessibility Tests**:
- WCAG 2.1 AA compliance
- Keyboard navigation
- Screen reader support
- Color contrast

**Running Frontend Tests**:
```bash
cd frontend
npm test                        # All Playwright tests (83)
npm run test:e2e                # E2E tests (99)
npm run test:ui                 # Interactive UI mode
npm run test:coverage           # Coverage report
npm run test:e2e:report         # HTML report

# Specific test files
npx playwright test chat.spec.ts
npx playwright test admin.spec.ts
npx playwright test accessibility.spec.ts
npx playwright test compliance-details.spec.ts
```

### Test-Driven Development (TDD) Approach

**All features built with TDD**:
1. Write failing tests first
2. Implement minimal code to pass
3. Refactor while maintaining green tests
4. Regression tests for migrations
5. 100% backward compatibility

## Common Tasks

### Adding a New Jinja2 Prompt Template

**Example**: Adding a new advisor prompt

1. **Create Template** (`src/guidance_agent/templates/advisor/new_feature.jinja2`):
```jinja2
{# Purpose: Brief description of what this prompt does #}
{# Inputs: List expected variables #}
{# Output: Description of expected model output #}

You are a pension guidance advisor.

Context:
{{ context }}

Task:
{{ task }}

Guidelines:
{% for guideline in guidelines %}
- {{ guideline }}
{% endfor %}

Provide your response:
```

2. **Create Loader** (`src/guidance_agent/templates/loader.py`):
```python
def load_new_feature_template(context: str, task: str, guidelines: list[str]) -> str:
    """Load and render the new_feature template."""
    template = env.get_template("advisor/new_feature.jinja2")
    return template.render(
        context=context,
        task=task,
        guidelines=guidelines
    )
```

3. **Write Tests** (`tests/templates/test_template_rendering.py`):
```python
def test_new_feature_template_rendering():
    """Test new_feature template renders correctly."""
    rendered = load_new_feature_template(
        context="Sample context",
        task="Sample task",
        guidelines=["Guideline 1", "Guideline 2"]
    )
    assert "You are a pension guidance advisor" in rendered
    assert "Sample context" in rendered
    assert "Sample task" in rendered
    assert "Guideline 1" in rendered
    assert "Guideline 2" in rendered
```

4. **Run Tests**:
```bash
pytest tests/templates/test_template_rendering.py::test_new_feature_template_rendering -v
```

### Adding a New API Endpoint

**Example**: Adding a `/api/analytics` endpoint

1. **Create Router** (`src/guidance_agent/api/routers/analytics.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_db

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/metrics")
async def get_metrics(db: AsyncSession = Depends(get_db)):
    """Get system metrics."""
    # Implementation
    return {"metrics": {...}}
```

2. **Register Router** (`src/guidance_agent/api/main.py`):
```python
from .routers import analytics

app.include_router(analytics.router)
```

3. **Write Tests** (`tests/api/test_analytics.py`):
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_metrics(client: AsyncClient):
    """Test GET /api/analytics/metrics."""
    response = await client.get("/api/analytics/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
```

4. **Run Tests**:
```bash
pytest tests/api/test_analytics.py -v
```

### Adding a New Database Model

**Example**: Adding a `Feedback` model

1. **Create Model** (`src/guidance_agent/models/feedback.py`):
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .base import Base
from datetime import datetime

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True)
    consultation_id = Column(Integer, ForeignKey("consultations.id"))
    rating = Column(Float)  # 1.0-5.0
    comment = Column(Text)
    embedding = Column(Vector(1536))  # Vector embedding
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    consultation = relationship("Consultation", back_populates="feedback")
```

2. **Create Migration**:
```bash
alembic revision --autogenerate -m "Add feedback table"
alembic upgrade head
```

3. **Create API Router** (`src/guidance_agent/api/routers/feedback.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.feedback import Feedback
from ..dependencies import get_db

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.post("/")
async def create_feedback(
    consultation_id: int,
    rating: float,
    comment: str,
    db: AsyncSession = Depends(get_db)
):
    """Create feedback for a consultation."""
    # Implementation
    pass
```

4. **Write Tests** (`tests/api/test_feedback.py`):
```python
@pytest.mark.asyncio
async def test_create_feedback(client: AsyncClient):
    """Test POST /api/feedback."""
    response = await client.post("/api/feedback", json={
        "consultation_id": 1,
        "rating": 5.0,
        "comment": "Excellent guidance"
    })
    assert response.status_code == 201
```

### Adding a Frontend Component

**Example**: Adding a feedback form component

1. **Create Component** (`frontend/app/components/FeedbackForm.vue`):
```vue
<template>
  <div class="feedback-form">
    <h3>Rate this consultation</h3>
    <UInput v-model="rating" type="number" min="1" max="5" />
    <UTextarea v-model="comment" placeholder="Your feedback..." />
    <UButton @click="submitFeedback">Submit</UButton>
  </div>
</template>

<script setup lang="ts">
const rating = ref(5)
const comment = ref('')

const submitFeedback = async () => {
  const response = await $fetch('/api/feedback', {
    method: 'POST',
    body: {
      consultation_id: props.consultationId,
      rating: rating.value,
      comment: comment.value
    }
  })
  // Handle response
}
</script>
```

2. **Write Tests** (`frontend/tests/components/feedback-form.spec.ts`):
```typescript
import { test, expect } from '@playwright/test'

test('feedback form submission', async ({ page }) => {
  await page.goto('/consultation/123')
  await page.fill('input[type="number"]', '5')
  await page.fill('textarea', 'Great service!')
  await page.click('button:has-text("Submit")')
  await expect(page.locator('.success-message')).toBeVisible()
})
```

3. **Run Tests**:
```bash
cd frontend && npm run test -- feedback-form.spec.ts
```

## Development Workflow

### Starting Development

1. **Start Backend Stack** (Recommended: Docker):
```bash
docker-compose up -d postgres phoenix backend
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Phoenix UI: http://localhost:6006
```

2. **Start Frontend** (Local for hot reload):
```bash
cd frontend
npm install
npm run dev
# Frontend: http://localhost:3000
```

3. **Run Tests in Watch Mode**:
```bash
# Terminal 3: Backend tests
pytest --watch

# Terminal 4: Frontend tests
cd frontend && npm run test:watch
```

### Code Style & Linting

**Backend (Python)**:
```bash
# Format with Ruff
ruff format .

# Lint with Ruff
ruff check .

# Type checking with MyPy
mypy src/guidance_agent
```

**Frontend (TypeScript/Vue)**:
```bash
cd frontend

# Lint
npm run lint

# Format
npm run format

# Type check
npm run typecheck
```

### Making Changes

**TDD Workflow**:
1. Write failing test first
2. Run test to confirm failure
3. Implement minimal code to pass
4. Run test to confirm pass
5. Refactor while maintaining green tests
6. Run full test suite to ensure no regressions
7. Commit with descriptive message

**Example TDD Cycle**:
```bash
# 1. Write test
vim tests/api/test_new_feature.py

# 2. Run test (should fail)
pytest tests/api/test_new_feature.py::test_new_endpoint -v

# 3. Implement feature
vim src/guidance_agent/api/routers/new_feature.py

# 4. Run test (should pass)
pytest tests/api/test_new_feature.py::test_new_endpoint -v

# 5. Run full suite (should all pass)
pytest

# 6. Commit
git add .
git commit -m "Add new_feature endpoint with tests"
```

## Environment Configuration

### Required Environment Variables

Create `.env` file in project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/guidance_agent

# LiteLLM Provider (choose one or multiple)
# Option 1: OpenAI
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4-turbo-preview

# Option 2: Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-sonnet-20241022

# Option 3: AWS Bedrock
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_REGION=us-east-1
LLM_MODEL=bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0

# Option 4: Azure OpenAI
AZURE_API_KEY=...
AZURE_API_BASE=https://your-resource.openai.azure.com
AZURE_API_VERSION=2024-02-15-preview
LLM_MODEL=azure/gpt-4

# Option 5: LM Studio (Local)
OPENAI_API_BASE=http://localhost:1234/v1
LLM_MODEL=local-model

# Option 6: Ollama (Local)
LLM_MODEL=ollama/llama2

# Embeddings
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536

# Phoenix Observability
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:6006

# Application
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### LLM Provider Configuration

**Supported Providers** (via LiteLLM):
1. **OpenAI**: GPT-4, GPT-3.5-turbo
2. **Anthropic**: Claude 3.5 Sonnet, Claude 3 Opus/Haiku
3. **AWS Bedrock**: Claude, Llama, Titan
4. **Azure OpenAI**: GPT-4, GPT-3.5
5. **LM Studio**: Local models
6. **Ollama**: Local open-source models

**Provider Selection** (`src/guidance_agent/core/llm.py`):
```python
# Automatically detects provider from model name
# Examples:
# - "gpt-4" → OpenAI
# - "claude-3-5-sonnet-20241022" → Anthropic
# - "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0" → AWS Bedrock
# - "azure/gpt-4" → Azure OpenAI
# - "ollama/llama2" → Ollama
```

## Performance Optimization

### Key Metrics
- **Time to first token**: <2 seconds (SSE streaming)
- **Page load**: <2 seconds
- **API response**: <100ms (simple queries)
- **Test execution**: ~30 seconds (83 Playwright tests)

### Optimization Techniques

**Backend**:
1. **Async/Await**: All I/O operations are async (FastAPI, SQLAlchemy, LiteLLM)
2. **Connection Pooling**: SQLAlchemy connection pool (10 connections)
3. **Vector Indexing**: pgvector IVFFlat index for fast similarity search
4. **LLM Caching**: Prompt caching for Anthropic/OpenAI (reduces latency & cost)
5. **SSE Streaming**: Server-Sent Events for real-time token streaming

**Frontend**:
1. **Code Splitting**: Nuxt auto-splits routes
2. **Lazy Loading**: Components loaded on demand
3. **State Management**: Pinia for efficient reactive state
4. **Debouncing**: Input debouncing for API calls
5. **Caching**: API response caching where appropriate

**Database**:
1. **Indexes**: B-tree indexes on foreign keys and frequently queried columns
2. **Vector Indexes**: IVFFlat indexes for pgvector similarity search
3. **JSONB**: Efficient storage for conversation history
4. **Query Optimization**: Eager loading for relationships

## Troubleshooting

### Common Issues

**1. Database Connection Errors**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**2. LLM API Errors**
```bash
# Check environment variables
cat .env | grep API_KEY

# Test LiteLLM connection
python -c "from guidance_agent.core.llm import get_llm_client; client = get_llm_client(); print(client.models.list())"

# Check Phoenix traces for detailed errors
# Visit: http://localhost:6006
```

**3. Frontend Build Errors**
```bash
# Clear cache and reinstall
cd frontend
rm -rf .nuxt node_modules package-lock.json
npm install
npm run dev
```

**4. Test Failures**
```bash
# Run single test with verbose output
pytest tests/path/to/test.py::test_name -v -s

# Run frontend tests in headed mode (see browser)
cd frontend && npm run test -- --headed

# Check test logs
cat frontend/test-results/results.json
```

**5. Vector Embedding Dimension Mismatch**
```bash
# If you change embedding dimensions, you need to:
# 1. Update EMBEDDING_DIMENSIONS in .env
# 2. Create migration to alter vector columns
alembic revision -m "Update embedding dimensions"
# 3. Re-generate all embeddings
python scripts/bootstrap_all_knowledge.py
```

## Security Considerations

### Best Practices Implemented

1. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries
2. **XSS Prevention**: Vue auto-escapes by default, explicit sanitization where needed
3. **CSRF Protection**: FastAPI CSRF middleware (production)
4. **Authentication**: JWT tokens for admin dashboard (future enhancement)
5. **HTTPS**: Nginx SSL termination (production)
6. **Environment Secrets**: Never commit `.env` to git
7. **Input Validation**: Pydantic models validate all API inputs
8. **Rate Limiting**: API rate limiting (production)
9. **CORS**: Configured for frontend origin only
10. **Audit Logging**: All database changes logged with timestamps

### Security Checklist for New Features

- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (use ORM)
- [ ] XSS prevention (sanitize HTML if rendering user content)
- [ ] Authentication check (if admin feature)
- [ ] Authorization check (if user-specific data)
- [ ] Audit logging (for sensitive operations)
- [ ] Rate limiting (if expensive operation)
- [ ] Error messages don't leak sensitive info

## Key Documentation Files

### Essential Reading

1. **README.md**: User-facing documentation, quick start guide
2. **docs/DEPLOYMENT.md**: Production deployment (700+ lines)
3. **docs/TESTING.md**: Comprehensive testing guide
4. **specs/architecture.md**: System architecture (41KB)
5. **specs/implementation-plan.md**: Implementation details (105KB)
6. **specs/fca-compliance-manual.md**: Compliance guidelines (80KB)
7. **specs/JINJA_MIGRATION_COMPLETE.md**: Template migration report

### Implementation Phase Summaries

- **PHASE1_SUMMARY.md**: Frontend foundation
- **PHASE2_UI_SUMMARY.md**: Chat interface
- **docs/PHASE3_IMPLEMENTATION_SUMMARY.md**: Backend API
- **PHASE4_UI_SUMMARY.md**: Admin dashboard
- **specs/PHASE5_ADMIN_SETTINGS_COMPLETE.md**: Admin settings
- **specs/PHASE6_ADMIN_DATA_MODELS.md**: Admin data models (all phases)
- **specs/PHASE10_QA_COMPLETION_REPORT.md**: QA testing report
- **specs/validation-reasoning-display-plan.md**: Compliance UI spec

## LLM Integration Patterns

### Using LiteLLM

**Basic Usage** (`src/guidance_agent/core/llm.py`):
```python
from litellm import completion

response = await completion(
    model="gpt-4-turbo-preview",  # or claude-3-5-sonnet-20241022
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello!"}
    ],
    temperature=0.7,
    max_tokens=1000
)

content = response.choices[0].message.content
```

**Streaming Response**:
```python
response = await completion(
    model="gpt-4-turbo-preview",
    messages=messages,
    stream=True
)

async for chunk in response:
    content = chunk.choices[0].delta.content
    yield content
```

**Prompt Caching** (Anthropic/OpenAI):
```python
# Mark system prompt for caching
messages = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": long_system_prompt,
                "cache_control": {"type": "ephemeral"}  # Cache this
            }
        ]
    },
    {"role": "user", "content": user_message}
]

response = await completion(model="claude-3-5-sonnet-20241022", messages=messages)
```

### Jinja2 Prompt Templates

**Loading and Rendering**:
```python
from jinja2 import Environment, FileSystemLoader

# Setup (done in src/guidance_agent/templates/loader.py)
env = Environment(
    loader=FileSystemLoader("src/guidance_agent/templates"),
    trim_blocks=True,
    lstrip_blocks=True
)

# Load template
template = env.get_template("advisor/guidance.jinja2")

# Render with context
prompt = template.render(
    customer_message="I want to retire early",
    context_memories=[...],
    context_cases=[...],
    context_rules=[...],
    fca_guidelines=[...]
)

# Use in LLM call
response = await completion(
    model="gpt-4-turbo-preview",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
)
```

**Template Best Practices**:
1. Always add comments explaining purpose, inputs, and outputs
2. Use descriptive variable names
3. Test with various contexts
4. Handle missing/empty values gracefully
5. Escape user input if needed (Jinja2 auto-escapes in HTML mode, but not in text mode)

## Phoenix Observability

### Accessing Phoenix UI

**URL**: http://localhost:6006

**Features**:
- LLM call tracing (latency, tokens, cost)
- Prompt/response inspection
- Error tracking
- Performance metrics
- Span visualization

### Instrumenting Code

Phoenix tracing is automatically configured on application startup via the `llm_config` module. All LiteLLM calls are automatically traced without any code changes needed.

#### Automatic Setup

Phoenix tracing is enabled by default in development environments. Configuration in `src/guidance_agent/core/llm_config.py`:

```python
# Auto-setup on module import if Phoenix is available and in development environment
if (
    PHOENIX_AVAILABLE
    and os.getenv("ENVIRONMENT") == "development"
    and os.getenv("PHOENIX_AUTO_SETUP", "true").lower() == "true"
):
    setup_phoenix_tracing()
```

**Environment Variables**:
```bash
# Enable Phoenix tracing (default: true)
PHOENIX_AUTO_SETUP=true

# Phoenix collector endpoint (default: http://localhost:4317)
PHOENIX_COLLECTOR_ENDPOINT=http://localhost:4317

# Environment (must be "development" for auto-setup)
ENVIRONMENT=development

# Project name (default: guidance-agent)
PHOENIX_PROJECT_NAME=guidance-agent
```

#### Critical: Import Order Requirement

**IMPORTANT**: Phoenix instrumentation MUST happen BEFORE any code imports LiteLLM. This is critical for tracing to work.

**Correct Pattern** (`src/guidance_agent/api/main.py`):
```python
from fastapi import FastAPI
import os

# CRITICAL: Initialize Phoenix tracing BEFORE importing anything that uses litellm
# This must be the FIRST guidance_agent import to ensure instrumentation happens first
from guidance_agent.core import llm_config  # noqa: F401

# Now safe to import routers (which import advisor, which imports litellm)
from guidance_agent.api.routers import consultations, customers, admin
```

**Incorrect Pattern** (will NOT work):
```python
from fastapi import FastAPI
import os

# ❌ WRONG: Importing routers first
from guidance_agent.api.routers import consultations  # This imports litellm!
from guidance_agent.core import llm_config  # Too late - litellm already imported
```

#### How It Works

The `setup_phoenix_tracing()` function in `llm_config.py`:

1. **Registers Phoenix tracer provider** with OpenTelemetry
2. **Creates OTLP exporter** for gRPC communication
3. **Adds BatchSpanProcessor** for async compatibility (critical for FastAPI)
4. **Instruments LiteLLM** to automatically trace all completion calls
5. **Creates test span** to verify tracing is active

```python
def setup_phoenix_tracing() -> bool:
    """Set up Phoenix tracing for LiteLLM with async-compatible BatchSpanProcessor."""

    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "guidance-agent")

    # Register Phoenix tracer provider
    tracer_provider = register(
        project_name=project_name,
        endpoint=endpoint,
    )

    # Create OTLP exporter with explicit settings
    exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=True  # Required for HTTP endpoints
    )

    # Add BatchSpanProcessor for async compatibility
    # This batches spans before sending to reduce overhead
    batch_processor = BatchSpanProcessor(
        exporter,
        max_queue_size=2048,
        schedule_delay_millis=5000,  # Send every 5 seconds
        max_export_batch_size=512,
    )
    tracer_provider.add_span_processor(batch_processor)

    # Instrument LiteLLM - this automatically traces ALL LiteLLM calls!
    instrumentor = LiteLLMInstrumentor()
    instrumentor.instrument()

    logger.info(f"✓ Phoenix tracing enabled (BatchSpanProcessor): {endpoint}")
    logger.info(f"  Project: {project_name}")
    logger.info(f"  UI: http://localhost:6006")
    logger.info("  LiteLLM instrumentation: ACTIVE")

    return True
```

#### Verifying Tracing Works

After starting the backend, you should see these log messages:

```
✓ Phoenix tracing enabled (BatchSpanProcessor): http://localhost:4317
  Project: guidance-agent
  UI: http://localhost:6006
  LiteLLM instrumentation: ACTIVE
  ✓ Test span created - should appear in Phoenix UI
```

Then visit http://localhost:6006 and you should see:
1. A test span from initialization
2. LLM traces from consultations (after making a chat request)

#### Troubleshooting

**Problem**: Traces don't appear in Phoenix UI

**Solution 1 - Check Import Order**:
```bash
# Verify llm_config is imported FIRST in main.py
grep -n "import" src/guidance_agent/api/main.py | head -20

# Should see llm_config import before any routers
```

**Solution 2 - Check Phoenix Container**:
```bash
# Verify Phoenix is running
docker-compose ps phoenix

# Check Phoenix logs
docker-compose logs phoenix

# Restart Phoenix if needed
docker-compose restart phoenix
```

**Solution 3 - Check Environment Variables**:
```bash
# Verify configuration
cat .env | grep PHOENIX
cat .env | grep ENVIRONMENT

# Should see:
# PHOENIX_COLLECTOR_ENDPOINT=http://localhost:4317
# ENVIRONMENT=development
```

**Solution 4 - Check Backend Logs**:
```bash
# Look for Phoenix initialization logs
docker-compose logs backend | grep Phoenix

# Should see "✓ Phoenix tracing enabled"
```

**Problem**: Test spans appear but LLM calls don't

**Cause**: This indicates OpenTelemetry setup is correct, but LiteLLM wasn't instrumented before being imported.

**Solution**: Verify import order in main.py. The llm_config import MUST come before any code that imports the advisor agent or LiteLLM.

#### Manual Instrumentation (Advanced)

If you need to add custom spans around specific operations:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("custom-operation") as span:
    # Add custom attributes
    span.set_attribute("operation.type", "retrieval")
    span.set_attribute("operation.user_id", user_id)

    # Your operation here
    result = perform_operation()

    # Add result metadata
    span.set_attribute("result.count", len(result))
```

Custom spans will appear in Phoenix UI alongside automatic LiteLLM traces, providing a complete view of your agent's execution.

## Future Enhancements

### Planned Features (from specs)

1. **Authentication & Authorization**:
   - JWT-based admin authentication
   - Role-based access control (RBAC)
   - Customer login for consultation history

2. **Advanced Analytics**:
   - Compliance trend analysis
   - Learning effectiveness metrics
   - Customer satisfaction tracking
   - A/B testing for different prompts

3. **Multi-tenancy**:
   - Support multiple organizations
   - Isolated data per tenant
   - Custom branding per tenant

4. **Enhanced Learning**:
   - Active learning with human feedback
   - Reinforcement learning from ratings
   - Automated retraining pipelines

5. **Integrations**:
   - CRM integration (Salesforce, HubSpot)
   - Pension provider APIs
   - Calendar scheduling
   - Email notifications

6. **Mobile App**:
   - Native iOS/Android apps
   - Push notifications
   - Offline support

### Contributing New Features

1. Review relevant specification documents in `specs/`
2. Write implementation plan
3. Create TDD test suite
4. Implement with incremental commits
5. Update documentation
6. Create pull request with summary

## Contact & Support

- **Documentation Issues**: Check `docs/` and `specs/` directories first
- **Bug Reports**: Include logs, environment details, and reproduction steps
- **Feature Requests**: Provide use case and expected behavior

## Additional Resources

### External Documentation

- **FastAPI**: https://fastapi.tiangolo.com
- **Nuxt 3**: https://nuxt.com/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org
- **LiteLLM**: https://docs.litellm.ai
- **pgvector**: https://github.com/pgvector/pgvector
- **Playwright**: https://playwright.dev
- **Pydantic**: https://docs.pydantic.dev
- **Arize Phoenix**: https://docs.arize.com/phoenix

### Research Papers

1. **Generative Agents: Interactive Simulacra of Human Behavior**
   - Paper: https://arxiv.org/abs/2304.03442
   - Concepts: Memory stream, reflection, importance scoring, retrieval

2. **Agent Hospital: A Simulacrum of Hospital with Evolving Medical Agents (MedAgent-Zero)**
   - Paper: https://arxiv.org/abs/2405.02957
   - Concepts: SEAL framework, dual memory, closed-loop learning

---

**Last Updated**: November 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
