# Customer Agent Specification

## Overview

Customer Agents are LLM-powered simulated customers used in the virtual training environment. They are inspired by the patient agent generation in Agent Hospital, using **LLM + Knowledge Base coupling** to create diverse, realistic pension guidance scenarios.

## Purpose

Customer Agents serve two primary purposes:

1. **Virtual Training**: Generate thousands of diverse customer scenarios for advisor agents to practice with
2. **Outcome Simulation**: Provide feedback on guidance quality by simulating customer comprehension, satisfaction, and goal achievement

## Customer Profile Structure

```python
class CustomerProfile:
    # Demographics
    customer_id: str
    name: str
    age: int  # 22-80 (working age to retirement)
    gender: str
    occupation: str
    employment_status: str  # "employed" | "self-employed" | "unemployed" | "retired"

    # Financial Situation
    annual_income: float
    pension_pots: List[PensionPot]
    total_pension_value: float
    other_savings: float
    debts: float

    # Pension Details
    pension_pots: List[PensionPot]

    # Goals & Preferences
    retirement_age_target: int
    primary_goals: List[str]  # ["simplify_pensions", "reduce_fees", "increase_contributions", "understand_options"]
    risk_tolerance: str  # "low" | "moderate" | "high"
    life_events: List[str]  # ["divorce", "inheritance", "career_change", "health_issue"]

    # Knowledge & Behavior
    financial_literacy: str  # "low" | "moderate" | "high"
    pension_knowledge: str  # "minimal" | "basic" | "informed"
    engagement_level: str  # "passive" | "active" | "anxious"
    communication_style: str  # "direct", "verbose", "hesitant", "questioning"

    # Initial Inquiry
    presenting_question: str  # What brings them to guidance session
    underlying_concerns: List[str]  # Deeper worries (may not articulate initially)
```

```python
class PensionPot:
    pension_id: str
    provider: str
    pension_type: str  # "defined_contribution" | "defined_benefit" | "personal" | "stakeholder"
    current_value: float  # For DC pensions
    promised_income: float  # For DB pensions (monthly amount at retirement age)
    contribution_rate: float  # Current % of salary (if still contributing)
    annual_fees: float
    special_features: List[str]  # ["guaranteed_annuity_rate", "protected_tax_free_cash", "low_fees", "flexible_access"]
    years_of_service: int  # For DB pensions
    normal_retirement_age: int
```

## Customer Generation Process

Based on Agent Hospital's LLM + Knowledge Base coupling approach.

### Step 1: Generate Demographics

```python
def generate_customer_demographics(diversity_requirement: str = "high") -> Dict:
    """
    Uses LLM to generate diverse customer demographics.
    """
    prompt = f"""
Generate realistic customer demographics for pension guidance simulation.

Requirements:
- Age: {random.randint(22, 80)}
- Diversity: {diversity_requirement} (ensure variety in occupations, backgrounds, situations)
- Realism: Based on typical UK demographics and pension scenarios

Generate JSON with:
- name (realistic UK name)
- age
- gender
- occupation (varied - teacher, nurse, engineer, retail worker, self-employed, etc.)
- employment_status
- location (UK city/region)

Return only valid JSON.
"""

    demographics = llm_call(prompt)
    return json.loads(demographics)
```

### Step 2: Generate Financial Situation

```python
def generate_financial_situation(demographics: Dict, pension_knowledge_base: Dict) -> Dict:
    """
    Generates realistic financial situation based on demographics and pension knowledge.
    """
    # Use age and occupation to determine realistic income range
    income_range = get_income_range(demographics["age"], demographics["occupation"])

    prompt = f"""
Generate realistic financial situation for pension guidance simulation.

Customer: {demographics["name"]}, {demographics["age"]}-year-old {demographics["occupation"]}

Based on UK pension statistics and typical patterns:
- Age {demographics["age"]} in occupation {demographics["occupation"]}
- Income range: £{income_range["min"]:,} - £{income_range["max"]:,}
- Number of pension pots: Typically 1-6 (more if older with multiple jobs)

Consider:
- Younger workers: Fewer pensions, smaller values, workplace auto-enrollment
- Mid-career: Mix of old and current workplace pensions
- Near retirement: Multiple pots from career history, larger values
- Career changes: More fragmented pension picture

Generate JSON with:
- annual_income (realistic for age/occupation)
- number_of_pension_pots (realistic for age/career stage)
- total_estimated_pension_value (age-appropriate)
- other_savings (realistic proportion)
- debts (realistic types and amounts)

Return only valid JSON.
"""

    financial_situation = llm_call(prompt)
    return json.loads(financial_situation)
```

