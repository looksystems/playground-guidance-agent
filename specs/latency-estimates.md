# Latency Estimates and Performance Targets

## Overview

This document provides detailed latency estimates for real client interactions with the Financial Guidance Agent system. Understanding and optimizing latency is critical for delivering a responsive user experience that meets or exceeds customer expectations.

**Scope:**
- Real-time client interaction latency
- Component-level performance breakdown
- Optimization strategies for production deployment
- User experience benchmarks and SLAs
- Monitoring and alerting recommendations

**Related Documents:**
- `specs/cost-estimates.md` - Token usage and cost analysis
- `specs/implementation-plan.md` - Overall system architecture
- `specs/advisor-agent.md` - Advisor agent implementation details

**Last Updated:** November 1, 2025

---

## Expected Latency Per Advisor Response

### Sequential Operations (Critical Path)

A typical advisor response involves the following sequential operations:

#### **1. Query Embedding Generation**
```
Input: Customer's question (50-200 tokens)
Model: text-embedding-3-small (1536 dimensions)
Operation: Convert question to vector for retrieval
```
- **Typical latency: 50-150ms**
- **Percentage of total: 1-2%**
- Can be cached for common queries

#### **2. Context Retrieval (Parallel)**

Three retrieval operations run in parallel:

```python
# All three execute concurrently via asyncio
memory_results = memory_stream.retrieve(query_embedding, top_k=10)
case_results = case_base.retrieve(query_embedding, top_k=3)
rule_results = rules_base.retrieve(query_embedding, top_k=4)
```

| Retrieval Type | Latency | Details |
|----------------|---------|---------|
| Memory stream | 20-50ms | pgvector HNSW index, 10 results |
| Case base | 20-50ms | pgvector HNSW index, 3 results |
| Rules base | 20-50ms | pgvector HNSW index, 4 results, confidence weighted |
| **Parallel total** | **50-80ms** | Limited by slowest operation |

- **Percentage of total: 1%**
- Depends on database load and index quality

#### **3. Advisor LLM Generation (Main Bottleneck)**

```
Model: GPT-4o, GPT-5, or Claude 3.5/4 Sonnet
Input tokens: 2,000-4,000 (retrieved context + conversation history + prompts)
Output tokens: 300-600 (guidance response)
```

**Latency breakdown:**
- **Streaming (time to first token): 640ms-850ms**
- **Streaming (full completion): 3-6 seconds**
- **Percentage of total: 75-80%**

**This is the primary bottleneck** - LLM inference dominates overall latency.

**Token generation rate (2025 models):**
- GPT-4 Turbo: ~31-39 tokens/second
- GPT-4o: ~50-151 tokens/second (2x faster than GPT-4 Turbo)
- GPT-5: ~80-120 tokens/second (estimated)
- Claude 3.5 Sonnet: ~51 tokens/second (0.64s TTFT)
- Claude 4.5 Sonnet: ~55-65 tokens/second (estimated)
- Claude Haiku 3.5: ~53 tokens/second (0.36s TTFT, fastest TTFT)
- Claude Haiku 4.5: ~200-250 tokens/second (4-5x faster than Sonnet)

#### **4. Compliance Validation**

```
Model: GPT-3.5 Turbo or GPT-4
Input tokens: ~1,000 (guidance + customer context + FCA rules)
Output tokens: ~200 (validation result + issues)
```

- **Latency: 1-2 seconds**
- **Percentage of total: 15-20%**
- Can run in parallel with step 3 (async) or after streaming completes

---

### Total Latency Estimates

#### **Without Streaming (Blocking)**

User waits for complete response before seeing anything:

| Scenario | Latency | Breakdown |
|----------|---------|-----------|
| **Optimistic** | **4.5s** | Fast retrieval (60ms) + fast LLM (3s) + fast validation (1.2s) |
| **Typical** | **6-8s** | Normal retrieval (70ms) + normal LLM (4-5s) + validation (1.5s) |
| **Pessimistic** | **10-12s** | Slow retrieval (100ms) + slow LLM (6s) + slow validation (2s) + network |

