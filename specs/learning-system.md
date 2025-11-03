# Learning System Specification

## Overview

The Learning System enables advisor agents to continuously improve through practice, implementing the **zero-shot learning** approach from Agent Hospital. Advisors evolve without manual data labeling through:

1. **Case Base**: Learning from successful guidance (episodic memory)
2. **Rules Base**: Learning from failures through reflection (semantic memory)
3. **Tuning-Free**: No parameter updates to LLM, only knowledge base growth
4. **Hybrid Learning**: Combining virtual training with real-world experience

## Learning Philosophy

### Zero-Shot Medical Expertise (adapted to Pensions)

From Agent Hospital:
> "MedAgent-Zero evolves through practice alone, without using labeled benchmark data"

Applied to pension guidance:
- Advisor starts with base LLM + FCA knowledge
- Improves through practice with simulated customers
- No fine-tuning or labeled datasets required
- Learning happens through memory accumulation and reflection

### Tuning-Free Rule Accumulation

Key insight from Agent Hospital:
> "Learning from failures by reflecting on mistakes, validating principles, and storing reusable rules - all without parameter updates"

This approach:
- Works with frozen LLMs (no training required)
- Rules stored in natural language (interpretable)
- Validated before storage (quality control)
- Continuously grows knowledge base

## Dual Memory Architecture

### Memory System 1: Case Base (Episodic Memory)

Stores successful guidance interactions as retrievable examples.

#### Structure

```python
class CaseBase:
    """Repository of successful guidance cases."""

    def __init__(self):
        self.cases_by_task: Dict[TaskType, List[Case]] = defaultdict(list)
        self.vector_store: VectorStore = ChromaDB()  # Or Pinecone

class Case:
    """Individual case of successful guidance."""

    case_id: str
    task_type: TaskType  # RISK_ASSESSMENT, CONSOLIDATION_ADVICE, etc.
    customer_profile: CustomerProfile
    customer_situation: str  # Natural language summary
    advisor_reasoning: str  # Chain of thought
    guidance_provided: str  # What advisor said
    outcome: OutcomeResult  # Customer satisfaction, comprehension, etc.
    compliance_verified: bool
    success_factors: List[str]  # What made this successful
    timestamp: datetime
    embedding: Vector  # For similarity search
```

#### Population Methods

**1. Virtual Training** (Primary method)

```python
def learn_from_successful_consultation(advisor: AdvisorAgent,
                                        customer: CustomerAgent,
                                        outcome: OutcomeResult):
    """
    Store successful guidance as a case for future retrieval.
    """
    # Only store if outcome was successful
    if not outcome.successful:
        return

    # Extract key information
    case = Case(
        case_id=generate_id(),
        task_type=classify_task_type(customer.presenting_question),
        customer_profile=customer.profile,
        customer_situation=summarize_situation(customer),
        advisor_reasoning=advisor.last_reasoning,
        guidance_provided=advisor.last_guidance,
        outcome=outcome,
        compliance_verified=True,  # Already checked before delivery
        success_factors=outcome.advisor_strengths,
        timestamp=datetime.now(),
        embedding=embed(summarize_situation(customer))
    )

    # Add to case base
    advisor.case_base.add(case)

    print(f"✓ Case {case.case_id} added to base (satisfaction: {outcome.customer_satisfaction})")
```

**2. Knowledge Learning** (Secondary method)

Convert FCA guidance documents and best practice guides into cases:

```python
def import_fca_guidance_as_cases(advisor: AdvisorAgent, fca_documents: List[Document]):
    """
    Convert FCA guidance documents into case format.
    """
    for doc in fca_documents:
        # Extract scenario-guidance pairs
        scenarios = extract_scenarios(doc)

        for scenario in scenarios:
            case = Case(
                case_id=f"FCA-{generate_id()}",
                task_type=scenario.task_type,
                customer_situation=scenario.customer_context,
                guidance_provided=scenario.recommended_approach,
                compliance_verified=True,  # From FCA directly
                outcome=OutcomeResult(successful=True, source="FCA_guidance"),
                timestamp=datetime.now(),
                embedding=embed(scenario.customer_context)
            )
            advisor.case_base.add(case)
```

#### Retrieval