### Step 3: Generate Pension Pots (with Knowledge Base Grounding)

```python
def generate_pension_pots(demographics: Dict, financial_situation: Dict,
                          pension_knowledge_base: PensionKnowledgeBase) -> List[PensionPot]:
    """
    Generates detailed pension pot information grounded in pension knowledge base.
    """
    num_pots = financial_situation["number_of_pension_pots"]
    pots = []

    for i in range(num_pots):
        # Determine pension type based on demographics and era
        pension_type = determine_pension_type(
            demographics["age"],
            demographics["occupation"],
            pot_index=i,
            knowledge_base=pension_knowledge_base
        )

        prompt = f"""
Generate realistic pension pot details for pension guidance simulation.

Customer: {demographics["name"]}, age {demographics["age"]}, {demographics["occupation"]}
Pension pot {i+1} of {num_pots}
Type: {pension_type}
Total pension wealth: £{financial_situation["total_estimated_pension_value"]:,}

Pension Knowledge Base Context:
{get_relevant_pension_rules(pension_type, pension_knowledge_base)}

Generate realistic details:
- If DC pension: Current value based on years of contributions
- If DB pension: Years of service, accrual rate, promised monthly income
- Provider (realistic UK provider: Aviva, Royal London, NEST, older ones for older pots)
- Annual fees (typical for pot size and provider)
- Any special features (guaranteed annuity rates for pre-2000 pots, protected tax-free cash, etc.)

Ensure:
- Values are consistent with customer age and career
- DB pensions only for older workers or public sector
- Fees realistic for pot size (higher % for small pots)
- Special features rare but valuable when present

Return JSON:
"""

        pot = llm_call(prompt)
        pots.append(json.loads(pot))

    return pots
```

### Step 4: Generate Goals and Inquiry

```python
def generate_customer_goals_and_inquiry(profile: CustomerProfile,
                                        pension_knowledge_base: PensionKnowledgeBase) -> Dict:
    """
    Generates customer's goals, concerns, and presenting question.
    """
    prompt = f"""
Generate realistic customer goals and inquiry for pension guidance simulation.

Customer Profile:
- {profile.name}, age {profile.age}, {profile.occupation}
- Income: £{profile.annual_income:,}
- {len(profile.pension_pots)} pension pots, total value £{profile.total_pension_value:,}
- Pension types: {[p.pension_type for p in profile.pension_pots]}

Common customer concerns based on this profile:
{get_typical_concerns_for_profile(profile, pension_knowledge_base)}

Generate:
1. Primary goals (1-3 main objectives like "understand my pensions", "reduce complexity", "plan for retirement")
2. Underlying concerns (deeper worries they may not articulate: "worried I haven't saved enough", "anxious about making wrong decision", "confused by terminology")
3. Presenting question (what they ask in first message to advisor - natural, conversational)
4. Financial literacy level (low/moderate/high based on question sophistication)
5. Engagement level (passive/active/anxious based on tone)

Ensure:
- Question is realistic for someone seeking pension guidance
- Reflects genuine confusion or information need
- Appropriate for their age and situation
- Not too sophisticated (most customers aren't pension experts)

Return JSON:
"""

    goals_inquiry = llm_call(prompt)
    return json.loads(goals_inquiry)
```

### Step 5: Quality Control (from Agent Hospital)

```python
def validate_customer_profile(profile: CustomerProfile,
                               pension_knowledge_base: PensionKnowledgeBase) -> ValidationResult:
    """
    Quality control agent ensures generated customer adheres to pension knowledge.
    Inspired by Agent Hospital's quality control mechanism.
    """
    prompt = f"""
You are a quality control agent for pension guidance simulations.

Review this generated customer profile for realism and adherence to UK pension rules:

{json.dumps(profile.to_dict(), indent=2)}

Check:
1. Age-appropriate pension values (not too high/low for career stage)
2. Realistic number of pension pots for age and career
3. Appropriate pension types (e.g., DB pensions rare for young private sector workers)
4. Fees realistic for pot sizes and providers
5. Income consistent with occupation and age
6. Goals and concerns realistic for situation
7. No contradictions (e.g., high pension knowledge but asking basic questions)

Pension Knowledge Base Rules:
- Auto-enrollment started 2012 (workers under 42 likely have AE pensions)
- DB pensions mainly public sector or pre-2000s private sector
- Small pot values (<£10k) common with high % fees
- Typical contribution rates: 8% total (5% employer, 3% employee)

Does this profile pass quality control? If not, what needs correction?

Return JSON with:
- passes: true/false
- issues: [list of problems]
- suggestions: [how to fix]
"""

    result = llm_call(prompt)
    return json.loads(result)
```

