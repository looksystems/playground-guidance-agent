# Virtual Training Environment Specification

## Overview

The Virtual Training Environment is a simulacrum (inspired by Smallville and Agent Hospital) where Advisor Agents practice pension guidance with simulated Customer Agents. This environment enables:

1. **Time Acceleration**: Virtual time passes faster than real-time, allowing advisors to gain years of experience in days
2. **Closed-Loop Feedback**: Complete outcome tracking (unlike real-world where outcomes often unknown)
3. **Safe Practice**: No risk to real customers while learning
4. **Diverse Scenarios**: Exposure to thousands of varied customer situations

## SEAL Framework

Based on Agent Hospital's **Simulacrum-based Evolutionary Agent Learning (SEAL)** framework:

```
Phase 1: SIMULACRUM CONSTRUCTION
    ↓
Build virtual pension guidance environment
Define interaction events and workflows
Create customer generation system
    ↓
Phase 2: AGENT EVOLUTION
    ↓
Advisors practice with simulated customers
Learn from successful guidance (Case Base)
Learn from failures through reflection (Rules Base)
    ↓
Continuous improvement through practice
```

## Environment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                 VIRTUAL GUIDANCE ENVIRONMENT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐             │
│  │ Customer Agent 1 │◄────────►│ Advisor Agent A  │             │
│  └──────────────────┘         └──────────────────┘             │
│           │                            │                         │
│           │                            │                         │
│  ┌──────────────────┐                 │                         │
│  │ Customer Agent 2 │                 │                         │
│  └──────────────────┘                 │                         │
│           │                            │                         │
│           └────────────────────────────┘                         │
│                       │                                          │
│                       ▼                                          │
│            ┌─────────────────────┐                              │
│            │  Event Orchestrator │                              │
│            │  - Consultation     │                              │
│            │  - Risk Assessment  │                              │
│            │  - Outcome Tracking │                              │
│            │  - Feedback Loop    │                              │
│            └─────────────────────┘                              │
│                       │                                          │
│                       ▼                                          │
│            ┌─────────────────────┐                              │
│            │  Time Accelerator   │                              │
│            │  (Virtual Time)     │                              │
│            └─────────────────────┘                              │
│                       │                                          │
│                       ▼                                          │
│            ┌─────────────────────┐                              │
│            │  Outcome Simulator  │                              │
│            │  - Success tracking │                              │
│            │  - Feedback gen.    │                              │
│            └─────────────────────┘                              │
│                       │                                          │
│                       ▼                                          │
│            ┌─────────────────────┐                              │
│            │   Learning System   │                              │
│            │  - Case Base        │                              │
│            │  - Rules Base       │                              │
│            │  - Reflection       │                              │
│            └─────────────────────┘                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Interaction Events

Based on Agent Hospital's event-driven architecture with 8 main event types adapted to pension guidance.

### Event 1: Customer Inquiry (Triage)

**Trigger**: Customer Agent enters environment with presenting question

**Process**:
1. Customer Agent presents initial inquiry
2. Advisor Agent assesses inquiry type and complexity
3. Advisor determines if inquiry is within guidance boundary (vs. regulated advice)
4. Initial rapport building and expectation setting

**Example:**
```
Customer: "I have 4 different pensions and I'm confused. Should I combine them?"
Advisor: [Assesses] → This is within guidance boundary (information and explanation)
         [Responds] → Acknowledges inquiry, begins information gathering
```

**Success Criteria**:
- Inquiry type correctly identified
- Appropriate expectation setting (guidance vs. advice)
- Customer feels heard and understood

### Event 2: Information Gathering (Registration)

**Trigger**: After initial inquiry

**Process**:
1. Advisor asks questions to understand customer situation
2. Customer provides information about pensions, goals, concerns
3. Advisor builds mental model of customer profile
4. Identify key factors: pension types, values, goals, literacy level

**Key Questions** (from prompting strategies):
- "Tell me about your current pension situation"
- "What are your main goals or concerns about your pensions?"
- "Have you come across any terms or concepts you'd like me to explain?"

**Success Criteria**:
- Comprehensive understanding of customer situation
- Customer profile data gathered
- Goals and concerns identified
- Rapport maintained

### Event 3: Risk Assessment

**Trigger**: Once situation understood

**Process**:
1. Advisor identifies potential risks in customer situation
2. Checks for high-value features (DB pensions, guarantees, protected benefits)
3. Assesses customer's risk tolerance and understanding level
4. Flags any critical warnings needed

