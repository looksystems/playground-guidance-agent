# Advisor Agent Specification

## Overview

The Advisor Agent is an LLM-powered agent that provides FCA-compliant pension guidance to customers. It combines the cognitive architecture from Generative Agents (Simulacra) with the learning mechanisms from Agent Hospital (MedAgent-Zero).

## Agent Profile

Each advisor agent is initialized with a natural language profile:

```python
class AdvisorProfile:
    name: str
    role: str  # "Pension Guidance Specialist"
    expertise: List[str]  # ["pension consolidation", "retirement planning", "contribution advice"]
    personality: str  # "Patient, clear communicator, detail-oriented, empathetic"
    experience_level: str  # "junior" | "intermediate" | "senior" (evolves with practice)
    communication_style: str  # "Uses simple language, checks understanding frequently, analogies for complex concepts"
```

**Example Initialization:**

```
Sarah Chen is a pension guidance specialist at [Financial Institution]. She has
expertise in pension consolidation, contribution planning, and retirement age
guidance. Sarah is known for her patient, clear communication style. She
excels at explaining complex pension concepts using everyday analogies and
always verifies customer understanding before moving forward. Sarah is committed
to providing balanced, FCA-compliant guidance that empowers customers to make
informed decisions about their pensions.
```

## Cognitive Architecture

The advisor agent operates on a **perceive → retrieve → reflect → plan → act** cycle adapted from Simulacra.

### 1. Perception

The agent perceives customer inputs and environmental context.

**Inputs Perceived:**
- Customer statements (questions, concerns, clarifications)
- Customer profile data (age, income, pension details, goals)
- Emotional/comprehension signals (confusion, understanding, anxiety)
- Environmental context (FCA regulation updates, market conditions)

**Perception Processing:**

```python
def perceive(customer_input: str, customer_profile: Dict, context: Dict) -> List[Observation]:
    """
    Processes inputs and creates observation memories.
    """
    observations = []

    # Parse customer statement
    observations.append(Observation(
        description=f"Customer stated: '{customer_input}'",
        importance=rate_importance(customer_input),
        timestamp=now
    ))

    # Detect comprehension signals
    understanding_level = assess_understanding(customer_input)
    observations.append(Observation(
        description=f"Customer comprehension level: {understanding_level}",
        importance=7.0 if understanding_level == "low" else 3.0,
        timestamp=now
    ))

    # Detect emotional signals
    if detect_anxiety(customer_input):
        observations.append(Observation(
            description="Customer expressing anxiety about pension decisions",
            importance=8.0,
            timestamp=now
        ))

    return observations
```

### 2. Retrieval

Uses RAG to retrieve relevant context from memory stream, case base, and rules base (see architecture.md for details).

**Query Formulation:**

Different queries for different tasks:

```python
def formulate_query(task_type: TaskType, customer_situation: str) -> str:
    """
    Creates query for RAG retrieval based on current task.
    """
    queries = {
        TaskType.RISK_ASSESSMENT: f"What factors should I consider for risk assessment given: {customer_situation}?",
        TaskType.CONSOLIDATION_ADVICE: f"What are pros and cons of consolidation for: {customer_situation}?",
        TaskType.CONTRIBUTION_PLANNING: f"How should I guide contribution levels for: {customer_situation}?",
        TaskType.UNDERSTANDING_CHECK: f"How can I verify customer understands: {customer_situation}?"
    }
    return queries.get(task_type, customer_situation)
```

**Retrieved Context Structure:**

```python
class RetrievedContext:
    memories: List[MemoryNode]  # Top-10 relevant memories
    cases: List[Case]  # Top-3 similar customer cases
    rules: List[GuidanceRule]  # Top-4 applicable rules
    fca_requirements: List[str]  # Relevant FCA compliance requirements
    reasoning: str  # Why this context was selected
```

### 3. Decision Making

The agent decides whether to continue its current plan or react to new information.

**Decision Prompt:**

```
[Advisor Profile: Sarah Chen, Pension Guidance Specialist]

Current Plan:
- Phase 2 (10 minutes remaining): Explain consolidation benefits and risks

Customer Situation:
- Customer: "Wait, I'm confused. What exactly is a defined benefit pension?"

Recent Relevant Memories:
- Customer previously expressed low confidence with pension terminology
- Customer responded well to savings account analogy earlier
- FCA requirement: Verify understanding before proceeding with guidance

Should Sarah react to this observation, and if so, what would be an appropriate reaction?
```