## Customer Behavior During Interaction

Customer Agents simulate realistic behavior during guidance sessions.

### Comprehension Simulation

```python
def simulate_comprehension(customer: CustomerProfile, guidance_provided: str,
                          conversation_history: List[str]) -> ComprehensionResult:
    """
    Simulates whether customer understood the guidance based on their literacy level
    and communication quality.
    """
    prompt = f"""
Simulate customer comprehension of pension guidance.

Customer Profile:
- Financial literacy: {customer.financial_literacy}
- Pension knowledge: {customer.pension_knowledge}
- Engagement: {customer.engagement_level}

Guidance Provided:
"{guidance_provided}"

Previous conversation:
{conversation_history[-3:]}  # Last 3 exchanges

Assess:
1. Would this customer understand the guidance given their literacy level?
2. Was technical language explained appropriately?
3. Were analogies/examples helpful for their learning style?
4. Did advisor check understanding?

Based on these factors, determine:
- understanding_level: "not_understood" | "partially_understood" | "fully_understood"
- confusion_points: [specific concepts that confused customer]
- customer_feeling: "confident" | "uncertain" | "overwhelmed" | "satisfied"

If customer didn't understand or is confused, they will ask follow-up questions.
If customer understood, they will move forward or ask about next steps.

Return JSON:
"""

    result = llm_call(prompt)
    return json.loads(result)
```

### Response Generation

```python
def generate_customer_response(customer: CustomerProfile, advisor_message: str,
                                comprehension: ComprehensionResult,
                                conversation_history: List[str]) -> str:
    """
    Generates realistic customer response based on comprehension and personality.
    """
    prompt = f"""
Generate realistic customer response in pension guidance conversation.

Customer: {customer.name}, {customer.age}, {customer.communication_style} communication style
Financial literacy: {customer.financial_literacy}
Current feeling: {comprehension.customer_feeling}
Understanding level: {comprehension.understanding_level}

Advisor just said:
"{advisor_message}"

Comprehension assessment:
- Understanding: {comprehension.understanding_level}
- Confusion points: {comprehension.confusion_points}

Previous conversation context:
{conversation_history[-2:]}

Generate customer's response that:
- Reflects their communication style ({customer.communication_style})
- Shows their understanding level (ask for clarification if confused)
- Is natural and conversational (not overly formal)
- Appropriate length (1-3 sentences for most responses)
- Shows realistic customer behavior:
  * If confused: Ask about specific point
  * If understood: Acknowledge and move to next concern
  * If anxious: Express worry or ask for reassurance
  * If satisfied: Express appreciation

Customer response:
"""

    response = llm_call(prompt)
    return response.strip()
```

### Outcome Simulation (Closed-Loop Feedback)

After guidance session completes, simulate the outcome.

```python
def simulate_guidance_outcome(customer: CustomerProfile, guidance_session: GuidanceSession,
                               advisor: AdvisorAgent) -> OutcomeResult:
    """
    Simulates customer outcome based on guidance quality.
    This creates the closed-loop feedback for advisor learning.
    """
    prompt = f"""
Simulate the outcome of a pension guidance session.

Customer: {customer.name}
Goals: {customer.primary_goals}
Concerns: {customer.underlying_concerns}

Guidance Session Summary:
- Duration: {guidance_session.duration_minutes} minutes
- Topics covered: {guidance_session.topics_covered}
- Advisor: {advisor.name}
- Key guidance points:
{guidance_session.key_points}

Comprehension throughout session:
{guidance_session.comprehension_checks}

Assess:
1. Did guidance address customer's goals? (goal_alignment: 0-10)
2. Were risks clearly explained? (risk_clarity: 0-10)
3. Did customer understand? (comprehension: 0-10)
4. Was guidance FCA-compliant? (compliance: 0-10)
5. Overall customer satisfaction (satisfaction: 0-10)

Based on these scores, determine:
- outcome_quality: "poor" | "fair" | "good" | "excellent"
- customer_satisfaction: 0-10
- likelihood_to_follow_guidance: "unlikely" | "possible" | "likely" | "very_likely"
- unmet_needs: [what customer still needs]
- advisor_strengths: [what advisor did well]
- advisor_improvements: [what could be better]

Return JSON:
"""

    outcome = llm_call(prompt)
    outcome_result = json.loads(outcome)

    # Determine success/failure for advisor learning
    outcome_result["successful"] = (
        outcome_result["customer_satisfaction"] >= 7 and
        outcome_result["goal_alignment"] >= 7 and
        outcome_result["comprehension"] >= 7 and
        outcome_result["compliance"] == 10  # Compliance must be perfect
    )

    return outcome_result
```