```python
def retrieve_similar_cases(query: str, task_type: TaskType,
                           case_base: CaseBase, top_k: int = 3) -> List[Case]:
    """
    Retrieve top-k most similar cases for current situation.
    """
    # Filter by task type first
    relevant_cases = case_base.cases_by_task[task_type]

    # Compute similarity scores
    query_embedding = embed(query)
    scored_cases = []

    for case in relevant_cases:
        similarity = cosine_similarity(query_embedding, case.embedding)

        # Optionally boost recent cases slightly
        recency_boost = 1.0 + (0.1 if is_recent(case) else 0.0)

        score = similarity * recency_boost
        scored_cases.append((score, case))

    # Return top-k
    sorted_cases = sorted(scored_cases, key=lambda x: x[0], reverse=True)
    return [case for _, case in sorted_cases[:top_k]]
```

#### Usage in Guidance

Cases are retrieved and included in advisor prompts:

```
Similar Cases (from Case Base):

Case #127: Customer aged 54 with DB pension
Customer situation: 4 pensions including valuable DB pension from public sector, considering consolidation
Guidance provided: Explained DB guarantees, warned against transfer, suggested consolidating only DC pensions
Outcome: Customer satisfaction 9/10, understood risks, kept DB separate
Success factors: Clear explanation of DB value, balanced view, good use of analogies

Case #089: Low literacy customer asking about consolidation
Customer situation: 3 DC pensions, confused by terminology, worried about making mistakes
Guidance provided: Used simple language, savings account analogy, checked understanding frequently
Outcome: Customer satisfaction 8.5/10, felt empowered to decide
Success factors: Appropriate language level, frequent verification, patient approach

Case #213: Customer with protected tax-free cash
Customer situation: Old personal pension with 25% protected TFC (valuable), considering consolidation
Guidance provided: Identified valuable feature, explained it would be lost on transfer, advised keeping separate
Outcome: Customer satisfaction 9.5/10, grateful for spotting valuable benefit
Success factors: Thorough feature check, clear risk explanation, prevented suboptimal decision
```

### Memory System 2: Rules Base (Semantic Memory)

Stores validated principles learned from reflection on failures.

#### Structure

```python
class RulesBase:
    """Repository of learned guidance principles."""

    def __init__(self):
        self.rules: List[GuidanceRule] = []
        self.vector_store: VectorStore = ChromaDB()

class GuidanceRule:
    """Individual principle learned from experience."""

    rule_id: str
    principle: str  # Natural language rule
    domain: str  # "risk_disclosure", "db_pensions", "understanding_verification", etc.
    confidence: float  # 0-1 based on validation performance
    supporting_evidence: List[str]  # Case IDs where rule proved helpful
    counter_evidence: List[str]  # Cases where rule didn't help (if any)
    fca_compliant: bool  # Passed compliance validation
    created_from: str  # Memory ID of failed case that led to this rule
    refinement_history: List[str]  # How rule evolved over time
    timestamp: datetime
    embedding: Vector
```

#### Creation Process (Tuning-Free Rule Accumulation)

Based on Agent Hospital's 4-step process:

**Step 1: Reflection**

When guidance outcome is suboptimal, reflect on what went wrong:

```python
def reflect_on_failure(advisor: AdvisorAgent, customer: CustomerAgent,
                       outcome: OutcomeResult) -> Reflection:
    """
    Analyze suboptimal outcome to extract learning.
    """
    prompt = f"""
You are reflecting on a pension guidance consultation that had a suboptimal outcome.

Customer Situation:
{customer.profile}

Guidance Provided:
{advisor.last_guidance}

Reasoning Used:
{advisor.last_reasoning}

Outcome:
- Customer satisfaction: {outcome.customer_satisfaction}/10
- Comprehension: {outcome.comprehension}/10
- Goal alignment: {outcome.goal_alignment}/10
- Issues: {outcome.issues}

What guidance should have been provided instead?
{get_better_alternative(customer, outcome)}

Compare your guidance with the better alternative. What principle or rule can you extract?

Format your response as:
PROBLEM: [What went wrong]
ROOT_CAUSE: [Why it went wrong]
PRINCIPLE: [General rule to prevent this in future]

Example:
PROBLEM: Customer didn't understand DB pension warning because technical language used
ROOT_CAUSE: Advisor assumed higher financial literacy than customer had
PRINCIPLE: When explaining DB pensions to customers with low literacy, use concrete analogies (e.g., "guaranteed monthly income like a salary") rather than technical definitions

Your reflection:
"""

    reflection = llm_call(prompt)
    return parse_reflection(reflection)
```

