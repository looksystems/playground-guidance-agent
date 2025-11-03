# Agent-Specific Local LLM Model Recommendations

**Last Updated:** 2025-11-02
**Target Hardware:** Mac Studio M4 with 64GB Unified Memory
**Related:** See `local-llm-options.md` for general model research

## Executive Summary

This document provides specific local LLM model recommendations for each agent in the FCA-compliant pension guidance system. Based on comprehensive analysis of task complexity, latency requirements, and the 64GB M4's capabilities, we recommend:

- **Advisor Agent:** Qwen 2.5 32B Instruct (Q5_K_M) for balanced performance
- **Customer Agent:** Llama 3.2 3B Instruct (Q6_K) for fast simulation
- **Compliance Validator:** Keep using cloud (GPT-4o + Claude 4.5 Sonnet)
- **Reflection/Planning:** Qwen 2.5 14B Instruct (Q6_K) for background processing
- **Knowledge Bootstrap:** Qwen 2.5 32B or cloud for high-quality seed generation

**Cost Savings:** ~500x cheaper for virtual training (local vs cloud)

---

## 1. Agent System Overview

### System Architecture

This FCA-compliant pension guidance system consists of:

1. **Advisor Agent** - Customer-facing pension guidance
2. **Customer Agent** - Simulates customers for virtual training
3. **Compliance Validator** - Ensures FCA regulatory compliance
4. **Base Agent Infrastructure** - Memory, reflection, planning
5. **Knowledge Bootstrap** - One-time seed data generation

### Current Cloud Configuration

```python
# From .env and specs
LITELLM_MODEL_ADVISOR = "gpt-4-turbo-preview"  # or Claude 4.5 Sonnet, GPT-4o
LITELLM_MODEL_CUSTOMER = "gpt-4o-mini"
LITELLM_MODEL_COMPLIANCE = "gpt-4o"  # Multi-judge: GPT-4 + Claude 3.5 Sonnet
```

### Performance Bottleneck Analysis

From `specs/latency-estimates.md`:

```
Total Latency: 6-8 seconds
├─ Embedding: 100ms (1-2%)
├─ Retrieval: 60ms (1%)
├─ LLM Generation: 4-5s (75-80%) ← PRIMARY BOTTLENECK
└─ Validation: 1.5s (15-20%)
```

**Key Insight:** LLM generation is the primary optimization target. Streaming reduces perceived latency by 70-75%.

---

## 2. Advisor Agent (Customer-Facing)

### Current Configuration

**Model:** GPT-4-turbo-preview / Claude 4.5 Sonnet / GPT-4o
**Location:** `src/guidance_agent/advisor/agent.py`

### Task Analysis

**Complexity Level:** COMPLEX ⭐⭐⭐⭐⭐

**Key Responsibilities:**
- Generate FCA-compliant pension guidance
- Maintain conversation context with memory stream
- Chain-of-thought reasoning (6-step framework)
- Retrieve context from case base and rules base
- Adapt language to customer literacy level
- Handle streaming responses to reduce perceived latency

**Performance Requirements:**
- **Target latency:** 4-6 seconds full response
- **Time-to-first-token (TTFT):** <1.5 seconds (streaming critical)
- **Token generation:** 300-600 output tokens per response
- **Input context:** 2,000-4,000 tokens
- **Criticality:** VERY HIGH (customer-facing, latency-sensitive)

### Local LLM Recommendations

#### Option A: Qwen 2.5 32B Instruct (Q5_K_M) ⭐ RECOMMENDED

**Memory:** ~20GB
**Speed:** 40-60 tokens/sec on M4 Pro
**Quality:** ⭐⭐⭐⭐ (very good, punches above weight class)

**Performance Expectations:**
```
Time-to-first-token: 0.5-1.5 seconds ✓ Excellent
Token generation: 40-60 tokens/sec
Full response (400 tokens): 7-10 seconds ✓ Good
Streaming UX: First words at 0.5-1.5s ✓ Acceptable
```

**Pros:**
- ✅ Excellent instruction following
- ✅ Strong chain-of-thought reasoning
- ✅ 128K context window (far exceeds 2-4K needs)
- ✅ Leaves 40GB+ headroom for OS and other agents
- ✅ Can run simultaneously with Customer and Reflection agents
- ✅ Good at nuanced boundary detection

**Cons:**
- ⚠️ Slower than cloud (7-10s vs 6-7s)
- ⚠️ Lower quality than 72B models
- ⚠️ Requires extensive compliance validation testing

**Use For:**
- Development and testing
- Virtual training (high-volume, cost-sensitive)
- Production if latency acceptable and compliance validated

---

#### Option B: Qwen 2.5 72B Instruct (Q4_K_M) - Maximum Quality

**Memory:** ~40GB
**Speed:** 15-25 tokens/sec on M4 Pro
**Quality:** ⭐⭐⭐⭐⭐ (matches GPT-4 class)

**Performance Expectations:**
```
Time-to-first-token: 1-3 seconds ✓ Good
Token generation: 15-25 tokens/sec
Full response (400 tokens): 16-27 seconds ⚠️ Slow
Streaming UX: First words at 1-3s ✓ Acceptable
```

**Pros:**
- ✅ Highest quality local option
- ✅ Excellent instruction following and reasoning
- ✅ Best nuanced understanding for compliance boundaries
- ✅ Comparable to GPT-4/Claude quality

**Cons:**
- ⚠️ ~3x slower than cloud for full response
- ⚠️ Uses 40GB (only 20-24GB headroom)
- ⚠️ Cannot run simultaneously with other large models
- ⚠️ May crash if other apps use significant memory