## Customer Diversity Requirements

To ensure comprehensive advisor training, generate diverse customer populations.

### Diversity Dimensions

1. **Age Distribution:**
   - 22-30: Early career (20%)
   - 31-45: Mid-career (30%)
   - 46-55: Pre-retirement (25%)
   - 56-67: Near retirement (20%)
   - 68+: Already retired (5%)

2. **Pension Complexity:**
   - Simple: 1-2 DC pensions, clear situation (30%)
   - Moderate: 3-4 mixed pensions, some complexity (40%)
   - Complex: 5+ pensions, DB pensions, special features (30%)

3. **Financial Literacy:**
   - Low: Struggles with terms, needs analogies (40%)
   - Moderate: Understands basics, some gaps (40%)
   - High: Informed, asks sophisticated questions (20%)

4. **Life Situations:**
   - Standard: Employed, standard career progression (60%)
   - Life events: Divorce, inheritance, redundancy, illness (25%)
   - Special cases: Self-employed, expat pensions, transfers (15%)

5. **Goals:**
   - Simplification: Reduce number of pensions (35%)
   - Fee reduction: Lower costs (25%)
   - Understanding: Just want to understand what they have (20%)
   - Planning: Preparing for retirement (15%)
   - Problem-solving: Specific issue to resolve (5%)

### Population Generation

```python
def generate_customer_population(n: int, diversity: str = "high") -> List[CustomerProfile]:
    """
    Generates population of n customers with specified diversity.
    """
    population = []

    # Define target distributions
    age_dist = [22-30: 0.2, 31-45: 0.3, 46-55: 0.25, 56-67: 0.2, 68+: 0.05]
    literacy_dist = ["low": 0.4, "moderate": 0.4, "high": 0.2]
    complexity_dist = ["simple": 0.3, "moderate": 0.4, "complex": 0.3]

    for i in range(n):
        # Sample from distributions to ensure diversity
        age = sample_from_distribution(age_dist)
        literacy = sample_from_distribution(literacy_dist)
        complexity = sample_from_distribution(complexity_dist)

        # Generate customer with these constraints
        demographics = generate_customer_demographics_constrained(age)
        financial_situation = generate_financial_situation(demographics, complexity)
        pension_pots = generate_pension_pots(demographics, financial_situation)
        goals_inquiry = generate_customer_goals_and_inquiry_constrained(
            demographics, financial_situation, literacy
        )

        customer = CustomerProfile(
            demographics=demographics,
            financial_situation=financial_situation,
            pension_pots=pension_pots,
            goals_inquiry=goals_inquiry
        )

        # Quality control
        if validate_customer_profile(customer).passes:
            population.append(customer)
        else:
            i -= 1  # Retry

    return population
```

## Customer Knowledge Base

Ground customer generation in factual pension knowledge.

### Knowledge Base Structure

