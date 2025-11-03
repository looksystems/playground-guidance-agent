# System Architecture Specification

## Overview

This financial guidance agent system is based on two foundational papers:
1. **Generative Agents (Simulacra)** - Memory stream architecture, reflection, hierarchical planning
2. **Agent Hospital (MedAgent-Zero)** - SEAL framework, dual memory system, closed-loop learning

The system combines these approaches to create an FCA-compliant pension guidance agent that learns from both virtual and real-world interactions.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GUIDANCE AGENT SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌──────────────┐      ┌────────────┐ │
│  │   Customer  │◄────►│   Advisor    │◄────►│    FCA     │ │
│  │    Agent    │      │    Agent     │      │ Compliance │ │
│  │ (Simulated) │      │  (LLM-based) │      │  Validator │ │
│  └─────────────┘      └──────────────┘      └────────────┘ │
│         │                     │                      │       │
│         │                     ▼                      │       │
│         │          ┌──────────────────┐             │       │
│         │          │  Memory System   │             │       │
│         │          ├──────────────────┤             │       │
│         │          │  Memory Stream   │             │       │
│         │          │  Case Base       │             │       │
│         │          │  Rules Base      │             │       │
│         │          │  Reflection Log  │             │       │
│         │          └──────────────────┘             │       │
│         │                     │                      │       │
│         └─────────────────────┴──────────────────────┘       │
│                               │                               │
│                               ▼                               │
│                    ┌──────────────────┐                      │
│                    │ Knowledge Bases  │                      │
│                    ├──────────────────┤                      │
│                    │ FCA Guidance     │                      │
│                    │ Pension Rules    │                      │
│                    │ Tax Regulations  │                      │
│                    │ Best Practices   │                      │
│                    └──────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Memory Stream Architecture (from Simulacra)

The memory stream is a comprehensive database storing all agent experiences in natural language.

**Structure:**
```python
class MemoryNode:
    description: str           # Natural language description
    timestamp: datetime        # When memory was created
    last_accessed: datetime    # Most recent retrieval
    importance: float          # 1-10 score for observations
    memory_type: str          # "observation" | "reflection" | "plan"
    embedding: Vector          # Semantic embedding for retrieval
    citations: List[str]       # Memory IDs supporting this (for reflections)
```

**Memory Types:**

1. **Observations** (base layer)
   - Customer statements: "Customer is 55 years old with £250k in multiple pension pots"
   - Interaction events: "Customer expressed concern about pension consolidation risks"
   - Environmental: "FCA updated guidance boundary on pension consolidation"

2. **Reflections** (synthesized layer)
   - Pattern recognition: "Customer prioritizes security over growth potential"
   - Relationship insights: "Customer has low financial literacy but high engagement"
   - Principle extraction: "Customers near retirement prefer simpler pension structures"

3. **Plans** (future-oriented)
   - Consultation structure: "Gather customer pension details, assess consolidation benefits, explain risks"
   - Guidance sequence: "First explain pension types, then discuss consolidation pros/cons, finally provide recommendation"

### 2. Dual Memory System (from Agent Hospital)

In addition to the memory stream, the advisor agent maintains two specialized knowledge bases:

#### A. Financial Case Base (Episodic Memory)

Stores successful guidance interactions as question-answer pairs organized by task type.

**Structure:**
```python
class CaseBase:
    cases: Dict[TaskType, List[Case]]

class Case:
    task_type: TaskType  # "risk_assessment" | "consolidation_advice" | "contribution_planning"
    customer_profile: Dict  # Age, income, pension situation, goals
    context: str  # Full customer situation in natural language
    guidance_provided: str  # Advice given with reasoning
    outcome: str  # Customer satisfaction + goal achievement
    compliance_verified: bool  # FCA validation passed
    embedding: Vector  # For similarity search

TaskType = Enum([
    "RISK_ASSESSMENT",
    "CONSOLIDATION_ADVICE",
    "CONTRIBUTION_PLANNING",
    "DRAWDOWN_GUIDANCE",
    "TAX_OPTIMIZATION",
    "RETIREMENT_AGE_PLANNING"
])
```

