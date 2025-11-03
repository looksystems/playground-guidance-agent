# Cost and Token Usage Estimates

## Overview

This document provides detailed estimates for the token usage and costs required to bootstrap the Financial Guidance Agent system through Phase 6 (Evaluation and Metrics). These estimates are based on the implementation plan and assume a complete development, training, and validation cycle.

**Scope:**
- Development and testing iterations (Phases 2-5)
- Initial training run (5,000 virtual customer consultations)
- LLM-as-judge validation study
- Excludes production deployment costs (covered in implementation-plan.md)

**Last Updated:** November 1, 2025

---

## Token Usage Analysis

### Development & Testing Phase (Phases 2-5)

**Included Activities:**
- Building learning functions (Phase 2)
- Implementing advisor agent with prompt engineering (Phase 3)
- Developing customer agent and outcome simulation (Phase 4)
- Creating virtual environment and orchestration (Phase 5)
- Component and integration testing
- Debugging and iteration cycles

**Estimated Token Usage:**

| Activity | Estimated Tokens | Notes |
|----------|------------------|-------|
| Component testing | 5-10M tokens | ~100-200 test consultations |
| Integration testing | 3-5M tokens | ~50-100 full consultations |
| Debugging iterations | 2-5M tokens | ~500-1,000 LLM calls |
| **Total** | **10-20M tokens** | Varies by iteration count |

**Estimated Costs:**
- **Range: $1,500 - $4,000**
- Assumes mix of GPT-4 (advisor testing) and GPT-3.5 (customer simulation)
- Higher end if extensive prompt engineering iterations needed

---

### Training Run (5,000 Virtual Customers)

This is the main bootstrap training phase where the advisor learns from 5,000 simulated customer consultations in the virtual environment.

#### **Option 1: OpenAI Stack (GPT-4o + GPT-4o-mini)**

| Component | Token Usage | Cost | Model | Notes |
|-----------|-------------|------|-------|-------|
| Customer generation | ~25M tokens | $31 | GPT-4o-mini ($0.25/$2 per 1M) | Profile + pension pot generation |
| Consultations (advisor) | ~15M tokens | $188 | GPT-4o ($2.5/$10 per 1M) | Multi-turn guidance sessions |
| Outcome simulation | ~13M tokens | $16 | GPT-4o-mini | Post-consultation outcomes |
| Embeddings | ~100M tokens | $2 | text-embedding-3-small | Memories, cases, rules |
| Reflection & learning | ~5M tokens | $63 | GPT-4o | Failure analysis, rule generation |
| LLM-as-judge (training) | ~50M tokens | $63 | GPT-4o-mini | Single judge, confidence scoring |
| **Total** | **~208M tokens** | **~$363** | Mixed | Per 5,000 customer run |

**Token Breakdown:**
- **Embeddings: 48%** (100M tokens) - Vectorizing all memories, cases, and rules
- **Consultations: 24%** (50M tokens) - Multi-turn advisor-customer conversations
- **LLM-as-judge: 24%** (50M tokens) - Compliance validation during training
- **Other: 4%** (8M tokens) - Customer generation, reflection, learning

#### **Option 2: Mixed Stack (Claude 4.5 Sonnet + Haiku 4.5) - RECOMMENDED**

| Component | Token Usage | Cost | Model | Notes |
|-----------|-------------|------|-------|-------|
| Customer generation | ~20M tokens | $13 | Claude Haiku 4.5 ($1/$5 per 1M) | Fast, efficient structured generation |
| Consultations (advisor) | ~13M tokens | $234 | Claude 4.5 Sonnet ($3/$15 per 1M) | Highest-quality guidance |
| Outcome simulation | ~12M tokens | $8 | Claude Haiku 4.5 | Ultra-fast outcome simulation |
| Embeddings | ~100M tokens | $2 | text-embedding-3-small | Same as Option 1 |
| Reflection & learning | ~4.5M tokens | $81 | Claude 4.5 Sonnet | Rule generation and reflection |
| LLM-as-judge (training) | ~50M tokens | $63 | GPT-4o-mini | Cost-effective validation |
| **Total** | **~199.5M tokens** | **~$401** | Mixed | **10% cost savings vs Option 1** |

**Why Recommended:**
- Claude 4.5 Sonnet: Best quality for advisor guidance
- Claude Haiku 4.5: 4-5x faster for high-throughput tasks
- LiteLLM automatic fallbacks to OpenAI if needed
- Excellent reasoning for complex guidance scenarios
- Both support 90% prompt caching discounts
- 50% batch processing discount available
- Total savings: Can reach $200-240 per run with caching

---

### Validation Study (One-Time)

The LLM-as-judge validation study validates the compliance validation system against expert human judgments.