```yaml
pension_knowledge_base:
  pension_types:
    defined_contribution:
      description: "Pension pot built from contributions, value depends on investment growth"
      typical_providers: ["NEST", "Aviva", "Royal London", "Standard Life"]
      common_features: ["flexible_access", "investment_choice"]
      typical_fees: "0.3% - 1.5% annual management charge"

    defined_benefit:
      description: "Guaranteed income based on salary and years of service"
      typical_sectors: ["public_sector", "large_employers_pre_2000"]
      calculation: "accrual_rate × years_service × final_salary"
      common_features: ["guaranteed_income", "inflation_protection", "survivor_benefits"]
      warning: "Valuable guarantees lost if transferred out"

    personal_pension:
      description: "Private pension arranged by individual"
      typical_providers: ["Legal & General", "Prudential", "Scottish Widows"]
      common_issues: ["higher_fees", "outdated_products", "no_employer_contributions"]

  regulations:
    auto_enrollment:
      started: 2012
      minimum_contributions: "8% (5% employer, 3% employee)"
      applies_to: "Employers, workers aged 22+ earning £10,000+"

    small_pots:
      definition: "Pensions under £10,000"
      common_issue: "High fees relative to value"
      consolidation_benefit: "Often beneficial due to fee savings"

    db_transfers:
      regulation: "Requires regulated advice if value >£30,000"
      fca_warning: "Most people worse off transferring from DB"
      special_features: ["guaranteed_annuity_rates", "protected_tax_free_cash"]

  typical_scenarios:
    young_worker:
      age_range: "22-30"
      pension_situation: "1-2 workplace DC pensions, small values"
      common_goals: ["understand basics", "check on track", "increase contributions"]

    mid_career:
      age_range: "31-45"
      pension_situation: "2-4 pensions from job changes, growing values"
      common_goals: ["consolidate pensions", "reduce fees", "understand what I have"]

    pre_retirement:
      age_range: "46-55"
      pension_situation: "Multiple pensions, mix of types, may include DB"
      common_goals: ["consolidation", "retirement planning", "maximize retirement income"]

    near_retirement:
      age_range: "56-67"
      pension_situation: "Full career history of pensions, considering drawdown"
      common_goals: ["access options", "tax planning", "make pension last"]
```

## Example Customer Profiles

### Example 1: Simple Case

```json
{
  "customer_id": "CUST-001",
  "name": "Emma Thompson",
  "age": 28,
  "occupation": "Primary School Teacher",
  "annual_income": 32000,
  "pension_pots": [
    {
      "type": "defined_contribution",
      "provider": "Teachers' Pension (DC section)",
      "value": 8500,
      "contribution_rate": 0.08,
      "fees": 0.005
    },
    {
      "type": "personal_pension",
      "provider": "Aviva",
      "value": 2200,
      "contribution_rate": 0,
      "fees": 0.012
    }
  ],
  "goals": ["understand my pensions", "check if I'm saving enough"],
  "financial_literacy": "low",
  "pension_knowledge": "minimal",
  "presenting_question": "Hi, I have two pensions and I'm not really sure what they are or if I'm saving enough for retirement. Can you help me understand?"
}
```

### Example 2: Complex Case

```json
{
  "customer_id": "CUST-042",
  "name": "David Chen",
  "age": 58,
  "occupation": "IT Consultant (formerly local government)",
  "annual_income": 65000,
  "pension_pots": [
    {
      "type": "defined_benefit",
      "provider": "Local Government Pension Scheme",
      "years_of_service": 12,
      "promised_monthly_income": 850,
      "special_features": ["inflation_protection", "survivor_benefits"]
    },
    {
      "type": "defined_contribution",
      "provider": "Standard Life",
      "value": 145000,
      "contribution_rate": 0.10,
      "fees": 0.0075
    },
    {
      "type": "personal_pension",
      "provider": "Prudential",
      "value": 35000,
      "fees": 0.015,
      "special_features": ["guaranteed_annuity_rate"]
    },
    {
      "type": "defined_contribution",
      "provider": "NEST",
      "value": 8000,
      "contribution_rate": 0,
      "fees": 0.013
    }
  ],
  "goals": ["simplify pension arrangements", "plan retirement at 65", "maximize retirement income"],
  "underlying_concerns": ["worried DB pension transfer restrictions", "anxious about making wrong decision with valuable benefits"],
  "financial_literacy": "moderate",
  "pension_knowledge": "basic",
  "presenting_question": "I have 4 different pensions including an old local government one. I'm thinking of retiring in about 7 years. Should I be combining these or leaving them separate? I'm confused about what's best."
}
```

## Integration with Virtual Environment

Customer Agents interact with Advisor Agents in the virtual training environment (see `virtual-environment.md`):

1. **Customer initiated**: Customer Agent enters with presenting question
2. **Advisor responds**: Advisor Agent provides guidance using RAG retrieval
3. **Customer reacts**: Customer Agent responds based on comprehension
4. **Iteration**: Conversation continues until guidance complete
5. **Outcome**: Customer Agent simulates outcome, providing feedback
6. **Learning**: Successful guidance → Case Base; Suboptimal → Reflection → Rules Base

## Summary

Customer Agents enable:
- **Unlimited practice scenarios** for advisor training
- **Diverse, realistic situations** covering full range of pension guidance needs
- **Closed-loop feedback** through outcome simulation
- **Automatic quality control** grounded in pension knowledge
- **Behavioral realism** through comprehension and response simulation

This approach eliminates manual data labeling while ensuring advisor agents gain comprehensive experience before real-world deployment.