**Population Methods:**
1. **Virtual Training**: Successful simulated customer interactions
2. **Real-World**: Human-validated successful guidance (with privacy compliance)
3. **Knowledge Learning**: FCA guidance documents converted to Q&A format

#### B. Guidance Rules Base (Semantic Memory)

Stores validated principles learned from reflection on suboptimal outcomes.

**Structure:**
```python
class RulesBase:
    rules: List[GuidanceRule]

class GuidanceRule:
    principle: str  # Natural language rule
    confidence: float  # Validation score (0-1)
    supporting_evidence: List[str]  # Case IDs where rule proved helpful
    fca_compliant: bool  # Passed compliance check
    domain: str  # "risk", "consolidation", "tax", etc.
    created_from: str  # Memory ID of failed case that led to this rule
    embedding: Vector  # For similarity search
```

**Example Rules:**
- "Customers over 55 with multiple small pots (<£10k each) typically benefit from consolidation to reduce fees, but must verify no valuable guarantees would be lost"
- "When customer has limited pension knowledge, explain concepts using analogies to familiar savings products before introducing technical terms"
- "Always verify customer understanding of key risks before providing consolidation guidance, as required by FCA boundary"

**Creation Process (Tuning-Free Rule Accumulation):**
1. **Reflection**: Compare suboptimal guidance with better alternatives, derive principle
2. **Validation**: Test principle against exemplar cases from FCA guidance documents
3. **Refinement**: Reformat principle with consistent structure
4. **Judgment**: Evaluate if rule is truly helpful before storing

### 3. Retrieval-Augmented Generation (RAG) System

All advisor decisions are informed by retrieving relevant memories, cases, and rules.

**Retrieval Function:**

```python
def retrieve_context(query: str, memory_stream: List[MemoryNode],
                     case_base: CaseBase, rules_base: RulesBase) -> Context:
    """
    Retrieves relevant context for a query using multi-faceted scoring.
    Based on Simulacra's retrieval mechanism.
    """
    context = Context()

    # 1. Retrieve from memory stream
    for memory in memory_stream:
        score = (
            alpha_recency * recency_score(memory) +
            alpha_importance * importance_score(memory) +
            alpha_relevance * relevance_score(memory, query)
        )
        memory.score = score

    # Select top-k memories (k=10 default)
    context.memories = sorted(memory_stream, key=lambda m: m.score, reverse=True)[:10]

    # 2. Retrieve from case base (top-3 similar cases)
    task_type = classify_task(query)
    similar_cases = case_base.search(task_type, query, top_k=3)
    context.cases = similar_cases

    # 3. Retrieve from rules base (top-4 relevant rules)
    relevant_rules = rules_base.search(query, top_k=4)
    context.rules = relevant_rules

    return context
```

**Scoring Components:**

1. **Recency Score**
   ```python
   def recency_score(memory: MemoryNode) -> float:
       hours_since_access = (now - memory.last_accessed).hours
       decay_factor = 0.995
       return decay_factor ** hours_since_access
   ```

2. **Importance Score**
   - Generated by LLM at memory creation
   - Scale 1-10, where 1 is mundane (routine questions) and 10 is critical (life-changing pension decisions)
   - Normalized to [0, 1]

3. **Relevance Score**
   ```python
   def relevance_score(memory: MemoryNode, query: str) -> float:
       query_embedding = embed(query)
       return cosine_similarity(memory.embedding, query_embedding)
   ```

**Embedding Model:**
- OpenAI `text-embedding-3-large` (3072 dimensions)
- Alternative: `text-embedding-ada-002` for cost optimization

### 4. Reflection Mechanism (from Simulacra)

Periodically synthesizes memories into higher-level insights.

**Trigger Condition:**
- Sum of importance scores for new observations exceeds threshold (e.g., 150 points)
- Approximately 2-3 times per day in active usage

**Reflection Process:**