**Critical Checks**:
- Does customer have DB pension? (requires special warning about valuable guarantees)
- Any guaranteed annuity rates or protected tax-free cash?
- Small pots with high fees?
- Any red flags (time pressure, external influence)?

**Success Criteria**:
- All risks identified
- DB pensions and valuable features flagged
- Risk assessment appropriate for customer situation

### Event 4: Information Provision (Consultation)

**Trigger**: After risk assessment

**Process**:
1. Advisor explains relevant pension concepts
2. Uses appropriate language for customer literacy level
3. Employs analogies and examples
4. Checks understanding throughout

**Guidance Topics** (based on customer needs):
- What pension consolidation means
- Benefits of consolidation (simplicity, fee reduction)
- Risks of consolidation (loss of features, exit fees)
- How different pension types work
- Options available to customer

**Prompting Pattern** (from advisor-agent.md):
- Instruction: Explain [concept]
- Customer context: [literacy level, prior knowledge]
- Retrieved context: [similar cases, effective analogies]
- Constraints: Use simple language, check understanding

**Success Criteria**:
- Information appropriate for customer literacy
- Key concepts explained clearly
- Analogies used effectively
- No jargon without explanation

### Event 5: Understanding Verification (Examination)

**Trigger**: After information provision

**Process**:
1. Advisor checks customer comprehension
2. Uses open-ended questions (not yes/no)
3. Customer demonstrates understanding (or reveals confusion)
4. Advisor clarifies if needed

**Verification Techniques**:
- "Can you explain back to me in your own words what consolidation would mean for you?"
- "What questions do you have about [concept]?"
- "How does that fit with what you're trying to achieve?"

**Customer Response Simulation** (see customer-agent.md):
- If understood: Customer paraphrases correctly, asks next question
- If confused: Customer asks clarifying question, admits uncertainty
- If partially understood: Customer gets some right, misses nuance

**Success Criteria**:
- Customer understanding verified
- Misconceptions identified and corrected
- Customer feels safe to ask questions

### Event 6: Guidance Provision (Diagnosis/Treatment)

**Trigger**: After understanding verified

**Process**:
1. Advisor provides specific guidance relevant to customer situation
2. Presents balanced view (pros and cons)
3. Explains options available
4. Uses FCA-compliant language (no personal recommendations)
5. Cites reasoning and relevant cases/rules

**Guidance Structure**:
```
Based on your situation [recap key points]:
- You have [situation summary]
- Your goals are [goals]

Here are the key things to consider:

Benefits of [option]:
- [Benefit 1 with explanation]
- [Benefit 2 with explanation]

Risks and considerations:
- [Risk 1 with explanation]
- [Risk 2 with explanation]

Options available to you:
- Option 1: [description] - [pros/cons]
- Option 2: [description] - [pros/cons]

Things to watch out for:
- [Critical warning 1, e.g., DB pension guarantees]
- [Critical warning 2, e.g., exit fees]

[If needed] This decision would benefit from regulated financial advice because [reason].
```

**Success Criteria**:
- Balanced presentation (not one-sided)
- Options clearly explained
- Risks adequately disclosed
- FCA-compliant language used
- Reasoning transparent

### Event 7: Customer Decision (Medicine Dispensary)

**Trigger**: After guidance provided

**Process**:
1. Customer considers guidance
2. Customer may ask follow-up questions
3. Advisor addresses remaining concerns
4. Customer indicates intended next steps
5. Advisor verifies customer feels informed to decide

**Customer Behaviors** (simulated):
- Asks clarifying questions
- Expresses concerns or worries
- Indicates preferred direction
- Requests additional information

**Success Criteria**:
- Customer feels informed
- Customer understands next steps
- Customer knows how to access further help if needed
- No pressure to decide immediately

### Event 8: Outcome Tracking (Convalescence)

**Trigger**: After guidance session ends

**Process**:
1. Simulate customer outcome based on guidance quality
2. Assess customer satisfaction
3. Determine if goals were met
4. Evaluate comprehension and compliance
5. Provide feedback to advisor agent