**Output:**
```json
{
  "should_react": true,
  "reason": "Customer is confused about key terminology needed for consolidation discussion",
  "reaction_type": "clarify_concept",
  "resume_plan": true
}
```

### 4. Response Generation

Generates guidance using LLM with retrieved context.

**Prompting Strategy (Multi-Part Structure):**

#### Part 1: Advisor Identity & Role

```
You are Sarah Chen, a pension guidance specialist at [Financial Institution].

Your expertise includes:
- Pension consolidation guidance
- Contribution planning
- Retirement age planning

Your communication style:
- Patient and empathetic
- Use simple language and everyday analogies
- Check customer understanding frequently
- Provide balanced views (pros and cons)

Your role is to provide FCA-compliant GUIDANCE (not regulated advice):
- Help customers understand their options
- Explain benefits and risks clearly
- Empower customers to make informed decisions
- Do NOT make personal recommendations or tell customers what they "should" do
```

#### Part 2: Customer Context

```
Current Customer Profile:
- Name: John Thompson
- Age: 55
- Occupation: Teacher
- Pension situation: 4 separate pensions (total value £250,000)
  - Workplace pension 1: £120,000 (defined contribution)
  - Workplace pension 2: £80,000 (defined contribution)
  - Old workplace: £35,000 (defined benefit - valuable guaranteed income)
  - Personal pension: £15,000 (high fees)
- Goals: Simplify pensions, reduce fees, retire at 65
- Risk tolerance: Moderate
- Financial literacy: Low-moderate (struggles with technical terms)
```

#### Part 3: Conversation History Summary

```
Conversation so far:
1. Customer asked about combining pensions to simplify
2. You explained what pension consolidation means using analogy to combining bank accounts
3. Customer understood the basic concept and seemed interested
4. You began explaining benefits (lower fees, easier management)
5. Customer just asked: "What exactly is a defined benefit pension?"

Current phase: Explaining consolidation benefits and risks
```

#### Part 4: Retrieved Context

```
Similar Cases (from Case Base):

Case #127: Customer aged 54 with DB pension
- Customer situation: Similar mix of DB and DC pensions
- Guidance provided: Explained DB pension as "guaranteed monthly income like a salary in retirement, very valuable"
- Used analogy: "DB pension is like a promise from employer to pay you £X per month for life"
- Outcome: Customer understood importance of DB guarantees, chose to consolidate only DC pensions
- Compliance: FCA validated ✓

Case #089: Customer with low literacy asking about DB pensions
- Explained: "Defined Benefit means the benefit (money you get) is defined (fixed) in advance"
- Contrasted with DC: "Defined Contribution means contribution (money you put in) is defined, but what you get depends on investment growth"
- Customer feedback: "That makes sense now, thanks for explaining in plain English"

Case #213: DB pension consolidation consideration
- Key point emphasized: "DB pensions have valuable guarantees that disappear if you transfer out"
- Risk highlighted: "Most people would be worse off transferring from DB to DC pension"
- FCA compliance: Stressed this is general information, not personal recommendation

Relevant Rules (from Rules Base):

Rule #034: Explaining defined benefit pensions
- "When explaining DB pensions to customers with low financial literacy, use analogy to salary/income guarantee rather than technical definitions"
- Confidence: 0.92 | FCA Compliant: ✓
- Evidence: Successfully used in cases 127, 089, 156, 201, 213

Rule #071: DB pension consolidation warning
- "Always emphasize DB pensions have valuable guarantees before discussing consolidation; most people would lose out by transferring away from DB"
- Confidence: 0.98 | FCA Compliant: ✓
- Evidence: FCA guidance, cases 213, 187, 098

Rule #103: Checking understanding
- "After explaining technical concepts, ask open-ended questions like 'Can you explain that back to me in your own words?' rather than 'Does that make sense?'"
- Confidence: 0.87 | FCA Compliant: ✓
- Evidence: Cases 089, 167, 204, 299

FCA Requirements:
- Clear, fair, and not misleading communication
- Appropriate for customer's knowledge and experience
- Explain technical terms in plain language
- Balance benefits with risks
- Verify customer understanding
```

#### Part 5: Task & Constraints

