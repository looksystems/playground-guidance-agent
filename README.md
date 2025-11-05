# Pension Guidance Chat - AI-Powered Compliant Pension Advice

An enterprise-grade AI agent that provides FCA-compliant pension guidance through an intuitive chat interface. Built with FastAPI, Vue 3, and advanced agentic learning capabilities.

## 🌟 Features

### Customer-Facing Chat Interface
- **Real-time streaming**: SSE-powered responses with <2s latency
- **Accessible design**: WCAG 2.1 AA compliant
- **Responsive**: Works on desktop, tablet, and mobile
- **User-friendly**: Natural conversation flow with typing indicators

### Admin Dashboard
- **Compliance monitoring**: Real-time compliance scores per message with detailed validation reasoning
- **Validation transparency**: Expandable compliance analysis showing LLM reasoning, issues found, and pass/fail status
- **Analytics**: Metrics, charts, and time-series data
- **Review tools**: Detailed transcript review with learning insights
- **Export**: PDF and JSON export for auditing
- **Data Management**: Admin interfaces for all 7 core data models (Memory, Case, Rule, FCA Knowledge, Pension Knowledge, Customer, System Settings)

### AI Capabilities
- **Compliant guidance**: Real-time FCA compliance validation with detailed reasoning and issue tracking
- **Validation transparency**: Full LLM reasoning stored and displayed for audit trails
- **Learning system**: Improves from past consultations
- **Context-aware**: Retrieves relevant similar cases
- **Reflection**: Generates strategic insights

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+

### Running the Full Stack

**Option 1: Docker (Recommended for Backend)**
```bash
# Start backend services
docker-compose up -d postgres phoenix backend

# Access services
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
# Phoenix UI: http://localhost:6006
```

**Option 2: Local Development**
```bash
# Terminal 1: Backend
uv sync
uv run uvicorn guidance_agent.api.main:app --reload

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

### Running Tests

**Frontend Tests (83 Playwright tests)**
```bash
cd frontend
npm test                    # Playwright tests
npm run test:coverage      # Coverage report
```

**Backend Tests (146 API + 8 integration + 40 template + 20 regression tests)**
```bash
pytest tests/api/          # API tests (146 tests)
pytest tests/integration/  # Integration tests (8 tests)
pytest tests/templates/    # Template rendering tests (40 tests)
pytest tests/regression/   # Template migration regression tests (20 tests)
pytest --cov              # With coverage
```

**Frontend E2E Tests (99 Playwright tests)**
```bash
cd frontend
npm run test:e2e          # Playwright E2E tests
npm run test:e2e:ui       # Interactive UI mode
npm run test:e2e:report   # View HTML report
```

## 📁 Project Structure

```
guidance-agent/
├── src/guidance_agent/        # Backend Python code (11K+ lines)
│   ├── api/                   # FastAPI REST API
│   ├── advisor/               # Advisor agent implementation
│   ├── compliance/            # FCA compliance validation
│   ├── core/                  # Core infrastructure (DB, LLM, embeddings)
│   ├── customer/              # Customer agent (simulated)
│   ├── learning/              # Case-based & reflection learning
│   ├── models/                # Database models (7 core models)
│   ├── retrieval/             # RAG retrieval system
│   ├── templates/             # Jinja2 prompt templates (20 files)
│   └── knowledge/             # Knowledge base
├── frontend/                  # Nuxt 3 frontend (8.5K+ lines)
│   ├── app/
│   │   ├── components/        # Vue components
│   │   ├── pages/             # Page routes (file-based)
│   │   ├── composables/       # Vue composables
│   │   ├── stores/            # Pinia state management
│   │   └── utils/             # API client
│   └── tests/                 # Playwright tests (203 tests)
├── tests/                     # Backend tests (214 tests)
├── docs/                      # Documentation (8 guides)
├── specs/                     # Specifications (63 files, 700KB+)
├── scripts/                   # Utility scripts
├── alembic/                   # Database migrations
├── docker-compose.yml         # Multi-service orchestration
├── Dockerfile                 # Backend container
└── CLAUDE.md                  # AI assistant guide
```

## 🧪 Testing

### Test Coverage
- **Frontend**: 203 Playwright tests (83 component/page + 99 E2E + 21 validation reasoning, 100% pass rate)
- **Backend**: 214 tests (146 API + 8 integration + 40 template + 20 regression, 100% pass rate)
- **Total**: 417+ tests

### Running Specific Tests
```bash
# Frontend Playwright tests
cd frontend && npm test

# Backend API tests
pytest tests/api/test_consultations.py -v

# Playwright tests with UI
cd frontend && npm run test:ui

# Accessibility tests
cd frontend && npx playwright test accessibility.spec.ts
```

## 🚢 Deployment

### Docker Deployment (Production)

**Quick Deploy**:
```bash
./scripts/deploy.sh
```

**Manual Deploy**:
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check health
curl http://localhost:8000/health
curl http://localhost/health

# View logs
docker-compose logs -f backend
```