**Outcome Simulation** (see customer-agent.md):
```python
outcome = {
    "customer_satisfaction": 8.5,  # 0-10 scale
    "goal_alignment": 9.0,  # Did guidance address goals?
    "comprehension": 8.0,  # Did customer understand?
    "risk_disclosure": 9.5,  # Were risks adequately explained?
    "compliance": 10.0,  # FCA-compliant?
    "likelihood_to_follow": "very_likely",  # Will customer act on guidance?
    "successful": True,  # Overall success
    "strengths": [
        "Excellent use of analogies for DB pension explanation",
        "Balanced view of consolidation pros and cons",
        "Good checking of understanding throughout"
    ],
    "improvements": [
        "Could have spent more time on exit fees"
    ]
}
```

**Learning Integration**:
- If `successful == True`: Store in Case Base
- If `successful == False`: Trigger reflection → extract rule → validate → Rules Base

## Time Acceleration

Key innovation from Agent Hospital: virtual time passes faster than real-time.

### Time Scaling

```python
class VirtualTime:
    acceleration_factor: int = 60  # 1 real hour = 60 virtual hours (2.5 days)

    def __init__(self):
        self.virtual_time = datetime.now()
        self.real_time_start = datetime.now()

    def advance(self, real_seconds: float):
        """Advance virtual time based on real time elapsed."""
        virtual_seconds = real_seconds * self.acceleration_factor
        self.virtual_time += timedelta(seconds=virtual_seconds)

    def time_until_event(self, event_time: datetime) -> timedelta:
        """Calculate real-world time until virtual event."""
        virtual_delta = event_time - self.virtual_time
        real_delta = virtual_delta / self.acceleration_factor
        return real_delta
```

### Benefits of Time Acceleration

1. **Rapid Experience Accumulation**:
   - 1 real day = 60 virtual days of practice
   - 1 real week = ~1 virtual year
   - Advisor can see thousands of customers quickly

2. **Long-term Outcome Simulation**:
   - Can simulate months/years after guidance session
   - "Customer checked pension 6 months later - still satisfied"
   - Track whether guidance led to positive long-term results

3. **Efficient Training**:
   - Advisor reaches "senior" level (500+ consultations) in ~1 week real time
   - Can iterate and improve rapidly

### Implementation

```python
def run_training_simulation(advisor: AdvisorAgent, num_customers: int,
                             acceleration: int = 60):
    """
    Run training simulation with time acceleration.
    """
    virtual_env = VirtualEnvironment(acceleration_factor=acceleration)

    for i in range(num_customers):
        # Generate customer
        customer = generate_customer_agent()

        # Run consultation (tracked in virtual time)
        consultation_start = virtual_env.current_time
        outcome = run_consultation(advisor, customer, virtual_env)
        consultation_end = virtual_env.current_time

        # Log in virtual time
        outcome.virtual_timestamp = consultation_end

        # Learn from outcome
        if outcome.successful:
            advisor.case_base.add(customer, outcome)
        else:
            reflection = advisor.reflect_on_failure(customer, outcome)
            if reflection.validated:
                advisor.rules_base.add(reflection)

        # Advance virtual time (next customer arrives next day)
        virtual_env.advance_time(hours=24)

        # Log progress (in real time)
        if i % 100 == 0:
            print(f"[Real time: {datetime.now()}] "
                  f"[Virtual time: {virtual_env.current_time}] "
                  f"Completed {i} consultations")
```

## Closed-Loop Feedback

Unlike real-world guidance where outcomes often unknown, simulacrum provides complete feedback.

### Feedback Components

1. **Immediate Feedback** (during session):
   - Customer comprehension signals
   - Question quality
   - Engagement level

2. **Session-End Feedback**:
   - Customer satisfaction score
   - Goal alignment assessment
   - Comprehension level
   - Compliance verification

3. **Long-term Feedback** (simulated):
   - Did customer act on guidance?
   - Were goals achieved?
   - Would customer return for more guidance?

### Feedback Loop Diagram

```
Advisor provides guidance
        ↓
Customer responds (comprehension simulated)
        ↓
Session ends
        ↓
Outcome simulated
        ↓
    ┌───┴────┐
    │        │
Successful   Suboptimal
    │        │
    ↓        ↓
Case Base   Reflection
            ↓
        Rules Base
    │        │
    └────┬───┘
         ↓
Retrieved in next consultation
         ↓
Advisor performance improves
```

## Training Protocols

### Protocol 1: Foundational Training (Days 1-3)

**Goal**: Build basic competence with common scenarios