```
Current Task: Respond to customer's question "What exactly is a defined benefit pension?"

Constraints:
- Use simple, clear language appropriate for customer's literacy level
- Provide analogy or everyday comparison to aid understanding
- Explain in context of why this matters for their consolidation consideration
- Prepare to warn about value of DB guarantees (don't rush, but set up for it)
- Check customer understanding before proceeding
- Stay within FCA guidance boundary (provide information, not personal recommendation)

Language to AVOID (regulated advice):
- "You should..."
- "I recommend..."
- "The best option for you is..."
- "You need to..."

Language to USE (FCA-compliant guidance):
- "You could consider..."
- "Some people choose to..."
- "Options available to you include..."
- "One thing to think about is..."

Generate response (max 150 words):
```

**Example Generated Response:**

```
Good question, John. Let me explain what makes a defined benefit pension special.

Think of a defined benefit pension like a guaranteed monthly salary that your
former employer has promised to pay you in retirement. They've committed to
giving you a specific amount each month for the rest of your life, no matter
how long you live or what happens in the stock market.

Your other pensions - the defined contribution ones - work differently. With
those, the amount you'll get depends on how much was paid in and how well the
investments perform. There's no guarantee.

The defined benefit pension you mentioned (the £35,000 one from your old workplace)
likely comes with valuable guarantees that the others don't have. That's important
to understand as we discuss consolidation options.

Can you explain back to me in your own words what makes a DB pension different?
I want to make sure this makes sense before we continue.
```

### 5. Chain-of-Thought Reasoning (from Agent Hospital)

For complex decisions (e.g., consolidation suitability), the agent uses step-by-step reasoning before generating guidance.

**Reasoning Prompt:**

```
Based on the customer profile and retrieved context, think through this step-by-step:

Customer: John Thompson, 55, 4 pensions including 1 DB pension
Question: Should consolidation be considered for this customer?

Think through:
(1) What are the key features of this customer's pension situation?
(2) What does the retrieved context tell us about similar cases?
(3) What rules or principles apply here?
(4) What are the potential benefits of consolidation for this customer?
(5) What are the risks or warnings needed?
(6) What guidance can I provide within FCA boundary?

Reasoning:
```

**Example Reasoning Output:**

```
(1) Customer has 4 pensions: 3 defined contribution (£215k total) and 1 defined benefit (£35k).
    DB pension is a significant portion. Customer goal is simplification and fee reduction.

(2) Retrieved case #127 shows similar situation - customer consolidated only DC pensions,
    kept DB pension separate due to valuable guarantees. Case #213 emphasizes DB transfer
    risks. Both cases had successful outcomes with this approach.

(3) Rule #071 applies: Must emphasize DB guarantees and typical loss from transferring.
    Rule #034: Explain DB in simple terms (already addressed in previous response).
    FCA requires balanced view and clear risk disclosure.

(4) Potential benefits:
    - Could consolidate 3 DC pensions into one (simplification)
    - May reduce overall fees (personal pension has high fees)
    - Easier to manage and track

(5) Risks/warnings:
    - CRITICAL: DB pension should almost certainly not be consolidated (valuable guarantees)
    - Need to check for other valuable features (guaranteed annuity rates, protected tax-free cash)
    - Consolidation has costs (exit fees, transfer delays)
    - May lose some fund choices or features

(6) Guidance approach:
    - Explain consolidation CAN be considered for the 3 DC pensions
    - Strongly caution against DB pension transfer (this requires regulated advice anyway)
    - Present pros and cons of DC consolidation
    - Signpost to regulated adviser if customer wants personal recommendation
    - Verify understanding throughout
```

### 6. FCA Compliance Validation

Every response is checked by the **HybridComplianceValidator** before delivery. This uses a two-stage process: rule-based hard constraints, then LLM-as-judge consensus.

**Hybrid Validation Process:**

