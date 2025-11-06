# Agent Prompt & Code Improvement Plan

**Date**: 2025-01-06
**Status**: Planning Phase
**Scope**: Comprehensive review of advisor agent templates and code
**Focus Areas**: FCA Compliance, Conversational Quality

---

## Executive Summary

This document outlines 13 improvement opportunities across agent prompt templates and code, organized into 4 phases. Analysis revealed critical issues in FCA neutrality enforcement, incomplete context retrieval integration, and opportunities to enhance conversational quality scoring.

**Key Findings:**
- FCA neutrality instructions duplicated across 3 templates (maintenance risk)
- Context retrieval incomplete - cases and rules not being used (empty lists)
- Post-streaming validation cannot prevent bad outputs reaching users
- Conversational quality scoring too simplistic (keyword counting)
- Emotional evolution detection has edge cases (ambiguous "okay" detection)

---

## Current System Analysis

### Template Structure

**Core Advisor Templates:**
1. `guidance_main.jinja` (140 lines) - Main guidance generation
2. `reasoning.jinja` (52 lines) - Chain-of-thought pre-generation
3. `guidance_with_reasoning.jinja` (78 lines) - Guidance after reasoning
4. `compliance_refinement.jinja` (59 lines) - Post-validation refinement
5. `borderline_strengthening.jinja` (44 lines) - Low-confidence improvement

**Compliance Template:**
6. `validation.jinja` (160 lines) - LLM-as-judge compliance checking

**Key Strengths:**
✅ Comprehensive FCA neutrality instructions with clear examples
✅ Strong conversational framework (signposting, transitions, personalization)
✅ Sophisticated emotional state tracking with evolution detection
✅ Two-stage retrieval with conversational context re-ranking
✅ Confidence-based validation with human review triggers
✅ Chain-of-thought reasoning integration

### Agent Code Architecture

**AdvisorAgent** (`src/guidance_agent/advisor/agent.py`):
- `provide_guidance()` - Main synchronous flow
- `provide_guidance_stream()` - Streaming with async validation
- `_retrieve_context()` - Context assembly (lines 317-381)
- `_detect_conversation_phase()` - Opening/middle/closing detection
- `_assess_emotional_state()` - Emotional arc tracking with evolution
- `_calculate_conversational_quality()` - 4-component scoring (variety, signposting, personalization, engagement)

**ComplianceValidator** (`src/guidance_agent/compliance/validator.py`):
- LLM-as-judge pattern with think tag filtering
- Structured validation parsing with confidence thresholds (<0.70 requires review)
- Relevance checking integrated

**Retrieval System** (`src/guidance_agent/retrieval/retriever.py`):
- CaseBase with conversational re-ranking (similarity + quality boost + phase matching)
- Five-source retrieval: memories, cases, rules, FCA knowledge, pension knowledge

---

## Phase 1: FCA Compliance Enhancements (HIGH PRIORITY)

### 1.1 Consolidate FCA Neutrality Instructions

**Problem**: FCA neutrality section duplicated across 3 templates
- `guidance_main.jinja` (lines 71-108)
- `guidance_with_reasoning.jinja` (lines 30-66)
- `validation.jinja` (lines 43-90)

**Impact**: Changes must be replicated 3x; inconsistency risk; maintenance burden

**Solution**:
```jinja
{# Create: templates/_shared/fca_neutrality.jinja #}
{% macro fca_neutrality_instructions() %}
## CRITICAL: FCA Neutrality Requirements

**The Core Distinction:**
- ✅ **Process Warmth (COMPLIANT)**: Enthusiasm about the guidance process
- ❌ **Circumstantial Evaluation (PROHIBITED)**: Judgments about customer's financial position

[... full instructions ...]

**Borderline Phrases (Avoid These Too):**
- "Meaningful amount" - Implies value judgment
- "Good planning" when referring to accumulation, not seeking guidance
- Comparative statements even if indirect ("many people have less")
- "On track" or "behind" - Position assessments
- "Strong foundation" or "solid base" - Adequacy evaluations
{% endmacro %}
```

**Implementation**:
1. Create `templates/_shared/fca_neutrality.jinja`
2. Add borderline examples section
3. Update 3 templates to import and use macro:
   ```jinja
   {% from '_shared/fca_neutrality.jinja' import fca_neutrality_instructions %}
   {{ fca_neutrality_instructions() }}
   ```
4. Update all 20 template tests to verify macro inclusion

**Files Modified**: 4 (1 new, 3 updated)
**Tests Updated**: 20 template regression tests

### 1.2 Strengthen Compliance Validation

**Problem**: Validator lacks explicit categories for FCA neutrality violations
- Template lists 4 "Critical Validation Checks" (evaluative language, social proof, combination risk, suitability)
- Parser only extracts 6 generic issue types
- Missing: Explicit parsing for "combination risk" (name + social proof + option)

**Current Parser** (validator.py lines 287-346):
```python
if "Guidance vs Advice boundary: FAIL" in response:  # Generic catch-all
```

**Solution**: Add specific issue types and parsing

```python
# validator.py - Add to IssueType enum
class IssueType(str, Enum):
    EVALUATIVE_LANGUAGE = "evaluative_language"
    SOCIAL_PROOF_VIOLATION = "social_proof_violation"
    COMBINATION_RISK = "combination_risk"  # Name + social proof + option
    SUITABILITY_ASSESSMENT = "suitability_assessment"
    # ... existing types
```

```python
# Enhanced parsing logic
if "Evaluative Language Check:" in response and "FAIL" in ...:
    issues.append(ValidationIssue(
        issue_type=IssueType.EVALUATIVE_LANGUAGE,
        description="Contains evaluative language about customer circumstances",
        severity="high"
    ))

if "Social Proof + Circumstances:" in response and "FAIL" in ...:
    issues.append(ValidationIssue(
        issue_type=IssueType.SOCIAL_PROOF_VIOLATION,
        description="Combines social proof with customer circumstances",
        severity="high"
    ))

if "Combination Risk Check:" in response and "FAIL" in ...:
    issues.append(ValidationIssue(
        issue_type=IssueType.COMBINATION_RISK,
        description="Dangerous combination: name + social proof + option",
        severity="critical"
    ))
```

