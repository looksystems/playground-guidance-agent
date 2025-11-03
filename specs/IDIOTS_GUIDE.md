# Financial Guidance Agent: An Idiot's Guide

> **TL;DR**: This is a self-training AI system that learns to give compliant pension advice by having AI advisors practice on AI customers in a virtual environment. Think of it as a flight simulator for financial advisors, but both the instructor and the trainee are AI.

---

## What Is This Project?

The **Financial Guidance Agent** is an AI-powered system that provides personalized pension guidance to customers. It's like a chatbot, but much smarter and more careful because:

- It deals with people's retirement money (serious stuff!)
- It must follow FCA (Financial Conduct Authority) regulations
- It learns and improves from every interaction
- It needs to be fast, accurate, and compliant

**The Cool Part**: Instead of learning from real customers (risky!), the system trains itself using AI-generated fake customers. It's like practicing surgery on a dummy before operating on real people.

---

## The Big Idea: Virtual Training

### The Problem
You can't train a financial advisor AI on real customers because:
- Mistakes could cost people money
- It would take forever (you'd need thousands of real interactions)
- Real customers won't tolerate bad advice while the AI is learning

### The Solution
Create thousands of fake customer personas (AI-generated) and have the advisor practice on them:

```
┌─────────────────────────────────────────────────────────────┐
│                    TRAINING PHASE                            │
│  (Safe practice - AI learning from AI)                       │
│                                                              │
│  Fake Customer ←──→ Advisor Agent ──→ AI Judge             │
│   "I'm 45 with         "Here's my      "That advice         │
│    £150k, want         advice..."       is 85% compliant"   │
│    to retire                                                 │
│    at 60"                  ↓                                │
│                     Learn from                               │
│                   mistakes & wins                            │
│                          ↓                                   │
│                  Update Knowledge                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
            (After 5,000 practice sessions)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                   PRODUCTION PHASE                           │
│  (Real people getting real advice)                           │
│                                                              │
│  Real Customer ←──→ Trained Advisor ──→ AI Judge            │
│                   (Uses everything          (Still checking  │
│                    it learned)               for compliance) │
└─────────────────────────────────────────────────────────────┘
```

---

## How It Works: The Simple Version

1. **Customer asks a question** about their pension
2. **Advisor searches its brain** (knowledge base) for:
   - Similar questions from the past
   - Relevant compliance rules
   - Important things it remembers about this customer
3. **Advisor generates an answer** using a powerful AI (Claude or GPT-4)
4. **Answer streams to the user** (words appear as they're generated - fast!)
5. **In the background**, another AI checks if the advice is compliant
6. **If something went wrong**, the system learns from the mistake

**Total time**: First words in 1-2 seconds, complete answer in 4-6 seconds

---

## The Main Characters (Components)

### 1. 🤖 Advisor Agent (`src/guidance_agent/advisor/`)
**What it does**: The main AI that talks to customers

**Think of it as**: A financial advisor with a really good memory and access to all past cases

**How it works**:
- Receives customer questions
- Searches for relevant past experiences
- Generates personalized guidance
- Streams the response (so customers don't wait forever)

**Status**: ✅ Fully working with streaming support (Phase 1 complete)

### 2. 👥 Customer Agent (Training Only)
**What it does**: Pretends to be a customer during training

**Think of it as**: An actor playing different roles in a training scenario

**How it works**:
- Has a fake persona (age, savings, goals, worries)
- Asks realistic questions
- Gives feedback on the advisor's answers

**Status**: ✅ Used during the bootstrap training phase

### 3. 🧠 Knowledge Systems (`src/guidance_agent/retrieval/`)
**What it does**: The advisor's "memory" and reference library

**Contains**:
- **Memory Stream**: Recent conversations and observations (with time-decay - old stuff matters less)
- **Case Base**: Database of past successful consultations
- **Rules Base**: FCA compliance rules with confidence scores
- **Vector Store**: Fast semantic search (finds similar questions even if worded differently)

**Think of it as**: A combination of:
- Personal diary (memories)
- Case law library (past cases)
- Rulebook (compliance rules)

### 4. 📚 Learning System (`src/guidance_agent/learning/`)
**What it does**: Makes the advisor smarter over time

**How it learns**:
- **From successes**: "This worked well, save it as a template"
- **From failures**: "This violated a rule, let's figure out why and remember not to do it again"
- **From validation**: "This new rule seems accurate based on past cases"

**Think of it as**: A coach reviewing game footage and creating playbooks

### 5. ⚖️ Compliance Validator (`src/guidance_agent/compliance/`)
**What it does**: Double-checks that advice follows FCA rules

**How it works**:
- Reads the advisor's guidance
- Compares it against regulations
- Assigns a compliance score (0-100%)
- Runs in the background (doesn't slow down responses)

**Think of it as**: A legal reviewer checking contracts before they go out

---

## The Technology Stack (What We Use & Why)

### AI Brains (LLMs)

**LiteLLM** - The Traffic Controller
- Lets us use different AI providers (Anthropic, OpenAI, etc.)
- Automatically switches if one is down
- Handles rate limits

**The AI Models**:
- **Claude Sonnet 4.5**: Main advisor brain (smart but expensive)
- **GPT-4o**: Backup option (also smart, slightly cheaper)
- **Claude Haiku 4.5**: For quick tasks (4-5x faster, cheaper, but less capable)
- **GPT-4o-mini**: Compliance checking (cheap and good enough for validation)
- **text-embedding-3-small**: Converts text to numbers for similarity search

### Database & Memory

**PostgreSQL + pgvector**
- Stores everything: cases, rules, memories, customer profiles
- pgvector = superpower for finding similar content quickly

**Think of it as**: A filing cabinet with a genius assistant who instantly finds related documents

### Monitoring

**Phoenix** - The Observatory
- Watches every AI call
- Tracks costs, speed, errors
- Helps us optimize and debug

**Think of it as**: Mission control for NASA, but for AI calls

### Web Framework

**FastAPI** - The API Builder
- Modern Python framework for building APIs
- Auto-generates documentation
- Handles async operations (doing multiple things at once)

---

## Important Concepts Explained

### 🎯 LLM-as-Judge

**Problem**: How do you check if advice is compliant without hiring 100 human experts?

**Solution**: Use a separate AI to judge the advisor's work

```
Advisor: "You should withdraw 25% of your pension pot at age 60..."
Judge AI: "Let me check this against FCA rules..."
         "✅ Compliant (Score: 92%)"
```

**Why it works**:
- Fast (1.5s per check)
- Cheap (uses GPT-4o-mini)
- Scalable (can check thousands of interactions)
- Consistent (same standards every time)

### ⚡ Streaming Responses (✅ Implemented)

**Problem**: Waiting 6-8 seconds staring at a loading spinner feels like forever

**Solution**: Show words as they're generated (like ChatGPT does)

**Impact**:
```
Before: "..." → wait → wait → wait → "Here's your guidance [full answer]" (6-8s)
After:  "Here's" → "your" → "guidance" → [...] (first word in 1-2s, done in 4-6s)
```

**Perceived speedup**: 70-75% faster

**Status**: ✅ 33/33 tests passing (November 2025)

### 💰 Prompt Caching (🚧 Planned)

**Problem**: We send the same compliance rules and instructions with every AI call - paying full price each time

**Solution**: Tell the AI provider "cache this content, I'll reuse it"

**Savings**: 90% discount on cached content

**Example**:
```
Without caching:
  Call 1: Send 10,000 tokens (compliance rules) → Pay $0.30
  Call 2: Send same 10,000 tokens → Pay $0.30
  Call 3: Send same 10,000 tokens → Pay $0.30
  Total: $0.90

With caching:
  Call 1: Send 10,000 tokens → Pay $0.30 (cache it)
  Call 2: Use cached 10,000 tokens → Pay $0.03
  Call 3: Use cached 10,000 tokens → Pay $0.03
  Total: $0.36 (60% savings!)
```

**Status**: 🚧 Not implemented yet (Phase 2)

### 📦 Batch Processing (🚧 Planned)

**Problem**: Real-time AI calls are expensive. Not everything needs an instant answer.

**Solution**: Batch non-urgent work and run it overnight at 50% discount

**Use cases**:
- Nightly analysis of the day's failures
- Bulk validation of old cases
- Periodic knowledge base updates

**Tradeoff**: Takes 12-24 hours instead of seconds (but who cares if it's not urgent?)

**Status**: 🚧 Not implemented yet (Phase 3)

### 🧠 Memory with Time Decay

**Problem**: Not all memories are equally important, and recent stuff matters more

**Solution**: Score memories by importance AND freshness

```
Memory Score = Base Importance × Decay Factor^(days_old)

Examples:
"Customer mentioned early retirement" (2 days ago, important) → Score: 9.5
"Customer asked about tax forms" (30 days ago, medium) → Score: 3.2
"Customer said hello" (60 days ago, trivial) → Score: 0.1
```

Only high-scoring memories get retrieved for context (saves tokens = saves money)

### 🤔 Chain-of-Thought Reasoning

**Pattern**: Make the AI "think out loud" before answering

**Why it helps**: Forces structured reasoning, catches mistakes early

**Example**:
```
User: "Can I retire at 55 with £180k?"

AI (thinking):
Step 1: Analyze situation
  - Current age: 52 (assuming 3 years until retirement)
  - Pension pot: £180k
  - Target retirement age: 55

Step 2: Identify considerations
  - Early retirement means longer drawdown period (potentially 30+ years)
  - Tax-free lump sum: 25% = £45k
  - Remaining: £135k needs to last decades
  - State pension not available until 67

Step 3: Formulate guidance
  [Actual advice here...]
```

**Result**: More accurate, explainable answers

---

## What Makes This Project Special

### 1. 🎭 Self-Training System
Most AI projects train on fixed datasets (like photos or text). This system has AI agents training each other in a virtual world - it's more like The Matrix than a traditional ML pipeline.

### 2. ⚖️ Compliance-Critical Domain
One mistake = someone's retirement fund at risk + regulatory penalties. The compliance layer isn't optional - it's essential.

### 3. 🔄 Continuous Learning
The system improves without human labeling:
1. Detect failure (LLM-as-judge catches non-compliant advice)
2. Reflect on what went wrong
3. Generate new rules
4. Validate rules against past cases
5. Add high-confidence rules to knowledge base
6. Repeat

It's like having a team that runs A/B tests and updates processes automatically.

### 4. 💸 Cost-Performance Engineering
Every decision has trade-offs carefully analyzed:

| Optimization | Cost Savings | Latency Impact | Complexity |
|--------------|--------------|----------------|------------|
| Streaming | $0 | -70% perceived | Medium |
| Prompt caching | -55% | +0ms | Low |
| Batch processing | -50% (eligible work) | +12-24h | Medium |
| Model switching | Variable | -50% to +20% | Low |

The specs show deep cost modeling most projects never do.

### 5. 📊 Production-Grade Observability
Phoenix integration tracks:
- Every AI call and its cost
- Token usage breakdown
- Latency percentiles (p50, p95, p99)
- Error rates and types
- Model performance comparison

You can answer questions like:
- "Why did costs spike on Tuesday?"
- "Which prompts are slowest?"
- "Is Claude or GPT-4o better for our use case?"

### 6. 🔀 Multi-Provider Strategy
Uses LiteLLM to avoid vendor lock-in:
- Switch between Anthropic and OpenAI based on performance/cost
- Automatic fallbacks if one provider is down
- Can A/B test different models easily

---

## Current Status (November 2025)

### ✅ Phase 1: Streaming Support - COMPLETE
- **Goal**: Reduce perceived latency by 70%
- **Status**: 33/33 tests passing
- **Results**:
  - Time to first token: 1-2s (target: <1.5s) ✅
  - Full response time: 4-6s ✅
  - Async compliance validation: Working ✅

### 🚧 Phase 2: Prompt Caching - PLANNED
- **Goal**: Reduce costs by 55-60%
- **Status**: Designed but not implemented
- **Expected impact**:
  - Training cost: $363-401 → $161-201
  - Per-customer cost: $0.08 → $0.04

### 🚧 Phase 3: Batch Processing - PLANNED
- **Goal**: Cut offline work costs by 50%
- **Status**: Use cases identified, not implemented
- **Applications**:
  - Nightly reflection on failures
  - Bulk historical validation
  - Periodic knowledge updates

---

## The Numbers

### 💰 Cost Estimates

**Bootstrap Training** (5,000 virtual customers):
```
Without optimizations:     $363-401
With prompt caching:       $161-201  (55-60% cheaper)
With batch processing:     $181-201  (on eligible work)
```

**Per Real Customer Interaction**:
```
Advisor guidance:       $0.040-0.060
Compliance validation:  $0.001-0.002
Learning/reflection:    $0.005-0.010
Total:                  $0.046-0.072 (or ~$0.04 with caching)
```

**Full Project Budget**:
```
Development & Testing:  $800-2,000
Bootstrap Training:     $363-401 (current) or $161-201 (with caching)
Validation Study:       $800-1,500

GRAND TOTAL:            $2,001-$5,150
With optimizations:     $1,761-$3,701
```

### ⚡ Performance Targets

**Latency** (Real customer interactions):
```
p50 (median):          <5s
p95 (95th percentile): <8s
p99 (99th percentile): <12s
Time to first token:   <2s
System availability:   >99.5%
```

**Bootstrap Training Scale**:
```
Virtual customers:      5,000
Interactions per customer: 1-3
Total advisor calls:    5,000-15,000
Total compliance checks: Same
Expected duration:      Few hours (parallelized)
```

---

## Project Structure: Where to Find Stuff

```
guidance-agent/
│
├── src/guidance_agent/          # Main source code
│   │
│   ├── advisor/                 # 🤖 The Advisor Agent
│   │   ├── agent.py            #    Main logic + streaming
│   │   └── prompts.py          #    Prompt templates
│   │
│   ├── core/                    # 🏗️ Foundation
│   │   ├── agent.py            #    Base agent class
│   │   ├── database.py         #    Database models
│   │   ├── llm_config.py       #    LiteLLM setup
│   │   ├── memory.py           #    Memory stream
│   │   └── types.py            #    Type definitions
│   │
│   ├── learning/                # 📚 Learning System
│   │   ├── case_learning.py    #    Store successful cases
│   │   ├── reflection.py       #    Learn from failures
│   │   └── validation.py       #    Validate new rules
│   │
│   ├── compliance/              # ⚖️ Compliance Checking
│   │   └── validator.py        #    FCA compliance validator
│   │
│   └── retrieval/               # 🔍 Knowledge Retrieval
│       ├── embeddings.py       #    Generate embeddings
│       ├── retriever.py        #    Context retrieval
│       └── vector_store.py     #    pgvector operations
│
├── specs/                       # 📋 Documentation
│   ├── IDIOTS_GUIDE.md         #    👈 You are here!
│   ├── architecture.md         #    System architecture
│   ├── implementation-plan.md  #    Development roadmap
│   ├── advisor-agent.md        #    Advisor agent details
│   ├── customer-agent.md       #    Customer agent details
│   ├── learning-system.md      #    Learning system details
│   ├── cost-estimates.md       #    Detailed cost analysis
│   ├── latency-estimates.md    #    Performance targets
│   ├── performance-optimizations.md  # 3-phase optimization plan
│   └── [3 more spec files...]
│
├── tests/                       # 🧪 Test Suite
│   ├── unit/                   #    Unit tests
│   │   └── advisor/
│   │       └── test_streaming.py  # 13 streaming tests
│   └── integration/            #    Integration tests
│       └── test_streaming.py   #    End-to-end streaming tests
│
├── examples/                    # 📖 Examples & Demos
│   └── phase1_demo.py          #    Streaming demonstration
│
├── alembic/                     # 🔄 Database Migrations
│
├── scripts/                     # 🛠️ Utility Scripts
│
├── docker-compose.yml           # 🐳 Local development setup
├── pyproject.toml               # 📦 Dependencies & config
└── README.md                    # 👋 Project overview
```

### 🎯 Key Files to Understand First

1. **README.md** - Start here for project overview
2. **specs/architecture.md** - Understand the system design
3. **src/guidance_agent/advisor/agent.py** - See the main advisor logic
4. **specs/IDIOTS_GUIDE.md** - You're reading it! 😊

---

## Quick Start Mental Model

If you're trying to understand the codebase, follow this path:

1. **Read this guide** (✅ you're doing it!)
2. **Check `specs/architecture.md`** - See how components connect
3. **Look at `src/guidance_agent/core/types.py`** - Understand the data structures
4. **Read `src/guidance_agent/advisor/agent.py`** - See the main logic
5. **Run `examples/phase1_demo.py`** - See it in action
6. **Explore `tests/`** - See how it's supposed to work

---

## Common Questions

### Q: Why not just use ChatGPT's API directly?
**A**: We need:
- Multiple providers for redundancy (Anthropic + OpenAI)
- Custom compliance checking
- Specialized knowledge retrieval
- Learning from interactions
- Cost optimization (caching, batching)
- Regulatory compliance

ChatGPT is great, but it's a general-purpose tool. We need something specialized for FCA-compliant financial guidance.

### Q: Why train on fake customers instead of real data?
**A**:
- **Speed**: Generate 5,000 personas in hours vs. waiting months for real interactions
- **Safety**: No risk of giving bad advice to real people
- **Control**: Test edge cases (e.g., "customer with £10M pension pot") that rarely occur naturally
- **Privacy**: No real customer data = no privacy concerns

### Q: How do you know the AI judge is accurate?
**A**: Great question! We validate it:
1. Test on known good/bad examples
2. Compare against human expert ratings
3. Measure inter-rater reliability (does it give consistent scores?)
4. Continuously monitor in production

The specs show a planned validation study with 100-200 cases reviewed by humans.

### Q: What happens if the AI gives bad advice?
**A**: Multiple safety layers:
1. **LLM-as-judge** catches most issues immediately
2. **Confidence scores** on rules (low confidence = flag for human review)
3. **Learning system** reflects on failures and generates new rules
4. **Human oversight** for edge cases (not automated yet, but planned)

### Q: Why is this better than a human advisor?
**A**: It's not meant to replace humans! It's for:
- **Accessibility**: Available 24/7, no appointments needed
- **Consistency**: Same quality every time
- **Scale**: Can handle thousands of customers simultaneously
- **Cost**: Much cheaper than human advisors for basic guidance

Complex cases still need human experts.

### Q: How much does it cost to run in production?
**A**: ~$0.04-0.07 per customer interaction (with optimizations). For 10,000 customers/month:
```
10,000 × $0.05 = $500/month in AI costs
```

Plus infrastructure (database, monitoring, hosting) maybe $200-500/month.

**Total**: ~$700-1,000/month for 10,000 customers

Compare to human advisors: £50-150 per consultation × 10,000 = £500k-1.5M/month

---

## The Bottom Line

This project is solving a genuinely hard problem: **How do you create an AI system that gives compliant financial advice at scale, learns from experience, and does it cost-effectively?**

The solution combines:
- **Virtual training environments** (AI practicing on AI)
- **LLM-as-judge** (automated compliance checking)
- **Continuous learning** (reflection + validation)
- **Smart optimizations** (streaming, caching, batching)
- **Production-grade engineering** (observability, multi-provider, cost modeling)

**Current status**: Phase 1 (streaming) complete and working. Phases 2 & 3 (caching, batching) designed and ready to implement.

**What's next**: Deploy prompt caching for 55% cost reduction, then add batch processing for offline work.

---

## Getting Help

- **For technical specs**: Check the other files in `specs/`
- **For code questions**: Look at the source code in `src/guidance_agent/`
- **For examples**: Run demos in `examples/`
- **For testing**: Check test files in `tests/`

**Most importantly**: Don't be intimidated! This is complex, but each piece is understandable. Start with one component, understand it, then move to the next. You've got this! 🚀

---

*Last updated: November 2025 (Phase 1 complete, 33/33 tests passing)*
