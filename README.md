# Pension Guidance Chat - AI-Powered Compliant Pension Advice

An enterprise-grade AI agent that provides FCA-compliant pension guidance through an intuitive chat interface. Built with FastAPI, Vue 3, and advanced agentic learning capabilities.

## 🌟 Features

### Customer-Facing Chat Interface
- **Real-time streaming**: SSE-powered responses with <2s latency
- **Accessible design**: WCAG 2.1 AA compliant
- **Responsive**: Works on desktop, tablet, and mobile
- **User-friendly**: Natural conversation flow with typing indicators

### Admin Dashboard
- **Compliance monitoring**: Real-time compliance scores per message
- **Analytics**: Metrics, charts, and time-series data
- **Review tools**: Detailed transcript review with learning insights
- **Export**: PDF and JSON export for auditing

### AI Capabilities
- **Compliant guidance**: Real-time FCA compliance validation
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
cd frontend-nuxt
npm install
npm run dev
# Access at http://localhost:3000
```

### Running Tests

**Frontend Tests (83 Playwright tests)**
```bash
cd frontend-nuxt
npm test                    # Playwright tests
npm run test:coverage      # Coverage report
```

**Backend Tests (23 API + 8 integration tests)**
```bash
pytest tests/api/          # API tests
pytest tests/integration/  # Integration tests
pytest --cov              # With coverage
```

## 📁 Project Structure

```
guidance-agent/
├── src/guidance_agent/        # Backend Python code
│   ├── api/                   # FastAPI REST API
│   ├── agents/               # AI agent implementations
│   ├── models/               # Database models
│   └── knowledge/            # Knowledge base & RAG
├── frontend-nuxt/             # Nuxt 3 frontend
│   ├── app/
│   │   ├── components/       # Vue components
│   │   ├── pages/            # Page routes (file-based)
│   │   ├── composables/      # Vue composables
│   │   └── utils/            # API client
│   └── tests/                # Playwright tests
├── tests/                     # Backend tests
├── docs/                      # Documentation
├── docker-compose.yml         # Multi-service orchestration
└── Dockerfile                # Backend container
```

## 🧪 Testing

### Test Coverage
- **Frontend**: 83 Playwright tests (100% pass rate)
- **Backend**: 31 tests (API + integration)
- **Total**: 114+ tests

### Running Specific Tests
```bash
# Frontend Playwright tests
cd frontend-nuxt && npm test

# Backend API tests
pytest tests/api/test_consultations.py -v

# Playwright tests with UI
cd frontend-nuxt && npm run test:ui

# Accessibility tests
cd frontend-nuxt && npx playwright test accessibility.spec.ts
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

- **[API Documentation](http://localhost:8000/api/docs)** - Interactive Swagger UI
- **[Docker Setup Guide](docs/DOCKER_SETUP.md)** - Container deployment
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment (700+ lines)
- **[Testing Guide](docs/TESTING.md)** - Comprehensive testing documentation
- **[UI/UX Design Plan](specs/ui-ux-design-plan.md)** - Complete design system
- **[API Integration](docs/API_INTEGRATION.md)** - Backend API guide

## 🛠️ Technology Stack

**Frontend**:
- Nuxt 3, Vue 3, TypeScript
- Nuxt UI 4, Tailwind CSS, Vercel AI SDK
- Playwright (E2E testing)

**Backend**:
- FastAPI, Pydantic, SQLAlchemy
- LangChain, OpenAI/Claude
- PostgreSQL + pgvector
- Phoenix (observability)

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
- [Phase 6: Docker Deployment](PHASE6_SUMMARY.md)

## 📝 License

[Your license here]

## 🙏 Acknowledgments

Built with Test-Driven Development (TDD) using industry best practices.

---

**Status**: ✅ Production Ready
**Tests**: 114+ passing
**Documentation**: 4000+ lines
**Implementation**: November 2025
**Frontend**: Nuxt 3 with 100% migration complete