**Step 2: Validation**

Test the extracted principle against exemplar cases:

```python
def validate_rule(principle: str, advisor: AdvisorAgent,
                  validation_cases: List[Case]) -> ValidationResult:
    """
    Validate that principle is actually helpful using test cases.
    """
    success_count = 0
    total_cases = len(validation_cases)

    for case in validation_cases:
        prompt = f"""
Apply this principle to the following case:

Principle: {principle}

Customer Situation:
{case.customer_situation}

Task: Would applying this principle lead to better guidance? How would you apply it?

Your response:
"""

        application = llm_call(prompt)

        # Check if application is appropriate and helpful
        is_helpful = evaluate_application(application, case.guidance_provided)

        if is_helpful:
            success_count += 1

    # Principle is valid if it helps in most cases
    confidence = success_count / total_cases
    valid = confidence >= 0.7  # 70% threshold

    return ValidationResult(
        valid=valid,
        confidence=confidence,
        success_count=success_count,
        total_cases=total_cases
    )
```

**Step 3: Refinement**

Reformat principle for consistency:

```python
def refine_principle(raw_principle: str, domain: str) -> str:
    """
    Format principle consistently for better retrieval and application.
    """
    prompt = f"""
Reformat this guidance principle for consistency and clarity.

Raw principle: {raw_principle}

Domain: {domain}

Requirements:
- Clear, actionable statement
- Specific about when to apply
- Explains why (reasoning)
- Natural language (not code or rigid structure)

Format as:
"When [situation], [action] because [reason]"

Example:
"When customer has low financial literacy, explain DB pensions using everyday analogies (e.g., 'guaranteed salary in retirement') rather than technical terms because customers understand concepts better when related to familiar experiences"

Refined principle:
"""

    refined = llm_call(prompt)
    return refined.strip()
```

**Step 4: Judgment**

Before storing, verify rule is truly helpful and FCA-compliant:

```python
def judge_rule_value(rule: GuidanceRule, fca_knowledge: FCAKnowledge) -> bool:
    """
    Final check before adding rule to knowledge base.
    """
    prompt = f"""
Evaluate whether this guidance principle should be added to the knowledge base.

Principle: {rule.principle}
Domain: {rule.domain}
Confidence: {rule.confidence}
Validation performance: {rule.confidence * 100}% success rate

FCA Compliance Check:
- Does this principle align with FCA guidance boundary?
- Does it encourage appropriate risk disclosure?
- Does it avoid personal recommendations?

{fca_knowledge.relevant_rules}

Quality Check:
- Is principle clear and actionable?
- Is it generalizable (not too specific to one case)?
- Does it add value beyond common sense?

Decision: ACCEPT or REJECT
Reasoning: [Explain your decision]

Your evaluation:
"""

    evaluation = llm_call(prompt)
    decision = parse_decision(evaluation)

    return decision == "ACCEPT"
```

**Complete Pipeline:**

```python
def process_suboptimal_outcome(advisor: AdvisorAgent, customer: CustomerAgent,
                                outcome: OutcomeResult):
    """
    Complete learning-from-failure pipeline.
    """
    # Step 1: Reflect
    reflection = reflect_on_failure(advisor, customer, outcome)

    # Step 2: Validate
    validation_cases = get_exemplar_cases(reflection.domain, n=10)
    validation = validate_rule(reflection.principle, advisor, validation_cases)

    if not validation.valid:
        print(f"✗ Principle rejected (confidence {validation.confidence:.2f} below threshold)")
        return

    # Step 3: Refine
    refined_principle = refine_principle(reflection.principle, reflection.domain)

    # Step 4: Judge
    rule = GuidanceRule(
        rule_id=generate_id(),
        principle=refined_principle,
        domain=reflection.domain,
        confidence=validation.confidence,
        supporting_evidence=[],
        fca_compliant=True,  # Checked in judgment
        created_from=outcome.consultation_id,
        timestamp=datetime.now(),
        embedding=embed(refined_principle)
    )

    if judge_rule_value(rule, advisor.fca_knowledge):
        advisor.rules_base.add(rule)
        print(f"✓ Rule {rule.rule_id} added to base (confidence {rule.confidence:.2f})")
    else:
        print(f"✗ Rule rejected in final judgment")
```