#### **With Streaming (Recommended)**

User sees progressive response as tokens arrive:

| Metric | Latency | User Perception |
|--------|---------|-----------------|
| **Time to first token** | **1-2s** | "AI is thinking..." → First words appear |
| **Partial response visible** | **2-3s** | User starts reading while AI continues |
| **Full response visible** | **4-6s** | Complete guidance displayed |
| **Validation completes** | **6-8s** | Background operation, transparent to user |

**Key insight:** Streaming reduces **perceived latency by 70-75%**

---

## Component Breakdown Table

| Component | Latency | % of Total | Optimization Potential | Priority |
|-----------|---------|------------|------------------------|----------|
| Query embedding | 50-150ms | 1-2% | ✓ High (caching) | Low |
| Vector retrieval (3x) | 50-80ms | 1% | ✓ Medium (index tuning) | Low |
| **Advisor LLM** | **3-6s** | **75-80%** | △ Limited (model choice) | **HIGH** |
| Compliance validation | 1-2s | 15-20% | ✓ High (async/parallel) | Medium |
| Database writes | 20-50ms | <1% | — Already optimal | Low |
| Network overhead | 100-350ms | 2-5% | △ Limited (CDN, regions) | Low |

**Critical path:** Embedding → Retrieval → LLM → Validation

**Main bottleneck:** LLM inference (75-80% of total latency)

---

## Optimization Strategies

### 1. Streaming Response (HIGHEST IMPACT)

**Implementation:**
```python
from litellm import completion

response = completion(
    model="claude-3-5-sonnet-20250219",
    messages=messages,
    stream=True  # Enable streaming
)

for chunk in response:
    # Send chunk to user immediately
    yield chunk.choices[0].delta.content
```

**Impact:**
- Perceived latency: **1-2s** (vs 6-8s blocking)
- Reduction: **70-75%**
- User starts reading while AI generates
- Industry standard for conversational AI

**User experience:**
```
0.0s: User sends question
1.2s: First words appear ✓ (feels responsive)
2.5s: User reading partial response
4.8s: Full response complete ✓ (acceptable)
6.2s: Validation complete (background)
```

**Recommendation:** ✅ **MUST IMPLEMENT** - Dramatic UX improvement

---

### 2. Parallel Compliance Validation

**Current (sequential):**
```python
guidance = generate_guidance()  # 4-6s
validation = validate_compliance(guidance)  # 1-2s
# Total: 5-8s
```

**Optimized (parallel):**
```python
# Start streaming response immediately
async for chunk in generate_guidance_stream():
    send_to_user(chunk)
    guidance_buffer += chunk

# Validate in background while streaming
validation = await validate_compliance(guidance_buffer)

# Only intervene if validation fails (rare <2%)
if not validation.passed:
    send_correction_to_user()
```

**Impact:**
- Saves: **1-2 seconds** in happy path (98%+ of cases)
- User sees response immediately
- Validation runs transparently
- Only blocks on validation failure (rare)

**Recommendation:** ✅ **IMPLEMENT** - Significant latency reduction

---

### 3. Query Embedding Caching

**Implementation:**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_embedding(query: str) -> list[float]:
    return embed(query)

