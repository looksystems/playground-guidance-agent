# Free API Tier Options for LLM Development

**Last Updated:** 2025-11-02
**Target System:** FCA-Compliant Pension Guidance Agent
**Geographic Context:** UK-based deployment
**Related:** See `local-llm-options.md` for local model alternatives

## Executive Summary

This document provides comprehensive analysis of free LLM API tiers available in 2025 as alternatives or supplements to paid cloud APIs and local models. The landscape has evolved significantly, with some providers enhancing free offerings while others have scaled back.

**Key Findings:**
- **Google Gemini** offers the most generous free tier BUT is **blocked in UK/EEA/Switzerland**
- **Groq** provides exceptional speed (400+ tokens/sec) with 500K tokens/day and **no geographic restrictions**
- **Cerebras** offers 1M tokens/day with extreme speed (2,500+ tokens/sec)
- **DeepSeek R1** provides 1M free tokens upon signup, then ultra-cheap paid tier ($6/month for 100K users)
- **Together AI** eliminated free tier (August 2025)
- **OpenRouter** reduced free tier by 75% (now 50 requests/day)

**Critical for UK Pension System:**
- ❌ Cannot use Gemini free tier (geo-blocked)
- ✅ Groq is best free option (500K tokens/day, UK-accessible)
- ⚠️ Free tiers only for development/testing, not production (GDPR compliance)

**Cost Savings:** ~$200-300 in development phase using free tiers

---

## Table of Contents