### Cloud Deployment
See detailed guides:
- AWS: [docs/DEPLOYMENT.md#aws](docs/DEPLOYMENT.md#aws)
- GCP: [docs/DEPLOYMENT.md#gcp](docs/DEPLOYMENT.md#gcp)
- Azure: [docs/DEPLOYMENT.md#azure](docs/DEPLOYMENT.md#azure)

## 📚 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive AI assistant guide (900+ lines)
- **[API Documentation](http://localhost:8000/api/docs)** - Interactive Swagger UI
- **[Docker Setup Guide](docs/DOCKER_SETUP.md)** - Container deployment
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment (700+ lines)
- **[Testing Guide](docs/TESTING.md)** - Comprehensive testing documentation
- **[UI/UX Design Plan](specs/ui-ux-design-plan.md)** - Complete design system
- **[API Integration](docs/API_INTEGRATION.md)** - Backend API guide
- **[Architecture](specs/architecture.md)** - System architecture (41KB)
- **[Implementation Plan](specs/implementation-plan.md)** - Implementation details (105KB)

## 🛠️ Technology Stack

**Frontend**:
- Nuxt 3, Vue 3, TypeScript
- Nuxt UI 4, Tailwind CSS, Vercel AI SDK
- Playwright (E2E testing)

**Backend**:
- FastAPI, Pydantic, SQLAlchemy
- LiteLLM (multi-provider: OpenAI, Anthropic, AWS Bedrock, Azure, LM Studio, Ollama)
- PostgreSQL + pgvector
- Arize Phoenix (LLM observability)
- Jinja2 (20 prompt templates)

**Infrastructure**:
- Docker, Docker Compose
- Nginx, Uvicorn
- GitHub Actions (CI/CD)

## 📊 Architecture

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Nuxt 3    │ SSE  │   FastAPI   │      │ PostgreSQL  │
│  Frontend   │<─────│   Backend   │<─────│  + pgvector │
└─────────────┘      └─────────────┘      └─────────────┘
                            │
                            ├──────> OpenAI/Claude LLM
                            │
                            └──────> Phoenix (Tracing)
```

## 📖 Knowledge Base & Metadata

The system uses two knowledge models with rich metadata support:

### FCA Knowledge Model
Stores FCA compliance guidelines with metadata including:
- **principle**: Core principle text
- **fca_reference**: Reference to FCA documentation
- **mandatory**: Boolean for mandatory requirements
- **example_type**: Classification ("compliant" or "non_compliant")
- **parent_principle**: Links examples to parent principles
- **template_type**: Template categorization
- **key_elements**: List of required elements

### Pension Knowledge Model
Stores UK pension domain knowledge with metadata including:
- Pension type details (description, fca_considerations)
- Regulation specifics (age limits, contribution rules)
- Scenario information (age_range, pension_count_range, total_value_range)
- Common customer goals and patterns

### Current Metadata Usage
- **API Responses**: Metadata exposed via REST endpoints for admin dashboard display
- **Data Provenance**: Tracking source information and classifications
- **Linking**: Connecting related knowledge items (examples to principles)
- **Supplementary Data**: Storing structured information for display and audit purposes

### Bootstrap & Population
```bash
# Bootstrap all knowledge bases (FCA, Pension, Cases, Rules)
uv run python scripts/bootstrap_all_knowledge.py

# Verify knowledge bases
uv run python scripts/verify_knowledge_bases.py
```

**Knowledge Base Status** (as of November 2025):
- FCA Compliance: 16 entries with embeddings
- Pension Domain: 10 entries with embeddings
- Case Base: 12 seed cases
- Rules Base: 8 seed rules

## 🎯 Performance

- **Time to first token**: <2 seconds (70% improvement via SSE)
- **Page load**: <2 seconds
- **API response**: <100ms (simple queries)
- **Test execution**: ~30 seconds (83 Playwright tests)

## ✅ Compliance

- **FCA Standards**: Real-time compliance validation
- **WCAG 2.1 AA**: Full accessibility compliance
- **Audit Trail**: Complete consultation history
- **Data Security**: Encrypted storage, GDPR-ready

## 🤝 Contributing

See implementation summaries:
- [Phase 1: Frontend Foundation](PHASE1_SUMMARY.md)
- [Phase 2: Chat Interface](PHASE2_UI_SUMMARY.md)
- [Phase 3: Backend API](docs/PHASE3_IMPLEMENTATION_SUMMARY.md)
- [Phase 4: Admin Dashboard](PHASE4_UI_SUMMARY.md)
- [Phase 5: Admin Settings Complete](specs/PHASE5_ADMIN_SETTINGS_COMPLETE.md)
- [Phase 6: Admin Data Models](specs/PHASE6_ADMIN_DATA_MODELS.md) - ✅ Complete (All Phases)
- [Phase 10: QA Testing Report](specs/PHASE10_QA_COMPLETION_REPORT.md) - ✅ Complete
- [Validation Reasoning Display](specs/validation-reasoning-display-plan.md) - ✅ Complete (TDD Implementation)
- [Jinja Template Migration](specs/JINJA_MIGRATION_COMPLETE.md) - ✅ Complete (20 templates, 60 tests, TDD)

## 📝 License

[Your license here]

## 🙏 Acknowledgments

Built with Test-Driven Development (TDD) using industry best practices.

---

**Status**: ✅ Production Ready
**Tests**: 417+ passing (214 backend, 203 frontend)
**Documentation**: 8000+ lines
**Implementation**: November 2025
**Frontend**: Nuxt 3 with 100% migration complete
**Latest**: Jinja Template Migration Complete - All 20 prompts migrated with TDD (60 new tests, 100% backward compatible)