# Common queries cached in Redis
COMMON_QUERIES = {
    "pension options": [...],  # Pre-computed embedding
    "transfer value": [...],
    "defined benefit": [...],
}
```

**Common query patterns:**
- "What are my pension options?"
- "Should I transfer my defined benefit pension?"
- "When can I access my pension?"
- "What is a lifetime allowance?"

**Impact:**
- Saves: **50-150ms** on cache hits
- Expected hit rate: 15-25% (common questions)
- Minimal implementation complexity

**Recommendation:** ✅ Implement - Low effort, measurable improvement

---

### 4. Model Selection Trade-offs

| Model | Latency | Quality | Cost/1M (in/out) | Tokens/sec | Recommendation |
|-------|---------|---------|------------------|------------|----------------|
| **Claude 4.5 Sonnet** | 2-4s | Excellent | $3/$15 | 55-65 | **PRIMARY (recommended)** |
| **GPT-4o** | 2-3s | Excellent | $2.5/$10 | 50-151 | **Alternative primary** |
| Claude 3.5 Sonnet | 3-5s | Excellent | $3/$15 | 51 | Production option |
| GPT-4 Turbo | 4-6s | Excellent | $30/$60 | 31-39 | Legacy fallback |
| Claude Haiku 4.5 | 0.5-1s | Very Good | $1/$5 | 200-250 | **Fast/budget option** |
| Claude Haiku 3.5 | 0.8-1.5s | Good | $0.8/$4 | 53 | Dev/testing |
| GPT-5 | 2-3s | Excellent | $1.25/$10 | 80-120 | Premium option |
| GPT-5 Mini | 1-2s | Very Good | $0.25/$2 | 100-150 | Budget alternative |

**Recommendation: Claude 4.5 Sonnet or GPT-4o**
- ✅ Claude 4.5 Sonnet: Best balance of quality, speed, and cost
- ✅ GPT-4o: 20% cheaper, comparable quality, excellent speed
- ✅ Claude Haiku 4.5: **4-5x faster** for high-throughput needs
- ✅ Both support 90% cost reduction with prompt caching
- ✅ More consistent latency than previous generation models

**LiteLLM Fallback Strategy:**
```python
completion(
    model="claude-sonnet-4.5",
    fallbacks=[
        "gpt-4o",              # Fast, cost-effective fallback
        "claude-3.5-sonnet",   # Second fallback
        "gpt-5"                # Premium fallback if needed
    ]
)
```

**Fallback latency penalty:** +1-3s (only when primary fails, <1% of time)

---

### 5. pgvector Index Tuning

**Current implementation (HNSW):**
```sql
CREATE INDEX memories_embedding_idx
ON memories
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

**Performance by index type:**

| Index Type | Build Time | Query Latency | Recall@10 | Recommendation |
|------------|------------|---------------|-----------|----------------|
| **HNSW** | Longer | **10-30ms** | 95-98% | **Production** ✓ |
| IVFFlat | Fast | 20-80ms | 90-95% | Development |
| No index | N/A | 500ms+ | 100% | Never use |

**HNSW tuning parameters:**
- `m`: Higher = better recall, slower build (16-32 recommended)
- `ef_construction`: Higher = better recall, slower build (64-128 recommended)
- `ef_search`: Runtime parameter, higher = better recall, slower search (40-200)

**Recommendation:**
```sql
-- Production settings (balanced)
m = 16, ef_construction = 64, ef_search = 100

-- High-performance settings (if latency critical)
m = 32, ef_construction = 128, ef_search = 200
```

**Impact:**
- Optimized HNSW: **10-20ms** per retrieval
- 3 retrievals (parallel): **~20ms** total
- Improvement: **30-60ms** vs IVFFlat

---

### 6. Database Connection Pooling