1. [Tier 1 Recommendations](#tier-1-recommendations)
2. [Tier 2 Options](#tier-2-options)
3. [Providers No Longer Free](#providers-no-longer-free)
4. [UK-Specific Constraints](#uk-specific-constraints)
5. [GDPR & Data Privacy](#gdpr--data-privacy)
6. [Cost Analysis](#cost-analysis)
7. [Integration Guide](#integration-guide)
8. [Comparison Tables](#comparison-tables)
9. [Use Case Mapping](#use-case-mapping)
10. [Action Plan](#action-plan)

---

## Tier 1 Recommendations

### 1. Google Gemini (Best Overall - BUT UK BLOCKED)

#### Free Tier Details

**Gemini 2.5 Pro (Premium Reasoning)**
- **Requests:** 5 RPM, 25-100 requests/day (conservative: 25/day)
- **Tokens:** 250,000 tokens/minute
- **Context Window:** 1 million tokens
- **Best for:** Complex reasoning, compliance validation

**Gemini 2.5 Flash (Balanced)**
- **Requests:** 10 RPM, 250 requests/day
- **Tokens:** 250,000 tokens/minute
- **Context Window:** 1 million tokens
- **Best for:** General-purpose development and testing

**Gemini 2.5 Flash-Lite (High Throughput)**
- **Requests:** 15 RPM, 1,000 requests/day
- **Tokens:** 250,000 tokens/minute
- **Context Window:** 1 million tokens
- **Best for:** High-volume testing, rapid prototyping

**Google AI Studio Access**
- **Requests:** 15 RPM, up to 1 million requests/day (extremely generous)
- **All Gemini models** available
- **Best free tier offering** in the market (if accessible)

#### Quality & Performance

**Benchmarks:**
- Higher performance scores than GPT-4o on many tasks
- **250+ tokens/second** vs GPT-4o's 131 tokens/second
- **0.25-second time-to-first-token** (excellent for real-time)
- **Context window:** 1M tokens vs GPT-4o's 128K
- **Cost:** ~25x cheaper than GPT-4o when paid

**Strengths:**
- Ultra-low-latency responses
- Superior for financial/analytical workloads
- Excellent reasoning with 2.5 Pro
- Multimodal capabilities (voice, video)

**Weaknesses:**
- Geographic restrictions (see below)
- Multimodal understanding less nuanced than GPT-4o for complex media

#### Rate Limits & Throttling

- **Reset time:** Midnight Pacific Time daily
- **Throttling:** 429 status code when exceeded
- **Per-minute enforcement:** Strict limits in addition to daily caps
- **Monitoring:** Track usage to avoid hitting limits

#### Commercial Use & Restrictions

**Commercial Use:**
- ✅ Allowed on free tier
- ⚠️ Rate limits make it impractical for production at scale
- **Recommended:** Prototyping, development, testing only

**⚠️ CRITICAL GEOGRAPHIC RESTRICTIONS:**
- **BLOCKED:** European Economic Area, Switzerland, **United Kingdom**
- **Reason:** EU AI Act and GDPR compliance requirements
- **UK Impact:** Free tier completely unavailable - **must use paid Vertex AI**
- **Implication:** UK pension system **cannot use Gemini free tier**

**Data Privacy:**
- Free tier data **may be used to improve Google models**
- For strict confidentiality: Use paid Vertex AI or negotiate contracts
- **Not recommended** for sensitive pension data on free tier

#### LiteLLM Integration

```python
# Fully supported with native integration
from litellm import completion

# Google AI Studio (free tier - if not UK)
response = completion(
    model="gemini/gemini-2.5-flash",
    messages=[{"role": "user", "content": "Calculate pension..."}]
)

# Vertex AI (paid tier - UK-compatible)
response = completion(
    model="vertex_ai/gemini-2.5-flash",
    messages=[{"role": "user", "content": "Calculate pension..."}]
)
```

**Features:**
- ✅ Prompt caching cost calculation
- ✅ Streaming and non-streaming responses
- ✅ September 2025 models with latest pricing
- ✅ Both AI Studio and Vertex AI endpoints

#### Sustainability & Future Outlook

**Long-term viability:** ⭐⭐⭐⭐⭐ **Very Strong**
- Google committed to developer ecosystem
- Free tier drives Vertex AI paid conversions
- Expected gradual 10% reduction post-Q4 2025
- Trend toward larger context windows, improved capabilities

**Recommendation confidence:** **High** - unlikely to eliminate free tier

**UK Impact:** Must plan for paid Vertex AI from start

---

### 2. Groq (Best for Speed + UK Access)

#### Free Tier Details

**Token Limits:**
- **500,000 tokens per day** (confirmed)
- **No credit card required** for free tier
- **Daily reset:** Not specified in documentation

**⚠️ Important:** Some users report unexpected billing charges despite free tier - monitor usage carefully

#### Available Models (2025)

**Meta LLaMA Series:**
- **Llama 3.3 70B** - Latest, excellent quality
- **Llama 3 70B** - 284 tokens/sec
- **Llama 3 8B** - 876 tokens/sec
- **DeepSeek R1 Distill Llama 70B** - Advanced reasoning

**Qwen Series:**
- **Qwen 2.5 32B**
- **Qwen 2.5 Coder 32B** - Coding-focused
- **Qwen QWQ 32B** - Question answering

**Other Models:**
- **Mixtral 8x7B** - 420 tokens/sec
- **Gemma 7B** - 814 tokens/sec
- **Whisper Large v3** - Audio transcription

#### Speed & Performance - EXCEPTIONAL

**LPU Benchmarks (Language Processing Unit):**

| Model | Groq Speed | Industry Avg | Speedup |
|-------|------------|--------------|---------|
| Llama 3 70B | 284 tokens/sec | 30-60 tokens/sec | **5-9x faster** |
| Llama 3 8B | 876 tokens/sec | ~100 tokens/sec | **8-9x faster** |
| Gemma 7B | 814 tokens/sec | ~100 tokens/sec | **8x faster** |
| Mixtral 8x7B | 420 tokens/sec | ~60 tokens/sec | **7x faster** |

**Independent Verification:**
- ArtificialAnalysis.ai confirmed 241+ tokens/sec
- **18x faster** output throughput vs other cloud providers
- More than **double** the speed of next-fastest provider

**Use Case Fit:**
- ✅ **Ideal for:** Real-time pension guidance conversations
- ✅ **Ideal for:** Rapid batch processing of pension queries
- ✅ **Ideal for:** Development with instant feedback loops
- ✅ **Ideal for:** CI/CD pipelines requiring fast testing

#### Rate Limits

**Documented limits:**
- Primary constraint: 500K tokens/day
- Based on token consumption, not just request count
- Free tier has lower limits than Developer/Enterprise tiers
- Specific per-minute limits not publicly documented

**Recommended monitoring:**
- Track daily token usage
- Implement fallback to other providers
- Monitor for 429 (rate limit) errors

#### Quality

**Model Quality:**
- Uses **open-source models** (Llama, Mixtral, Qwen)
- Quality depends on underlying model selection
- **Llama 3.3 70B:** Competitive with GPT-4 for many tasks
- **DeepSeek R1:** 77.9% MMLU (excellent reasoning)
- **Qwen 2.5 Coder 32B:** Excellent for coding tasks

**Comparison:**
- On par with cloud providers for same models
- Speed advantage with no quality compromise
- Good for pension calculations and policy interpretation

#### LiteLLM Integration

```python
from litellm import completion

# Groq provider
response = completion(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Explain pension lifetime allowance"}]
)

# With streaming
response = completion(
    model="groq/qwen-2.5-coder-32b",
    messages=[{"role": "user", "content": "Generate pension calculation code"}],
    stream=True
)
```

**Features:**
- ✅ Fully supported with dedicated provider
- ✅ Fixed streaming ASCII encoding issues (recent update)
- ✅ OpenAI-compatible API format
- ✅ Production deployment guides available

#### Commercial Use & Restrictions

**Commercial Use:**
- ✅ **Allowed** on free tier
- ⚠️ 500K tokens/day **not suitable for high-volume production**
- ✅ **No geographic restrictions** (unlike Gemini)
- **Recommended use:** Development, testing, low-volume production

**Geographic Access:**
- ✅ **UK-accessible** (critical for UK pension system)
- ✅ **EEA-accessible**
- ✅ **Global access** (no restrictions)

#### Reliability & Uptime

**Reported Performance:**
- Generally positive community feedback
- ⚠️ Some billing inconsistencies reported (monitor carefully)
- No published uptime guarantees for free tier
- Fast response times maintained even on free tier

**Recommendations:**
- Implement fallback to other providers
- Monitor for unexpected charges
- Use for development/testing with confidence
- Production use requires careful monitoring

#### Sustainability & Future Outlook

**Confidence:** ⭐⭐⭐⭐ **Medium-High**
- Business model: Upsell to paid tiers
- Free tier drives adoption of LPU technology
- 500K/day is sustainable for experimentation
- **Risk:** May reduce limits if usage spikes significantly

**Recommended approach:** Use confidently for development, plan for paid tier if production needs arise

---

### 3. Cerebras (Fastest Available)

#### Free Tier Details

**Token Limits:**
- **1 million tokens per day** (very generous)
- **Context length:** 8,192 tokens (standard), 128K available on request
- **No credit card required** initially

**Rate Limits:**
- Not publicly specified for free tier
- Developer tier: **10x higher limits** than free
- Max tier: 1.5M tokens per minute (paid)

#### Available Models

**Llama Series:**
- **Llama 3.1 8B** - Fast, efficient
- **Llama 3.1 70B** - High quality
- **Llama 3.3 70B** - Latest (if available)

**Focus:**
- Speed optimization over model variety
- Standard Llama models with extreme acceleration

#### Performance - FASTEST AVAILABLE

**Speed Benchmarks:**

| Model | Cerebras Speed | Industry Avg | Speedup |
|-------|----------------|--------------|---------|
| Llama 3.1 8B | **1,800 tokens/sec** | 90 tokens/sec | **20x faster** |
| Llama 3.1 70B | **450 tokens/sec** | 25 tokens/sec | **18x faster** |
| General | **2,500+ tokens/sec** | 100 tokens/sec | **25x faster** |

**Key Advantages:**
- **Eliminates lag** for real-time applications
- **Instant responses** for development iteration
- **Rapid batch processing** (1M tokens in minutes)
- **CI/CD optimization** - run 100s of tests quickly

**Use Case Fit:**
- ✅ Ultra-fast prototyping
- ✅ Performance benchmarking
- ✅ CI/CD test suites
- ✅ Batch processing pension calculations
- ✅ Real-time conversational interfaces

#### Quality

**Model Quality:**
- Uses standard Llama models (quality depends on model version)
- **Speed does not compromise output quality**
- Same models as other providers, just faster inference
- Good for structured tasks (calculations, analysis)

**Comparison:**
- Quality identical to Llama on other platforms
- Speed advantage with zero quality tradeoff

#### LiteLLM Integration

```python
# Cerebras support via compatible APIs
response = completion(
    model="cerebras/llama-3.1-70b",
    messages=[{"role": "user", "content": "Calculate pension projections"}]
)
```

**Features:**
- ✅ OpenAI-compatible API
- ✅ Native support via Vellum and other platforms
- ✅ Pay-per-token model for scaling
- ✅ Streaming support

#### Pricing (Paid Tier)

**When free tier exhausted:**
- Llama 3.1 8B: **$0.10 per million tokens**
- Llama 3.1 70B: **$0.60 per million tokens**
- **10x cheaper** than many alternatives
- Extremely cost-effective scaling path

#### Commercial Use & Restrictions

**Commercial Use:**
- ✅ **Allowed** on free tier
- 1M tokens/day suitable for **substantial development**
- Can support **limited production** use cases
- ✅ **No geographic restrictions**

**Geographic Access:**
- ✅ **UK-accessible**
- ✅ **Global access**

#### Sustainability & Future Outlook

**Confidence:** ⭐⭐⭐⭐⭐ **High**
- Cerebras investing heavily in developer adoption
- Free tier drives awareness of CS-3 chip technology
- 1M tokens/day is sustainable
- Clear path to paid tier for conversions

**Recommended approach:** Use for performance-critical development and testing

---

## Tier 2 Options

### 4. DeepSeek R1 (Excellent Reasoning, Ultra-Cheap Paid Tier)

#### Free Tier Details

**DeepSeek Official API:**
- **~1 million free tokens** upon signup (one-time)
- **$1 credit** included with signup
- **No strict RPM limits** (may slow during peak times)
- **128K context window**

**OpenRouter Access:**
- **50 requests/day** (free tier)
- **1,000 requests/day** (with $10+ credits on file)
- **No token charges** on free tier

**Azure OpenAI:**
- **8 API calls per day** (very limited, not recommended)

#### Performance & Quality

**Benchmarks:**
- **77.9% MMLU score** (excellent reasoning capability)
- **128K context window** (handle long pension documents)
- Competitive with GPT-4 for complex reasoning
- Excellent for policy interpretation and compliance

**Strengths:**
- Leading open-source reasoning model
- Excellent for complex pension analysis
- Good for compliance and policy interpretation
- Strong chain-of-thought capabilities

#### Paid Tier Pricing (Post-Free)

**Extremely affordable:**
- Input: **$0.001 per 1K tokens** ($1 per million)
- Output: **$0.002 per 1K tokens** ($2 per million)
- Cache hits: **$0.14 per 1M tokens** (90% savings)

**Cost examples:**
- 10K users/month (~30M tokens): **$60/month**
- 100K users/month (~300M tokens): **$600/month**
- **2% of OpenAI's inference cost**

#### LiteLLM Integration

```python
# DeepSeek provider
response = completion(
    model="deepseek/deepseek-r1",
    messages=[{"role": "user", "content": "Analyze pension transfer risks"}]
)

# Via OpenRouter
response = completion(
    model="openrouter/deepseek/deepseek-r1:free",
    messages=[{"role": "user", "content": "..."}]
)
```

#### Commercial Use

- ✅ **Allowed** on free and paid tiers
- 1M tokens suitable for **initial development**
- Ultra-cheap paid tier makes production viable
- **No geographic restrictions**

#### Sustainability

**Confidence:** ⭐⭐⭐ **Medium**
- 1M tokens is one-time signup bonus
- Transition to paid tier expected
- **Paid tier so cheap** it's effectively "near-free"
- Consider as "very cheap" rather than "free"

**Recommendation:** Use 1M free tokens for prototyping, then paid tier at $6-60/month

---

### 5. Anthropic Claude (Highest Quality, Limited Free)

#### Free Tier Details

**Initial Credits:**
- **$5 in free credits** for new users (one-time)
- **Phone verification required**
- **No expiration** on credits
- **No credit card required** initially

**What $5 Gets You:**

| Model | Input Tokens | Output Tokens | Use Case |
|-------|--------------|---------------|----------|
| Claude Haiku 3 | 20M | ~7M | High-volume testing |
| Claude Haiku 3.5 | 6.25M | ~2M | Balanced testing |
| Claude Haiku 4.5 | 5M | ~1.6M | Latest Haiku |
| Claude Sonnet 4 | 1.67M | ~555K | High quality |
| Claude Opus 4.1 | 333K | ~111K | Highest quality |
| Claude 3.5 Sonnet | 330K | ~110K | Industry-leading |

#### Geographic Limitations

**Phone verification eligibility:**
- ✅ **US phone numbers:** Consistently qualify
- ❌ **UK phone numbers:** Explicitly excluded
- ⚠️ **Other regions:** Variable eligibility

**UK Impact:**
- **UK pension system likely cannot access $5 credit**
- May need to purchase credits from start
- Check eligibility before planning around this option

#### Student Programs

**Academic Access:**
- University students: Apply for **$500+ credits**
- Requires application through Anthropic website
- Enables substantial projects and research
- Good for academic pension research projects

#### Quality & Performance

**Industry-leading:**
- **Highest quality** among free options
- Claude 3.5 Sonnet: Top-tier for many tasks
- Excellent for **compliance and reasoning**
- Strong safety guardrails (good for regulatory work)

**Benchmarks:**
- Outperforms GPT-4 on many reasoning tasks
- Excellent instruction following
- Strong at nuanced policy interpretation
- Good at detecting compliance boundaries

#### LiteLLM Integration

```python
# Fully supported
response = completion(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Validate FCA compliance"}]
)
```

**Features:**
- ✅ Native Anthropic provider
- ✅ All Claude models accessible
- ✅ Streaming support
- ✅ Excellent documentation

#### Commercial Use

- ✅ **Allowed** with API credits
- ⚠️ **Not a sustainable free tier** - one-time $5
- Must plan to purchase credits for ongoing use
- Good for **quality validation** during development

#### Sustainability

**Confidence:** ⭐ **Very Low**
- ❌ **NOT SUSTAINABLE** - one-time credits only
- No ongoing free tier
- Must budget for paid usage after $5 depleted
- UK users may not even get $5 credit

**Recommendation:** Use $5 credit (if accessible) for quality benchmarking, then plan for paid or alternative providers

---

### 6. OpenRouter (Declining, Not Recommended)

#### Free Tier Details - SIGNIFICANT 2025 CHANGES

**⚠️ MAJOR POLICY SHIFT (July 2025):**
- **Previous:** 200 free requests/day
- **Current:** **50 free requests/day** (75% reduction)
- **Enhanced tier:** 1,000 requests/day with $10+ credit purchase

**Rate Limits:**
- **20 requests per minute** for `:free` models
- **50 requests per day** (no credits)
- **1,000 requests per day** (with $10+ credits on file)
- **BYOK (Bring Your Own Key):** 1 million free requests/month

#### Available Free Models

**Access to 300+ models** (as of 2025), including:
- DeepSeek R1 (`:free`)
- Toppy
- Zephyr
- Various open-source models with `:free` suffix

**Important:** Only models ending in `:free` count toward free tier

#### Quality & Performance

**Characteristics:**
- **Model-dependent:** Quality varies by underlying model
- **Latency:** Additional routing overhead vs direct APIs
- **Uptime:** Distributed infrastructure with provider fallback
- **Status page:** Public trust center with incident history

**Strengths:**
- Access to many models in one place
- Good for testing model diversity
- Public status monitoring

**Weaknesses:**
- 50/day limit very restrictive
- Routing adds latency
- Failed attempts count toward quota

#### Integration

**LiteLLM Support:**
```python
# All OpenRouter models supported
response = completion(
    model="openrouter/deepseek/deepseek-r1:free",
    messages=[{"role": "user", "content": "..."}]
)
```

**Features:**
- ✅ All 300+ models supported
- ✅ Format: `openrouter/<model-id>`
- ✅ Recent fixes for Claude 4 max_output_tokens
- ✅ OpenAI-compatible API

#### Reliability & Uptime

**Strengths:**
- ✅ Distributed across multiple providers for better uptime
- ✅ Automatic failover when one provider down
- ✅ Public status page and incident history

**Weaknesses:**
- ⚠️ Free tier rate limiting especially during peak times
- ⚠️ Failed attempts count toward daily quota
- ⚠️ Negative balance blocks even free model access (402 errors)

#### Commercial Use & Restrictions

- ✅ Commercial use allowed
- ⚠️ **Not suitable for production** (50 requests/day)
- ⚠️ Negative balance blocks access
- **Recommended:** Development/testing only, or use BYOK approach

#### Sustainability & Future Outlook

**Confidence:** ⭐⭐ **Low - Declining**
- 75% reduction in free limits (2025)
- Clear trend toward paid model
- Free tier likely to remain but **continue shrinking**
- **Not recommended** for critical development paths

**Recommendation:** Use only as backup or for testing model diversity, not as primary development option

---

### 7. Mistral AI (Free Tier with Undisclosed Limits)

#### Free Tier Details

**La Plateforme Free Tier:**
- ✅ Free tier **exists** for experimentation
- ⚠️ **Specific limits not publicly disclosed**
- View your limits at: `https://admin.mistral.ai/plateforme/limits`
- Designed for **testing, not production**

**Special: Codestral**
- **Almost entirely free** API
- **Very high or no rate limits**
- Excellent for coding applications
- Good for pension calculation code generation

#### Available Models

**Model Range:**
- Mistral Large - Flagship model
- Mistral Medium - Balanced
- Mistral Small - Fast
- Codestral - Coding-focused
- Open-source models (Mixtral, etc.)

#### Quality & Performance

**Characteristics:**
- Competitive with GPT-3.5/4 for many tasks
- Strong European alternative
- Good multilingual capabilities (French, English, etc.)
- GDPR-compliant (EU-based company)

#### Upgrading

**Transition to Paid:**
- ✅ Seamless transition to commercial tier
- ✅ Full data isolation available
- ✅ Zero-retention options for compliance
- ✅ Enterprise contracts available

#### LiteLLM Integration

```python
# Mistral provider
response = completion(
    model="mistral/mistral-large-latest",
    messages=[{"role": "user", "content": "..."}]
)
```

**Features:**
- ✅ Supported via Mistral provider
- ✅ OpenAI-compatible format
- ✅ Streaming support

#### Commercial Use & GDPR

**Free Tier:**
- Experimental use only
- Check limits dashboard for your account

**Commercial Tier:**
- Required for production
- GDPR-compliant (EU-based)
- Data residency options
- Good for UK/EU deployments

#### Sustainability

**Confidence:** ⭐⭐⭐⭐ **Medium-High**
- Mistral committed to developer access
- Free tier drives adoption
- Likely to maintain restrictive but available free tier
- European focus aligns with GDPR needs

**Recommendation:** Good for testing, especially for EU/UK projects needing GDPR compliance

---

### 8. Cohere (Trial Tier)

#### Free Tier Details

**Trial API Key Limits:**
- **1,000 API calls per month** (not token-based)
- **20 RPM** for Chat endpoint
- **100 RPM** for Embed endpoint
- **Important:** Limit is on calls, not tokens

**Token Context:**
- Large context calls count same as small calls
- Can process significant data within 1,000 calls
- Up to 128K tokens per call

#### Available Models

**Model Range:**
- Command R - Balanced performance
- Command R+ - Higher performance
- Embed models - For retrieval systems
- Good for RAG (Retrieval-Augmented Generation) applications

#### Quality & Performance

**Characteristics:**
- Competitive with GPT-3.5/4
- Excellent for **RAG applications**
- Strong embedding models for document retrieval
- Good for pension knowledge base retrieval

**Use Case Fit:**
- ✅ Building pension knowledge retrieval systems
- ✅ Semantic search for pension regulations
- ✅ Context-aware Q&A systems

#### LiteLLM Integration

```python
# Cohere provider
response = completion(
    model="cohere/command-r-plus",
    messages=[{"role": "user", "content": "..."}]
)
```

**Features:**
- ✅ Fully supported
- ✅ Cohere provider in LiteLLM
- ✅ Embed endpoint support

#### Commercial Use

**Trial Tier:**
- **Learning and prototyping only**
- Production requires paid tier
- 1,000 calls/month **not suitable for production**

**Paid Tier:**
- Pay-per-use pricing
- Enterprise options available

#### Sustainability

**Confidence:** ⭐⭐⭐ **Medium**
- Trial tier clearly maintained
- Drives paid conversions
- 1,000 calls/month likely to remain stable
- Good for RAG experimentation

**Recommendation:** Use for RAG/embedding experiments, not primary LLM generation

---

### 9. Hugging Face Inference API (Vague Limits)

#### Free Tier Details

**Rate Limits:**
- **~Few hundred requests per hour** (vague documentation)
- **No specific token limits** published
- **Model-dependent** - varies by size and resource requirements

**Monthly Credits:**
- All users receive **monthly credits** for experimentation
- **20x more credits** with PRO account ($9/month)
- Credits refresh monthly

#### Available Models

**Model Library:**
- **Thousands of models** available
- Focus on **open-source models**
- Text generation, embeddings, classification, etc.
- Community-contributed and official models
- Can deploy custom models

#### Quality & Performance

**Characteristics:**
- **Highly variable** - depends on model selection
- **Serverless:** No guaranteed response times
- Best for **experimentation**, not production
- Some models may have long cold-start times
- Community models may be unstable

#### Integration

**LiteLLM:**
```python
# Hugging Face support
response = completion(
    model="huggingface/<model-name>",
    messages=[{"role": "user", "content": "..."}]
)
```

**Challenges:**
- May require additional configuration
- Not as streamlined as OpenAI-compatible APIs
- Model availability varies

#### Commercial Use

- ✅ Allowed for most models (check individual licenses)
- ⚠️ Rate limits make production use impractical
- Best for **prototyping and experimentation**
- Good for testing custom/fine-tuned models

#### Sustainability

**Confidence:** ⭐⭐⭐ **Medium**
- Core to Hugging Face's business model
- Drives PRO subscriptions
- Likely to remain but with continued vague limits
- Focus on community contributions

**Recommendation:** Use for experimentation with specific models, not production workloads

---

## Providers No Longer Free

### Together AI - ❌ Eliminated Free Tier (August 2025)

**Previous Status:**
- $25 in free credits for new users

**Current Status (August 2025):**
- ❌ **No free credits** for new users
- **Minimum purchase:** $5 required to access platform
- Existing users with <$1 credits need payment method

**Implications:**
- No longer suitable for free development
- Must consider as paid option only
- Removed from recommendations

---

### Fireworks AI - Minimal Free Tier (Not Recommended)

**Free Tier:**
- **$1 in free credits** for new users (minimal)
- Automatically applied
- **Payment method required** after depletion

**Pricing:**
- Pay-as-you-go model
- Token-based billing
- Competitive pricing but minimal free access

**Sustainability:**
- ⭐ **Very Low** - $1 credit is insufficient
- Clearly focused on paid customers
- Not suitable for free development

---

### Perplexity AI - Requires PRO Subscription

**Free Tier:**
- Limited free access on consumer product
- PRO users: **$5 monthly pplx-api credit** (recurring)
- Non-PRO: Usage-based billing
- **Not truly "free"** - requires PRO subscription ($20/month)

**Use Case:**
- Excellent for search-augmented generation
- Real-time web integration
- Good for fact-checking and research

**Recommendation:**
- Not a primary development option
- Consider for specific search-augmented features
- Better alternatives available for general LLM use

---

## UK-Specific Constraints

### Critical Geographic Restrictions

#### Google Gemini - BLOCKED in UK

**Status:**
- ❌ **FREE TIER COMPLETELY BLOCKED** in UK, EEA, Switzerland
- **Reason:** EU AI Act and GDPR compliance requirements
- **Alternative:** Paid Vertex AI available in UK with data residency

**Impact on UK Pension System:**
- **Cannot use Gemini free tier** for UK-based development
- Must budget for paid tier from day one
- Significant constraint given Gemini's otherwise excellent free offering
- Paid Vertex AI pricing: ~$0.075-0.30 per 1M tokens

**Workaround:**
- None for free tier (geo-IP blocking enforced)
- Must use paid Vertex AI for UK compliance
- Consider other free providers (Groq, Cerebras)

---

#### Anthropic Claude - UK Phone Numbers Excluded

**Status:**
- ⚠️ **UK phone numbers explicitly excluded** from $5 free credit
- US phone numbers consistently qualify
- Other regions variable

**Impact:**
- UK developers likely cannot access $5 credit
- Must purchase credits from start
- No free trial for UK-based projects

**Workaround:**
- None - phone verification is mandatory
- Consider purchasing small credit amount ($10-20) for testing
- Use alternative free providers for development

---

### Recommended UK-Compatible Free Tier Strategy

**Primary Providers (UK-Accessible):**

1. **Groq** - 500K tokens/day, 400+ tokens/sec
   - ✅ No geographic restrictions
   - ✅ Excellent speed for development
   - ✅ Good model selection (Llama 3.3 70B, Qwen 2.5, etc.)

2. **Cerebras** - 1M tokens/day, 2,500+ tokens/sec
   - ✅ No geographic restrictions
   - ✅ Fastest inference available
   - ✅ Good for rapid testing

3. **DeepSeek R1** - 1M tokens one-time
   - ✅ No restrictions
   - ✅ Excellent reasoning
   - ✅ Ultra-cheap paid tier ($6/month for production)

**Development Strategy:**
```yaml
Phase 1 (Prototyping):
  Primary: DeepSeek R1 (1M tokens, burn through for initial build)

Phase 2 (Development):
  Primary: Groq (500K tokens/day, real-time feedback)
  Testing: Cerebras (1M tokens/day, batch tests)

Phase 3 (Pre-Production):
  Development: Groq + Cerebras (free tiers)
  Quality validation: DeepSeek R1 paid tier ($6-60/month)

Phase 4 (Production):
  Primary: DeepSeek R1 paid OR Vertex AI paid
  Compliance: Anthropic Claude paid (with enterprise DPA)
  Fallback: Groq free tier (emergency capacity)
```

---

## GDPR & Data Privacy

### Free Tier Data Privacy Concerns

**⚠️ CRITICAL ISSUE FOR PENSION DATA:**

| Provider | Data Usage Policy (Free Tier) | Suitable for Pension Data? |
|----------|-------------------------------|---------------------------|
| Google Gemini | May use to improve models | ❌ **Not recommended** |
| Anthropic Claude | Standard terms, check docs | ⚠️ **Use paid with DPA** |
| OpenAI | Check terms per tier | ⚠️ **Use paid with DPA** |
| Groq | Open-source models, verify | ⚠️ **Check data handling** |
| Cerebras | Check terms | ⚠️ **Verify before use** |
| DeepSeek | Chinese company, check terms | ⚠️ **Data residency concerns** |
| OpenRouter | Varies by provider | ❌ **Complex compliance** |

### GDPR Compliance Requirements (2025)

**Key Requirements:**
1. **Privacy by design** from project start
2. **Data minimization:** Only necessary data processed
3. **Consent management:** Clear user consent mechanisms
4. **Right to erasure:** Can delete user data on request
5. **Data processing agreements (DPAs):** With API providers
6. **EU/UK data residency:** For UK/EU users
7. **Data breach notification:** Within 72 hours

### Free Tier Challenges for GDPR

**Common Issues:**
- ❌ Limited or no DPAs available on free tiers
- ❌ Data may be used for model training
- ❌ No guaranteed data residency
- ❌ Difficult to exercise deletion rights
- ❌ No audit trails or compliance certifications
- ❌ No SLAs or liability guarantees

### Best Practices for Development

**Using Free Tiers Safely:**

1. **Use ONLY synthetic/anonymized data**
   ```python
   # Always anonymize before API calls
   anonymized_data = pension_anonymizer.sanitize(real_data)
   response = completion(model=free_tier_model, messages=anonymized_data)
   ```

2. **Implement data sanitization pipeline**
   - Remove all PII (names, addresses, National Insurance numbers)
   - Replace with synthetic equivalents
   - Hash identifiers consistently
   - Log what data was sent to which provider

3. **Use paid tiers with explicit DPAs for production**
   - Google Vertex AI (GDPR-compliant, UK data residency)
   - Anthropic Claude (enterprise DPA available)
   - Azure OpenAI (comprehensive compliance)

4. **Consider self-hosted models for sensitive processing**
   - Complete control over data
   - No third-party data sharing
   - Higher operational cost but maximum control
   - See `local-llm-options.md` for local model recommendations

### Production GDPR Compliance

**Recommended for UK Pension System:**

**Option 1: Paid Cloud with DPA**
- Google Vertex AI (Gemini) - UK data residency
- Microsoft Azure OpenAI - Comprehensive compliance
- Anthropic Claude - Enterprise contract with DPA
- **Cost:** $450-1,500/month for 10K users

**Option 2: Self-Hosted Models**
- Llama 3.3 70B or Qwen 2.5 72B locally
- Complete data control
- See `local-llm-options.md` and `agent-model-recommendations.md`
- **Cost:** $0 API fees, electricity only

**Option 3: Hybrid Approach**
- Self-hosted for sensitive pension data processing
- Paid cloud with DPA for compliance validation
- Free tiers for development/testing with synthetic data
- **Cost:** $100-500/month for validation, $0 for main processing

### Data Handling Architecture

```python
class GDPRCompliantLLMHandler:
    """Handle LLM calls with GDPR compliance."""

    def __init__(self):
        self.anonymizer = PensionDataAnonymizer()
        self.environments = {
            'development': 'free_tier',  # Synthetic data only
            'staging': 'paid_tier',      # With DPA
            'production': 'paid_tier'    # With DPA + audit
        }

    def prepare_data(self, pension_data, environment):
        """Prepare data based on environment."""
        if environment == 'development':
            # Full anonymization for free tier
            return self.anonymizer.full_anonymize(pension_data)
        else:
            # Minimal sanitization for paid tier with DPA
            return self.anonymizer.minimal_sanitize(pension_data)

    def call_llm(self, data, environment):
        """Call appropriate LLM based on environment."""
        sanitized = self.prepare_data(data, environment)

        # Ensure no PII in free tier calls
        if environment == 'development':
            assert not self.contains_pii(sanitized), "PII detected in dev data!"
            model = "groq/llama-3.3-70b-versatile"  # Free tier
        else:
            model = "vertex_ai/gemini-2.5-flash"  # Paid with DPA

        # Log the call for audit trail
        self.audit_log.record(environment, model, len(sanitized))

        return completion(model=model, messages=sanitized)
```

---

## Cost Analysis

### Development Phase (3 Months)

**Estimated Token Usage:**
- 10 developers × 100K tokens/day × 90 days = **90 million tokens**

**Free Tier Coverage (UK-Compatible):**

| Provider | Daily Capacity | 90-Day Total | Coverage |
|----------|----------------|--------------|----------|
| Groq | 500K tokens/day | 45M tokens | **50%** |
| Cerebras | 1M tokens/day | 90M tokens | **100%** |
| DeepSeek (one-time) | 1M tokens | 1M tokens | **1%** |
| **Combined** | **1.5M/day** | **135M tokens** | **✅ 150%** |

**Result:** Free tiers can cover **100%+ of development needs**

**Cost Comparison:**

| Scenario | Cost |
|----------|------|
| **Free tiers (Groq + Cerebras)** | **$0** |
| Paid Gemini Flash (90M tokens) | $6.75 |
| Paid Claude Sonnet (90M tokens) | $270 |
| Paid GPT-4o (90M tokens) | $225 |

**Savings with free tiers:** $200-270 in development phase

---

### Testing Phase (1 Month)

**Estimated Usage:**
- Functional tests: 10,000 requests
- Compliance tests: 5,000 requests (complex, ~2K tokens each)
- Integration tests: 5,000 requests
- **Total:** ~40 million tokens

**Free Tier Coverage:**

| Provider | Monthly Capacity | Coverage |
|----------|------------------|----------|
| Groq (500K/day × 30) | 15M tokens | **38%** |
| Cerebras (1M/day × 30) | 30M tokens | **75%** |
| **Combined** | **45M tokens** | **✅ 113%** |

**Result:** Free tiers can cover **100%+ of testing needs**

**Cost Comparison:**

| Scenario | Cost |
|----------|------|
| **Free tiers (Groq + Cerebras)** | **$0** |
| Paid Gemini Flash | $3 |
| Paid GPT-4o | $100 |
| Paid Claude Sonnet | $120 |

**Savings:** $100-120

---

### Small Pilot Production (100 Users)

**Monthly Usage:**
- 100 users × 10 queries/day × 30 days = 30,000 queries
- Average 1-2K tokens per query
- **Total:** ~30-60 million tokens/month

**Free Tier Coverage:**

| Provider | Monthly Capacity | Coverage |
|----------|------------------|----------|
| Groq | 15M tokens | **25-50%** |
| Cerebras | 30M tokens | **50-100%** |
| **Combined** | **45M tokens** | **75-150%** |

**Result:** Free tiers can support small pilot

**Cost Comparison (if paid):**

| Provider | Monthly Cost (60M tokens) |
|----------|---------------------------|
| Gemini Flash | **$4.50** |
| DeepSeek R1 | **$120** |
| GPT-4o | **$150** |
| Claude Haiku | **$180** |

**Recommendation:** Use free tiers for pilot, then upgrade to DeepSeek R1 paid ($6-120/month) or Gemini Vertex AI ($4.50-45/month)

---

### Full Production (10,000 Users)

**Monthly Usage:**
- 10,000 users × 10 queries/day × 30 days = 3 million queries
- Average 1-2K tokens per query
- **Total:** ~3-6 billion tokens/month

**Free Tier Coverage:**

| Provider | Monthly Capacity | Coverage |
|----------|------------------|----------|
| Groq | 15M tokens | **0.25-0.5%** |
| Cerebras | 30M tokens | **0.5-1%** |
| **Combined** | **45M tokens** | **<1%** |

**Result:** Free tiers provide **emergency fallback only**, not primary capacity

**Paid Tier Costs (6B tokens/month):**

| Provider | Monthly Cost | Annual Cost |
|----------|--------------|-------------|
| **DeepSeek R1** | **$6,000** | **$72,000** |
| **Gemini Vertex AI** | **$450** | **$5,400** |
| Claude Haiku | $1,500 | $18,000 |
| GPT-4o Mini | $900 | $10,800 |
| GPT-4o | $15,000 | $180,000 |

**Best value:** Gemini Vertex AI ($450/month) or DeepSeek R1 ($6,000/month for 6B tokens)

**Free tier role:** Emergency fallback capacity (45M tokens/month = 7,500-45,000 queries)

---

### Total Cost Summary

**Development to Production (Year 1):**

| Phase | Duration | Free Tier Coverage | Paid Cost (if needed) |
|-------|----------|--------------------|-----------------------|
| Development | 3 months | ✅ 100%+ | $0 (vs $200-270) |
| Testing | 1 month | ✅ 100%+ | $0 (vs $100-120) |
| Pilot (100 users) | 2 months | ✅ 75-150% | $0-10 |
| Production (10K users) | 6 months | ⚠️ <1% | $2,700 (Gemini) |
| **TOTAL** |  | | **$2,700-2,710** |

**Compared to all-paid from start:**
- Gemini paid all phases: $3,000
- GPT-4o paid all phases: $90,000+
- Claude paid all phases: $18,000+

**Savings from free tiers:** $300-370 in development/testing

**Production reality:** Must use paid tier, but free tiers provide:
- ✅ $300-370 development savings
- ✅ Emergency fallback capacity
- ✅ Development/testing environment (ongoing)
- ✅ Load testing overflow capacity

---

## Integration Guide

### Multi-Provider LiteLLM Configuration

#### Development Configuration (UK-Compatible)

```python
# .env file
LITELLM_MODEL_GROQ=groq/llama-3.3-70b-versatile
LITELLM_MODEL_CEREBRAS=cerebras/llama-3.1-70b
LITELLM_MODEL_DEEPSEEK=deepseek/deepseek-r1

# Multi-provider config
DEVELOPMENT_CONFIG = {
    "primary": "groq/llama-3.3-70b-versatile",      # Fast, 500K/day
    "fast_testing": "cerebras/llama-3.1-70b",       # Very fast, 1M/day
    "reasoning": "deepseek/deepseek-r1",            # Complex reasoning
    "fallback": "groq/qwen-2.5-coder-32b",          # Alternative
}
```

#### Production Configuration

```python
# Production with paid tiers + free tier fallback
PRODUCTION_CONFIG = {
    "primary": "vertex_ai/gemini-2.5-flash",        # Paid, GDPR-compliant
    "high_quality": "anthropic/claude-3-5-sonnet",  # Paid, compliance
    "fast": "groq/llama-3.3-70b-versatile",         # Free, emergency
    "cheap": "deepseek/deepseek-r1",                # Paid but ultra-cheap
}
```

#### Task-Based Model Selection

```python
from litellm import completion
import os

class ModelSelector:
    """Select appropriate model based on task and environment."""

    def __init__(self, environment='development'):
        self.environment = environment
        self.daily_limits = {
            'groq': 500_000,
            'cerebras': 1_000_000,
            'deepseek_free': 1_000_000  # One-time
        }
        self.usage_tracker = UsageTracker()

    def select_model(self, task_type, priority='balanced'):
        """Select model based on task and priority."""

        if self.environment == 'production':
            return self._select_production_model(task_type, priority)
        else:
            return self._select_development_model(task_type, priority)

    def _select_development_model(self, task_type, priority):
        """Select from free tiers for development."""

        # Check usage limits
        groq_available = self.usage_tracker.check_limit('groq', self.daily_limits['groq'])
        cerebras_available = self.usage_tracker.check_limit('cerebras', self.daily_limits['cerebras'])

        if task_type == 'simple_query':
            # Use fastest available
            if cerebras_available and priority == 'speed':
                return "cerebras/llama-3.1-8b"
            elif groq_available:
                return "groq/llama-3.3-70b-versatile"
            else:
                return "cerebras/llama-3.1-70b"

        elif task_type == 'compliance_check':
            # Use highest quality available
            if groq_available:
                return "groq/llama-3.3-70b-versatile"
            else:
                return "cerebras/llama-3.1-70b"

        elif task_type == 'complex_reasoning':
            # Use reasoning model
            return "deepseek/deepseek-r1"  # Or paid tier if free exhausted

        elif task_type == 'batch_processing':
            # Use high-capacity provider
            if cerebras_available:
                return "cerebras/llama-3.1-70b"
            else:
                return "groq/llama-3.3-70b-versatile"

        else:
            # Default: Groq for balanced performance
            return "groq/llama-3.3-70b-versatile" if groq_available else "cerebras/llama-3.1-70b"

    def _select_production_model(self, task_type, priority):
        """Select from paid tiers for production."""

        if task_type == 'simple_query':
            return "vertex_ai/gemini-2.5-flash"  # Fast, cheap

        elif task_type == 'compliance_check':
            return "anthropic/claude-3-5-sonnet"  # Highest quality

        elif task_type == 'complex_reasoning':
            return "anthropic/claude-3-5-sonnet"  # Best reasoning

        elif task_type == 'batch_processing':
            return "vertex_ai/gemini-2.5-flash"  # Fast, cheap

        elif task_type == 'cost_optimized':
            return "deepseek/deepseek-r1"  # Cheapest

        else:
            return "vertex_ai/gemini-2.5-flash"  # Default

# Usage example
selector = ModelSelector(environment='development')

# Simple query
model = selector.select_model('simple_query', priority='speed')
response = completion(model=model, messages=[{"role": "user", "content": "..."}])

# Compliance check
model = selector.select_model('compliance_check')
response = completion(model=model, messages=[{"role": "user", "content": "..."}])
```

#### Fallback Strategies

```python
from litellm import completion
from litellm.exceptions import RateLimitError, APIError

class RobustLLMCaller:
    """Call LLM with automatic fallback."""

    def __init__(self, environment='development'):
        self.environment = environment
        self.selector = ModelSelector(environment)

    def call_with_fallback(self, messages, task_type='simple_query', max_retries=3):
        """Call LLM with automatic fallback on failure."""

        # Define fallback chain based on environment
        if self.environment == 'production':
            fallback_chain = [
                "vertex_ai/gemini-2.5-flash",     # Primary
                "anthropic/claude-3-5-sonnet",    # High quality fallback
                "groq/llama-3.3-70b-versatile",   # Free tier emergency
                "cerebras/llama-3.1-70b"          # Last resort
            ]
        else:
            fallback_chain = [
                "groq/llama-3.3-70b-versatile",   # Primary free
                "cerebras/llama-3.1-70b",         # Secondary free
                "deepseek/deepseek-r1"            # Tertiary
            ]

        last_error = None

        for model in fallback_chain:
            try:
                response = completion(
                    model=model,
                    messages=messages,
                    timeout=30
                )
                return response

            except RateLimitError as e:
                print(f"Rate limit hit on {model}, trying next...")
                last_error = e
                continue

            except APIError as e:
                print(f"API error on {model}: {e}, trying next...")
                last_error = e
                continue

            except Exception as e:
                print(f"Unexpected error on {model}: {e}, trying next...")
                last_error = e
                continue

        # All models failed
        raise Exception(f"All fallback models failed. Last error: {last_error}")

# Usage
caller = RobustLLMCaller(environment='development')

try:
    response = caller.call_with_fallback(
        messages=[{"role": "user", "content": "Calculate pension..."}],
        task_type='simple_query'
    )
    print(response.choices[0].message.content)
except Exception as e:
    print(f"All models failed: {e}")
```

#### Usage Tracking

```python
import redis
from datetime import datetime, timedelta

class UsageTracker:
    """Track API usage across providers to manage free tier limits."""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def record_usage(self, provider, tokens):
        """Record token usage for a provider."""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"usage:{provider}:{today}"

        # Increment token count
        self.redis_client.incrby(key, tokens)

        # Set expiration for 48 hours (allow for timezone differences)
        self.redis_client.expire(key, timedelta(hours=48))

    def get_usage(self, provider):
        """Get today's usage for a provider."""
        today = datetime.now().strftime('%Y-%m-%d')
        key = f"usage:{provider}:{today}"

        usage = self.redis_client.get(key)
        return int(usage) if usage else 0

    def check_limit(self, provider, limit):
        """Check if provider is under daily limit."""
        usage = self.get_usage(provider)
        return usage < limit

    def get_remaining(self, provider, limit):
        """Get remaining tokens for provider."""
        usage = self.get_usage(provider)
        return max(0, limit - usage)

# Usage
tracker = UsageTracker()

# Before making a call
if tracker.check_limit('groq', 500_000):
    response = completion(model="groq/llama-3.3-70b-versatile", ...)
    # Estimate tokens (or get from response)
    estimated_tokens = len(str(response)) * 0.75  # Rough estimate
    tracker.record_usage('groq', estimated_tokens)
else:
    # Use alternative provider
    response = completion(model="cerebras/llama-3.1-70b", ...)

# Check remaining
print(f"Groq remaining: {tracker.get_remaining('groq', 500_000)} tokens")
```

---

## Comparison Tables

### Provider Feature Matrix

| Provider | Daily Tokens | Daily Requests | Speed (t/s) | Quality | Sustainability | UK Access | GDPR Safe |
|----------|--------------|----------------|-------------|---------|----------------|-----------|-----------|
| **Gemini AI Studio** | 250K/min | 1M/day | 250 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ❌ **BLOCKED** | ⚠️ Paid only |
| **Groq** | 500K/day | Not specified | 400+ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ YES | ⚠️ Check terms |
| **Cerebras** | 1M/day | Not specified | 2,500 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ✅ YES | ⚠️ Check terms |
| **DeepSeek R1** | 1M (one-time) | Unlimited | ~100 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ YES | ⚠️ Data residency |
| **Claude** | $5 (one-time) | Unlimited | ~100 | ⭐⭐⭐⭐⭐ | ⭐ | ⚠️ UK excluded | ⚠️ Paid DPA only |
| **OpenRouter** | Varies | 50/day | Varies | ⭐⭐⭐⭐ | ⭐⭐ | ✅ YES | ❌ Complex |
| **Mistral** | Not disclosed | Not disclosed | ~100 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ✅ YES | ✅ EU-based |
| **Cohere** | 1K calls/month | 1K/month | ~100 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ✅ YES | ⚠️ Check terms |
| **Hugging Face** | ~100s req/hr | ~100/hour | Varies | ⭐⭐⭐ | ⭐⭐⭐ | ✅ YES | ❌ Variable |

---

### Cost Comparison (Production - 10K Users, 6B tokens/month)

| Provider | Monthly Cost | Annual Cost | Notes |
|----------|--------------|-------------|-------|
| **Free Tiers** | $0 | $0 | ⚠️ <1% coverage, emergency only |
| **Gemini Vertex AI** | **$450** | **$5,400** | ✅ Best value, GDPR-compliant |
| **DeepSeek R1** | **$6,000** | **$72,000** | ✅ Good reasoning, cheap |
| **Claude Haiku** | $1,500 | $18,000 | ✅ High quality, fast |
| **GPT-4o Mini** | $900 | $10,800 | Balanced |
| **Claude Sonnet** | $18,000 | $216,000 | Highest quality |
| **GPT-4o** | $15,000 | $180,000 | Premium pricing |

**Free tier role in production:** Emergency fallback only (~$0, provides 7.5-45K queries/month backup)

---

### Use Case Suitability

| Use Case | Best Free Provider | Alternative | Paid Upgrade Path |
|----------|-------------------|-------------|-------------------|
| **UK Development** | Groq (500K/day) | Cerebras (1M/day) | Vertex AI / DeepSeek R1 |
| **Speed-critical** | Cerebras (2,500 t/s) | Groq (400 t/s) | Cerebras paid / Groq paid |
| **Complex reasoning** | DeepSeek R1 (1M) | Groq Llama 3.3 70B | DeepSeek R1 paid / Claude |
| **Batch processing** | Cerebras (1M/day) | Groq (500K/day) | Vertex AI / Cerebras paid |
| **Compliance testing** | Groq Llama 3.3 70B | DeepSeek R1 | Claude Sonnet / GPT-4o |
| **Cost optimization** | Groq + Cerebras | DeepSeek R1 | DeepSeek R1 paid ($6/month) |
| **GDPR compliance** | ⚠️ None (synthetic data only) | - | Vertex AI / Azure OpenAI |

---

## Use Case Mapping

### Development Phase

**Recommended Free Tier Allocation:**

| Activity | Provider | Allocation | Reasoning |
|----------|----------|------------|-----------|
| **General development** | Groq | 400K/day (80%) | Fast feedback, good quality |
| **Performance testing** | Cerebras | 900K/day (90%) | Ultra-fast, high capacity |
| **Quality validation** | DeepSeek R1 | 100K (10%) | Use one-time tokens wisely |
| **Diversity testing** | OpenRouter | 50 req/day | Test different models |

**Expected Coverage:** 100%+ of development needs

**Workflow:**
```bash
# Morning: Use Groq for active development (fast feedback)
# Afternoon: Run batch tests on Cerebras (high capacity)
# Evening: Quality checks with DeepSeek R1 (save tokens)
```

---

### Testing Phase

**Functional Testing:**
- **Provider:** Groq (fast, reliable)
- **Coverage:** 250K tokens/day = ~1,000 test cases
- **Allocation:** 50% of daily quota

**Compliance Testing:**
- **Provider:** Groq Llama 3.3 70B (best free quality)
- **Fallback:** DeepSeek R1 for complex cases
- **Coverage:** 100K tokens/day = ~50 complex scenarios

**Integration Testing:**
- **Provider:** Cerebras (high throughput)
- **Coverage:** 500K tokens/day = ~2,000 integration tests

**Load Testing:**
- ⚠️ **Not feasible with free tiers** (will hit limits immediately)
- **Alternative:** Use paid tier with temporary credits
- **Or:** Stagger load tests across multiple days

---

### Production Workloads

**⚠️ Free tiers NOT suitable for primary production capacity**

**Suitable uses in production:**

1. **Emergency Fallback** (recommended)
   ```python
   # Primary: Paid Vertex AI
   # Fallback: Free Groq (45M tokens/month emergency capacity)
   if primary_api_down:
       use_free_tier_emergency()
   ```

2. **Development/Staging Environments** (ongoing)
   - Free tiers for development even after production launch
   - Test new features without paid costs
   - Staging environment for QA

3. **Low-Volume Internal Tools** (if appropriate)
   - Admin dashboards (100-1,000 queries/month)
   - Internal reports (low frequency)
   - Monitoring tools

**Required for production:**
- **Must use paid tier with DPA** for customer-facing pension guidance
- **GDPR compliance** requires paid tier with data residency
- **FCA regulations** require audit trails and SLAs
- **Free tiers** only for fallback/development

---

## Action Plan

### Week 1: Setup & Initial Testing

**Day 1-2: Account Creation**
```bash
# UK-accessible providers
1. Sign up for Groq: https://console.groq.com/
2. Sign up for Cerebras: https://cerebras.net/
3. Sign up for DeepSeek: https://platform.deepseek.com/

# Get API keys
4. Store in .env file securely
```

**Day 3-4: Integration**
```python
# Install LiteLLM
pip install litellm

# Test each provider
from litellm import completion

# Test Groq
response = completion(
    model="groq/llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": "Test message"}]
)
print("Groq:", response.choices[0].message.content)

# Test Cerebras
response = completion(
    model="cerebras/llama-3.1-70b",
    messages=[{"role": "user", "content": "Test message"}]
)
print("Cerebras:", response.choices[0].message.content)

# Test DeepSeek
response = completion(
    model="deepseek/deepseek-r1",
    messages=[{"role": "user", "content": "Test message"}]
)
print("DeepSeek:", response.choices[0].message.content)
```

**Day 5-7: Usage Tracking Setup**
```python
# Implement usage tracker (see Integration Guide)
# Set up Redis for tracking
# Configure daily limits
# Test fallback mechanisms
```

**Deliverables:**
- ✅ All free tier accounts created
- ✅ API keys secured in environment
- ✅ Basic integration tested
- ✅ Usage tracking implemented

---

### Month 1: Development Phase

**Week 1-2: Active Development**
- **Primary:** Groq (500K tokens/day)
- **Testing:** Cerebras (1M tokens/day)
- **Target:** Build core advisor agent logic

**Week 3-4: Quality Validation**
- **Reasoning:** DeepSeek R1 (use 1M token budget)
- **Compliance:** Groq Llama 3.3 70B
- **Target:** Validate FCA compliance framework

**Expected Usage:**
- ~30M tokens total
- 100% covered by free tiers
- $0 cost vs $200-300 with paid APIs

**Monitoring:**
- Daily usage tracking
- Quality metrics per provider
- Latency measurements
- Fallback trigger frequency

---

### Month 2-3: Testing & Validation

**Functional Testing:**
- Groq: 15M tokens/month
- Cerebras: 30M tokens/month
- Coverage: 100%+

**Compliance Testing:**
- Groq Llama 3.3 70B: High-quality validation
- Cross-validate with local models (see `local-llm-options.md`)
- Compare free tier quality vs paid tier benchmarks

**Integration Testing:**
- Multi-provider fallback testing
- Performance benchmarking
- GDPR compliance validation with synthetic data

**Expected Usage:**
- ~45M tokens/month
- 100% covered by free tiers
- $0 cost

---

### Month 4: Pre-Production

**Activities:**
1. **Evaluate paid tier migration**
   - Based on quality metrics from testing
   - Based on latency requirements
   - Based on GDPR compliance needs

2. **Set up paid tier accounts** (if needed)
   - Google Vertex AI (UK data residency)
   - Or DeepSeek R1 paid tier ($6-60/month)
   - Configure DPAs and compliance

3. **Configure hybrid architecture**
   - Paid tier for production
   - Free tier for development/fallback
   - Usage tracking across both

**Decision Matrix:**
```python
use_paid_tier = (
    requires_gdpr_compliance and    # UK pension system: YES
    customer_facing and             # YES for advisor agent
    latency_critical and            # YES (4-6s target)
    can_budget_450_month            # Check budget
)

if use_paid_tier:
    production_provider = "vertex_ai/gemini-2.5-flash"  # $450/month
    fallback_provider = "groq/llama-3.3-70b-versatile"  # Free tier
else:
    production_provider = "groq/llama-3.3-70b-versatile"  # Free (limited)
    fallback_provider = "cerebras/llama-3.1-70b"  # Free
```

---

### Month 5+: Production

**Production Configuration:**
```yaml
Primary (Paid):
  Provider: Google Vertex AI (Gemini 2.5 Flash)
  Cost: $450/month (10K users)
  SLA: 99.9% uptime
  Data: UK residency

Compliance (Paid):
  Provider: Anthropic Claude 3.5 Sonnet
  Cost: $100/month (validation only)
  Quality: Highest
  DPA: Enterprise agreement

Fallback (Free):
  Provider: Groq Llama 3.3 70B
  Capacity: 500K tokens/day (emergency only)
  Cost: $0

Development (Free):
  Provider: Groq + Cerebras
  Capacity: 1.5M tokens/day
  Cost: $0 (ongoing savings)
```

**Ongoing Monitoring:**
- Track paid tier usage and costs
- Monitor free tier for development
- Measure fallback trigger frequency
- Optimize model selection based on task type

**Expected Costs:**
- Production: $450-550/month (paid tiers)
- Development: $0/month (free tiers)
- Emergency capacity: $0 (free tier fallback)

---

## Summary & Final Recommendations

### For UK-Based Pension Guidance System

**✅ Best Free Tier Strategy:**

1. **Development (Months 1-3):**
   - **Primary:** Groq (500K tokens/day, fast, UK-accessible)
   - **Testing:** Cerebras (1M tokens/day, very fast)
   - **Reasoning:** DeepSeek R1 (1M tokens one-time)
   - **Coverage:** 100%+
   - **Cost:** $0 (vs $200-300 with paid)

2. **Production (Month 4+):**
   - **Primary:** Google Vertex AI Gemini (paid, GDPR-compliant)
   - **Compliance:** Anthropic Claude (paid, highest quality)
   - **Fallback:** Groq (free, emergency capacity)
   - **Development:** Groq + Cerebras (free, ongoing)
   - **Cost:** $450-550/month paid + $0 development

### Key Takeaways

1. ✅ **Free tiers can cover 100% of development costs** (~$200-300 savings)
2. ❌ **UK projects cannot use Gemini free tier** (geo-blocked)
3. ✅ **Groq is best UK-accessible free option** (500K/day, 400 t/s)
4. ✅ **Cerebras provides highest speed** (2,500 t/s, 1M/day)
5. ⚠️ **Never use free tiers with real pension data** (GDPR risk)
6. ❌ **No free tier suitable for primary production** (must use paid with DPA)
7. ✅ **DeepSeek R1 offers ultra-cheap paid tier** ($6-60/month for production)
8. ✅ **Free tiers provide valuable emergency fallback** in production
9. ✅ **Multi-provider strategy essential** for resilience
10. ✅ **Ongoing development savings** with free tiers even after production launch

### Recommended Path Forward

**Phase 1 (Now):** Set up Groq + Cerebras + DeepSeek accounts
**Phase 2 (Week 1-12):** Use free tiers for 100% of development
**Phase 3 (Month 4):** Migrate to Vertex AI paid tier for production
**Phase 4 (Ongoing):** Maintain free tiers for development/fallback

**Expected Total Cost (Year 1):**
- Development: **$0** (free tiers)
- Production: **$5,400** (Vertex AI, 6 months)
- **Total: $5,400** (vs $90,000+ with GPT-4o)
- **Savings: 94%**

### Critical Compliance Note

**⚠️ For UK Pension System:**
- **MUST use paid tier with DPA for production** (GDPR/FCA requirements)
- **MUST NOT send real pension data to free tiers** (privacy risk)
- **MUST implement data anonymization** for development use
- **MUST have audit trails** for regulatory compliance
- **Consider self-hosted models** for maximum control (see `local-llm-options.md`)

### Next Steps

1. **Immediate:** Create Groq, Cerebras, DeepSeek accounts
2. **Week 1:** Integrate with LiteLLM and test
3. **Month 1-3:** Use free tiers for development (save $200-300)
4. **Month 4:** Evaluate and set up paid Vertex AI for production
5. **Ongoing:** Maintain free tiers for development and emergency fallback

**Questions or need help?** Refer to:
- `local-llm-options.md` - For self-hosted alternatives
- `agent-model-recommendations.md` - For agent-specific model recommendations
- `provider-flexibility.md` - For multi-provider architecture guidance