```python
def reflect(memory_stream: List[MemoryNode]) -> List[MemoryNode]:
    """
    Generates high-level insights from recent experiences.
    """
    # 1. Extract recent important memories
    recent_memories = get_recent_memories(memory_stream, limit=100)

    # 2. Generate salient questions
    questions = llm_generate_questions(recent_memories, num_questions=3)
    # Example: "What financial concerns are customers expressing most frequently?"

    reflections = []
    for question in questions:
        # 3. Retrieve relevant memories for each question
        relevant = retrieve_for_reflection(question, memory_stream)

        # 4. Synthesize insights with citations
        insights = llm_synthesize_insights(question, relevant, num_insights=5)
        # Example: "Customers prioritize pension security over growth (from memories 42, 87, 103)"

        # 5. Store reflections back in memory stream
        for insight in insights:
            reflection = MemoryNode(
                description=insight.text,
                memory_type="reflection",
                importance=8.0,  # Reflections are high importance
                citations=insight.citation_ids,
                timestamp=now,
                embedding=embed(insight.text)
            )
            reflections.append(reflection)

    return reflections
```

**Reflection Trees:**

Reflections can reference prior reflections, creating hierarchical abstractions:

```
[Root] Customers value clear explanations of risks over technical accuracy
  ├─ [Reflection] Customers with low literacy prefer simple language
  │   ├─ [Observation] Customer struggled with "defined benefit" terminology
  │   ├─ [Observation] Customer understood analogy to savings account
  │   └─ [Observation] Customer requested "plain English" explanation
  ├─ [Reflection] Customers appreciate step-by-step guidance
  └─ [Reflection] Risk disclosure must be explicit and verified
```

### 5. Hierarchical Planning (from Simulacra)

Advisor agents create multi-scale plans for customer interactions.

**Three Planning Levels:**

1. **Consultation-Level Plan** (top level)
   - Example: "1) Understand customer's current pension situation, 2) Assess consolidation needs, 3) Explain benefits and risks, 4) Provide guidance within FCA boundary, 5) Verify understanding"
   - Duration: 30-60 minutes
   - Generated at start of customer interaction

2. **Phase-Level Plan** (middle level)
   - Example: "Phase 1 (5 min): Ask about existing pensions, gather details on providers, values, types; Phase 2 (10 min): Calculate total fees, identify any valuable features like guarantees..."
   - Duration: 5-15 minutes per phase
   - Decomposition of consultation-level plan

3. **Action-Level** (moment-to-moment)
   - Example: "Ask: 'Do you know how many pension pots you currently have?'", "Explain: 'Consolidation means combining multiple pensions into one'", "Check understanding: 'Does that make sense so far?'"
   - Duration: 30 seconds - 2 minutes
   - Specific utterances and actions

**Plan Revision:**
- Plans can be interrupted when customer asks unexpected questions
- Agent decides: continue current plan or react to new information?
- Reaction creates new sub-plan, then returns to original plan

### 6. FCA Compliance Layer

Every piece of guidance must satisfy FCA requirements.

**Hybrid Compliance Validator:**

The system uses a **hybrid validation approach** combining rule-based hard constraints with LLM-as-judge consensus for nuanced evaluation.