**Implementation (already in plan - SQLAlchemy):**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # Connections per instance
    max_overflow=10,        # Additional connections under load
    pool_pre_ping=True,     # Verify connection health
    pool_recycle=3600       # Recycle connections hourly
)
```

**Impact:**
- Eliminates connection setup latency (~50-100ms)
- Consistent performance under load
- Essential for production

**Recommendation:** ✅ Already in implementation plan

---

## User Experience Benchmarks

### Acceptable Latency Targets

Based on UX research for conversational AI systems:

| Metric | Target | User Perception | Our System |
|--------|--------|-----------------|------------|
| Time to first token | **<1.5s** | Feels responsive | **1-2s** ✓ Borderline |
| Time to partial response | **<3s** | Can start reading | **2-3s** ✓ Good |
| Time to complete response | **<5s** | Acceptable | **4-6s** ✓ Acceptable |
| Time to full validation | **<8s** | Background, transparent | **6-8s** ✓ Good |
| Maximum timeout | **<15s** | Escalate to human | **20s** △ Adjust |

**Assessment:** Current architecture meets UX targets with streaming enabled

### Comparison to Alternatives

#### **vs Human Advisor (Phone/Chat)**

| Metric | AI System | Human Advisor | Advantage |
|--------|-----------|---------------|-----------|
| Initial response time | **1-2s** | 10-30s | **10-15x faster** |
| Complete answer | **4-6s** | 2-5 min | **20-50x faster** |
| Context retrieval (similar cases) | **50ms** | 2-5 min | **2400-6000x faster** |
| Compliance check | **1-2s** | Manual/post-hoc | **Automatic + instant** |
| Availability | 24/7 instant | Business hours + queue | **Always available** |

**Key insight:** AI provides dramatically faster initial response, enabling real-time guidance

#### **vs Other Conversational AI Systems**

| System | Typical Latency | Notes |
|--------|-----------------|-------|
| ChatGPT (GPT-4) | 3-8s | Similar to our system |
| Claude.ai (Claude 3.5 Sonnet) | 2-6s | Slightly faster |
| Google Bard (Gemini Pro) | 2-5s | Comparable |
| **Our system (optimized)** | **4-6s** | Competitive with industry leaders |

**Assessment:** Our latency is competitive with leading conversational AI products

---

## Real-World Latency Factors

### Network Latency

**User → Server (UK domestic):**
- Typical: 20-50ms
- 95th percentile: 100-150ms
- Peak hours: +20-30ms

**Server → LLM API:**
- OpenAI (US-East): 50-100ms from UK
- Anthropic (US-West): 80-150ms from UK
- Azure OpenAI (UK regions): 10-30ms

**Total network overhead:**
- Optimistic: 100ms
- Typical: 150-250ms
- Pessimistic: 300-400ms

**Mitigation:**
- Use CDN for static assets
- Deploy API server in UK region (London)
- Use Azure OpenAI UK endpoints if available
- Consider multi-region deployment for global users

---

### LLM Provider Variability

#### **OpenAI (GPT-4o / GPT-5)**

| Condition | Latency | Variance |
|-----------|---------|----------|
| Off-peak hours (2am-8am GMT) | 2-3s | Low |
| Business hours (9am-5pm GMT) | 3-5s | Low-Medium |
| Peak hours (7pm-11pm GMT) | 4-7s | Medium (15-30% slower) |
| Outages/degradation | Infinite | LiteLLM fallback to Claude |

**Characteristics:**
- GPT-4o significantly faster than GPT-4 Turbo
- GPT-5 offers improved consistency
- 90% cost reduction with prompt caching
- Occasional rate limiting (mitigated by LiteLLM)
- Generally reliable infrastructure

#### **Anthropic (Claude 4.5 Sonnet / Claude Haiku 4.5)**

| Condition | Latency | Variance |
|-----------|---------|----------|
| Off-peak hours | 2-3s | Very Low |
| Business hours | 2-4s | Low |
| Peak hours | 3-5s | Low (10-20% slower) |
| Outages/degradation | Infinite | LiteLLM fallback to GPT-4o |

**Characteristics:**
- Claude 4.5 Sonnet: Most consistent latency across all time periods
- Claude Haiku 4.5: 4-5x faster than Sonnet for high-throughput needs
- Excellent reliability record
- 50% batch processing discount available
- 90% savings with prompt caching
- Lower variance overall

**Recommendation:** Use Claude 4.5 Sonnet as primary for best consistency, with GPT-4o as fast fallback

#### **LiteLLM Automatic Fallback**

**Scenario: Primary provider down**
```python
# Automatic fallback sequence
1. Try Claude 4.5 Sonnet → Fails (timeout)
2. Fallback to GPT-4o → Success (+1-3s latency penalty)
3. If both fail → Fallback to Claude 3.5 Sonnet
4. Final fallback → GPT-5
```

**Fallback latency penalty:**
- Detection: 3-5s timeout (improved from older versions)
- Retry on fallback: +1-3s
- **Total: +4-8s** (rare, <1% of requests)
- Better than complete failure
- Faster recovery than previous generation models

---

### Database Load Impact

**pgvector Performance Under Load:**

| Concurrent Users | Query Latency | Notes |
|------------------|---------------|-------|
| 1-10 users | 20-30ms | Baseline performance |
| 11-50 users | 30-50ms | Minimal degradation |
| 51-100 users | 50-80ms | Moderate increase |
| 100+ users | 80-150ms | Consider read replicas |

**PostgreSQL connection pooling** (already in plan) prevents connection exhaustion

**Scaling recommendations:**
- <50 concurrent users: Single database instance
- 50-200 users: Connection pooling + optimized indexes
- 200+ users: Read replicas for retrieval operations
- 1000+ users: Horizontal sharding or managed service

**Current design handles:** 50-100 concurrent users with <80ms retrieval latency

---

## Multi-Turn Conversation Latency

### Cold Start vs Warm Cache

#### **First Interaction (Cold Start)**

```
User: "What are my pension options at 55?"