```python
def validate_guidance(customer_profile: Dict, guidance: str, reasoning: str,
                      mode: str = "production") -> ValidationResult:
    """
    Two-stage hybrid validation with confidence scoring.
    """
    validator = HybridComplianceValidator(mode=mode)

    # STAGE 1: Rule-based checks (binary pass/fail)
    rule_checks = [
        check_db_pension_warning(guidance, customer_profile),  # Critical!
        check_prohibited_language(guidance),  # "should", "recommend", etc.
        check_signposting_present(guidance, customer_profile),
        check_risk_keywords_present(guidance)  # Must mention risks
    ]

    if any(not check.passed for check in rule_checks):
        return ValidationResult(
            passed=False,
            confidence=1.0,
            source="RULE_BASED",
            issues=[c.issue for c in rule_checks if not c.passed],
            requires_human_review=False  # Clear violation
        )

    # STAGE 2: LLM-as-judge consensus (nuanced evaluation)
    judge_results = []
    for judge in validator.judges:
        result = judge.evaluate_with_confidence(
            guidance=guidance,
            customer=customer_profile,
            reasoning=reasoning
        )
        judge_results.append(result)

    # Compute consensus
    consensus = compute_consensus(judge_results)

    # STAGE 3: Confidence-based decision
    if consensus.confidence < validator.confidence_threshold:
        return ValidationResult(
            passed=False,
            confidence=consensus.confidence,
            source="LLM_JUDGE_CONSENSUS",
            issues=["LOW_CONFIDENCE_REQUIRES_HUMAN_REVIEW"],
            requires_human_review=True,
            judge_details=judge_results
        )

    return ValidationResult(
        passed=consensus.passed,
        confidence=consensus.confidence,
        source="LLM_JUDGE_CONSENSUS",
        issues=consensus.issues,
        requires_human_review=False
    )
```

**LLM Judge Evaluation Prompt:**

Each judge evaluates guidance using this structured prompt:

```python
judge_prompt = f"""
You are an FCA compliance officer with expertise in the guidance vs advice boundary.
Evaluate this pension guidance for regulatory compliance.

Customer Profile:
{json.dumps(customer_profile, indent=2)}

Guidance Provided:
"{guidance}"

Advisor Reasoning:
{reasoning}

FCA Context:
{fca_knowledge_snippets}

EVALUATION CRITERIA:

1. GUIDANCE vs ADVICE BOUNDARY (CRITICAL):
   - GUIDANCE: General information, options, considerations ("could consider", "some people")
   - ADVICE: Personal recommendation, specific direction ("should", "recommend", "best for you")
   - Assess: Does this cross into personal recommendation territory?
   - Look for disguised recommendations: "might want to", "I'd probably", etc.

2. RISK DISCLOSURE ADEQUACY:
   - Are risks explained with sufficient detail and clarity?
   - Is the view balanced (benefits AND drawbacks)?
   - For DB pension: Are guarantees and transfer risks explicitly mentioned?

3. CUSTOMER UNDERSTANDING VERIFICATION:
   - Are verification questions open-ended vs yes/no?
   - Do questions genuinely test comprehension vs box-ticking?

4. LANGUAGE APPROPRIATENESS:
   - Is jargon level appropriate for customer's financial literacy?
   - Are technical terms explained in accessible language?
   - Is tone professional but not alienating?

5. CONTEXTUAL APPROPRIATENESS:
   - Does guidance fit customer's actual situation and goals?
   - Is reasoning chain sound and well-supported?
   - Are retrieved cases/rules correctly applied?

Return JSON:
{{
  "passed": true/false,
  "confidence": 0.0-1.0,  // Your confidence in this evaluation
  "issues": ["specific issue 1", "specific issue 2"],
  "reasoning": "Detailed explanation of your evaluation",
  "boundary_classification": "GUIDANCE" | "ADVICE" | "BORDERLINE",
  "severity": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
}}

IMPORTANT: If you're uncertain about the boundary (confidence < 0.8), mark as BORDERLINE.
"""
```

**Confidence Thresholds by Mode:**

```python
CONFIDENCE_THRESHOLDS = {
    "training": 0.6,      # Lenient - allow exploration, learn from borderline
    "production": 0.9,    # Conservative - escalate uncertainty to humans
    "batch_qa": 0.95      # Very strict - quality assurance audits
}
```

**Example: Borderline Cases Requiring Human Review**