#### Retrieval

```python
def retrieve_relevant_rules(query: str, rules_base: RulesBase,
                            top_k: int = 4) -> List[GuidanceRule]:
    """
    Retrieve top-k most relevant rules for current situation.
    """
    query_embedding = embed(query)
    scored_rules = []

    for rule in rules_base.rules:
        similarity = cosine_similarity(query_embedding, rule.embedding)

        # Weight by confidence
        score = similarity * rule.confidence

        scored_rules.append((score, rule))

    # Return top-k
    sorted_rules = sorted(scored_rules, key=lambda x: x[0], reverse=True)
    return [rule for _, rule in sorted_rules[:top_k]]
```

#### Usage in Guidance

Rules are retrieved and included in advisor prompts:

```
Relevant Rules (from Rules Base):

Rule #034: Explaining defined benefit pensions
Principle: "When explaining DB pensions to customers with low financial literacy, use concrete analogies (e.g., 'guaranteed monthly income like a salary') rather than technical definitions because customers understand concepts better when related to familiar experiences"
Domain: pension_education
Confidence: 0.92 | FCA Compliant: ✓
Evidence: Successfully applied in cases 127, 089, 156, 201, 213

Rule #071: DB pension consolidation warning
Principle: "When customer has DB pension and is considering consolidation, always emphasize valuable guarantees and that most people would lose out by transferring, before discussing any potential benefits, because DB pensions have special protections that must be preserved"
Domain: risk_disclosure
Confidence: 0.98 | FCA Compliant: ✓
Evidence: Prevented suboptimal decisions in cases 213, 187, 098, 312

Rule #103: Checking understanding effectively
Principle: "When verifying customer understanding, ask open-ended questions that require paraphrasing (e.g., 'Can you explain that back to me?') rather than yes/no questions (e.g., 'Does that make sense?') because customers often say 'yes' even when confused to avoid seeming uninformed"
Domain: understanding_verification
Confidence: 0.87 | FCA Compliant: ✓
Evidence: Improved comprehension detection in cases 089, 167, 204, 299, 358

Rule #156: Signposting threshold
Principle: "When customer asks for help choosing between specific products or wants a personal recommendation on consolidation, signpost to regulated financial advice because this crosses from guidance (general information) into advice (personal recommendation) boundary defined by FCA"
Domain: regulatory_compliance
Confidence: 0.95 | FCA Compliant: ✓
Evidence: Correct boundary management in cases 245, 278, 301, 412
```

#### Compliance Feedback Loop

The **HybridComplianceValidator** with LLM-as-judge provides rich feedback that feeds directly into the learning system.

**How Compliance Validation Enhances Learning:**

```python
def handle_compliance_validation(advisor: AdvisorAgent, customer: CustomerAgent,
                                  guidance: str, validation: ValidationResult):
    """
    Use compliance validation feedback for continuous learning.
    """
    # Case 1: Clear compliance violation (rule-based rejection)
    if validation.source == "RULE_BASED" and not validation.passed:
        # Critical failure - learn immediately
        for issue in validation.issues:
            if issue == "MISSING_DB_WARNING":
                reflection = create_compliance_reflection(
                    problem="Failed to include mandatory DB pension warning",
                    principle="When customer has DB pension, ALWAYS include warning about guaranteed benefits before ANY discussion of consolidation"
                )
                add_to_rules_base_urgent(reflection, domain="regulatory_compliance")

    # Case 2: Low confidence from LLM judges (borderline case)
    elif validation.requires_human_review:
        # Borderline cases are valuable learning opportunities
        analyze_judge_disagreements(validation.judge_details)

        # Extract what made this borderline
        borderline_pattern = extract_borderline_pattern(
            guidance=guidance,
            judge_results=validation.judge_details,
            confidence=validation.confidence
        )

        # Store for future reference
        store_borderline_case(
            guidance=guidance,
            customer=customer,
            pattern=borderline_pattern,
            resolution="PENDING_HUMAN_REVIEW"
        )

    # Case 3: Failed LLM-as-judge consensus (nuanced violation)
    elif validation.source == "LLM_JUDGE_CONSENSUS" and not validation.passed:
        # Nuanced compliance failure - extract learning
        compliance_reflection = reflect_on_compliance_failure(
            guidance=guidance,
            customer=customer,
            judge_issues=validation.issues,
            judge_reasoning=[j.reasoning for j in validation.judge_details]
        )

        # Process through standard learning pipeline
        process_reflection_to_rule(advisor, compliance_reflection, domain="regulatory_compliance")
```