Operations:
- No conversation history (minimal context)
- No cached embeddings
- Full retrieval + LLM generation
```

**Latency: 6-8 seconds**

#### **Subsequent Turns (Warm)**

```
User: "What about the tax implications?"

Operations:
- Conversation history in context (smaller incremental context)
- Query might hit cache
- Faster due to context continuity
```

**Latency: 4-6 seconds** (15-25% faster)

**Reasons for improvement:**
- Smaller context delta (just new question + previous response)
- Better LLM performance with established context
- Potential query cache hits
- Connection pooling already warmed

---

### Typical Consultation Timeline

**Full consultation (10-15 turns):**

| Turn | Type | Latency | Cumulative |
|------|------|---------|------------|
| 1 | Initial question (cold) | 7s | 7s |
| 2-5 | Follow-up questions | 5s each | 27s |
| 6-10 | Deeper exploration | 5s each | 52s |
| 11-15 | Clarifications | 4s each | 72s |

**Total AI thinking time:** ~50-72 seconds across 10-15 turns

**User activities (between turns):**
- Reading AI response: 30-60s per turn
- Thinking about next question: 10-30s
- Typing question: 10-20s
- **Total user time per turn:** 50-110 seconds

**Full consultation duration:**
- AI time: ~60 seconds (1 minute)
- User time: ~600-900 seconds (10-15 minutes)
- **Total: 11-16 minutes**

**Comparison to human advisor:**
- Phone consultation: 15-30 minutes
- In-person consultation: 30-60 minutes
- **AI is 2-4x faster while maintaining quality**

---

## Phoenix Observability Integration

### Automatic Latency Tracking

The implementation plan (lines 1835-1920) includes Phoenix for observability. **All latency metrics are automatically captured via OpenTelemetry.**

**Example trace (single response):**

```
Trace ID: customer-consultation-12345
Total Duration: 6.2s

├─ Query embedding generation
│  Duration: 85ms
│  Model: text-embedding-3-small
│  Tokens: 42
│
├─ Context retrieval (parallel)
│  Duration: 58ms
│  ├─ Memory retrieval: 42ms (10 results)
│  ├─ Case retrieval: 38ms (3 results)
│  └─ Rules retrieval: 45ms (4 results, confidence weighted)
│
├─ Advisor LLM generation
│  Duration: 4.2s ← Main bottleneck
│  Model: claude-3-5-sonnet-20250219
│  Input tokens: 3,240
│  Output tokens: 487
│  Tokens/second: 116
│  Cost: $0.065
│  Time to first token: 1.1s ✓
│
└─ Compliance validation
   Duration: 1.8s
   Model: gpt-3.5-turbo
   Input tokens: 1,120
   Output tokens: 156
   Result: PASSED
   Confidence: 0.94