```python
# Case 1: Disguised Recommendation (Judge Disagreement)
guidance_1 = "Given your situation, you might want to consider consolidating those pensions."

Judge 1 (GPT-4): FAIL, confidence=0.75, "might want to" is softened recommendation
Judge 2 (Claude): PASS, confidence=0.70, "consider" is option language
Judge 3 (GPT-4 v2): FAIL, confidence=0.82, implicit personal direction

Consensus: FAIL, confidence=0.76 → HUMAN REVIEW (below 0.9 threshold)

# Case 2: Risk Disclosure Adequacy (Low Confidence)
guidance_2 = "Consolidation simplifies management and may reduce fees, though you'd need to
check for exit charges."

Judge 1: PASS, confidence=0.65, risks mentioned but brief
Judge 2: FAIL, confidence=0.72, insufficient detail on "may reduce fees"
Judge 3: PASS, confidence=0.68, exit charges mentioned

Consensus: Mixed votes, avg confidence=0.68 → HUMAN REVIEW (below 0.9 threshold)

# Case 3: Clear Pass (High Confidence)
guidance_3 = "Consolidation is one option some people consider. Benefits include simpler
management and potentially lower fees. However, risks include possible exit charges, loss
of fund options, and transfer delays. Can you walk me through your current pension setup
so we can explore what might make sense for your situation?"

All Judges: PASS, confidence=0.95+ → APPROVED (above 0.9 threshold)
- Clear option language, balanced view, open-ended question, no recommendation

# Case 4: Clear Fail (Rule Violation)
guidance_4 = "You should definitely consolidate your pensions into a single pot."

Rule Check: FAIL (prohibited "should" detected) → REJECTED immediately
- No LLM judges needed, clear violation
```

**Handling Validation Results:**

```python
# In advisor agent cognitive loop
validation = validate_guidance(customer.profile, guidance, reasoning, mode="production")

if validation.requires_human_review:
    # Escalate to compliance expert
    review_ticket = enqueue_for_human_review(
        customer=customer,
        guidance=guidance,
        validation=validation,
        priority="HIGH" if validation.confidence < 0.5 else "NORMAL"
    )

    # Provide fallback response
    response = f"""
    Your question requires careful consideration of FCA compliance boundaries.
    I've escalated this to a compliance expert who will review within 24 hours.
    Reference: {review_ticket.id}
    """

elif not validation.passed:
    # Failed validation - refine guidance
    refinement_prompt = f"""
    Your guidance failed FCA compliance validation.

    Issues identified:
    {validation.issues}

    Original guidance: "{guidance}"

    Please revise to address these issues while maintaining helpfulness.
    """

    guidance = llm_refine(refinement_prompt, context)

    # Re-validate (allow 1 retry)
    validation = validate_guidance(customer.profile, guidance, reasoning)

    if not validation.passed:
        # Still failing - escalate to human
        enqueue_for_human_review(customer, guidance, validation)
        response = fallback_response()
    else:
        response = guidance

else:
    # Passed validation - deliver guidance
    response = guidance
```

**Benefits of LLM-as-Judge Approach:**

1. **Nuanced Boundary Detection:** Catches disguised recommendations ("might want to", "I'd probably")
2. **Confidence Scoring:** Enables risk stratification and human escalation
3. **Natural Language Feedback:** Helps advisor agent learn WHY something fails
4. **Consensus Reduces Bias:** Multiple judges catch what one might miss
5. **Adaptable:** Prompts update faster than hardcoded rules when FCA guidance evolves

### 7. Action Execution

Once validated, the guidance is delivered to the customer.

**Actions:**
- Textual response (primary)
- Provide document/link (if requested)
- Signpost to regulated adviser (when needed)
- Update customer profile with new information

## Prompting Strategies Summary

### Key Techniques from Papers

1. **Structured Prompts** (Agent Hospital approach)
   - Part 1: Identity & role
   - Part 2: Customer context
   - Part 3: Conversation history
   - Part 4: Retrieved context (cases, rules, FCA requirements)
   - Part 5: Task & constraints

2. **Chain-of-Thought Reasoning** (Agent Hospital)
   - Step-by-step analysis before guidance
   - Citations to retrieved cases and rules
   - Explicit consideration of benefits and risks

3. **Memory-Informed Generation** (Simulacra)
   - Retrieval of relevant past experiences
   - Adaptation based on what worked before
   - Reflection-based insights inform approach

4. **Natural Language Throughout**
   - All context in natural language (not code or rigid structures)
   - Reasoning explanations stored as memories
   - Cases and rules in plain English

### Prompt Templates

#### Template 1: Initial Customer Inquiry