**Compliance Confidence Scoring as Learning Signal:**

```python
def use_confidence_for_learning(validation: ValidationResult, guidance: str):
    """
    Confidence scores indicate which aspects need attention.
    """
    if validation.confidence < 0.7:
        # Low confidence - unclear boundary
        learn_boundary_clarification(guidance, validation)

    elif 0.7 <= validation.confidence < 0.9:
        # Medium confidence - could be improved
        identify_ambiguous_language(guidance, validation)

    elif validation.confidence >= 0.9:
        # High confidence - good example
        if validation.passed:
            # Store as positive example (gold standard)
            add_to_case_base_as_exemplar(guidance)
        else:
            # High confidence failure - clear negative example
            add_to_compliance_training_set(guidance, label="NON_COMPLIANT")
```

**Example: Learning from Judge Feedback**

```python
# Scenario: Judge identifies disguised recommendation
guidance = "Given your situation, you might want to consider consolidating those pensions."

Judge 1 (GPT-4):
- passed: False
- confidence: 0.75
- reasoning: "'might want to' is a softened recommendation. Suggests personal direction."
- boundary_classification: ADVICE

Judge 2 (Claude):
- passed: True
- confidence: 0.70
- reasoning: "'consider' is option language, not directive."
- boundary_classification: BORDERLINE

Judge 3 (GPT-4 v2):
- passed: False
- confidence: 0.82
- reasoning: "'Given your situation' personalizes it, making it advice-like."
- boundary_classification: ADVICE

Consensus: FAILED (2/3), confidence=0.76 → Human review required

# Learning extraction:
reflection = Reflection(
    problem="Used 'might want to consider' which judges flagged as disguised recommendation",
    root_cause="Trying to be helpful led to personalizing language too much",
    principle="Avoid 'might want to' or 'given your situation' phrasing. Instead use 'some people consider' or 'options include' to maintain guidance boundary"
)

# After validation and judgment:
new_rule = GuidanceRule(
    principle="When presenting consolidation as an option, use depersonalized language like 'some people consider' or 'options include' rather than 'you might want to' or 'given your situation', because personalized phrasing crosses into advice territory per FCA boundary",
    domain="regulatory_compliance",
    confidence=0.88,  # High after validation
    fca_compliant=True,
    created_from="judge_feedback_borderline_case_127"
)
```

**Validation Study Integration:**

The LLM-as-judge validation study (Phase 6) creates a gold-standard compliance dataset:

```python
class ComplianceDataset:
    """Gold-standard dataset from validation study."""

    def __init__(self):
        self.expert_labeled_cases = []  # 200-500 cases labeled by FCA expert
        self.borderline_cases = []      # Cases where judges disagreed
        self.clear_passes = []          # High-confidence compliant examples
        self.clear_fails = []           # High-confidence violations

    def use_for_learning(self, advisor: AdvisorAgent):
        """Integrate validation dataset into learning system."""

        # 1. Add clear passes to case base as exemplars
        for case in self.clear_passes:
            advisor.case_base.add(
                Case(
                    guidance=case.guidance,
                    outcome="SUCCESSFUL",
                    compliance_verified=True,
                    is_exemplar=True  # Use in few-shot prompts
                )
            )

        # 2. Extract principles from clear fails
        for case in self.clear_fails:
            reflection = reflect_on_compliance_failure(case)
            process_reflection_to_rule(advisor, reflection, "regulatory_compliance")

        # 3. Study borderline cases for boundary understanding
        patterns = analyze_borderline_patterns(self.borderline_cases)
        for pattern in patterns:
            add_boundary_clarification_rule(advisor, pattern)
```