```

### Latency Dashboards

**Phoenix provides built-in dashboards:**

1. **Latency Overview**
   - p50, p95, p99 latencies
   - Latency distribution histogram
   - Latency by time of day
   - Latency by model/provider

2. **Component Breakdown**
   - Embedding generation time
   - Retrieval time (per source)
   - LLM inference time
   - Validation time

3. **User Experience Metrics**
   - Time to first token
   - Full response completion time
   - Streaming metrics

4. **Provider Performance**
   - OpenAI vs Anthropic latency
   - Fallback frequency
   - Error rates by provider

**Example Dashboard View:**
```
Last 24 Hours:
├─ Total requests: 1,247
├─ Median latency (p50): 5.2s ✓ Good
├─ 95th percentile (p95): 8.1s ✓ Acceptable
├─ 99th percentile (p99): 11.3s △ Monitor
├─ Timeouts (>20s): 3 (0.24%) ✓ Low
└─ Fallback activations: 7 (0.56%)

Breakdown by component:
├─ Embeddings: 78ms median
├─ Retrieval: 52ms median
├─ LLM: 4.1s median ← 79% of total
└─ Validation: 1.6s median

By model:
├─ Claude 3.5 Sonnet: 4.8s median (92% of requests)
└─ GPT-4 Turbo: 6.2s median (8% fallback)
```

---

## Production Recommendations

### 1. Service Level Agreements (SLAs)

**Recommended SLAs for production:**

| Metric | Target | Alert Threshold | Escalation |
|--------|--------|-----------------|------------|
| **p50 latency** | <5s | >6s | Warning |
| **p95 latency** | <8s | >10s | Alert |
| **p99 latency** | <12s | >15s | Critical |
| **Timeout rate** | <1% | >2% | Alert |
| **Time to first token** | <2s | >3s | Warning |
| **Availability** | >99.5% | <99% | Critical |

**Rationale:**
- p50 <5s: Majority of users get fast responses
- p95 <8s: 95% of interactions feel responsive
- p99 <12s: Even outliers are acceptable
- <1% timeout: Rare enough to not impact UX significantly

---

### 2. Progressive Enhancement

**Implement graceful UX degradation:**

```python
async def provide_guidance_with_ux(customer_question: str):
    # Stage 1: Immediate acknowledgment
    yield {"status": "received", "timestamp": now()}

    # Stage 2: Show typing indicator (100ms)
    yield {"status": "thinking", "indicator": "typing"}

    # Stage 3: First token arrives (1-2s)
    async for chunk in generate_guidance_stream():
        yield {"status": "streaming", "content": chunk}

    # Stage 4: Complete response (4-6s)
    yield {"status": "complete"}

    # Stage 5: Validation in background (6-8s)
    validation = await validate_compliance()
    if not validation.passed:
        yield {"status": "correction", "issues": validation.issues}
```

**User sees:**
1. Instant acknowledgment (feels responsive)
2. Typing indicator (sets expectation)
3. Progressive text appearance (can start reading)
4. Complete response (satisfaction)
5. Optional corrections (rare, transparent)

---

### 3. Monitoring & Alerting

**Key metrics to track:**

```python
# Phoenix + custom monitoring
metrics = {
    # Latency metrics
    "latency_p50": timeseries,
    "latency_p95": timeseries,
    "latency_p99": timeseries,
    "time_to_first_token": timeseries,

    # Component metrics
    "embedding_latency": timeseries,
    "retrieval_latency": timeseries,
    "llm_latency": timeseries,
    "validation_latency": timeseries,

    # Provider metrics
    "openai_latency": timeseries,
    "anthropic_latency": timeseries,
    "fallback_rate": counter,

    # Error metrics
    "timeout_rate": counter,
    "error_rate": counter,
}
```

**Alert conditions:**

```python
# Warning alerts (Slack/email)
if p95_latency > 10s:
    alert("Latency degradation - investigate LLM provider")

if timeout_rate > 2%:
    alert("High timeout rate - check provider status")

# Critical alerts (PagerDuty)
if p50_latency > 15s:
    page_oncall("Critical latency - system degraded")