**Implementation**:
1. Update `IssueType` enum in `validator.py`
2. Enhance parsing logic in `_parse_validation_response()` (lines 287-346)
3. Update validation template to ensure LLM outputs match new categories
4. Add structured JSON output option for easier parsing
5. Add 8 new tests for each violation type

**Files Modified**: 2 (`validator.py`, `validation.jinja`)
**Tests Added**: 8 new edge case tests

### 1.3 Make Understanding Verification Required

**Problem**: Templates say "naturally checking understanding" (optional language) but validation expects it as required

**Current** (guidance_main.jinja line 136):
```jinja
- Naturally checking understanding when exploring complex topics
```

**Validation expectation** (validation.jinja lines 128-133):
```jinja
4. Understanding verification: [PASS/FAIL]
   - Are there checks like "Does this make sense?" when covering complex topics?
```

**Solution**: Strengthen guidance template wording
```jinja
- **Check understanding** when covering complex topics:
  - "Does this make sense so far?"
  - "Would you like me to explain any of this differently?"
  - "Is there anything you'd like me to clarify?"
```

**Implementation**:
1. Update all guidance templates (main, with_reasoning, refinement, strengthening)
2. Add specific example phrases
3. Update tests to verify understanding checks present

**Files Modified**: 4 templates
**Tests Updated**: Validation tests

### 1.4 Enhance Reasoning Template for FCA

**Problem**: Reasoning template question 4 is too vague: "What risks or important points must be covered?"

**Current** (reasoning.jinja line 39):
```jinja
4. What risks or important points must be covered?
```

**Gap**: Doesn't explicitly prompt for:
- Risk disclosure planning (market, longevity, inflation)
- DB scheme special handling
- Signposting decisions (when to direct to adviser)

**Solution**: Add structured FCA reasoning checklist

```jinja
4. **Risk Disclosure**: What specific risks must I explain?
   - Market risk (investment performance uncertainty)
   - Longevity risk (outliving retirement funds)
   - Inflation risk (purchasing power erosion)
   - Sequence risk (timing of withdrawals/market conditions)

5. **DB Scheme Check**: Does customer mention defined benefit pension?
   - If YES: Must warn about transfer value risks and specialist advice requirement
   - Flag for heightened scrutiny (DB transfers are regulated advice)

6. **Signposting Decision**: Does this require FCA-regulated advice?
   - Product recommendation? → Signpost immediately
   - Tax planning? → Signpost to tax adviser
   - Complex situation beyond guidance scope? → Signpost to financial adviser
   - General information/education? → Can provide within guidance boundaries

7. **Adequacy Trap Check**: Am I at risk of assessing whether their pension is "enough"?
   - Avoid: "You're on track", "behind", "ahead", "doing well"
   - Instead: State factors, offer exploration, or signpost for assessment
```

**Implementation**:
1. Update `reasoning.jinja` with expanded FCA reasoning prompts
2. Update agent code to handle longer reasoning output
3. Update reasoning tests to verify new prompts addressed
4. Add integration test verifying DB scheme detection

**Files Modified**: 2 (`reasoning.jinja`, agent test)
**Tests Added**: 3 integration tests

---

## Phase 2: Conversational Quality Improvements (HIGH PRIORITY)

### 2.1 Complete Context Retrieval Integration

**Problem**: Context retrieval returns empty lists for cases and rules

**Current Code** (agent.py lines 377-379):
```python
return RetrievedContext(
    memories=memories,
    cases=[],  # Will be populated in later integration
    rules=[],  # Will be populated in later integration
    fca_guidelines=fca_guidelines,
    pension_knowledge=pension_knowledge
)
```

**Impact**:
- Templates render "Similar Past Cases" and "Learned Guidance Rules" with no data
- Sophisticated CaseBase re-ranking (retriever.py lines 96-112) not being used
- Agent can't learn from successful past consultations
- Agent can't apply learned guidance principles

**Solution**: Complete the integration

```python
# agent.py _retrieve_context() method
async def _retrieve_context(
    self,
    customer_message: str,
    customer: Customer,
    conversation: List[dict]
) -> RetrievedContext:
    # ... existing memory retrieval ...

    # Generate embedding for multi-source retrieval
    query_embedding = await self.embedding_service.generate_embedding(customer_message)

    # Assemble conversational context for case re-ranking
    conversational_context = {
        "phase": self._detect_conversation_phase(conversation),
        "emotional_state": self._assess_emotional_state(conversation, customer),
        "turns_count": len(conversation),
        "customer_profile": {
            "age": customer.age,
            "pension_value": customer.pension_value,
            "has_db_scheme": customer.has_db_scheme
        }
    }

    # Retrieve cases with conversational re-ranking
    cases = await self.case_base.retrieve(
        query_embedding=query_embedding,
        top_k=3,
        conversation_context=conversational_context
    )

    # Retrieve rules
    rules = await self.rules_base.retrieve(
        query_embedding=query_embedding,
        top_k=5,
        confidence_threshold=0.7  # Only high-confidence rules
    )

    return RetrievedContext(
        memories=memories,
        cases=cases,
        rules=rules,
        fca_guidelines=fca_guidelines,
        pension_knowledge=pension_knowledge
    )
```

**Implementation**:
1. Update `_retrieve_context()` in `agent.py`
2. Verify CaseBase and RulesBase have `retrieve()` methods
3. Add conversational_context parameter support to retrievers
4. Update templates to handle populated case/rule sections
5. Add integration tests verifying context assembly