```python
class HybridComplianceValidator:
    """
    Multi-layered validation combining rules and LLM-as-judge.
    Defense-in-depth approach for regulatory compliance.
    """

    def __init__(self, mode: str = "production"):
        self.rule_validator = RuleBasedValidator()
        self.fca_knowledge = FCAKnowledgeBase()

        # Configure judges based on mode
        if mode == "training":
            # Single judge, lenient threshold (allow exploration)
            self.judges = [LLMJudge(model="gpt-3.5-turbo")]
            self.confidence_threshold = 0.6
        else:  # production
            # Multiple judges, conservative threshold (maximum safety)
            self.judges = [
                LLMJudge(model="gpt-4", prompt_version="v1"),
                LLMJudge(model="claude-3-5-sonnet", prompt_version="v1"),
                LLMJudge(model="gpt-4", prompt_version="v2")  # Different prompt
            ]
            self.confidence_threshold = 0.9

    def validate_guidance(self, customer_situation: Dict,
                          guidance: str,
                          reasoning: str) -> ValidationResult:
        """
        Two-stage validation: rules first, then LLM-as-judge.
        """
        # STAGE 1: Rule-based hard constraints (must pass)
        rule_result = self.rule_validator.validate(guidance, customer_situation)
        if not rule_result.passed:
            return ValidationResult(
                passed=False,
                confidence=1.0,
                issues=rule_result.issues,
                source="RULE_BASED",
                requires_human_review=False  # Clear violation
            )

        # STAGE 2: LLM-as-judge consensus (nuanced evaluation)
        judge_results = []
        for judge in self.judges:
            result = judge.evaluate(
                guidance=guidance,
                customer=customer_situation,
                reasoning=reasoning,
                fca_knowledge=self.fca_knowledge
            )
            judge_results.append(result)

        # Compute consensus
        consensus = self._compute_consensus(judge_results)

        # STAGE 3: Confidence-based decision
        if consensus.confidence < self.confidence_threshold:
            # Borderline case - requires human review
            return ValidationResult(
                passed=False,
                confidence=consensus.confidence,
                issues=["LOW_CONFIDENCE_REQUIRES_HUMAN_REVIEW"],
                source="LLM_JUDGE_CONSENSUS",
                requires_human_review=True,
                judge_details=judge_results
            )

        return ValidationResult(
            passed=consensus.passed,
            confidence=consensus.confidence,
            issues=consensus.issues,
            source="LLM_JUDGE_CONSENSUS",
            requires_human_review=False,
            judge_details=judge_results
        )

    def _compute_consensus(self, results: List[JudgeResult]) -> Consensus:
        """Majority voting with confidence weighting."""
        pass_votes = sum(1 for r in results if r.passed)

        if pass_votes >= 2:  # 2/3 agreement
            return Consensus(
                passed=True,
                confidence=mean(r.confidence for r in results if r.passed),
                issues=[]
            )
        else:
            return Consensus(
                passed=False,
                confidence=mean(r.confidence for r in results if not r.passed),
                issues=list(set(chain(r.issues for r in results)))
            )
```

**Rule-Based Hard Constraints (Stage 1):**

Critical checks that must pass before LLM evaluation:

1. **DB Pension Warning Enforcement**
   - If customer has DB pension → guidance MUST include warning
   - "DB pensions have valuable guarantees that disappear if you transfer"
   - Binary pass/fail (no judgment needed)

2. **Prohibited Language Detection**
   - Regex patterns for "should", "recommend", "must", "best for you"
   - Immediate rejection if detected
   - No false negatives acceptable

3. **Signposting Requirement**
   - If query crosses into regulated advice → must signpost
   - "This requires regulated financial advice from an authorized advisor"
   - Clear triggering conditions (specific product recommendations, etc.)

4. **Risk Disclosure Presence**
   - Keyword detection: "risk", "disadvantage", "loss", "fees"
   - Ensures some risk discussion present
   - LLM judges evaluate adequacy

**LLM-as-Judge Evaluation (Stage 2):**

Nuanced assessment requiring semantic understanding:

1. **Guidance/Advice Boundary Classification**
   ```
   Example 1: "You might want to consolidate those pensions"
   Judge: ADVICE (violation) - confidence 0.92
   Reasoning: "Might want" is disguised recommendation

   Example 2: "Consolidation could be considered for simplification"
   Judge: GUIDANCE (compliant) - confidence 0.95
   Reasoning: Presents as option without personal recommendation
   ```

2. **Risk Disclosure Adequacy**
   - Are risks explained with sufficient detail?
   - Is balance maintained (not just benefits)?
   - Is language appropriate for customer's financial literacy?

3. **Understanding Verification Quality**
   - Are questions open-ended vs yes/no?
   - Does advisor check key concepts?
   - Is verification genuine vs perfunctory?