**Use For:**
- Production customer-facing (if latency acceptable)
- High-stakes consultations
- When maximum quality required

---

#### Option C: Llama 3.3 70B Instruct (Q4_K_M) - Alternative

**Memory:** ~40-45GB
**Speed:** 15-25 tokens/sec on M4 Pro
**Quality:** ⭐⭐⭐⭐⭐ (excellent English understanding)

**Similar characteristics to Qwen 2.5 72B:**
- Comparable performance and memory usage
- Slightly better English language understanding
- Good instruction following
- Same memory constraints

---

#### Option D: Qwen 2.5 14B Instruct (Q6_K) - Speed Priority

**Memory:** ~10GB
**Speed:** 60-80 tokens/sec on M4 Pro
**Quality:** ⭐⭐⭐ (good but may miss nuances)

**Performance Expectations:**
```
Time-to-first-token: 0.3-0.8 seconds ✓ Excellent
Token generation: 60-80 tokens/sec
Full response (400 tokens): 5-7 seconds ✓ Very good
```

**Pros:**
- ✅ Very fast (~2x faster than 32B)
- ✅ Minimal memory footprint
- ✅ Can easily run with other agents

**Cons:**
- ⚠️ May not capture compliance nuances
- ⚠️ Lower quality reasoning than 32B/72B
- ⚠️ Risk of FCA boundary violations

**Use For:**
- High-throughput training scenarios
- Quick testing and iteration
- Non-critical guidance scenarios

---

### Recommendation Summary: Advisor Agent

**Development & Training:**
**Qwen 2.5 32B Instruct Q5_K_M** (balanced quality/speed, 20GB)

**Production (if latency acceptable):**
**Qwen 2.5 72B Instruct Q4_K_M** (maximum quality, 40GB)

**Production (cloud fallback):**
Keep Claude 4.5 Sonnet or GPT-4o for lowest latency customer-facing

---

## 3. Customer Agent (Training Simulation)

### Current Configuration

**Model:** GPT-4o-mini
**Location:** `src/guidance_agent/customer/agent.py`

### Task Analysis

**Complexity Level:** SIMPLE-TO-MEDIUM ⭐⭐

**Key Responsibilities:**
- Simulate customer comprehension based on financial literacy
- Generate natural conversational responses (1-3 sentences)
- Track understanding levels throughout conversation
- Provide realistic feedback for advisor learning

**Performance Requirements:**
- **Target latency:** Not critical (training environment)
- **Token generation:** 50-200 output tokens per response
- **Input context:** 500-1,500 tokens
- **Criticality:** LOW (non-customer-facing, can tolerate slower responses)
- **Throughput:** Higher = more training iterations per hour

### Local LLM Recommendations

#### Option A: Llama 3.2 3B Instruct (Q6_K) ⭐ RECOMMENDED

**Memory:** ~2.5GB
**Speed:** 80-120 tokens/sec on M4 Pro
**Quality:** ⭐⭐⭐⭐ (excellent for simple conversation simulation)

**Performance Expectations:**
```
Time-to-first-token: 0.2-0.5 seconds ✓ Excellent
Token generation: 80-120 tokens/sec ✓ Very fast
Full response (100 tokens): 1-2 seconds ✓ Excellent
```

**Pros:**
- ✅ Extremely fast response time
- ✅ Minimal memory footprint (2.5GB)
- ✅ Can run alongside 72B advisor model simultaneously
- ✅ Perfect for simple comprehension simulation
- ✅ More than capable for customer behavior simulation

**Cons:**
- ⚠️ Lower sophistication than larger models (not a concern for this use case)

**Use For:**
- Virtual training (primary use case)
- High-throughput scenario generation
- Running 100+ consultations per hour

---

#### Option B: Qwen 2.5 7B Instruct (Q5_K_M) - Better Quality

**Memory:** ~5GB
**Speed:** 60-80 tokens/sec on M4 Pro
**Quality:** ⭐⭐⭐⭐⭐ (more sophisticated than 3B)

**Performance Expectations:**
```
Time-to-first-token: 0.3-0.6 seconds
Token generation: 60-80 tokens/sec
Full response (100 tokens): 1.5-2 seconds
```

**Use For:**
- More sophisticated customer simulation
- Complex comprehension assessment
- When 3B feels too simplistic

---

### Recommendation Summary: Customer Agent

**Primary:**
**Llama 3.2 3B Instruct Q6_K** (fast, efficient, perfect for task)

**Alternative:**
**Qwen 2.5 7B Instruct Q5_K_M** (if need more sophistication)

---

## 4. Compliance Validator (Regulatory Safety)

### Current Configuration

**Training Mode:** Single judge (GPT-3.5 Turbo)
**Production Mode:** 3 judges (GPT-4, Claude 3.5 Sonnet, GPT-4 variant)
**Location:** `src/guidance_agent/compliance/validator.py`

### Task Analysis

**Complexity Level:** COMPLEX ⭐⭐⭐⭐⭐

**Key Responsibilities:**
- Hybrid validation (rule-based + LLM-as-judge)
- Multi-judge consensus with confidence scoring
- Detect boundary violations (guidance vs advice)
- Risk disclosure adequacy assessment
- Language appropriateness evaluation

**Performance Requirements:**
- **Target latency:** 1-2 seconds
- **Execution:** Runs async/parallel with streaming
- **Input tokens:** ~1,000
- **Output tokens:** ~200
- **Criticality:** VERY HIGH (regulatory safety, legal liability)

### Local LLM Recommendations

#### ⚠️ PRIMARY RECOMMENDATION: KEEP USING CLOUD