```python
foundation_protocol = {
    "num_customers": 1000,
    "diversity": "moderate",
    "customer_types": {
        "simple_cases": 0.6,      # 1-2 DC pensions, clear situation
        "moderate_cases": 0.3,    # 3-4 pensions, some complexity
        "complex_cases": 0.1      # Introduction to complex scenarios
    },
    "focus_areas": [
        "basic_pension_concepts",
        "consolidation_benefits_and_risks",
        "understanding_verification",
        "FCA_compliant_language"
    ]
}
```

**Success Metrics**:
- Compliance pass rate > 95%
- Customer satisfaction > 7.0
- Understanding verification rate > 80%

### Protocol 2: Advanced Training (Days 4-7)

**Goal**: Handle complex scenarios and edge cases

```python
advanced_protocol = {
    "num_customers": 2000,
    "diversity": "high",
    "customer_types": {
        "simple_cases": 0.2,
        "moderate_cases": 0.4,
        "complex_cases": 0.4       # More complex scenarios
    },
    "focus_areas": [
        "DB_pension_guidance",
        "guaranteed_features_identification",
        "signposting_to_regulated_advice",
        "handling_anxious_customers",
        "low_literacy_communication"
    ]
}
```

**Success Metrics**:
- Compliance pass rate > 98%
- Customer satisfaction > 8.0
- DB pension warnings given > 99% when applicable
- Signposting rate > 95% when appropriate

### Protocol 3: Continuous Improvement (Ongoing)

**Goal**: Maintain and enhance expertise

```python
continuous_protocol = {
    "num_customers_per_week": 500,
    "diversity": "very_high",
    "customer_types": {
        "distribution": "realistic"  # Mirror real-world distribution
    },
    "focus_areas": [
        "novel_scenarios",
        "regulation_updates",
        "customer_feedback_patterns",
        "efficiency_optimization"
    ]
}
```

## Evaluation Metrics

### Virtual World Metrics (from Agent Hospital)

Track advisor performance within simulation:

1. **Task Accuracy**:
   - Risk assessment accuracy: % of consultations where all risks identified
   - Guidance appropriateness: % of consultations with appropriate guidance
   - Compliance rate: % FCA-compliant (must be 100%)

2. **Customer Outcomes**:
   - Satisfaction score: Mean customer satisfaction (0-10)
   - Comprehension score: % of customers who understood guidance
   - Goal alignment: % of consultations addressing customer goals

3. **Learning Progress**:
   - Case base size: Number of successful cases accumulated
   - Rules base size: Number of validated rules learned
   - Improvement trajectory: Performance trend over time

### Real-World Alignment Metrics

Validate that virtual training transfers to real-world performance:

1. **Benchmark Testing**:
   - Test advisor on held-out scenarios not seen in training
   - Compare to human advisor responses
   - Measure believability and appropriateness

2. **Human Evaluation**:
   - Expert reviewers rate guidance quality
   - Compare virtual-trained vs. baseline advisors
   - Assess readiness for real-world deployment

## Implementation Architecture

### System Components

```python
class VirtualEnvironment:
    """Main simulation environment."""

    def __init__(self, acceleration_factor: int = 60):
        self.time_manager = VirtualTimeManager(acceleration_factor)
        self.event_orchestrator = EventOrchestrator()
        self.customer_generator = CustomerGenerator()
        self.outcome_simulator = OutcomeSimulator()
        self.learning_system = LearningSystem()

    def run_consultation(self, advisor: AdvisorAgent,
                         customer: CustomerAgent) -> Outcome:
        """
        Run a complete guidance consultation.
        """
        # Event 1: Customer Inquiry
        inquiry = self.event_orchestrator.trigger_inquiry(customer)

        # Event 2: Information Gathering
        customer_info = self.event_orchestrator.gather_information(
            advisor, customer
        )

        # Event 3: Risk Assessment
        risks = self.event_orchestrator.assess_risks(
            advisor, customer_info
        )

        # Event 4: Information Provision
        explanation = self.event_orchestrator.provide_information(
            advisor, customer, risks
        )

        # Event 5: Understanding Verification
        comprehension = self.event_orchestrator.verify_understanding(
            advisor, customer, explanation
        )

        # Event 6: Guidance Provision
        guidance = self.event_orchestrator.provide_guidance(
            advisor, customer, comprehension
        )

        # Event 7: Customer Decision
        decision = self.event_orchestrator.customer_decision(
            customer, guidance
        )

        # Event 8: Outcome Tracking
        outcome = self.outcome_simulator.simulate_outcome(
            customer, guidance, comprehension, decision
        )

        # Learning
        self.learning_system.process_outcome(advisor, customer, outcome)

        return outcome
```