```
System: You are {advisor_name}, a pension guidance specialist.

[Advisor profile and communication style]

Customer Profile:
{customer_demographics}
{pension_situation}
{goals_and_concerns}

The customer has just said: "{customer_input}"

Retrieved Context:
[Similar cases from case base]
[Relevant rules from rules base]
[FCA compliance requirements]

Task: Provide an appropriate opening response that:
1. Acknowledges customer's inquiry
2. Begins to understand their situation
3. Sets expectations for guidance vs. advice
4. Starts building rapport

Language constraints: Use FCA-compliant guidance language (not advice).

Your response:
```

#### Template 2: Risk Disclosure

```
System: You are {advisor_name}, a pension guidance specialist.

Customer: {customer_name}, age {age}
Situation: {pension_situation}

The customer is considering: {action_being_considered}

Retrieved Context:
[Cases showing outcomes of this action]
[Rules about risk disclosure for this action]
[FCA requirements for this scenario]

Your chain of thought:
(1) What are the main risks the customer should understand?
(2) How can I explain these risks clearly given their literacy level?
(3) What examples or analogies would help?
(4) How do I ensure balance (not just risks, but also potential benefits)?

Based on your reasoning, explain the key risks the customer should consider.
Use clear, simple language. Provide balance. Check understanding.

Your response (max 200 words):
```

#### Template 3: Understanding Verification

```
System: You are {advisor_name}, a pension guidance specialist.

You just explained: "{concept_explained}"

Customer's knowledge level: {literacy_level}
Importance of understanding this: {importance_reason}

Retrieved Context:
[Rules about effective understanding checks]
[Cases showing what worked for similar customers]

Task: Ask an open-ended question to verify the customer understood your explanation.

Guidelines:
- Don't ask "Does that make sense?" (customers often say yes even if confused)
- Ask them to explain back in their own words
- Or ask how they would apply the concept to their situation
- Keep it conversational, not like a test

Your question:
```

#### Template 4: Signposting to Regulated Advice

```
System: You are {advisor_name}, a pension guidance specialist.

Customer: {customer_name}
Situation: {situation_summary}

The customer has asked: "{customer_request}"

Your assessment: This question requires regulated financial advice, which is
outside the FCA guidance boundary.

Retrieved Context:
[Cases where signposting was done well]
[FCA requirements for signposting]

Task: Politely explain to the customer that:
1. This type of decision requires regulated advice (not guidance)
2. The difference between guidance and advice
3. How they can access a regulated financial adviser
4. You're still here to help with general information

Tone: Helpful and supportive (not defensive or bureaucratic)

Your response:
```

## Reasoning Approach: Chain-of-Thought vs Thinking Modes

### Decision: Use Chain-of-Thought for Customer Guidance

The advisor agent uses **explicit chain-of-thought (CoT) prompting** rather than models with native "thinking modes" (e.g., Claude with extended thinking, OpenAI o1) for customer-facing guidance generation.

### Rationale

This decision was made based on three key priorities for a regulated financial services application:

#### 1. Regulatory Compliance & Transparency

**Chain-of-Thought Advantages:**
- **Full reasoning visibility**: All reasoning is captured in structured format aligned with FCA principles
- **Auditable process**: Regulators can review exactly how guidance was generated
- **Controlled reasoning structure**: 6-step framework ensures all FCA requirements are addressed
- **Validated approach**: LLM-as-judge validation system calibrated for CoT reasoning patterns

**Thinking Mode Concerns:**
- **Extended thinking (Claude)**: Verbose, freeform reasoning that may be harder for regulators to audit
- **OpenAI o1**: Hidden reasoning is completely opaque, incompatible with regulatory transparency requirements
- **Validation complexity**: Would require re-calibrating entire LLM-as-judge system and expert validation

**FCA Considerations:**
When regulators ask "How does the AI reason about guidance?", we can demonstrate:
- Clear 6-step reasoning framework aligned with FCA principles
- Explicit consideration of customer context, risks, and compliance boundaries
- Transparent process suitable for regulatory submissions

#### 2. Provider Flexibility & Resilience

**Chain-of-Thought Advantages:**
- **Works with any LLM**: GPT-4o, Claude Sonnet, GPT-5 (future), local models
- **Robust fallback strategy**: LiteLLM can seamlessly switch providers if one fails
- **No vendor lock-in**: Not dependent on specific model capabilities
- **Future-proof**: As new models emerge, CoT approach transfers immediately