**Files Modified**: 3 (`agent.py`, `retriever.py`, integration tests)
**Tests Added**: 4 integration tests

### 2.2 Enhance Conversational Quality Scoring

**Problem**: Current algorithm is too simplistic (keyword counting)

**Current Issues** (agent.py lines 553-665):

1. **Language Variety (30%)**: Only checks 3 phrases
   - Doesn't detect other template-like repetition
   - False positives possible

2. **Signposting (30%)**: 15 phrases but some very similar
   - Doesn't penalize awkward overuse
   - Could reward "keyword stuffing"

3. **Personalization (20%)**: Only checks name usage
   - Doesn't check specific numbers/situations referenced
   - Misses "deep" personalization

4. **Engagement (20%)**: Simply counts question marks
   - Doesn't distinguish rhetorical vs. genuine questions
   - Multiple questions may not be better UX

**Solution**: Implement LLM-based quality assessment

```python
# New method: _assess_conversational_quality_llm()
async def _assess_conversational_quality_llm(
    self,
    guidance: str,
    conversation: List[dict],
    customer: Customer
) -> float:
    """
    Use LLM to assess conversational quality with nuanced judgment.
    Returns score 0.0-1.0
    """

    template = self.template_env.get_template("advisor/quality_assessment.jinja")
    prompt = template.render(
        guidance=guidance,
        conversation_history=self._format_conversation(conversation),
        customer_name=customer.name,
        customer_age=customer.age
    )

    response = await self.llm_service.complete(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Lower temperature for consistent scoring
    )

    # Parse structured output
    quality_data = self._parse_quality_assessment(response)

    return quality_data["overall_score"]
```

**New Template**: `templates/advisor/quality_assessment.jinja`
```jinja
You are assessing the conversational quality of pension guidance.

## Guidance to Assess
{{ guidance }}

## Conversation Context
{{ conversation_history }}

## Customer Profile
- Name: {{ customer_name }}
- Age: {{ customer_age }}

## Assessment Criteria

Rate each dimension 0-10, then provide overall score 0.0-1.0:

1. **Natural Language Flow** (0-10)
   - Variety in phrasing (not template-like)
   - Smooth transitions between topics
   - Avoids repetitive sentence structures
   - British English conventions maintained

2. **Signposting Quality** (0-10)
   - Clear topic transitions when appropriate
   - Not overused or forced
   - Helps customer navigate conversation
   - Natural integration (not keyword stuffing)

3. **Personalization Depth** (0-10)
   - References customer's specific situation (numbers, dates, circumstances)
   - Uses customer name naturally (not excessively)
   - Tailored to customer's expressed concerns
   - Shows continuity from conversation history

4. **Engagement Effectiveness** (0-10)
   - Genuine questions that invite dialogue (not rhetorical)
   - Appropriate pacing (not overwhelming)
   - Checks understanding at right moments
   - Encourages customer reflection

5. **FCA Neutrality Maintenance** (0-10)
   - Process warmth without circumstantial evaluation
   - No evaluative language about adequacy
   - Maintains professional boundary
   - Avoids "advice creep"

Output format (JSON):
{
  "natural_flow": 8,
  "signposting": 7,
  "personalization": 9,
  "engagement": 8,
  "fca_neutrality": 10,
  "overall_score": 0.84,
  "strengths": ["Strong personalization with specific numbers", "Excellent FCA neutrality"],
  "improvements": ["Reduce signposting frequency", "Vary question phrasing"]
}
```

**Implementation**:
1. Create new template `quality_assessment.jinja`
2. Add `_assess_conversational_quality_llm()` method to agent
3. Add fallback to keyword-based scoring if LLM fails
4. Update quality storage in Consultation model to include breakdown
5. Add A/B test comparing LLM vs keyword scoring
6. Update quality dashboard to show dimension breakdown

**Files Modified**: 4 (agent.py, new template, tests, dashboard)
**Tests Added**: 6 quality assessment tests

### 2.3 Refine Emotional Evolution Detection

**Problem**: "okay" detection has ambiguity and edge cases

**Current Code** (agent.py lines 817-850):
```python
if "okay" in last_message or "alright" in last_message:
    # Check if earlier messages showed anxiety/confusion
    earlier_context = "\n".join(messages[:-1]).lower()
    if any(keyword in earlier_context for keyword in anxious_keywords + confused_keywords):
        return "neutral"  # Evolved from anxious/confused to neutral
```

**Issues**:
- "okay" is ambiguous: agreement, resignation, confusion all possible
- Doesn't check negative context: "I'm not okay with this"
- Regex issues: "okaying" or "okay?" might trigger false positives
- No confidence scoring

**Solution**: Context-aware sentiment analysis

```python
def _assess_emotional_state(
    self,
    conversation: List[dict],
    customer: Customer
) -> Dict[str, Any]:
    """Enhanced emotional state detection with confidence scoring."""

    if not conversation:
        return {"state": "neutral", "confidence": 1.0, "evolution": None}

    # Get recent messages (up to 5 most recent)
    recent_messages = [msg for msg in conversation[-5:] if msg["role"] == "customer"]

    if not recent_messages:
        return {"state": "neutral", "confidence": 1.0, "evolution": None}

    # Analyze last message with context
    last_message = recent_messages[-1]["content"].lower()

    # Enhanced "okay" detection with context
    okay_indicators = ["okay", "ok", "alright", "sounds good"]
    if any(indicator in last_message for indicator in okay_indicators):
        # Check for negative context
        negative_patterns = [
            r"not\s+(okay|ok|alright)",
            r"(okay|ok|alright)\s+but",
            r"(okay|ok|alright)\?",  # Question form suggests uncertainty
            r"i\s+guess\s+(okay|ok)",  # Resignation
        ]

        if any(re.search(pattern, last_message) for pattern in negative_patterns):
            # Ambiguous or negative "okay"
            state = "uncertain"
            confidence = 0.6
        else:
            # Check for positive reinforcement
            positive_context = ["thanks", "helpful", "understand", "clear", "makes sense"]
            if any(word in last_message for word in positive_context):
                state = "confident"
                confidence = 0.8
            else:
                # Simple agreement
                state = "neutral"
                confidence = 0.7
    else:
        # Use existing keyword detection
        state = self._detect_emotional_keywords(last_message)
        confidence = 0.85

    # Detect evolution
    evolution = None
    if len(recent_messages) >= 2:
        previous_state = self._detect_emotional_keywords(recent_messages[-2]["content"].lower())
        if previous_state != state:
            evolution = {
                "from": previous_state,
                "to": state,
                "confidence": confidence * 0.9  # Slightly lower confidence for evolution
            }

    return {
        "state": state,
        "confidence": confidence,
        "evolution": evolution
    }
```