**Components:**

| Activity | Token Usage | Cost | Notes |
|----------|-------------|------|-------|
| Expert labeling | N/A | $1,000-2,000 | Human expert time (200-500 consultations) |
| LLM judge runs | ~25-50M tokens | $500-1,000 | 3 judges × multiple iterations |
| Prompt refinement | ~5-10M tokens | $200-500 | Iterative prompt improvements |
| **Total** | **~30-60M tokens** | **$1,500-3,000** | One-time validation cost |

**Validation Process:**
1. Expert labels 200-500 diverse consultations
2. Run 3 LLM judges (GPT-4, Claude 3.5 Sonnet, GPT-4 v2) on same set
3. Calculate agreement metrics (Cohen's kappa, F1, etc.)
4. Refine prompts based on disagreement patterns
5. Re-run on held-out validation set
6. Document methodology for regulatory audit

**Success Criteria:**
- Cohen's kappa > 0.85 (inter-rater reliability)
- False negative rate < 1% (compliance violations not missed)
- False positive rate < 10% (acceptable false alarms)

---

## Total Bootstrap Estimates

### **Conservative Estimate (Lower Bound)**

| Phase | Token Usage | Cost |
|-------|-------------|------|
| Development & Testing | 10M tokens | $800 |
| Training Run (Mixed models) | 200M tokens | $401 |
| Validation Study | 25M tokens | $800 |
| **TOTAL** | **~235M tokens** | **~$2,001** |

### **Upper Bound Estimate**

| Phase | Token Usage | Cost |
|-------|-------------|------|
| Development & Testing | 20M tokens | $2,000 |
| Training Run (OpenAI GPT-4o stack) | 208M tokens | $363 |
| Validation Study | 50M tokens | $1,500 |
| **TOTAL** | **~278M tokens** | **~$3,863** |

### **Most Likely Outcome (with LiteLLM + Caching) - 2025**

Using LiteLLM smart routing, mixed model strategy, and prompt caching:

- **Token Usage: ~250M tokens**
- **Base Cost: $2,500 - $3,500**
- **With Prompt Caching (90% savings on repeated content): $1,500 - $2,200**
- **Timeframe: 7-8 weeks** (development through validation)

**Cost Reduction Strategies:**
- Prompt caching: 90% discount on cache hits
- Batch processing: 50% discount on non-urgent workloads
- Smart model routing: Use Haiku 4.5 for simple tasks, Sonnet for complex ones

---

## Cost Drivers Analysis

### What Consumes the Most Tokens?

1. **Embeddings (40% of tokens)**
   - 100M tokens for vectorizing all memories, cases, and rules
   - Required for semantic retrieval system
   - Every observation, case, and rule needs embedding
   - **Cost: $10** (relatively cheap per token)

2. **Consultations (25% of cost, ~50M tokens)**
   - Multi-turn conversations between advisor and customer
   - Average 10-15 turns per consultation × 5,000 customers
   - Uses highest-quality models (GPT-4 Turbo or Claude Sonnet)
   - **Cost: $200-300** (most expensive per token)

3. **LLM-as-Judge Validation (24% of tokens, 20% of cost)**
   - Compliance checking for every piece of guidance
   - Single judge in training mode (lighter than production)
   - **Cost: $100**

4. **Reflection & Learning (20% of cost, ~5M tokens)**
   - Analyzing failures and generating rules
   - Importance scoring for memories
   - **Cost: $70-100**

5. **Customer & Outcome Simulation (8% of cost, ~25M tokens)**
   - Profile generation and outcome simulation
   - Uses cheaper models (GPT-3.5, Claude Haiku)
   - **Cost: $35-70**

### Cost Per Virtual Customer

**Option 1 (OpenAI GPT-4o):** $363 / 5,000 = **$0.073 per customer**

**Option 2 (Mixed Claude 4.5):** $401 / 5,000 = **$0.080 per customer** (recommended for quality)

**With Prompt Caching (90% discount):** $0.040-0.048 per customer

**Cost Breakdown Per Customer (2025 models):**
- Advisor consultations: $0.038-0.047
- Embeddings: $0.0004
- Outcome simulation: $0.002-0.003
- LLM-as-judge: $0.013
- Reflection/learning: $0.016-0.018

**Cost Reduction Opportunities:**
- Prompt caching can reduce per-customer cost by 40-50%
- Batch processing saves additional 50% on non-urgent tasks
- Combined savings: Up to **$0.024-0.032 per customer**

---

## Optimization Opportunities

### 1. **Embedding Model Selection**

| Model | Dimensions | Cost per 1M tokens | Quality | Recommendation |
|-------|------------|-------------------|---------|----------------|
| text-embedding-3-small | 1536 | $0.02 | Good | **Recommended** (50% cost savings) |
| text-embedding-3-large | 3072 | $0.13 | Better | If quality issues arise |
| text-embedding-ada-002 | 1536 | $0.10 | Baseline | Legacy, not recommended |

**Impact:** Switching from `-large` to `-small` saves **$5 per training run** (minimal impact on quality per benchmarks)

**Current plan uses:** text-embedding-3-small (1536 dims) for optimal pgvector HNSW performance

### 2. **LiteLLM Cost-Based Routing**

```python
# Automatic routing to cheapest available model
router = Router(routing_strategy="cost-based-routing")
```

**Benefits:**
- Automatically use cheapest model that meets requirements
- Fallback to alternatives if primary fails (no wasted retry costs)
- Estimated savings: **15-33% on LLM costs**

**Example:** If Claude is cheaper and available, route customer simulation there instead of GPT-3.5

### 3. **Batch Operations**

**Already in plan:**
- Batch embedding operations (reduces API overhead)
- Pre-generate customer population (reuse across experiments)

**Estimated savings:** 5-10% on API costs

### 4. **Caching Strategies**

**Opportunities:**
- Cache customer profiles between training runs
- Cache FCA knowledge embeddings (static)
- Cache common query embeddings

**Estimated savings:** $50-100 per training run (after first run)

### 5. **Model Selection by Task**

Current strategy optimized for 2025 models:

| Task | Best Model (2025) | Cost/1M | Why |
|------|-------------------|---------|-----|
| Advisor guidance | Claude 4.5 Sonnet | $3/$15 | Quality critical, excellent reasoning |
| Customer simulation | Claude Haiku 4.5 | $1/$5 | 4-5x faster, quality sufficient |
| Embeddings | text-embedding-3-small | $0.02 | Fast, cheap, good quality |
| Importance scoring | GPT-4o-mini | $0.25/$2 | Simple scoring task, very cheap |
| Reflection | Claude 4.5 Sonnet | $3/$15 | Complex reasoning needed |
| LLM-as-judge | GPT-4o-mini | $0.25/$2 | Cost-effective validation |
| Outcome simulation | Claude Haiku 4.5 | $1/$5 | Fast, efficient |

**This strategy saves ~65% vs using GPT-4 Turbo everywhere**
**With prompt caching: saves ~80-85% on repeated content**

### 6. **Progressive Training**

Instead of 5,000 customers upfront:

1. Start with 500 customers ($42-58)
2. Evaluate performance
3. Iterate on prompts/strategy
4. Scale to 5,000 when confident

**Estimated savings during development:** $500-1,000 (avoid full runs with poor prompts)

---

## Assumptions & Notes

### Token Usage Calculations

**Assumptions:**
- Average consultation: 10-15 turns
- Average message length: 300-500 tokens
- Reflection triggered on ~20% of failures (~1,000 consultations)
- Every memory/case/rule embedded once
- LLM-as-judge: single-judge training mode (production uses 3-judge consensus)

**Variance Factors:**
- Actual consultation length varies by customer complexity
- Token counts depend on specific prompt designs
- Reflection frequency depends on failure rate
- Embedding count grows with case/rule base size

### Cost Calculations

**Based on (as of November 2025):**
- GPT-5: $1.25/1M input, $10/1M output (+ 90% cache discount)
- GPT-5 Mini: $0.25/1M input, $2/1M output
- GPT-4o: $2.50/1M input, $10/1M output (+ 90% cache discount)
- GPT-4o-mini: $0.25/1M input, $2/1M output
- Claude Sonnet 4.5: $3/1M input, $15/1M output (+ 90% cache discount, + 50% batch discount)
- Claude Haiku 4.5: $1/1M input, $5/1M output
- Claude Haiku 3.5: $0.80/1M input, $4/1M output
- text-embedding-3-small: $0.02/1M tokens
- text-embedding-3-large: $0.13/1M tokens

**Note:** Actual costs may vary based on:
- Provider pricing changes
- Input vs output token ratios
- LiteLLM routing decisions
- Prompt caching utilization (90% savings on cache hits)
- Batch processing discounts (50% for Claude)
- Cache hit rates (typically 30-70% for repeated content)

### Not Included in Estimates

**Excluded from bootstrap costs:**
- Production infrastructure (covered in implementation-plan.md)
- Real customer consultations (post-deployment)
- Ongoing model fine-tuning
- Production LLM-as-judge (3-judge consensus: ~$1,500/year for 10K consultations)
- Human review costs (~$6,250/year for 5% escalation)

### Scaling Considerations

**Additional training runs:**
- Each 5,000 customer run: $420-580
- Typical project: 3-5 training runs during development
- Total training budget: $1,260-2,900

**Larger training sets:**
- 10,000 customers: $840-1,160
- 25,000 customers: $2,100-2,900
- Linear scaling (no volume discounts in estimates)

---

## Comparison to Alternatives

### vs Full Human Training

**Traditional approach:**
- Train advisor on 5,000 real customers
- Timeframe: 5-10 years
- Supervision cost: $250,000+ (human oversight)
- **Bootstrap cost: Virtual approach saves ~$245,000 and 5-10 years**

### vs Other Virtual Training Approaches

**Rule-based simulation (no LLMs):**
- Lower cost (~$0)
- Poor realism, limited learning
- Doesn't transfer to real scenarios

**Single-model approach (no LiteLLM):**
- GPT-4 everywhere: ~$800/run (+90% cost)
- No fallback handling (reliability risk)

**Current approach optimizes cost while maintaining quality**

---

## Budget Recommendations

### Minimum Viable Budget

**For proof-of-concept (2025 pricing):**
- Development/testing: $800
- Single training run (500 customers): $40
- Basic validation: $400
- **Total: ~$1,240**

**Gets you:**
- Working prototype
- Initial performance metrics
- Proof of approach viability

### Recommended Budget

**For production-ready system (2025 pricing):**
- Development/testing: $1,200-1,500
- 3 training runs (5,000 customers each): $1,203 base ($600 with caching)
- Full validation study: $1,200-1,500
- Buffer (15%): $540-650
- **Total: $4,140-5,150 (or $3,540-4,150 with prompt caching)**

**Gets you:**
- Fully validated system
- Multiple training iterations
- Regulatory-grade validation
- Confidence for deployment

**Cost Savings:**
- Prompt caching: 50% reduction ($600 saved)
- Batch processing: Additional 25% on non-urgent tasks
- Combined savings: Up to $900-1,200

### Enterprise Budget

**For comprehensive development (2025 pricing):**
- Extended development/testing: $2,000
- 5 training runs (increasing sizes): $2,005 base ($1,000 with caching)
- Comprehensive validation: $1,800
- Ablation studies: $600
- **Total: $6,405 base ($5,400 with caching)**

**Gets you:**
- Extensive experimentation
- Ablation studies (what components matter most)
- Multiple model comparisons
- Publication-quality results

---

## Cost Tracking & Monitoring

### Phoenix Integration

**Automatic tracking** (already in implementation plan):
- Real-time cost per LLM call
- Cost breakdown by model/provider
- Cost per customer consultation
- Cumulative training run costs
- **Zero additional cost** (self-hosted)

**Benefits:**
- Identify expensive operations
- Optimize prompts for cost
- Track against budget in real-time
- No surprises at end of month

### Recommended Monitoring

**Track these metrics:**
1. Cost per virtual customer (target: $0.08-0.12)
2. Cost per training run (target: $400-600)
3. Average tokens per consultation (target: 8K-12K)
4. Embedding count growth (monitor case/rule base size)

**Alert thresholds:**
- Single consultation > $0.50 (investigate prompt or model issue)
- Training run > $800 (pause and review)
- Embedding costs > $20/run (check for duplicates)

---

## References

- **Implementation Plan:** `specs/implementation-plan.md` (lines 1669-1831)
  - Production cost estimates
  - Infrastructure costs
  - Ongoing operational costs
- **LiteLLM Pricing:** https://docs.litellm.ai/docs/proxy/cost_tracking
- **OpenAI Pricing:** https://openai.com/pricing
- **Anthropic Pricing:** https://anthropic.com/pricing
- **Phoenix Observability:** `specs/implementation-plan.md` (lines 1835-1920)

---

## Summary

**Expected Bootstrap Costs (2025 Pricing):**
- **Conservative: $2,001** (10M dev tokens + 1 training run + minimal validation)
- **Recommended: $4,140-5,150** (15M dev tokens + 2-3 training runs + full validation)
- **With Prompt Caching: $3,540-4,150** (50% reduction on training runs)
- **Comprehensive: $6,405** base, **$5,400 with caching** (20M dev tokens + 5 training runs + extensive validation)

**Token Usage: 235-278M tokens** across entire bootstrap process

**Key Insight:** Virtual training with 2025 LLMs enables 5,000 customer equivalent experience for **$363-401**, compared to years and hundreds of thousands in traditional approaches.

**Optimization delivers:**
- **65-70% cost savings** through smart model selection vs GPT-4 Turbo everywhere
- **Additional 40-50% savings** with prompt caching on repeated content
- **Combined: 80-85% total cost reduction** vs baseline GPT-4 Turbo approach