**Thinking Mode Limitations:**
- **Provider-specific**: Extended thinking (Claude only), o1 (OpenAI only)
- **Fallback complexity**: If primary model fails, fallback must use different reasoning approach
- **Version dependency**: Thinking mode behavior changes with model versions

#### 3. Cost & Latency Efficiency

**Chain-of-Thought Performance:**
- **Cost**: 30-50% cheaper than extended thinking, 75-90% cheaper than o1
- **Latency**: 2-5s typical response time, meets SLA requirements
- **Predictable**: Token usage scales linearly with prompt complexity

**Thinking Mode Trade-offs:**
- **Extended thinking**: +50-100% cost, +2-10s latency (budget tokens required)
- **OpenAI o1**: 3-5x more expensive, 15-30s latency (slower reasoning process)
- **Variable**: Thinking time unpredictable, difficult to guarantee response SLAs

### Current Chain-of-Thought Implementation

**6-Step Reasoning Framework:**

```python
reasoning_prompt = """
Based on the customer profile and retrieved context, think through this step-by-step:

(1) What are the key features of this customer's pension situation?
(2) What does the retrieved context tell us about similar cases?
(3) What rules or principles apply here?
(4) What are the potential benefits for this customer?
(5) What are the risks or warnings needed?
(6) What guidance can I provide within FCA boundary?

Reasoning:
"""
```

**Benefits:**
- **FCA-aligned structure**: Each step maps to regulatory requirements
- **Evidence-based**: Explicitly cites retrieved cases and rules (step 2, 3)
- **Balanced view**: Separates benefits (step 4) from risks (step 5)
- **Compliance check**: Final step (6) ensures guidance boundary respected
- **Traceable**: All reasoning stored and available for audit

### Decision Criteria for Reconsideration

This decision will be revisited if thinking modes demonstrate:

1. **Significantly Better Compliance** (>20% improvement)
   - Blind expert evaluation shows thinking modes produce better FCA-compliant guidance
   - Measured improvement in compliance pass rates, risk disclosure quality, or boundary adherence

2. **Superior Edge Case Handling**
   - Demonstrable improvement in handling complex, ambiguous scenarios
   - Better reasoning quality in borderline cases that current CoT struggles with

3. **Regulatory Approval**
   - FCA explicitly approves or prefers extended thinking approaches
   - Auditability concerns resolved through standardized thinking extraction

**Measurement Protocol:**
If considering a switch, conduct:
- Blind evaluation by FCA compliance experts (200+ consultations)
- Side-by-side comparison: CoT vs thinking mode on same test cases
- Statistical analysis of compliance quality, reasoning soundness, edge case performance
- Cost-benefit analysis including latency impact and regulatory approval risk

### Potential Hybrid Approach (Future Consideration)

**When to Consider Extended Thinking:**

While chain-of-thought is the primary approach, extended thinking could be evaluated for:

1. **Learning Phase (Lower Risk)**
   - Use extended thinking in `learning/reflection.py` for failure analysis
   - Offline process, not customer-facing, latency doesn't matter
   - Potential benefit: Better extraction of complex patterns from failures
   - Cost impact: +$20-30 per 5,000-customer training run (+5%)
   - **Status**: Deferred until after Phase 6 completion

2. **Complex Edge Cases (Higher Risk)**
   - Use extended thinking only for consultations flagged as "high complexity"
   - Requires regulatory approval and validation study
   - Would need dual validation: CoT reasoning + extended thinking
   - **Status**: Requires evidence from learning phase experiments first

**Not Recommended:**
- **OpenAI o1 for any purpose**: Hidden reasoning violates regulatory transparency requirements

### Implementation Status

✅ **Current Implementation** (Phase 3 completed):
- Chain-of-thought reasoning implemented in `advisor/agent.py`
- Optional CoT mode via `use_reasoning=True` parameter
- Reasoning templates in `advisor/prompts.py`
- 196 tests passing, 100% compliance with FCA validation

📋 **Future Evaluation** (After Phase 6):
- Extended thinking experiments for learning phase
- Comparative training runs to measure rule quality improvement
- Decision: Keep if >10% quality improvement, otherwise revert to CoT-only

### Related Documentation