**Key Benefits of Compliance Feedback Loop:**

1. **Faster Convergence:** Advisor learns FCA boundary from explicit feedback, not just outcomes
2. **Reduced False Negatives:** Critical compliance rules are prioritized and learned immediately
3. **Confidence Calibration:** Borderline cases teach nuanced boundary understanding
4. **Gold Standard Dataset:** Validation study creates reusable training examples
5. **Adaptive Learning:** As FCA guidance evolves, new patterns are captured in rules base

**Compliance-Specific Rule Priority:**

```python
# Rules from compliance failures get higher importance
rule.importance_multiplier = {
    "regulatory_compliance": 2.0,      # Double weight (critical!)
    "risk_disclosure": 1.5,            # High importance
    "understanding_verification": 1.2, # Moderate importance
    "pension_education": 1.0           # Normal importance
}[rule.domain]

# During retrieval, compliance rules surface more readily
def retrieve_rules_with_compliance_priority(query: str, rules_base: RulesBase):
    rules = retrieve_relevant_rules(query, rules_base, top_k=6)

    # Ensure at least 1-2 compliance rules if relevant
    compliance_rules = [r for r in rules if r.domain == "regulatory_compliance"]

    if len(compliance_rules) < 2:
        # Force include high-confidence compliance rules
        additional = rules_base.get_top_compliance_rules(2)
        rules = additional + rules[:4]  # Keep top-4, add 2 compliance

    return rules[:4]  # Return top-4 total
```

## Learning Dynamics

### Scaling Laws in Evolution

Agent Hospital demonstrated continuous improvement with practice:
- Rapid improvement in first 10,000 patients (66% → 88%)
- Continued steady improvement up to 50,000 patients (88% → 95%)

Expected for pension guidance:

```python
def expected_performance_trajectory(num_consultations: int) -> float:
    """
    Model expected advisor performance based on Agent Hospital scaling laws.
    """
    if num_consultations < 100:
        # Initial rapid learning phase
        return 0.6 + 0.003 * num_consultations
    elif num_consultations < 1000:
        # Continued rapid improvement
        base = 0.9
        return base + 0.0005 * (num_consultations - 100)
    elif num_consultations < 5000:
        # Steady improvement
        base = 0.945
        return base + 0.00005 * (num_consultations - 1000)
    else:
        # Asymptotic approach to expert level
        base = 0.965
        improvement = 0.03 * (1 - math.exp(-(num_consultations - 5000) / 10000))
        return min(0.995, base + improvement)

# Expected performance:
# 100 consultations: 90% quality
# 1000 consultations: 94.5% quality
# 5000 consultations: 96.5% quality
# 10000+ consultations: 97-99% quality (expert level)
```

### Knowledge Base Growth

```python
class KnowledgeGrowth:
    """Track knowledge base accumulation over time."""

    @staticmethod
    def expected_case_base_size(num_consultations: int, success_rate: float) -> int:
        """
        Estimate case base size.
        Most successful consultations become cases (some duplicates filtered).
        """
        # Assume 80% of successful consultations stored (20% too similar to existing)
        successful = num_consultations * success_rate
        unique_cases = successful * 0.8
        return int(unique_cases)

    @staticmethod
    def expected_rules_base_size(num_consultations: int, success_rate: float) -> int:
        """
        Estimate rules base size.
        Rules come from failures, but only after validation.
        """
        # Failures decrease as performance improves
        failures = num_consultations * (1 - success_rate)

        # Only ~30% of failures yield validated rules
        # (Many failures are one-off errors, not systematic issues)
        validated_rules = failures * 0.3

        return int(validated_rules)

# After 5000 consultations at 96.5% success:
# - Case Base: ~3,860 successful cases
# - Rules Base: ~52 validated principles
```

### Reflection Frequency

```python
def trigger_reflection(advisor: AdvisorAgent) -> bool:
    """
    Determine if reflection should be triggered.
    Based on Simulacra's importance threshold approach.
    """
    recent_memories = advisor.memory_stream.recent(hours=24)
    importance_sum = sum(m.importance for m in recent_memories)

    REFLECTION_THRESHOLD = 150  # From Simulacra

    return importance_sum >= REFLECTION_THRESHOLD

# Approximately 2-3 reflections per day (virtual time)
# With time acceleration (60x), this means frequent learning opportunities
```