**Implementation**:
1. Update `_assess_emotional_state()` method with context awareness
2. Add confidence scoring to emotional state detection
3. Add negative pattern detection for "okay"
4. Store confidence scores in conversational_context
5. Add 6 edge case tests (not okay, okay?, okay but, I guess okay)
6. Update dashboard to show emotional confidence

**Files Modified**: 2 (agent.py, tests)
**Tests Added**: 6 edge case tests

---

## Phase 3: System Performance & Architecture (MEDIUM PRIORITY)

### 3.1 Fix Post-Streaming Validation Issue

**Problem**: Validation happens after guidance fully streamed to user; failures have no remediation

**Current Flow** (agent.py lines 186-191):
```python
# 4. Validate in background (doesn't block user experience)
full_guidance = "".join(guidance_buffer)
asyncio.create_task(
    self._validate_and_record_async(full_guidance, customer, context)
)
```

**Lines 295-299**:
```python
if not validation.passed and not validation.requires_human_review:
    # Could trigger re-generation or human review
    # For now, just log the issue
    pass  # DOES NOTHING
```

**Impact**: User sees non-compliant guidance before it's caught

**Solution**: Three-tier validation strategy

```python
class ValidationStrategy(str, Enum):
    PRE_STREAM = "pre_stream"      # Validate before streaming (slower, safer)
    POST_STREAM = "post_stream"    # Current behavior (faster, riskier)
    HYBRID = "hybrid"              # Pre-validate with cache, post-validate for changes

async def provide_guidance_stream(
    self,
    customer_message: str,
    customer: Customer,
    conversation: List[dict],
    validation_strategy: ValidationStrategy = ValidationStrategy.HYBRID
) -> AsyncGenerator[str, None]:
    """
    Streaming guidance with configurable validation.
    """

    # 1. Retrieve context
    context = await self._retrieve_context(customer_message, customer, conversation)

    # 2. Generate reasoning (optional)
    reasoning = None
    if self.use_reasoning:
        reasoning = await self._generate_reasoning(customer_message, context)

    # 3. Generate guidance
    if validation_strategy == ValidationStrategy.PRE_STREAM:
        # Generate complete guidance first
        full_guidance = await self._generate_guidance_complete(
            customer_message, context, reasoning
        )

        # Validate before streaming
        validation = await self.validator.validate(
            guidance=full_guidance,
            customer=customer,
            context=context
        )

        if not validation.passed:
            if validation.requires_human_review:
                # Critical failure - don't stream
                yield "[System: Guidance requires human review before delivery]"
                await self._flag_for_review(full_guidance, validation, customer)
                return
            else:
                # Attempt refinement
                full_guidance = await self._refine_guidance(
                    original_guidance=full_guidance,
                    validation=validation,
                    context=context
                )

                # Re-validate
                validation = await self.validator.validate(
                    guidance=full_guidance,
                    customer=customer,
                    context=context
                )

                if not validation.passed:
                    # Still failing - flag and don't stream
                    yield "[System: Guidance could not meet compliance standards]"
                    await self._flag_for_review(full_guidance, validation, customer)
                    return

        # Stream the validated guidance
        for chunk in self._chunk_text(full_guidance):
            yield chunk
            await asyncio.sleep(0.01)  # Simulate streaming

    elif validation_strategy == ValidationStrategy.HYBRID:
        # Use cached validation for similar queries
        cache_key = self._get_validation_cache_key(customer_message, context)
        cached_validation = await self._get_cached_validation(cache_key)

        if cached_validation and cached_validation.passed:
            # Trust cache, stream normally
            async for chunk in self._generate_guidance_stream(
                customer_message, context, reasoning
            ):
                yield chunk

            # Post-validate to update cache
            full_guidance = "".join(guidance_buffer)
            asyncio.create_task(
                self._validate_and_update_cache(full_guidance, cache_key, customer, context)
            )
        else:
            # No cache hit or previous failure - use pre-stream validation
            async for chunk in self.provide_guidance_stream(
                customer_message, customer, conversation,
                validation_strategy=ValidationStrategy.PRE_STREAM
            ):
                yield chunk

    else:  # POST_STREAM (current behavior)
        # Stream immediately, validate after
        guidance_buffer = []
        async for chunk in self._generate_guidance_stream(
            customer_message, context, reasoning
        ):
            guidance_buffer.append(chunk)
            yield chunk

        # Validate in background with retry logic
        full_guidance = "".join(guidance_buffer)
        asyncio.create_task(
            self._validate_with_retry(full_guidance, customer, context)
        )

async def _validate_with_retry(
    self,
    guidance: str,
    customer: Customer,
    context: RetrievedContext
):
    """Validate with automatic retry and flagging."""
    validation = await self.validator.validate(guidance, customer, context)

    if not validation.passed and not validation.requires_human_review:
        # Attempt automatic refinement
        refined_guidance = await self._refine_guidance(guidance, validation, context)

        # Store both versions
        await self._store_refinement_attempt(
            original=guidance,
            refined=refined_guidance,
            validation=validation,
            customer=customer
        )

        # Re-validate
        refined_validation = await self.validator.validate(
            refined_guidance, customer, context
        )

        if refined_validation.passed:
            # Success - log improvement
            logger.info(f"Automatic refinement successful for customer {customer.id}")
        else:
            # Still failing - flag for human review
            await self._flag_for_review(refined_guidance, refined_validation, customer)

    elif validation.requires_human_review:
        # Critical issue - flag immediately
        await self._flag_for_review(guidance, validation, customer)
```