- Implementation: `src/guidance_agent/advisor/agent.py` (lines 150-180)
- Prompt templates: `src/guidance_agent/advisor/prompts.py`
- Validation system: `src/guidance_agent/compliance/validator.py`
- Learning system: `specs/learning-system.md`

---

## Agent Evolution

The advisor agent improves over time through the learning mechanisms detailed in `learning-system.md`.

**Evolution Metrics:**

```python
class AdvisorMetrics:
    consultations_completed: int
    case_base_size: int  # Grows with experience
    rules_base_size: int  # Grows through reflection
    compliance_pass_rate: float  # % of guidance passing FCA validation first time
    customer_satisfaction: float  # Average satisfaction score
    understanding_verification_rate: float  # % of consultations where understanding checked
    signposting_rate: float  # % of out-of-boundary requests properly signposted
```

**Experience Levels:**

- **Junior** (0-100 consultations): Relies heavily on retrieved cases and rules, may over-explain
- **Intermediate** (100-500 consultations): Developing own style, better at reading customer comprehension
- **Senior** (500+ consultations): Natural communication, anticipates customer needs, handles edge cases smoothly

## Example End-to-End Interaction

**Customer:** "I have 4 different pensions from old jobs. It's confusing to manage them all. Can I just combine them into one?"

**Advisor Internal Process:**

1. **Perceive:**
   - Customer has multiple pensions, experiencing management complexity
   - Considering consolidation
   - Importance: 8/10 (significant financial decision)

2. **Retrieve:**
   - Query: "Should customer consider pension consolidation for multiple pensions?"
   - Retrieved 3 cases of similar multi-pension situations
   - Retrieved 4 rules about consolidation guidance
   - Retrieved FCA requirements for consolidation discussions

3. **Reflect:**
   - Pattern: Customers often focus on simplification benefit but unaware of risks
   - Need to balance customer's desire with comprehensive risk disclosure
   - Must check for DB pensions (critical warning needed)

4. **Plan:**
   - Phase 1: Acknowledge desire to simplify, gather more info about pensions
   - Phase 2: Explain what consolidation means
   - Phase 3: Present benefits AND risks
   - Phase 4: Check for valuable features (DB, guarantees)
   - Phase 5: Guide on next steps (might need regulated advice)

5. **Generate Response:**

**Advisor:** "I can understand why managing 4 separate pensions feels complicated, John. Consolidation - combining your pensions into one pot - is something many people consider for exactly that reason.

Before we explore whether consolidation could work for you, I'd like to understand a bit more about your pensions. Do you know what types they are? Specifically, are any of them 'defined benefit' pensions - the kind that promise you a set income in retirement?"

6. **Validate:**
   - Compliance check: PASS
   - Language appropriate: ✓
   - Open-ended question: ✓
   - Sets up risk discussion: ✓

7. **Store:**
   - Conversation added to memory stream
   - Customer inquiry importance: 8/10
   - Awaiting customer response to continue

**Customer:** "I'm not sure... how would I know?"

**Advisor Internal Process:**

1. **Perceive:** Customer doesn't know pension types (common with low financial literacy)
2. **Retrieve:** Rules about helping customers identify DB pensions
3. **Plan:** Help customer identify pension types, emphasize DB importance
4. **Generate:**

**Advisor:** "Good question! Here's an easy way to check. Look at your pension statements:

- If it says you'll get a specific amount per month when you retire (like '£500 per month from age 65'), that's a defined benefit pension - these are very valuable and need special consideration.

- If it shows a pot of money (like '£50,000') that you've built up, that's likely a defined contribution pension.

Defined benefit pensions have guarantees that would usually be lost if you consolidated them - which is why it's crucial to identify them first. Could you check your statements and let me know what you find?"

**[Interaction continues with advisor gradually building understanding, presenting balanced information, disclosing risks, and ultimately helping customer understand their options]**

## Summary

The Advisor Agent combines:
- **Memory-driven cognition** from Simulacra (perceive, retrieve, reflect)
- **RAG-based decisions** from Agent Hospital (cases + rules)
- **Chain-of-thought reasoning** for transparency
- **FCA compliance validation** at every step
- **Natural language** throughout for explainability
- **Continuous evolution** through virtual and real-world practice

See related specifications:
- `architecture.md`: Overall system architecture
- `customer-agent.md`: Customer simulation for training
- `virtual-environment.md`: Training environment design
- `learning-system.md`: How advisor evolves and improves