## Hybrid Learning (Virtual + Real-World)

### Virtual Training Phase

Initial training exclusively in simulacrum:

```python
def virtual_training_phase(advisor: AdvisorAgent, num_customers: int = 5000):
    """
    Phase 1: Pure virtual training to build foundational expertise.
    """
    print("Starting virtual training phase...")

    for i in range(num_customers):
        customer = generate_customer_agent()
        outcome = run_consultation(advisor, customer)

        if outcome.successful:
            learn_from_success(advisor, customer, outcome)
        else:
            learn_from_failure(advisor, customer, outcome)

        if i % 100 == 0:
            metrics = evaluate_advisor(advisor)
            print(f"Progress: {i}/{num_customers} - Performance: {metrics.quality:.1%}")

    print(f"Virtual training complete. Case base: {len(advisor.case_base)}, Rules base: {len(advisor.rules_base)}")
```

### Real-World Integration Phase

Gradually introduce real-world interactions with human oversight:

```python
class HybridLearning:
    """Combine virtual and real-world learning."""

    def __init__(self, advisor: AdvisorAgent):
        self.advisor = advisor
        self.human_supervisor = HumanSupervisor()

    def process_real_interaction(self, real_customer: Dict,
                                  guidance: str, reasoning: str) -> Decision:
        """
        Handle real-world interaction with human oversight.
        """
        # Human reviews before delivery (initially all, later sampling)
        review = self.human_supervisor.review(
            customer=real_customer,
            guidance=guidance,
            reasoning=reasoning
        )

        if review.status == "APPROVED":
            # Deliver guidance
            deliver_to_customer(guidance)

            # Track outcome (where possible)
            outcome = track_customer_outcome(real_customer, guidance)

            if outcome and outcome.successful:
                # Learn from successful real-world case
                anonymized = anonymize_for_privacy(real_customer)
                self.advisor.case_base.add_real_case(anonymized, guidance, outcome)

            return Decision.DELIVERED

        elif review.status == "NEEDS_REVISION":
            # Learn from human feedback
            revised_guidance = review.revised_version

            # Treat original as "failure", learn from difference
            self.learn_from_human_correction(
                customer=real_customer,
                advisor_version=guidance,
                human_version=revised_guidance,
                feedback=review.feedback
            )

            # Deliver revised version
            deliver_to_customer(revised_guidance)

            return Decision.REVISED_AND_DELIVERED

        else:  # REJECTED
            # Escalate to human advisor
            escalate_to_human(real_customer)

            # Learn from rejection
            self.learn_from_rejection(real_customer, guidance, review.issues)

            return Decision.ESCALATED

    def learn_from_human_correction(self, customer: Dict, advisor_version: str,
                                     human_version: str, feedback: str):
        """
        Extract learning from human revision.
        """
        prompt = f"""
Learn from human supervisor's correction to your guidance.

Customer Situation:
{customer}

Your Guidance:
{advisor_version}

Human Supervisor's Version:
{human_version}

Feedback:
{feedback}

What principle can you extract to improve future guidance?

Your reflection:
"""

        reflection = llm_call(prompt)

        # Go through validation pipeline
        process_reflection_to_rule(self.advisor, reflection, "human_feedback")
```

### Continuous Learning

Ongoing improvement during deployment:

```python
def continuous_learning_loop(advisor: AdvisorAgent):
    """
    Perpetual learning from both virtual and real interactions.
    """
    while True:
        # Virtual practice (overnight or background)
        if should_run_virtual_training():
            virtual_customers = generate_customer_batch(n=50)
            for customer in virtual_customers:
                outcome = run_consultation(advisor, customer)
                process_outcome(advisor, customer, outcome)

        # Real-world learning (during operation)
        if has_new_real_interaction():
            real_interaction = get_next_real_interaction()
            process_real_interaction_with_oversight(advisor, real_interaction)

        # Periodic reflection
        if trigger_reflection(advisor):
            reflections = reflect(advisor.memory_stream)
            advisor.memory_stream.extend(reflections)

        # Update metrics
        log_advisor_metrics(advisor)

        sleep(interval)
```

## Evaluation and Metrics