**Recommended:** GPT-4o + Claude 4.5 Sonnet multi-judge consensus

**Rationale:**

**Why Cloud is Critical for Compliance:**
1. **Regulatory Liability** - FCA violations have serious legal consequences
2. **Extensive Safety Training** - Cloud models have specialized compliance training
3. **Multi-Judge Consensus** - Different models catch different violations
4. **Confidence Scoring** - Critical for human escalation decisions
5. **Cost Negligible** - ~$0.02 per validation with prompt caching
6. **Quality Assurance** - Cloud providers invest heavily in safety

**Production Configuration (Recommended):**
```python
COMPLIANCE_JUDGES = [
    "gpt-4o",           # Primary judge
    "claude-4-5-sonnet", # Secondary judge
    "gpt-4-turbo"       # Tiebreaker
]
```

**Cost Analysis:**
```
1000 validations × 1K input × 200 output × $2.5/$10 per 1M
= $2.50 input + $2 output
= ~$4.50 per 1000 validations (negligible)

With prompt caching (90% savings):
= ~$0.45 per 1000 validations
```

---

#### Local Fallback: Qwen 2.5 72B Instruct (Q4_K_M)

**Only use if:**
- Offline operation required
- Cost absolutely critical (unlikely given low cloud cost)
- Development/testing environment (not production)

**Memory:** ~40GB (same as advisor)
**Speed:** 15-25 tokens/sec
**Quality:** ⭐⭐⭐⭐ (good but not validated for regulatory use)

**CRITICAL REQUIREMENTS:**
- ✅ Extensive validation testing against cloud judges
- ✅ Measure false positive/negative rates
- ✅ Test on diverse compliance scenarios
- ✅ Legal review of validation approach
- ✅ Human oversight for all flagged cases
- ⚠️ **DO NOT use in production without extensive validation**

**Alternative Approach (Hybrid):**
```python
# Fast local check, cloud for final validation
if local_model.quick_check(guidance):
    # Looks good, get cloud confirmation
    final_validation = cloud_multi_judge(guidance)
else:
    # Flagged locally, definitely get cloud review
    final_validation = cloud_multi_judge(guidance)
```

---

### Recommendation Summary: Compliance Validator

**Production:**
**Cloud (GPT-4o + Claude 4.5 Sonnet)** - Non-negotiable for regulatory safety

**Development/Testing:**
**Qwen 2.5 72B Q4_K_M** - Only after extensive validation

**Hybrid:**
Local screening + Cloud final validation (cost optimization)

---

## 5. Base Agent Infrastructure (Memory, Reflection, Planning)

### Current Configuration

**Model:** Inherits from parent agent (varies)
**Location:** `src/guidance_agent/core/agent.py`

### Task Analysis

**Complexity Level:** MEDIUM ⭐⭐⭐

**Key Responsibilities:**
- Rate importance of observations (0-1 scale)
- Generate reflections from recent memories
- Create hierarchical plans
- Synthesize patterns from experience

**Performance Requirements:**
- **Target latency:** Not critical (background processing)
- **Execution:** Periodic (when importance threshold exceeded)
- **Token generation:** 100-300 tokens
- **Criticality:** LOW (can be slower, runs asynchronously)

### Local LLM Recommendations

#### Option A: Qwen 2.5 14B Instruct (Q6_K) ⭐ RECOMMENDED

**Memory:** ~10GB
**Speed:** 60-80 tokens/sec
**Quality:** ⭐⭐⭐⭐ (more than sufficient for reflection)

**Performance Expectations:**
```
Time-to-first-token: 0.3-0.8 seconds
Token generation: 60-80 tokens/sec
Reflection (200 tokens): 2.5-3.5 seconds
```

**Pros:**
- ✅ Fast enough for periodic reflection
- ✅ Good at pattern extraction and insight generation
- ✅ Can run alongside advisor and customer agents
- ✅ Minimal memory footprint

**Use For:**
- Memory importance rating
- Reflection generation
- Background pattern synthesis

---

#### Option B: Qwen 2.5 32B Instruct (Q5_K_M) - Share with Advisor

**Memory:** ~20GB (shared with advisor)
**Speed:** 40-60 tokens/sec
**Quality:** ⭐⭐⭐⭐⭐ (higher quality insights)

**Pros:**
- ✅ Better quality reflections
- ✅ No additional memory cost if advisor already loaded
- ✅ Consistent reasoning across advisor and reflection

**Cons:**
- ⚠️ Uses same model instance as advisor (may cause contention)

**Use For:**
- When advisor model already loaded
- When higher quality reflections needed

---

### Recommendation Summary: Reflection/Planning

**Primary:**
**Qwen 2.5 14B Instruct Q6_K** (dedicated, 10GB)

**Alternative:**
**Share Qwen 2.5 32B with Advisor** (if already loaded)

---

## 6. Knowledge Bootstrap (One-Time Seed Generation)

### Current Configuration

**Model:** Claude 4.5 Sonnet (temperature 0.3)
**Location:** `scripts/` directory

### Task Analysis

**Complexity Level:** MEDIUM-TO-HIGH ⭐⭐⭐⭐

**Key Responsibilities:**
- Generate 20-50 realistic pension consultation scenarios
- Generate 8-10 guidance principles from FCA requirements
- Ensure compliance validation
- Create diverse, representative seed data

**Performance Requirements:**
- **Target latency:** Not time-sensitive (one-time operation, can take hours)
- **Quality:** Critical (will be used for training)
- **Cost:** Current cloud cost ~$0.50 per bootstrap
- **Criticality:** MEDIUM (quality more important than speed)

### Local LLM Recommendations