if availability < 99%:
    page_oncall("High error rate - system outage")
```

**Track by time of day:**
```python
# Identify peak hour patterns
latency_by_hour = {
    "00:00-06:00": 4.2s,  # Baseline
    "06:00-09:00": 5.1s,  # Morning
    "09:00-17:00": 6.3s,  # Peak business hours
    "17:00-23:00": 7.8s,  # Evening peak
    "23:00-00:00": 5.0s,  # Winding down
}

# Alert if deviation from baseline >40%
if current_latency > baseline * 1.4:
    alert("Latency spike detected")
```

---

### 4. Graceful Degradation

**Handling extreme latency or failures:**

```python
async def provide_guidance_with_fallbacks(customer: Customer):
    try:
        # Primary path (6-8s expected)
        with timeout(20):
            return await generate_guidance(customer)

    except TimeoutError:
        # Fallback 1: Simpler prompt (faster)
        try:
            with timeout(10):
                return await generate_guidance_simple(customer)
        except TimeoutError:
            # Fallback 2: Escalate to human
            return escalate_to_human(customer)

    except ProviderError as e:
        # LiteLLM already tried fallbacks
        if e.all_providers_failed:
            # Ultimate fallback: Queue for human advisor
            return queue_for_human_advisor(customer)
```

**Escalation thresholds:**
- Single response >20s: Retry with simpler prompt
- Single response >30s: Escalate to human queue
- Multiple timeouts (>3 in a row): System degradation alert
- Provider completely down: Full human fallback mode

**User communication:**
```
User sees:
"I'm taking a bit longer than usual. Your question is important -
let me connect you with a human advisor who can help right away."

[Seamless handoff to human advisor with full context]
```

---

### 5. Caching Strategy

**Multi-layer caching for optimal performance:**

```python
# Layer 1: In-memory LRU cache (fastest)
@lru_cache(maxsize=1000)
def get_common_query_embedding(query: str) -> Vector:
    """Cache embeddings for common queries (hit rate: 15-25%)"""
    return embed(query)

# Layer 2: Redis cache (fast)
def get_fca_knowledge_embedding(rule_id: str) -> Vector:
    """Cache static FCA knowledge embeddings (hit rate: 80%+)"""
    cached = redis.get(f"fca:embed:{rule_id}")
    if cached:
        return deserialize(cached)

    embedding = embed(fca_rules[rule_id])
    redis.setex(f"fca:embed:{rule_id}", 86400, serialize(embedding))
    return embedding

# Layer 3: Database query results (medium)
def get_retrieved_context(query_hash: str) -> Context:
    """Cache retrieval results for identical queries (hit rate: 5-10%)"""
    # PostgreSQL query result caching
    ...