**Configuration** (SystemSettings):
```python
# Default to HYBRID for best balance
validation_strategy = "hybrid"

# Validation cache TTL (seconds)
validation_cache_ttl = 3600  # 1 hour
```

**Implementation**:
1. Add `ValidationStrategy` enum
2. Implement three validation paths
3. Add validation caching layer (Redis or in-memory)
4. Add `_flag_for_review()` method with admin notification
5. Update SystemSettings to configure strategy
6. Add streaming tests for all three strategies
7. Add refinement retry tests
8. Update admin dashboard to show flagged consultations

**Files Modified**: 5 (agent.py, models.py, tests, admin UI, settings)
**Tests Added**: 8 streaming validation tests

### 3.2 Optimize Prompt Caching

**Problem**: Need to verify cache control structure in cached templates

**Investigation Required**:
1. Review `guidance_cached.jinja` structure
2. Verify static content (FCA rules, system instructions) marked for caching
3. Verify semi-static content (customer profile) cached appropriately
4. Verify variable content (current question) not cached
5. Measure cache hit rates

**Solution**: Structured caching layers

```jinja
{# templates/advisor/guidance_cached.jinja #}

{# LAYER 1: STATIC (cache for 24h) - System instructions and FCA rules #}
{% cache_control "static" %}
You are a pension guidance specialist providing FCA-compliant information.

## Your Role
[... static system instructions ...]

{% from '_shared/fca_neutrality.jinja' import fca_neutrality_instructions %}
{{ fca_neutrality_instructions() }}

## Conversational Framework
[... static conversational guidelines ...]
{% end_cache_control %}

{# LAYER 2: SEMI-STATIC (cache for 1h) - Customer profile and knowledge base #}
{% cache_control "semi_static" %}

## Customer Profile
- Name: {{ customer.name }}
- Age: {{ customer.age }}
- Pension Value: £{{ customer.pension_value | format_currency }}
- Employment Status: {{ customer.employment_status }}

## Retrieved Knowledge
{{ context.fca_guidelines | format_guidelines }}
{{ context.pension_knowledge | format_knowledge }}
{% end_cache_control %}

{# LAYER 3: DYNAMIC (no cache) - Current conversation and question #}
## Conversation History
{{ conversation | format_conversation }}

## Current Question
{{ customer_message }}
```

**Cache Control Headers** (agent.py):
```python
def _get_cache_headers(self, content_type: str) -> dict:
    """Get appropriate cache control headers based on content type."""

    cache_configs = {
        "static": {
            "type": "ephemeral",
            "ttl": 86400  # 24 hours
        },
        "semi_static": {
            "type": "ephemeral",
            "ttl": 3600  # 1 hour
        },
        "dynamic": {
            "type": "none"  # No caching
        }
    }

    return cache_configs.get(content_type, cache_configs["dynamic"])
```

**Monitoring**:
```python
# Add to Phoenix tracing
@tracer.start_as_current_span("prompt_cache_metrics")
async def _log_cache_metrics(self):
    """Log cache hit rates for optimization."""

    cache_stats = {
        "static_cache_hits": self.static_cache_hits,
        "semi_static_cache_hits": self.semi_static_cache_hits,
        "cache_hit_rate": self.cache_hits / self.total_requests,
        "estimated_token_savings": self.tokens_saved_by_cache,
        "estimated_cost_savings": self.tokens_saved_by_cache * COST_PER_TOKEN
    }

    logger.info(f"Cache metrics: {cache_stats}")
    return cache_stats
```

**Implementation**:
1. Review and update `guidance_cached.jinja` with structured layers
2. Implement cache control headers in agent
3. Add cache metrics to Phoenix tracing
4. Add cache hit rate monitoring
5. Calculate cost savings from caching
6. Add cache configuration to SystemSettings
7. Add cache performance tests

**Files Modified**: 4 (cached template, agent.py, observability, tests)
**Tests Added**: 3 cache performance tests

### 3.3 Consolidate British English Reminders

**Problem**: British English mentioned in 5 different templates

**Locations**:
- `guidance_main.jinja` line 30
- `guidance_with_reasoning.jinja` line 28
- `compliance_refinement.jinja` line 56
- `borderline_strengthening.jinja` line 42
- `validation.jinja` line 41

**Solution**: Move to shared system-level configuration

```jinja
{# templates/_shared/localization.jinja #}
{% macro localization_instructions() %}
## Language and Localization

**British English**: Use British spelling, phrasing, and conventions throughout:
- Spelling: "realise" not "realize", "organisation" not "organization"
- Currency: Always use "£" symbol, write out "pounds" in formal contexts
- Phrasing: "pension scheme" not "pension plan", "take advice" not "get advice"
- Tone: Professional but conversational, avoid American colloquialisms
{% endmacro %}
```

**Update SystemSettings**:
```python
# models.py - Add to SystemSettings
localization = Column(String, default="en_GB")  # ISO locale code
currency_symbol = Column(String, default="£")
currency_name = Column(String, default="pounds")
```

**Implementation**:
1. Create `templates/_shared/localization.jinja`
2. Update all 5 templates to use macro
3. Add localization to SystemSettings
4. Remove scattered British English comments
5. Add localization tests

**Files Modified**: 7 (1 new macro, 5 templates, models.py)
**Tests Updated**: 5 template tests