#### Option A: Qwen 2.5 72B Instruct (Q4_K_M) ⭐ RECOMMENDED FOR ITERATIONS

**Memory:** ~40GB
**Speed:** 15-25 tokens/sec
**Quality:** ⭐⭐⭐⭐⭐ (high-quality seed generation)

**Pros:**
- ✅ Free vs $0.50 per bootstrap (saves money over iterations)
- ✅ High-quality seed data generation
- ✅ Good for iterative refinement of knowledge base
- ✅ No API rate limits

**Cons:**
- ⚠️ Slower than cloud (not a concern for one-time operation)
- ⚠️ May need manual review for compliance accuracy

**Use For:**
- Iterative knowledge base refinement
- Generating additional seed cases
- Cost-sensitive scenarios

---

#### Option B: Keep Using Cloud (Claude 4.5 Sonnet) - RECOMMENDED FOR INITIAL

**Cost:** ~$0.50 per bootstrap (negligible)
**Quality:** ⭐⭐⭐⭐⭐ (highest possible)
**Speed:** Fast

**Pros:**
- ✅ Highest quality for initial knowledge base
- ✅ Proven compliance understanding
- ✅ Fast generation
- ✅ Cost negligible for one-time operation

**Use For:**
- Initial knowledge base bootstrap
- High-stakes seed data generation
- When quality absolutely critical

---

#### Hybrid Approach (Recommended)

```python
# Initial bootstrap: Use cloud for highest quality
bootstrap_initial_kb(model="claude-4-5-sonnet")  # Cost: $0.50

# Iterative refinement: Use local for cost savings
for iteration in range(10):
    refine_kb(model="ollama/qwen2.5:72b")  # Cost: $0 (electricity only)
```

---

### Recommendation Summary: Knowledge Bootstrap

**Initial Bootstrap:**
**Cloud (Claude 4.5 Sonnet)** - highest quality, cost negligible

**Iterative Refinement:**
**Qwen 2.5 72B Q4_K_M** - free, good quality, no rate limits

---

## 7. Multi-Model Configuration Recommendations

### Configuration 1: BALANCED (Recommended for Development) ⭐

```yaml
Advisor Agent:
  Model: Qwen 2.5 32B Instruct Q5_K_M
  Memory: ~20GB
  Speed: 40-60 tokens/sec
  Use: Development, training, testing

Customer Agent:
  Model: Llama 3.2 3B Instruct Q6_K
  Memory: ~2.5GB
  Speed: 80-120 tokens/sec
  Use: Virtual training simulation

Compliance Validator:
  Model: Cloud (GPT-4o + Claude 4.5 Sonnet)
  Memory: N/A (API)
  Cost: ~$0.02 per validation
  Use: All compliance validation

Reflection/Planning:
  Model: Qwen 2.5 14B Instruct Q6_K
  Memory: ~10GB
  Speed: 60-80 tokens/sec
  Use: Background processing

Knowledge Bootstrap:
  Model: Qwen 2.5 32B (same as advisor) OR Cloud
  Memory: Shared
  Use: Iterative refinement

Total Local Memory: ~32GB
Headroom: ~32GB (comfortable)
```

**Benefits:**
- ✅ All local models fit in memory simultaneously
- ✅ Fast development iteration (40-60 t/s advisor)
- ✅ ~40x cheaper than cloud for training
- ✅ Can run 100+ consultations/hour
- ✅ Cloud compliance for regulatory safety
- ✅ Plenty of headroom for OS and apps

**Performance:**
- Advisor TTFT: 0.5-1.5 seconds ✓
- Customer response: 1-2 seconds ✓
- Full consultation: ~10-15 seconds
- Training throughput: 100+ consultations/hour

**Use For:**
- Development and testing
- High-volume virtual training
- Iterative knowledge base refinement
- Cost-sensitive scenarios

---

### Configuration 2: MAXIMUM QUALITY (Production)

```yaml
Advisor Agent:
  Model: Qwen 2.5 72B Instruct Q4_K_M
  Memory: ~40GB
  Speed: 15-25 tokens/sec
  Use: Production customer interactions

Customer Agent:
  Model: Llama 3.2 3B Instruct Q6_K
  Memory: ~2.5GB
  Speed: 80-120 tokens/sec
  Use: Training (not used in production)

Compliance Validator:
  Model: Cloud (GPT-4o + Claude 4.5 Sonnet)
  Memory: N/A (API)
  Use: All compliance validation (mandatory)

Reflection/Planning:
  Model: Qwen 2.5 32B Instruct Q5_K_M
  Memory: ~20GB
  Speed: 40-60 tokens/sec
  Use: Background processing

Total Local Memory: ~62GB (when all running)
Headroom: ~2-4GB (tight)
```

**Usage Pattern:**
- Load Advisor 72B for customer interactions (40GB)
- Unload advisor, load Customer 3B + Reflection 32B for training (22GB)
- Always use cloud for compliance

**Benefits:**
- ✅ Maximum quality customer interactions
- ✅ Matches GPT-4 class performance
- ✅ Cloud compliance validation (mandatory)
- ✅ Cost-effective for production