```

**Cache hit impact:**
- L1 hit (common query): Saves 100-150ms
- L2 hit (FCA knowledge): Saves 50-100ms
- L3 hit (retrieval): Saves 50-80ms

**Expected performance improvement:**
- Combined hit rate: ~30-40%
- Average latency reduction: 100-200ms on cache hits
- Effective p50 latency: 4.8s → 4.6s (minor but noticeable)

---

### 6. Load Testing Recommendations

**Before production deployment:**

```python
# Simulate production load
load_test_scenarios = [
    {
        "name": "Baseline",
        "concurrent_users": 10,
        "duration": "10min",
        "expected_p95": "8s"
    },
    {
        "name": "Peak load",
        "concurrent_users": 50,
        "duration": "30min",
        "expected_p95": "10s"
    },
    {
        "name": "Spike test",
        "concurrent_users": "10→100→10",
        "duration": "15min",
        "expected_p95": "12s"
    },
    {
        "name": "Sustained high load",
        "concurrent_users": 100,
        "duration": "2hr",
        "expected_p95": "15s"
    }
]
```

**Tools:**
- Apache JMeter / Locust for load generation
- Phoenix for monitoring during test
- PostgreSQL pg_stat_statements for database analysis

**Success criteria:**
- No degradation >50% at peak load
- No connection pool exhaustion
- No database deadlocks
- Graceful degradation beyond capacity

---

## Summary

### Key Latency Metrics

| Metric | Without Streaming | With Streaming | Target |
|--------|-------------------|----------------|--------|
| Time to first token | N/A | **1-2s** | <1.5s |
| Perceived latency | 6-8s | **1-2s** | <2s |
| Complete response | 6-8s | **4-6s** | <5s |
| With validation | 8-10s | **6-8s** | <8s |

### Component Latency Breakdown

```
Total: 6-8 seconds
├─ Embedding: 100ms (1-2%)
├─ Retrieval: 60ms (1%)
├─ LLM: 4-5s (75-80%) ← Bottleneck
└─ Validation: 1.5s (15-20%)
```

### Optimization Priority

1. **✅ CRITICAL: Enable streaming** - 70-75% perceived latency reduction
2. **✅ HIGH: Parallel validation** - Saves 1-2s in happy path
3. **✅ HIGH: Use Claude 4.5 Sonnet or GPT-4o** - 30-40% faster than GPT-4 Turbo
4. **✅ HIGH: Enable prompt caching** - 90% cost reduction on repeated content
5. **△ MEDIUM: Query caching** - 100-200ms on cache hits (30% hit rate)
6. **△ LOW: HNSW index tuning** - Marginal 30-60ms improvement

### Recommended Configuration

**Best performance/cost/quality balance (2025):**

```yaml
Primary Model: Claude 4.5 Sonnet
- Latency: 2-4s
- Quality: Excellent
- Cost: $3/$15 per 1M tokens
- Tokens/sec: 55-65
- TTFT: ~0.64s

Alternative Primary: GPT-4o
- Latency: 2-3s
- Quality: Excellent
- Cost: $2.5/$10 per 1M tokens (20% cheaper)
- Tokens/sec: 50-151
- TTFT: ~0.85s

Fast Option: Claude Haiku 4.5
- Latency: 0.5-1s
- Quality: Very Good
- Cost: $1/$5 per 1M tokens (80% cheaper)
- Tokens/sec: 200-250 (4-5x faster)
- TTFT: ~0.36s

Streaming: Enabled
- Perceived latency: 0.6-1.2s
- UX: Excellent

Validation: Parallel (async)
- Transparent to user
- Minimal latency impact

Caching: Multi-layer + Prompt Caching
- Common queries (in-memory)
- Static knowledge (Redis)
- Prompt caching (90% savings)
- Query results (PostgreSQL)

Expected Performance (Claude 4.5 Sonnet):
- p50: 3.5-4.5s
- p95: 6-8s
- p99: 9-11s
- Time to first token: 0.6-0.9s
```

### User Experience Assessment

**Current system (optimized):**
- ✅ Competitive with leading conversational AI products
- ✅ 10-15x faster than human advisors (initial response)
- ✅ Meets industry UX benchmarks for responsiveness
- ✅ Handles 50-100 concurrent users with <8s p95 latency
- △ Room for improvement on time-to-first-token (<1.5s target)

**Recommendation:** System is production-ready with streaming enabled. Focus on monitoring and gradual optimization during beta.

---

## References

- **Implementation Plan:** `specs/implementation-plan.md`
  - Phoenix observability setup (lines 1835-1920)
  - LiteLLM configuration (lines 943-1022)
  - Database architecture (lines 206-265)

- **Cost Estimates:** `specs/cost-estimates.md`
  - Token usage analysis
  - Model selection trade-offs

- **Advisor Agent Spec:** `specs/advisor-agent.md`
  - Prompt engineering details
  - Compliance validation process

- **Industry Benchmarks:**
  - OpenAI GPT-4 response times: 3-8s (streaming)
  - Anthropic Claude response times: 2-6s (streaming)
  - UX research: <2s perceived latency for "responsive" feel

- **Database Performance:**
  - pgvector HNSW documentation
  - PostgreSQL connection pooling best practices