4. **Contextual Appropriateness**
   - Does guidance fit customer's actual situation?
   - Are retrieved cases/rules correctly applied?
   - Is reasoning chain sound?

5. **Language Tone and Clarity**
   - Jargon level appropriate for customer literacy?
   - Tone professional but accessible?
   - No false certainty or qualified statements?

**Confidence Thresholds:**

- **Training mode (0.6):** Allow exploration, borderline cases become learning opportunities
- **Production mode (0.9):** Very conservative, any uncertainty triggers human review
- **Batch QA (0.95):** Strictest evaluation for quality assurance audits

**Human Review Queue:**

Low-confidence cases (<threshold) automatically escalated to compliance experts:
- Judge disagreement (split vote)
- Low individual confidence scores
- Novel patterns not seen in training
- High-stakes situations (large pension values, DB transfers)

**FCA Knowledge Base Structure:**
- Guidance boundary definitions (what is guidance vs advice)
- Risk disclosure requirements with examples
- Customer understanding verification protocols
- Prohibited language patterns (avoid "recommend", "should", "best")
- Permitted language patterns ("you could consider", "some people choose", "options include")
- Case law and FCA precedents for boundary decisions

### 7. Agent Cognitive Loop

The advisor agent operates in a continuous perceive-retrieve-reflect-plan-act cycle.

**Core Loop:**

```python
def advisor_cognitive_loop(agent: AdvisorAgent, customer: CustomerAgent):
    """
    Main interaction loop for advisor agent.
    """
    while interaction_active:
        # 1. PERCEIVE
        observations = perceive_environment(customer)
        # Customer statements, body language cues, comprehension signals

        # 2. STORE
        for obs in observations:
            importance = rate_importance(obs)
            memory_node = create_memory(obs, importance)
            agent.memory_stream.append(memory_node)

        # 3. DECIDE: Continue plan or react?
        should_react = decide_reaction(observations, agent.current_plan)

        if should_react:
            # 4a. RETRIEVE (for reaction)
            query = formulate_query(observations[-1])  # Most recent observation
            context = retrieve_context(query, agent.memory_stream,
                                      agent.case_base, agent.rules_base)

            # 4b. GENERATE (reaction)
            response = generate_response(observations[-1], context, agent.profile)

            # 4c. VALIDATE (FCA compliance with confidence scoring)
            validation = agent.compliance_validator.validate_guidance(
                customer.profile, response, context.reasoning
            )

            if validation.requires_human_review:
                # Low confidence - escalate to human compliance expert
                enqueue_for_human_review(customer, response, validation)
                response = fallback_response("Your query requires expert review...")
            elif not validation.passed:
                # Failed validation - refine and retry
                response = refine_guidance(response, validation.issues)
                # Re-validate after refinement
                validation = agent.compliance_validator.validate_guidance(
                    customer.profile, response, context.reasoning
                )

            # 4d. ACT
            deliver_guidance(customer, response)

            # Store successful interaction in case base if outcome positive
            if customer.satisfied:
                agent.case_base.add_case(customer.profile, response, context)

        else:
            # Continue with current plan
            next_action = agent.current_plan.pop_next_action()
            execute_action(next_action, customer)

        # 5. REFLECT (if threshold exceeded)
        if sum_recent_importance(agent.memory_stream) > REFLECTION_THRESHOLD:
            reflections = reflect(agent.memory_stream)
            agent.memory_stream.extend(reflections)

            # Check for suboptimal outcomes and extract rules
            if customer.outcome_suboptimal:
                new_rule = extract_rule_from_failure(
                    agent.memory_stream, agent.case_base, customer
                )
                if validate_rule(new_rule, agent.fca_knowledge):
                    agent.rules_base.add_rule(new_rule)
```

## Data Flow

### 1. Virtual Training Flow