---

## Phase 4: Code Quality & Maintainability (LOW PRIORITY)

### 4.1 Enhance Conversation History Formatting

**Problem**: Basic formatting lacks metadata that could improve guidance

**Current Code** (prompts.py lines 71-89):
```python
def format_conversation(conversation: List[dict]) -> str:
    if not conversation:
        return "(No prior conversation)"

    formatted = []
    for msg in conversation:
        role = msg["role"].capitalize()
        content = msg["content"]
        formatted.append(f"{role}: {content}")

    return "\n".join(formatted)
```

**Missing Context**:
- Timestamps (for temporal awareness)
- Conversation phase indicators
- Emotional state markers
- Quality scores from previous advisor messages

**Solution**: Rich formatting with metadata

```python
def format_conversation(
    conversation: List[dict],
    include_metadata: bool = True,
    include_quality_scores: bool = False
) -> str:
    """
    Format conversation with optional metadata enrichment.

    Args:
        conversation: List of message dicts with role, content, timestamp, metadata
        include_metadata: Add phase/emotional indicators
        include_quality_scores: Show quality scores for advisor messages

    Returns:
        Formatted conversation string
    """
    if not conversation:
        return "(No prior conversation)"

    formatted = []

    # Detect phases if metadata requested
    phases = self._detect_all_phases(conversation) if include_metadata else None
    emotional_states = self._detect_all_emotions(conversation) if include_metadata else None

    for idx, msg in enumerate(conversation):
        role = msg["role"].capitalize()
        content = msg["content"]

        # Basic format
        line_parts = [f"{role}"]

        # Add timestamp
        if "timestamp" in msg and include_metadata:
            timestamp = msg["timestamp"].strftime("%H:%M:%S")
            line_parts.append(f"[{timestamp}]")

        # Add phase indicator
        if include_metadata and phases and idx in phases:
            phase = phases[idx]
            line_parts.append(f"[{phase.upper()}]")

        # Add emotional state for customer messages
        if include_metadata and role == "Customer" and emotional_states and idx in emotional_states:
            emotion = emotional_states[idx]
            emoji = self._get_emotion_emoji(emotion)
            line_parts.append(f"[{emotion.upper()} {emoji}]")

        # Add quality score for advisor messages
        if include_quality_scores and role == "Advisor" and "quality_score" in msg:
            score = msg["quality_score"]
            line_parts.append(f"[Quality: {score:.2f}]")

        # Combine metadata + content
        metadata_line = " ".join(line_parts)
        formatted.append(f"{metadata_line}: {content}")

        # Add separator between phases
        if include_metadata and phases and idx in phases and idx > 0:
            formatted.append("---")

    return "\n".join(formatted)

def _get_emotion_emoji(self, emotion: str) -> str:
    """Get emoji for emotional state."""
    emoji_map = {
        "anxious": "😟",
        "confused": "😕",
        "confident": "😊",
        "neutral": "😐",
        "uncertain": "🤔"
    }
    return emoji_map.get(emotion, "")
```

**Example Output**:
```
Advisor [14:32:01] [OPENING]: Hello Sarah, welcome to the pension guidance service. How can I help you today?
---
Customer [14:32:15] [OPENING] [UNCERTAIN 🤔]: I'm 45 and have about £150k in my pension. Is that enough?
---
Advisor [14:32:30] [MIDDLE] [Quality: 0.82]: Thank you for sharing that, Sarah. You have £150,000 in your pension at age 45. Whether this meets your retirement needs depends on several factors, including your desired retirement age, expected lifestyle, other income sources, and life expectancy. Would you like to explore what you might need for retirement?
---
Customer [14:32:45] [MIDDLE] [CONFIDENT 😊]: Yes, that would be helpful. I'm thinking of retiring at 67.
```

**Implementation**:
1. Update `format_conversation()` in `prompts.py`
2. Add metadata extraction methods
3. Update Consultation model to store rich conversation data
4. Add configuration toggle for metadata (SystemSettings)
5. Update templates to use rich formatting
6. Add formatting tests

**Files Modified**: 4 (prompts.py, models.py, templates, tests)
**Tests Added**: 5 formatting tests

### 4.2 Improve Think Tag Filtering

**Problem**: Think tag regex could miss edge cases

**Current Code** (validator.py lines 98-110):
```python
return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE).strip()
```

**Potential Issues**:
1. Nested tags: `<think><think>content</think></think>`
2. Malformed tags: `<think>content</thikn>`
3. Multiple tags with content between
4. Case variations (handled by IGNORECASE ✓)

**Solution**: Robust iterative filtering

```python
def remove_think_tags(self, text: str) -> str:
    """
    Remove all <think>...</think> tags from text, handling edge cases.

    Handles:
    - Nested tags
    - Malformed tags (within reason)
    - Multiple tags
    - Case variations

    Args:
        text: Text potentially containing think tags

    Returns:
        Text with all think tags removed
    """
    if not text or "<think>" not in text.lower():
        return text

    # Iteratively remove think tags (handles nested tags)
    max_iterations = 10  # Prevent infinite loop on malformed input
    iteration = 0

    while iteration < max_iterations:
        # Use non-greedy match with DOTALL (. matches newlines)
        cleaned = re.sub(
            r'<think>.*?</think>',
            '',
            text,
            flags=re.DOTALL | re.IGNORECASE
        )

        # If no change, we're done
        if cleaned == text:
            break

        text = cleaned
        iteration += 1

    # Log warning if max iterations reached (suggests malformed tags)
    if iteration >= max_iterations:
        logger.warning(f"Think tag removal reached max iterations: {max_iterations}")

    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Multiple blank lines -> double
    text = text.strip()

    return text
```