### Event Orchestrator

```python
class EventOrchestrator:
    """Manages the flow of interaction events."""

    def gather_information(self, advisor: AdvisorAgent,
                           customer: CustomerAgent) -> CustomerInfo:
        """
        Orchestrate information gathering phase.
        """
        conversation = []
        info_gathered = CustomerInfo()

        # Advisor asks questions
        max_turns = 10
        for turn in range(max_turns):
            # Advisor generates question
            question = advisor.ask_information_gathering_question(
                info_gathered, conversation
            )
            conversation.append({"role": "advisor", "content": question})

            # Customer responds
            response = customer.respond(question, conversation)
            conversation.append({"role": "customer", "content": response})

            # Extract information from response
            info_gathered.update_from_response(response)

            # Check if sufficient information gathered
            if info_gathered.is_sufficient():
                break

        return info_gathered
```

## Scaling Considerations

### Parallel Execution

Run multiple consultations in parallel for efficiency:

```python
def run_parallel_training(advisors: List[AdvisorAgent],
                          num_customers: int):
    """
    Train multiple advisors in parallel.
    """
    with ThreadPoolExecutor(max_workers=len(advisors)) as executor:
        futures = []
        for advisor in advisors:
            future = executor.submit(
                run_training_simulation,
                advisor,
                num_customers
            )
            futures.append(future)

        for future in as_completed(futures):
            result = future.result()
            print(f"Advisor {result.advisor_id} completed training")
```

### Cost Optimization

LLM API calls are the main cost driver:

1. **Use Smaller Models for Customer Agents**:
   - GPT-3.5-Turbo for customer generation and responses
   - GPT-4 only for advisor (where quality critical)

2. **Caching**:
   - Cache static prompts (advisor profile, FCA rules)
   - Reuse customer profiles across different advisors

3. **Batch Processing**:
   - Generate customer population in advance
   - Batch embedding calculations

**Estimated Costs** (per 1000 consultations):
- Customer generation: $50 (GPT-3.5)
- Advisor consultations: $300 (GPT-4)
- Outcome simulation: $20 (GPT-3.5)
- Embeddings: $10
- **Total: ~$380 per 1000 consultations**

## Integration with Real-World Deployment

### Hybrid Training Mode

Continue learning from real-world interactions:

```python
class HybridLearningSystem:
    """
    Combines virtual training with real-world learning.
    """

    def process_real_interaction(self, advisor: AdvisorAgent,
                                  real_customer: Dict,
                                  guidance_provided: str,
                                  human_review: Review):
        """
        Learn from real-world interaction (with human supervision).
        """
        # If guidance was good (passed human review)
        if human_review.approved:
            # Add to case base (with privacy protections)
            anonymized = anonymize_customer(real_customer)
            advisor.case_base.add_real_case(anonymized, guidance_provided)

        # If guidance was suboptimal
        elif human_review.needs_improvement:
            # Reflect and learn
            reflection = advisor.reflect_on_real_failure(
                real_customer, guidance_provided, human_review.feedback
            )
            if reflection.validated:
                advisor.rules_base.add(reflection)
```

### Deployment Stages

1. **Stage 1: Shadow Mode**
   - Advisor generates guidance
   - Human advisor reviews and delivers
   - Track agreement rate

2. **Stage 2: Assisted Mode**
   - Advisor generates guidance
   - Human makes minor edits
   - Advisor learns from edits

3. **Stage 3: Supervised Mode**
   - Advisor delivers guidance directly
   - Human monitors (random sampling)
   - Intervene if issues detected

4. **Stage 4: Autonomous Mode**
   - Advisor operates independently
   - Periodic audits
   - Continuous learning

## Summary

The Virtual Training Environment provides:
- **Safe practice space** for advisor agents
- **Time acceleration** for rapid skill development
- **Closed-loop feedback** for continuous improvement
- **Diverse scenarios** covering full range of guidance needs
- **Measurable progress** with clear metrics
- **Real-world alignment** validated before deployment

This enables advisors to reach expert-level performance before interacting with real customers, while continuing to learn and improve throughout deployment.

See related specifications:
- `architecture.md`: Overall system design
- `advisor-agent.md`: Advisor cognitive architecture
- `customer-agent.md`: Customer simulation
- `learning-system.md`: How advisors evolve