### Virtual World Evaluation

Track performance within simulation:

```python
class VirtualMetrics:
    """Metrics measured in virtual environment."""

    def evaluate_advisor(advisor: AdvisorAgent,
                         test_customers: List[CustomerAgent]) -> Metrics:
        """
        Evaluate advisor on held-out test set.
        """
        results = []

        for customer in test_customers:
            outcome = run_consultation(advisor, customer)
            results.append(outcome)

        return Metrics(
            # Task Accuracy
            risk_assessment_accuracy=mean(r.risks_identified for r in results),
            guidance_appropriateness=mean(r.guidance_appropriate for r in results),
            compliance_rate=mean(r.fca_compliant for r in results),  # Must be 100%

            # Customer Outcomes
            satisfaction=mean(r.customer_satisfaction for r in results),
            comprehension=mean(r.comprehension for r in results),
            goal_alignment=mean(r.goal_alignment for r in results),

            # Process Quality
            understanding_verification_rate=mean(r.understanding_checked for r in results),
            signposting_rate=mean(r.signposted_when_needed for r in results),
            db_warning_rate=mean(r.db_warning_given for r in results if r.has_db_pension),

            # Overall
            overall_quality=mean(r.successful for r in results)
        )
```

### Real-World Evaluation

Validate transfer to real-world performance:

```python
class RealWorldMetrics:
    """Metrics from actual customer interactions."""

    @staticmethod
    def evaluate_real_world_performance(advisor: AdvisorAgent,
                                         review_sample: List[RealInteraction]) -> Metrics:
        """
        Human evaluation of real-world guidance quality.
        """
        scores = []

        for interaction in review_sample:
            # Expert human evaluator scores guidance
            score = human_evaluator_score(interaction)
            scores.append(score)

        return Metrics(
            human_approval_rate=mean(s.approved for s in scores),
            revision_needed_rate=mean(s.needs_revision for s in scores),
            escalation_rate=mean(s.escalated for s in scores),
            customer_satisfaction=mean(s.customer_satisfaction for s in scores),
            expert_quality_rating=mean(s.expert_rating for s in scores)
        )
```

### Ablation Studies

Validate contribution of each component:

```python
def ablation_study():
    """
    Test importance of case base vs. rules base.
    Based on Agent Hospital's ablation study design.
    """
    # Baseline: No case base, no rules base (just LLM + FCA knowledge)
    advisor_baseline = AdvisorAgent(use_case_base=False, use_rules_base=False)

    # With case base only
    advisor_cases = AdvisorAgent(use_case_base=True, use_rules_base=False)

    # With rules base only
    advisor_rules = AdvisorAgent(use_case_base=False, use_rules_base=True)

    # Full system
    advisor_full = AdvisorAgent(use_case_base=True, use_rules_base=True)

    # Evaluate all variants
    test_customers = generate_test_set(n=200)

    results = {
        "baseline": evaluate_advisor(advisor_baseline, test_customers),
        "cases_only": evaluate_advisor(advisor_cases, test_customers),
        "rules_only": evaluate_advisor(advisor_rules, test_customers),
        "full": evaluate_advisor(advisor_full, test_customers)
    }

    return results

# Expected results (based on Agent Hospital findings):
# Baseline: ~88% quality
# Cases only: ~90% quality (+2%)
# Rules only: ~87% quality (rules need cases to contextualize)
# Full system: ~92% quality (+4% vs baseline)
```

## Summary

The Learning System enables:

- **Zero-shot expertise**: Learning through practice, no manual labeling
- **Dual memory**: Cases (what worked) + Rules (learned principles)
- **Tuning-free**: No LLM fine-tuning required, works with frozen models
- **Validated learning**: Rules must pass validation before storage
- **Continuous improvement**: Keeps learning from both virtual and real interactions
- **Interpretable**: All knowledge in natural language with citations
- **Hybrid approach**: Combines virtual training with real-world experience

This approach demonstrated by Agent Hospital shows continuous improvement with practice, with performance scaling predictably based on number of consultations.

See related specifications:
- `architecture.md`: Overall system design
- `advisor-agent.md`: How advisors use case and rules bases
- `virtual-environment.md`: Where learning happens
- `implementation-plan.md`: How to build this system