**Edge Case Tests**:
```python
# tests/unit/compliance/test_think_tag_filtering.py

def test_nested_think_tags():
    text = "<think>outer<think>inner</think>content</think>After"
    result = validator.remove_think_tags(text)
    assert result == "After"

def test_multiple_think_tags_with_content():
    text = "Before<think>A</think>Middle<think>B</think>After"
    result = validator.remove_think_tags(text)
    assert result == "BeforeMiddleAfter"

def test_malformed_closing_tag():
    # Should not remove if malformed
    text = "<think>content</thikn>After"
    result = validator.remove_think_tags(text)
    assert "<think>content</thikn>" in result  # Not removed

def test_case_variations():
    text = "<THINK>A</THINK><Think>B</Think><think>C</think>"
    result = validator.remove_think_tags(text)
    assert result == ""

def test_multiline_think_content():
    text = """
    Before
    <think>
    Line 1
    Line 2
    Line 3
    </think>
    After
    """
    result = validator.remove_think_tags(text)
    assert "Line 1" not in result
    assert "Before" in result
    assert "After" in result

def test_think_tag_with_attributes():
    # Edge case: tags with attributes (shouldn't happen but be defensive)
    text = '<think type="internal">content</think>After'
    result = validator.remove_think_tags(text)
    # Current regex won't match this - document limitation
    assert '<think type="internal">' in result or "After" == result
```

**Implementation**:
1. Update `remove_think_tags()` in `validator.py`
2. Add iterative removal for nested tags
3. Add malformed tag detection/logging
4. Add 6 edge case tests
5. Document known limitations (e.g., tags with attributes)

**Files Modified**: 2 (validator.py, tests)
**Tests Added**: 6 edge case tests

---

## Testing Strategy

### Test Coverage Goals

**Template Tests** (20 existing + updates):
- Verify all templates render without errors
- Verify macro inclusion (FCA neutrality, localization)
- Verify variable interpolation
- Regression tests for all changes

**Unit Tests** (40 new):
- FCA neutrality violation detection (8 tests)
- Conversational quality scoring (6 tests)
- Emotional evolution detection (6 edge cases)
- Think tag filtering (6 edge cases)
- Context retrieval (4 tests)
- Conversation formatting (5 tests)
- Cache control (3 tests)
- Validation strategy (8 tests)

**Integration Tests** (15 new):
- Complete guidance flow with populated context (4 tests)
- DB scheme detection and handling (1 test)
- Validation strategies (pre/post/hybrid) (3 tests)
- Quality assessment end-to-end (2 tests)
- Emotional state tracking across conversation (2 tests)
- Cache hit rate measurement (1 test)
- Refinement retry logic (2 tests)

**Regression Tests** (existing 20 + verification):
- Ensure all 20 template migrations still pass
- Verify no behavioral changes to existing consultations
- Validate backward compatibility where required

**E2E Tests** (frontend):
- Quality score display in admin dashboard
- Flagged consultations workflow
- Emotional state indicators in conversation view
- Validation reasoning display

### Test Execution Plan

```bash
# Phase 1: Template tests (after FCA consolidation)
pytest tests/templates/ -v

# Phase 2: Unit tests (after code changes)
pytest tests/unit/ -v

# Phase 3: Integration tests (after context retrieval)
pytest tests/integration/ -v

# Phase 4: Full suite
pytest -v

# Frontend tests
cd frontend && npm test && npm run test:e2e

# Performance tests (cache, quality scoring)
pytest tests/performance/ -v --benchmark
```

---

## Expected Outcomes

### FCA Compliance
✅ **Stronger neutrality enforcement** with explicit violation categories
✅ **Clearer boundaries** with borderline examples documented
✅ **Better detection** of combination risks and subtle violations
✅ **Proactive validation** prevents bad guidance from reaching users (HYBRID mode)
✅ **Required understanding checks** ensure customer comprehension

### Conversational Quality
✅ **Natural dialogue** with LLM-based quality assessment (not just keywords)
✅ **Better variety** through template detection and scoring
✅ **Deeper personalization** beyond name usage
✅ **Emotional intelligence** with confidence scoring and context-aware detection
✅ **Learning from success** via populated case/rule retrieval

### System Performance
✅ **Complete context retrieval** - advisor learns from past consultations
✅ **Optimized caching** with structured layers (static/semi-static/dynamic)
✅ **Better validation timing** with three-tier strategy (pre/post/hybrid)
✅ **Cost reduction** through prompt caching and efficient retrieval
✅ **Monitoring** via Phoenix tracing and cache metrics

### Code Maintainability
✅ **Reduced duplication** - single source of truth for FCA rules, localization
✅ **Consolidated instructions** - shared macros for common patterns
✅ **Clearer structure** - template organization and naming
✅ **Better documentation** - edge cases and limitations documented
✅ **Rich formatting** - conversation history with metadata for better context

---

## Implementation Checklist

### Phase 1: FCA Compliance (Week 1)
- [ ] Create `_shared/fca_neutrality.jinja` macro with borderline examples
- [ ] Update 3 templates to use FCA macro
- [ ] Add `IssueType` enum values (evaluative, social proof, combination)
- [ ] Enhance validator parsing logic
- [ ] Make understanding verification required
- [ ] Add FCA reasoning prompts (risk, DB, signposting)
- [ ] Update 20 template tests
- [ ] Add 8 new FCA violation tests
- [ ] Run full template test suite

### Phase 2: Conversational Quality (Week 2)
- [ ] Implement case/rule retrieval in `_retrieve_context()`
- [ ] Create `quality_assessment.jinja` template
- [ ] Add `_assess_conversational_quality_llm()` method
- [ ] Update emotional evolution detection with confidence
- [ ] Add negative context patterns for "okay"
- [ ] Add 4 context retrieval tests
- [ ] Add 6 quality assessment tests
- [ ] Add 6 emotional detection edge case tests
- [ ] Run integration tests