```
Customer Agent Generator
    ↓
Generate Diverse Customer Profile
    ↓
Advisor Agent: Provide Guidance (with RAG retrieval)
    ↓
Compliance Validator: Check FCA compliance
    ↓
Customer Agent: Simulate Outcome
    ↓
IF outcome_successful:
    Store in Case Base
ELIF outcome_suboptimal:
    Reflect → Extract Rule → Validate → Store in Rules Base
    ↓
Repeat with new customer
```

### 2. Real-World Interaction Flow

```
Real Customer Inquiry
    ↓
Advisor Agent: Retrieve Context (Cases + Rules + Memories)
    ↓
Generate Guidance with Reasoning
    ↓
Compliance Validator: Verify FCA compliance
    ↓
Human Supervisor: Review (initially all, later sampling)
    ↓
IF approved:
    Deliver to Customer
    Track Outcome (where possible)
    IF outcome_successful:
        Store in Case Base
```

## Scaling and Performance

### Time Acceleration (Virtual Environment)

Like Agent Hospital, virtual time passes faster than real-time:
- 1 real hour = 1 virtual day of customer interactions
- Enables advisor agent to gain experience equivalent to years of human advisor work
- Critical for accumulating diverse cases rapidly

### Context Window Management

**Token Budget:**
- GPT-4 Turbo: 128k context window
- Budget allocation:
  - System prompt + advisor profile: 2k tokens
  - Customer profile: 1k tokens
  - Retrieved memories (top-10): ~3k tokens
  - Retrieved cases (top-3): ~4k tokens
  - Retrieved rules (top-4): ~2k tokens
  - FCA compliance rules: 2k tokens
  - Generation space: 2k tokens
  - Buffer: 2k tokens
  - Total: ~18k tokens (well within limits)

**Efficiency Optimizations:**
- Cache static knowledge bases (FCA rules, pension regulations)
- Use compressed summaries for older memories
- Implement memory consolidation: merge similar memories periodically

### Vector Database

**Requirements:**
- Fast similarity search (sub-100ms for retrieval)
- Support for metadata filtering (by memory type, date range, importance threshold)
- Scalability to millions of memories, cases, rules

**Options:**
- **Pinecone**: Managed, fast, good for production
- **Chroma**: Open-source, good for development
- **Weaviate**: Hybrid search (vector + keyword), good for compliance requirements

## System Properties

### Key Properties from Papers

1. **Emergent Behavior** (from Simulacra)
   - Advisor personality emerges from accumulated memories and reflections
   - Guidance style adapts to customer patterns observed
   - No hard-coded rules for interaction flow

2. **Continuous Learning** (from Agent Hospital)
   - Advisor expertise grows with every customer interaction
   - Zero-shot improvement without manual labeling
   - Virtual-real alignment: skills learned in simulation transfer to real customers

3. **Explainability**
   - All reasoning in natural language
   - Citations to specific cases, rules, and memories
   - Audit trail for regulatory compliance

4. **Safety and Compliance**
   - Dual validation: LLM generation + rule-based compliance checking
   - Human oversight (especially in early deployment)
   - Fallback to human advisor when confidence low

### Failure Modes and Mitigations

**Potential Issues (from paper error analysis):**

1. **Retrieval Failures**: Missing relevant context
   - Mitigation: Redundant retrieval strategies, importance boosting for critical info

2. **Hallucinated Embellishments**: Agent adds plausible but unverified details
   - Mitigation: Citation requirements, compliance validator flags unsupported claims

3. **Overly Cooperative**: Agent agrees too readily, doesn't challenge poor decisions
   - Mitigation: Explicit prompting to probe customer understanding, validate decisions

4. **Formal Tone**: Instruction-tuned LLMs may be unnaturally formal
   - Mitigation: Fine-tuning on natural customer service dialogues, persona prompting

## Next Steps

This architecture specification provides the foundation. See related specs:
- `advisor-agent.md`: Detailed advisor agent design and prompting strategies
- `customer-agent.md`: Customer simulation for virtual training
- `virtual-environment.md`: Training simulacrum design
- `learning-system.md`: Case base and rules base evolution mechanisms
- `implementation-plan.md`: Technical implementation roadmap