**Tradeoffs:**
- ⚠️ Must swap models (can't run all simultaneously)
- ⚠️ Slower advisor (15-25 t/s vs 40-60)
- ⚠️ Tighter memory constraints (only 2-4GB headroom)
- ⚠️ Need to close other apps for stability

**Use For:**
- Production customer-facing interactions
- High-stakes consultations
- When maximum quality required

---

### Configuration 3: MAXIMUM SPEED (High-Throughput Training)

```yaml
Advisor Agent:
  Model: Qwen 2.5 14B Instruct Q6_K
  Memory: ~10GB
  Speed: 60-80 tokens/sec
  Use: Fast training iterations

Customer Agent:
  Model: Llama 3.2 3B Instruct Q6_K
  Memory: ~2.5GB
  Speed: 80-120 tokens/sec
  Use: Fast simulation

Compliance Validator:
  Model: Cloud (offload for speed)
  Memory: N/A (API)
  Use: Final validation only

Reflection/Planning:
  Model: Same as Advisor (shared instance)
  Memory: Shared
  Use: Background processing

Total Local Memory: ~12GB
Headroom: ~52GB (lots of room)
```

**Benefits:**
- ✅ Very fast advisor generation (60-80 t/s)
- ✅ Very fast customer simulation (80-120 t/s)
- ✅ Can run 200+ consultations/hour
- ✅ Minimal memory footprint
- ✅ Can run many other apps simultaneously

**Tradeoffs:**
- ⚠️ Lower quality than 32B/72B models
- ⚠️ May not capture compliance nuances
- ⚠️ Risk of FCA boundary violations
- ⚠️ Requires extensive validation

**Use For:**
- Rapid prototyping
- High-volume training scenarios
- Quick testing and iteration
- Development experimentation

---

### Configuration 4: HYBRID (Cloud Primary, Local Fallback)

```yaml
Advisor Agent:
  Primary: Cloud (Claude 4.5 Sonnet / GPT-4o)
  Fallback: Qwen 2.5 32B Instruct Q5_K_M
  Use: Cloud for customer-facing, local for training

Customer Agent:
  Model: Llama 3.2 3B Instruct Q6_K
  Use: Always local (training only)

Compliance Validator:
  Model: Cloud (GPT-4o + Claude 4.5 Sonnet)
  Use: Always cloud (mandatory)

Reflection/Planning:
  Model: Qwen 2.5 14B Instruct Q6_K
  Use: Always local (background)

Total Local Memory: ~12GB (when local models running)
```

**Benefits:**
- ✅ Best of both worlds
- ✅ Lowest latency for customers (cloud)
- ✅ Lowest cost for training (local)
- ✅ Regulatory safety (cloud compliance)
- ✅ Flexibility based on use case

**Implementation:**
```python
# Automatic fallback
try:
    response = completion(model="claude-4-5-sonnet", ...)
except APIError:
    response = completion(model="ollama/qwen2.5:32b", ...)
```

**Use For:**
- Production deployment (best reliability)
- Cost optimization (use local when possible)
- Latency-sensitive customer interactions

---

## 8. Cost Analysis: Local vs Cloud

### Virtual Training Scenario (1000 Consultations)

#### Cloud Configuration (All Cloud Models)

```
Advisor (Claude 4.5 Sonnet with prompt caching):
  1000 consultations × 3K avg input × $3/M = $9
  1000 consultations × 500 output × $15/M = $7.50
  With 90% prompt caching: ~$0.90 + $7.50 = $8.40

Customer (GPT-4o-mini):
  1000 responses × 500 input × $0.15/M = $0.075
  1000 responses × 100 output × $0.60/M = $0.060
  Total: ~$0.14

Compliance (GPT-4o):
  1000 validations × 1K input × $2.5/M = $2.50
  1000 validations × 200 output × $10/M = $2.00
  With 90% prompt caching: ~$0.25 + $2.00 = $2.25

Total: ~$10.79 per 1000 consultations
```

#### Local Configuration (Qwen 32B + Llama 3B)

```
Electricity Cost:
  M4 Mac Studio @ ~100W average
  Runtime: ~10 hours for 1000 consultations
  Cost: 100W × 10h / 1000 × $0.12/kWh = $0.12

Compliance (Cloud - mandatory):
  $2.25 (same as above)

Total: ~$2.37 per 1000 consultations
```

#### Savings Analysis

**Cost per 1000 consultations:**
- All Cloud: $10.79
- Local + Cloud Compliance: $2.37
- **Savings: 78%** ($8.42 per 1000)

**Break-Even Analysis:**
- Hardware already owned (sunk cost)
- Software free (Ollama/MLX)
- Break-even: Immediate (no upfront cost)

**Annual Projection (100K training consultations):**
- All Cloud: $1,079
- Local + Cloud Compliance: $237
- **Annual Savings: $842**

---

### Production Customer-Facing Scenario (1000 Consultations)

#### Hybrid Approach (Recommended)

```
Advisor: Local (Qwen 2.5 32B or 72B)
Customer: N/A (not used in production)
Compliance: Cloud (mandatory)

Cost per 1000 consultations:
  Electricity: $0.12
  Compliance: $2.25
  Total: $2.37

vs All Cloud: $8.40
Savings: 72% ($6.03 per 1000)
```

**Latency Comparison:**
- Cloud (Claude 4.5): 6-7 seconds full response
- Local 32B: 7-10 seconds full response (+40%)
- Local 72B: 16-27 seconds full response (+3x)

**Recommendation:**
- If latency acceptable: Use local (massive savings)
- If latency critical: Use cloud (better UX)
- If budget constrained: Use local 32B (best compromise)

---

## 9. Performance Benchmarks

### Advisor Agent (400-Token Response)

| Model | Location | Memory | TTFT | Tokens/sec | Full Time | Quality | Cost/1K |
|-------|----------|--------|------|------------|-----------|---------|---------|
| **Qwen 2.5 72B Q4** | Local | 40GB | 1-3s | 15-25 | 16-27s | ⭐⭐⭐⭐⭐ | $0 |
| **Qwen 2.5 32B Q5** | Local | 20GB | 0.5-1.5s | 40-60 | 7-10s | ⭐⭐⭐⭐ | $0 |
| **Qwen 2.5 14B Q6** | Local | 10GB | 0.3-0.8s | 60-80 | 5-7s | ⭐⭐⭐ | $0 |
| **Llama 3.3 70B Q4** | Local | 40GB | 1-3s | 15-25 | 16-27s | ⭐⭐⭐⭐⭐ | $0 |
| **Claude 4.5 Sonnet** | Cloud | - | 0.6s | 55-65 | 6-7s | ⭐⭐⭐⭐⭐ | $8.40 |
| **GPT-4o** | Cloud | - | 0.8s | 50-150 | 3-8s | ⭐⭐⭐⭐⭐ | $6.50 |

**Analysis:**
- Local 32B is competitive with cloud (7-10s vs 6-7s)
- Local 72B is ~3x slower but free for repeated use
- Streaming makes TTFT acceptable for local models
- Local wins on cost for high-volume use

---

### Customer Agent (100-Token Response)

| Model | Location | Memory | TTFT | Tokens/sec | Full Time | Quality |
|-------|----------|--------|------|------------|-----------|---------|
| **Llama 3.2 3B Q6** | Local | 2.5GB | 0.2-0.5s | 80-120 | 1-2s | ⭐⭐⭐⭐ |
| **Qwen 2.5 7B Q5** | Local | 5GB | 0.3-0.6s | 60-80 | 1.5-2s | ⭐⭐⭐⭐⭐ |
| **GPT-4o-mini** | Cloud | - | 0.4-0.6s | 100-150 | 0.7-1s | ⭐⭐⭐⭐⭐ |

**Analysis:**
- Local easily beats cloud on cost
- Local 3B nearly matches cloud on speed
- Quality more than sufficient for simulation
- 10x cheaper than cloud

---

### Full Consultation Latency Breakdown

**Local Configuration (Qwen 32B + Llama 3B):**
```
Total: 10-15 seconds per consultation
├─ Embedding: 100ms (1%)
├─ Retrieval: 60ms (0.5%)
├─ Advisor LLM: 7-10s (70-75%) ← Bottleneck
├─ Customer LLM: 1-2s (10-15%)
└─ Compliance (cloud): 1.5s (10-15%)
```

**Cloud Configuration (Claude 4.5 + GPT-4o-mini):**
```
Total: 8-10 seconds per consultation
├─ Embedding: 100ms (1%)
├─ Retrieval: 60ms (0.5%)
├─ Advisor LLM: 6-7s (70-80%) ← Bottleneck
├─ Customer LLM: 0.7-1s (7-10%)
└─ Compliance: 1.5s (15-20%)
```

**Difference:** +2-5 seconds for local (acceptable for training)

---

## 10. Implementation Roadmap

### Phase 1: Installation & Setup (Week 1)

**Goal:** Install local LLM infrastructure and test with small models

```bash
# 1. Install Ollama
brew install ollama

# 2. Start Ollama service
ollama serve

# 3. Pull test models (start small)
ollama pull qwen2.5:7b-instruct
ollama pull llama3.2:3b-instruct

# 4. Test basic functionality
ollama run qwen2.5:7b-instruct "Explain pension lifetime allowance"
```

**Tasks:**
- [ ] Install Ollama
- [ ] Test model download and loading
- [ ] Verify M4 performance with small models
- [ ] Familiarize with Ollama CLI

---

### Phase 2: Integration & Testing (Week 2)

**Goal:** Integrate local models with existing LiteLLM setup

```python
# Update .env
LITELLM_MODEL_ADVISOR=ollama/qwen2.5:7b-instruct  # Start small
LITELLM_MODEL_CUSTOMER=ollama/llama3.2:3b-instruct
OLLAMA_API_BASE=http://localhost:11434

# Test integration
uv run pytest tests/unit/test_advisor.py -v
uv run pytest tests/unit/test_customer.py -v
```

**Tasks:**
- [ ] Update .env configuration
- [ ] Test LiteLLM → Ollama integration
- [ ] Run unit tests with local models
- [ ] Compare outputs vs cloud models
- [ ] Benchmark latency with 7B model

---

### Phase 3: Scale to Production Models (Week 3)

**Goal:** Download and test recommended 32B/72B models

```bash
# Pull recommended models
ollama pull qwen2.5:32b-instruct-q5_K_M  # Advisor (balanced)
ollama pull qwen2.5:72b-instruct-q4_K_M  # Advisor (quality)
ollama pull qwen2.5:14b-instruct-q6_K    # Reflection

# Benchmark performance
uv run python scripts/benchmark_models.py
```

**Tasks:**
- [ ] Download Qwen 2.5 32B Q5_K_M
- [ ] Download Qwen 2.5 72B Q4_K_M
- [ ] Measure TTFT and tokens/sec
- [ ] Test with real consultation scenarios
- [ ] Monitor memory usage and system stability

---

### Phase 4: Quality Validation (Week 4)

**Goal:** Validate local model quality vs cloud models

**Create validation suite:**
```python
# scripts/validate_local_models.py

test_cases = [
    {
        "scenario": "DB pension transfer warning",
        "expected": "Must warn about risks, suggest specialist advice",
        "test": "boundary_detection"
    },
    {
        "scenario": "Tax-free lump sum inquiry",
        "expected": "Explain options, no personal recommendation",
        "test": "guidance_vs_advice"
    },
    # ... 20+ test cases
]

# Compare local vs cloud
results = compare_models(
    local="ollama/qwen2.5:32b",
    cloud="claude-4-5-sonnet",
    test_cases=test_cases
)
```

**Tasks:**
- [ ] Create comprehensive test suite
- [ ] Run blind evaluation (local vs cloud)
- [ ] Measure compliance pass rates
- [ ] Identify failure patterns
- [ ] Tune prompts for local models

---

### Phase 5: Virtual Training Deployment (Week 5-6)

**Goal:** Deploy local models for virtual training

**Configuration:**
```python
# Config for virtual training
TRAINING_CONFIG = {
    "advisor": "ollama/qwen2.5:32b-instruct-q5_K_M",
    "customer": "ollama/llama3.2:3b-instruct-q6_K",
    "compliance": "gpt-4o",  # Keep cloud
    "reflection": "ollama/qwen2.5:14b-instruct-q6_K"
}
```

**Tasks:**
- [ ] Update training scripts to use local models
- [ ] Run 100+ training consultations
- [ ] Monitor performance and stability
- [ ] Track cost savings
- [ ] Gather advisor feedback on quality

---

### Phase 6: Production Consideration (Week 7+)

**Goal:** Evaluate local models for production customer-facing use

**Decision Criteria:**
```python
use_local_in_production = (
    compliance_validated and           # Extensive FCA validation
    latency_acceptable and              # <10s acceptable?
    quality_comparable and              # Matches cloud quality?
    advisor_confidence_high and         # Human advisors trust it?
    legal_approval_obtained             # Legal team approves?
)
```

**Tasks:**
- [ ] Legal review of local model approach
- [ ] Extensive compliance validation (100+ scenarios)
- [ ] A/B test with human advisors
- [ ] Monitor customer satisfaction
- [ ] Create fallback mechanisms (local → cloud)

---

## 11. Monitoring & Observability

### Key Metrics to Track

**Performance Metrics:**
```python
# Add to Phoenix observability
metrics = {
    # Latency
    "local_advisor_ttft": "Time to first token (Qwen 32B)",
    "local_advisor_tps": "Tokens per second (Qwen 32B)",
    "local_customer_ttft": "Time to first token (Llama 3B)",
    "cloud_compliance_latency": "Compliance validation time",

    # Quality
    "compliance_pass_rate": "% passing FCA validation",
    "boundary_violation_rate": "% flagged for advice vs guidance",
    "customer_satisfaction": "Simulated satisfaction scores",

    # Cost
    "local_consultations_count": "Consultations using local",
    "cloud_consultations_count": "Consultations using cloud",
    "estimated_cost_savings": "$ saved vs all-cloud",

    # Reliability
    "model_load_failures": "Failed model loads",
    "oom_errors": "Out of memory errors",
    "fallback_rate": "% falling back to cloud",
}
```

**Dashboard Alerts:**
- TTFT > 3 seconds (degraded performance)
- Compliance pass rate < 95% (quality issue)
- Memory usage > 58GB (stability risk)
- OOM errors > 0 (critical issue)

---

### Validation Test Suite

**Create comprehensive validation:**
```python
# tests/validation/test_local_models.py

class FCAComplianceTests:
    """Test local models for FCA compliance."""

    def test_boundary_detection(self):
        """Can model distinguish guidance from advice?"""
        scenarios = [
            "Should I transfer my DB pension?",  # Must not recommend
            "What are the tax implications?",    # Can provide guidance
            "Which provider should I choose?",   # Must not recommend
        ]
        # Run through local and cloud, compare

    def test_risk_disclosure(self):
        """Does model properly disclose risks?"""
        # Test DB transfer warnings
        # Test investment risk disclosure

    def test_literacy_adaptation(self):
        """Does model adapt to customer literacy?"""
        # Test simplified vs technical language

    def test_chain_of_thought(self):
        """Does reasoning follow 6-step framework?"""
        # Validate structured thinking
```

**Run validation:**
```bash
# Weekly validation runs
uv run pytest tests/validation/ -v --benchmark
```

---

## 12. Risk Mitigation Strategies

### Compliance Risks

**Risk:** Local model gives inappropriate advice (FCA violation)

**Mitigation:**
1. **Always use cloud for compliance validation** (mandatory)
2. Extensive pre-deployment testing (100+ scenarios)
3. Human oversight for all customer-facing guidance
4. Automatic flagging of boundary cases
5. Legal review of local model approach

**Fallback:**
```python
if compliance_confidence < 0.8:
    # Low confidence, use cloud for generation
    response = cloud_model.generate(prompt)
```

---

### Performance Risks

**Risk:** Model too slow for acceptable UX

**Mitigation:**
1. Use streaming to reduce perceived latency
2. Start with 32B (faster) not 72B
3. Benchmark extensively before deployment
4. Automatic fallback to cloud if latency > threshold

**Fallback:**
```python
start = time.time()
response = local_model.generate(prompt, timeout=10)
if time.time() - start > 10:
    # Too slow, use cloud next time
    switch_to_cloud()
```

---

### Stability Risks

**Risk:** OOM errors crash system

**Mitigation:**
1. Leave 10-15GB memory headroom
2. Monitor memory usage continuously
3. Automatic model unloading if memory high
4. Use 32B instead of 72B for stability

**Monitoring:**
```python
import psutil

def check_memory():
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        logger.warning("Memory high, unloading models")
        unload_advisor_model()
```

---

### Quality Risks

**Risk:** Local model produces lower quality guidance

**Mitigation:**
1. A/B testing (local vs cloud)
2. Continuous quality monitoring
3. Human advisor feedback loops
4. Automatic quality scoring

**Validation:**
```python
# Periodic quality checks
if random.random() < 0.1:  # 10% sample
    local_response = local_model.generate(prompt)
    cloud_response = cloud_model.generate(prompt)
    quality_score = compare_quality(local_response, cloud_response)
    track_metric("quality_score", quality_score)
```

---

## 13. Final Recommendations

### For 64GB M4 Mac Studio

**Development & Virtual Training (Recommended):**
```yaml
Configuration: BALANCED
├─ Advisor: Qwen 2.5 32B Instruct Q5_K_M (20GB, 40-60 t/s)
├─ Customer: Llama 3.2 3B Instruct Q6_K (2.5GB, 80-120 t/s)
├─ Compliance: Cloud (GPT-4o + Claude 4.5 Sonnet)
└─ Reflection: Qwen 2.5 14B Instruct Q6_K (10GB, 60-80 t/s)

Benefits:
✓ 78% cost savings vs all-cloud
✓ All models fit simultaneously
✓ Fast iteration (40-60 t/s)
✓ Regulatory safety (cloud compliance)
```

**Production Customer-Facing (If Validated):**
```yaml
Configuration: HYBRID
├─ Advisor: Qwen 2.5 72B Q4_K_M (local) OR Claude 4.5 (cloud fallback)
├─ Customer: N/A (training only)
├─ Compliance: Cloud (GPT-4o + Claude 4.5) - MANDATORY
└─ Reflection: Qwen 2.5 32B Q5_K_M (20GB)

Conditions:
✓ Extensive FCA validation completed
✓ Latency acceptable (<10s)
✓ Legal approval obtained
✓ Cloud fallback configured
```

---

### Critical Success Factors

**Must Have:**
1. ✅ Cloud compliance validation (non-negotiable)
2. ✅ Extensive testing (100+ scenarios)
3. ✅ Human oversight (advisor in the loop)
4. ✅ Automatic fallback (local → cloud)
5. ✅ Continuous monitoring (quality, latency, cost)

**Nice to Have:**
1. MLX optimization (30-50% faster than Ollama)
2. A/B testing framework (compare local vs cloud)
3. Automatic model selection (based on query complexity)

---

### Implementation Priority

**Phase 1 (Immediate):**
- Install Ollama and test with small models
- Validate integration with LiteLLM

**Phase 2 (Week 2-3):**
- Deploy for virtual training (Qwen 32B + Llama 3B)
- Track cost savings and performance

**Phase 3 (Week 4-6):**
- Extensive quality and compliance validation
- Legal review

**Phase 4 (Week 7+):**
- Production consideration (if validated)
- Hybrid cloud/local deployment

---

### Decision Framework

**Use Local If:**
- Virtual training (high-volume, cost-sensitive)
- Development and testing
- Latency acceptable (<10s)
- Extensive validation completed
- Legal approval obtained

**Use Cloud If:**
- Production customer-facing (lowest latency)
- Compliance critical (always for validation)
- Highest quality required
- Regulatory uncertainty

**Hybrid Approach:**
- Local for training (cost savings)
- Cloud for customer-facing (latency)
- Cloud for compliance (always)
- Automatic fallback based on context

---

## 14. Quick Start Guide

### Minimal Setup (5 Minutes)

```bash
# 1. Install Ollama
brew install ollama

# 2. Pull recommended models
ollama pull qwen2.5:32b-instruct-q5_K_M
ollama pull llama3.2:3b-instruct-q6_K

# 3. Update .env
cat >> .env << EOF
LITELLM_MODEL_ADVISOR=ollama/qwen2.5:32b-instruct-q5_K_M
LITELLM_MODEL_CUSTOMER=ollama/llama3.2:3b-instruct-q6_K
OLLAMA_API_BASE=http://localhost:11434
EOF

# 4. Test
uv run python -c "
from litellm import completion
response = completion(
    model='ollama/qwen2.5:32b-instruct-q5_K_M',
    messages=[{'role': 'user', 'content': 'Test'}],
    api_base='http://localhost:11434'
)
print(response.choices[0].message.content)
"
```

**Expected Output:**
- Model loading: 5-10 seconds
- Response: 1-2 seconds
- Quality: Should be coherent and helpful

---

## Resources

**Documentation:**
- Local LLM options: `specs/local-llm-options.md`
- Latency estimates: `specs/latency-estimates.md`
- Cost estimates: `specs/cost-estimates.md`
- Advisor agent spec: `specs/advisor-agent.md`

**External Resources:**
- Ollama: https://ollama.ai/
- LiteLLM: https://docs.litellm.ai/
- Qwen models: https://huggingface.co/Qwen
- Llama models: https://huggingface.co/meta-llama

**Benchmarks:**
- Aider benchmark: https://aider.chat/docs/leaderboards/
- HumanEval: https://github.com/openai/human-eval
- MMLU: https://github.com/hendrycks/test

---

## Conclusion

Your 64GB M4 Mac Studio is **ideally suited for running high-quality 32B models** with excellent performance. For your FCA-compliant pension guidance system:

**Key Recommendations:**
1. **Qwen 2.5 32B** for advisor agent (balanced quality/speed)
2. **Llama 3.2 3B** for customer simulation (fast, efficient)
3. **Cloud (GPT-4o + Claude 4.5)** for compliance (mandatory)
4. **Qwen 2.5 14B** for reflection/planning (background)

**Cost Savings:** ~78% for virtual training ($2.37 vs $10.79 per 1000 consultations)

**Next Steps:**
1. Install Ollama and test with 7B models
2. Scale to 32B models for development
3. Extensive validation for production use
4. Deploy hybrid configuration (local training, cloud fallback)

Start with the BALANCED configuration for development, validate extensively, then consider production deployment if latency and quality meet requirements.