### Phase 3: System Performance (Week 3)
- [ ] Implement `ValidationStrategy` enum (pre/post/hybrid)
- [ ] Add validation caching layer
- [ ] Implement `_validate_with_retry()` with refinement
- [ ] Add `_flag_for_review()` with admin notification
- [ ] Update `guidance_cached.jinja` with structured layers
- [ ] Add cache metrics to Phoenix tracing
- [ ] Create `_shared/localization.jinja` macro
- [ ] Update SystemSettings with localization config
- [ ] Add 8 validation strategy tests
- [ ] Add 3 cache performance tests

### Phase 4: Code Quality (Week 4)
- [ ] Enhance `format_conversation()` with metadata
- [ ] Update Consultation model for rich conversation data
- [ ] Improve `remove_think_tags()` with iteration
- [ ] Add 5 formatting tests
- [ ] Add 6 think tag edge case tests
- [ ] Update admin dashboard for quality scores
- [ ] Update admin dashboard for flagged consultations
- [ ] Update admin dashboard for emotional indicators
- [ ] Run full test suite (417 + 40 new = 457 tests)
- [ ] Deploy to staging for QA

---

## Metrics and Success Criteria

### Compliance Metrics
- **Validation failure rate**: Target <1% (currently ~2%)
- **Human review flags**: Track rate over time
- **Violation categorization**: 100% of failures categorized by type
- **Refinement success rate**: >80% of failures fixed by automatic refinement

### Quality Metrics
- **Conversational quality score**: Average >0.80 (currently 0.75)
- **Language variety score**: Average >0.75 (currently 0.65)
- **Personalization depth**: Average >0.80 (currently name-only)
- **Emotional tracking confidence**: Average >0.75

### Performance Metrics
- **Cache hit rate**: Target >60% for static content
- **Token savings**: Measure reduction from caching
- **Cost per consultation**: Target 15% reduction from caching
- **Context retrieval usage**: Cases/rules populated in 100% of requests
- **Validation latency**: HYBRID mode <500ms overhead

### System Metrics
- **Test coverage**: Maintain >90% (currently 92%)
- **Code duplication**: Reduce by 30% (FCA rules, localization)
- **Template consistency**: 100% use shared macros
- **Documentation coverage**: All edge cases documented

---

## Risks and Mitigations

### Risk 1: LLM-based quality scoring increases latency
**Impact**: Medium
**Probability**: High
**Mitigation**:
- Use fast model (GPT-4-mini, Claude Haiku) for quality assessment
- Run quality scoring in background (doesn't block streaming)
- Add fallback to keyword-based scoring if LLM fails
- Cache quality assessments for similar guidance patterns

### Risk 2: Pre-stream validation hurts user experience
**Impact**: High
**Probability**: Medium
**Mitigation**:
- Default to HYBRID mode (best balance)
- Only use PRE_STREAM for high-risk situations (DB schemes)
- Optimize validation prompt for speed
- Use prompt caching for validation template

### Risk 3: Context retrieval increases database load
**Impact**: Medium
**Probability**: Medium
**Mitigation**:
- Add pgvector indexes on all embedding columns
- Implement connection pooling
- Add Redis cache for recent retrievals
- Monitor query performance with Phoenix

### Risk 4: Breaking changes affect existing consultations
**Impact**: Low (acceptable per user)
**Probability**: High
**Mitigation**:
- Version the template system (v1, v2)
- Store template version in Consultation model
- Add migration script to regenerate if needed
- Comprehensive testing before deployment

### Risk 5: Increased complexity makes system harder to maintain
**Impact**: Medium
**Probability**: Medium
**Mitigation**:
- Comprehensive documentation (this document)
- Code comments for complex logic
- Keep existing behavior as fallback options
- Training for team on new architecture

---

## Future Enhancements (Out of Scope)

These improvements are valuable but not included in current plan:

1. **Multi-language support**: Extend beyond British English
2. **Voice tone adaptation**: Adjust formality based on customer preference
3. **Proactive guidance**: Suggest topics customer hasn't considered
4. **A/B testing framework**: Systematically test prompt variations
5. **Reinforcement learning**: Learn from human review feedback
6. **Multi-modal input**: Accept documents, screenshots for context
7. **Real-time compliance alerts**: Admin dashboard for monitoring violations
8. **Customer feedback loop**: Integrate satisfaction ratings into quality scoring

---

## Appendix: Key Files and Line Numbers

### Templates
- `guidance_main.jinja` (140 lines) - FCA lines 71-108
- `guidance_with_reasoning.jinja` (78 lines) - FCA lines 30-66
- `validation.jinja` (160 lines) - FCA lines 43-90, checks 63-83
- `reasoning.jinja` (52 lines) - Vague prompt line 39
- `compliance_refinement.jinja` (59 lines)
- `borderline_strengthening.jinja` (44 lines)

### Agent Code
- `agent.py` - AdvisorAgent class
  - Line 82-133: `provide_guidance()`
  - Line 135-191: `provide_guidance_stream()`
  - Line 317-381: `_retrieve_context()` ⚠️ Empty cases/rules 377-379
  - Line 553-665: `_calculate_conversational_quality()`
  - Line 667-726: `_detect_conversation_phase()`
  - Line 728-872: `_assess_emotional_state()` ⚠️ "okay" detection 817-850

### Validation
- `validator.py` - ComplianceValidator class
  - Line 98-110: `remove_think_tags()`
  - Line 112-153: `validate()` LLM-as-judge
  - Line 241-394: `_parse_validation_response()`
  - Line 287-346: Issue parsing ⚠️ Missing explicit categories

### Retrieval
- `retriever.py`
  - Line 48-128: CaseBase with conversational re-ranking
  - Line 96-112: Conversational boost logic

### Prompts
- `prompts.py`
  - Line 71-89: `format_conversation()` ⚠️ Basic formatting

---

**Document Version**: 1.0
**Last Updated**: 2025-01-06
**Next Review**: After Phase 2 completion