"""Original f-string prompt functions preserved for regression testing.

This file contains the original prompt-building functions before migrating to Jinja templates.
These functions will be used for regression testing to ensure the Jinja templates produce
equivalent or better output than the original f-string implementations.

DO NOT MODIFY THIS FILE - it serves as a reference implementation.
"""

from typing import List
from guidance_agent.core.types import (
    Case,
    CustomerProfile,
    AdvisorProfile,
    GuidanceRule,
    RetrievedContext,
)
from guidance_agent.core.memory import MemoryNode


# ============================================================================
# From: src/guidance_agent/advisor/prompts.py
# Lines: 155-216
# ============================================================================

def original_build_guidance_prompt(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> str:
    """Build complete prompt for guidance generation.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY

    Args:
        advisor: Advisor profile
        customer: Customer profile
        context: Retrieved context (cases, rules, memories)
        conversation_history: Prior conversation

    Returns:
        Complete guidance generation prompt
    """
    from guidance_agent.advisor.prompts import (
        format_customer_profile,
        format_conversation,
        format_cases,
        format_rules,
        format_memories,
    )

    prompt = f"""You are {advisor.name}, a pension guidance specialist.

{advisor.description}

Your role is to provide FCA-compliant pension GUIDANCE (not advice). This means:
- Present options without recommending specific choices
- Use language like "you could consider" rather than "you should"
- Explain pros and cons of different options
- Ensure customer understanding throughout
- Signpost to FCA-regulated advisors for complex decisions

CUSTOMER PROFILE:
{format_customer_profile(customer)}

CONVERSATION HISTORY:
{format_conversation(conversation_history)}

RETRIEVED CONTEXT:

Similar Past Cases:
{format_cases(context.cases)}

Learned Guidance Rules:
{format_rules(context.rules)}

Relevant Memories:
{format_memories(context.memories)}

FCA REQUIREMENTS:
{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary, avoid regulated advice"}

CUSTOMER'S CURRENT QUESTION:
"{customer.presenting_question}"

TASK:
Provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level ({customer.demographics.financial_literacy if customer.demographics else 'medium'})
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding

Your guidance:"""

    return prompt


# ============================================================================
# From: src/guidance_agent/advisor/prompts.py
# Lines: 219-316
# ============================================================================

def original_build_guidance_prompt_cached(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> List[dict]:
    """Build cache-optimized prompt for guidance generation.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY

    This function structures the prompt to maximize cache hit rates:
    - Static content (system prompt, FCA requirements) goes first and is cached
    - Semi-static content (customer context) is cached within conversations
    - Variable content (current question) is not cached

    Args:
        advisor: Advisor profile
        customer: Customer profile
        context: Retrieved context (cases, rules, memories)
        conversation_history: Prior conversation

    Returns:
        List of message dictionaries with cache control markers
    """
    from guidance_agent.advisor.prompts import (
        format_customer_profile,
        format_conversation,
        format_cases,
        format_rules,
        format_memories,
    )

    # Part 1: System prompt (static, always cached)
    system_prompt = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""You are {advisor.name}, a pension guidance specialist.

{advisor.description}

Your role is to provide FCA-compliant pension GUIDANCE (not advice). This means:
- Present options without recommending specific choices
- Use language like "you could consider" rather than "you should"
- Explain pros and cons of different options
- Ensure customer understanding throughout
- Signpost to FCA-regulated advisors for complex decisions""",
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }

    # Part 2: FCA requirements and learned rules (static, always cached)
    fca_context = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""FCA Requirements and Guidelines:

{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary, avoid regulated advice"}

Learned Guidance Rules:
{format_rules(context.rules)}""",
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }

    # Part 3: Customer context and similar cases (semi-static, cached within conversation)
    customer_context = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""Customer Profile:
{format_customer_profile(customer)}

Similar Past Cases:
{format_cases(context.cases)}

Relevant Memories:
{format_memories(context.memories)}""",
                "cache_control": {"type": "ephemeral"},
            }
        ],
    }

    # Part 4: Conversation and current question (variable, not cached)
    user_message = {
        "role": "user",
        "content": f"""Previous conversation:
{format_conversation(conversation_history)}

Customer's current question: "{customer.presenting_question}"

Please provide appropriate pension guidance that:
1. Addresses the customer's specific question
2. Uses language appropriate for their literacy level ({customer.demographics.financial_literacy if customer.demographics else 'medium'})
3. Presents balanced information (pros and cons)
4. Stays clearly within the FCA guidance boundary
5. Checks customer understanding

Your guidance:""",
    }

    return [system_prompt, fca_context, customer_context, user_message]


# ============================================================================
# From: src/guidance_agent/advisor/prompts.py
# Lines: 319-361
# ============================================================================

def original_build_reasoning_prompt(
    customer: CustomerProfile,
    context: RetrievedContext,
) -> str:
    """Build prompt for chain-of-thought reasoning.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY

    Args:
        customer: Customer profile
        context: Retrieved context

    Returns:
        Reasoning prompt
    """
    from guidance_agent.advisor.prompts import (
        format_customer_profile,
        format_cases,
        format_rules,
    )

    prompt = f"""Before providing guidance, think through the situation step-by-step.

CUSTOMER PROFILE:
{format_customer_profile(customer)}

CUSTOMER'S QUESTION:
"{customer.presenting_question}"

RETRIEVED CONTEXT:
Similar Cases:
{format_cases(context.cases)}

Learned Rules:
{format_rules(context.rules)}

FCA REQUIREMENTS:
{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary"}

TASK:
Think through this step-by-step:
1. What is the customer really asking?
2. What are the key considerations for this situation?
3. What similar cases or rules are relevant?
4. What risks or important points must be covered?
5. How should I adapt my language for their literacy level?
6. What checks should I include to ensure understanding?

Your reasoning:"""

    return prompt


# ============================================================================
# From: src/guidance_agent/advisor/prompts.py
# Lines: 364-403
# ============================================================================

def original_build_guidance_prompt_with_reasoning(
    customer: CustomerProfile,
    context: RetrievedContext,
    reasoning: str,
) -> str:
    """Build prompt for guidance generation given reasoning.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY

    Args:
        customer: Customer profile
        context: Retrieved context
        reasoning: Chain-of-thought reasoning

    Returns:
        Guidance prompt with reasoning
    """
    from guidance_agent.advisor.prompts import format_customer_profile

    prompt = f"""You have analyzed a customer's pension question. Now provide guidance based on your reasoning.

CUSTOMER PROFILE:
{format_customer_profile(customer)}

CUSTOMER'S QUESTION:
"{customer.presenting_question}"

YOUR REASONING:
{reasoning}

FCA REQUIREMENTS:
{context.fca_requirements if context.fca_requirements else "Stay within guidance boundary, avoid regulated advice"}

TASK:
Based on your reasoning above, provide pension guidance that:
1. Addresses the customer's question
2. Uses appropriate language for their literacy level
3. Presents balanced information
4. Stays within FCA guidance boundary
5. Checks customer understanding

Your guidance:"""

    return prompt


# ============================================================================
# From: src/guidance_agent/advisor/agent.py
# Lines: 461-490
# ============================================================================

def original_refine_for_compliance_prompt(
    guidance: str,
    issues: List,
    customer: CustomerProfile,
) -> str:
    """Build refinement prompt for compliance issues.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/advisor/agent.py:461-490

    Args:
        guidance: Original guidance that failed validation
        issues: List of compliance issues
        customer: Customer profile

    Returns:
        Refinement prompt
    """
    # Build issues text
    issues_text = "\n".join(
        [
            f"- {issue.description} (Suggestion: {issue.suggestion})"
            for issue in issues
        ]
    )

    prompt = f"""The following pension guidance failed FCA compliance validation.
Please revise it to address the issues while maintaining the helpful intent.

ORIGINAL GUIDANCE:
{guidance}

COMPLIANCE ISSUES:
{issues_text}

CUSTOMER CONTEXT:
Age: {customer.demographics.age if customer.demographics else 'Unknown'}
Financial Literacy: {customer.demographics.financial_literacy if customer.demographics else 'medium'}
Question: {customer.presenting_question}

TASK:
Revise the guidance to:
1. Address all compliance issues
2. Maintain helpful and relevant content
3. Use appropriate language for customer's literacy level
4. Stay clearly within FCA guidance boundary

REVISED GUIDANCE:"""

    return prompt


# ============================================================================
# From: src/guidance_agent/advisor/agent.py
# Lines: 504-540
# ============================================================================

def original_handle_borderline_case_prompt(
    guidance: str,
    validation,
    context: RetrievedContext,
) -> str:
    """Build prompt for handling borderline validation case.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/advisor/agent.py:504-540

    Args:
        guidance: Guidance that passed but with low confidence
        validation: Validation result
        context: Retrieved context

    Returns:
        Strengthening prompt
    """
    prompt = f"""The following pension guidance passed compliance checks but with borderline confidence ({validation.confidence:.2f}).
Please strengthen and clarify it while maintaining compliance.

ORIGINAL GUIDANCE:
{guidance}

VALIDATION CONCERNS:
{validation.reasoning}

FCA REQUIREMENTS:
{context.fca_requirements}

TASK:
Strengthen the guidance by:
1. Making language more precise and clear
2. Being more explicit about guidance vs advice boundary
3. Ensuring all risks are clearly stated
4. Adding understanding verification
5. Maintaining warmth and helpfulness

STRENGTHENED GUIDANCE:"""

    return prompt


# ============================================================================
# From: src/guidance_agent/compliance/validator.py
# Lines: 182-274
# ============================================================================

def original_build_validation_prompt(
    guidance: str,
    customer: CustomerProfile,
    reasoning: str,
) -> str:
    """Build prompt for compliance validation.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/compliance/validator.py:182-274

    Args:
        guidance: The guidance text to validate
        customer: Customer profile
        reasoning: Reasoning behind the guidance

    Returns:
        Formatted validation prompt
    """
    # Check if customer has DB pension
    has_db_pension = any(p.is_db_scheme for p in customer.pensions)
    db_context = ""
    if has_db_pension:
        db_context = """
        IMPORTANT: Customer has a defined benefit (DB) pension scheme.
        DB transfers require FCA-regulated financial advice and come with
        significant warnings about giving up guaranteed income.
        """

    # Get customer literacy level for context
    literacy = (
        customer.demographics.financial_literacy
        if customer.demographics
        else "medium"
    )

    prompt = f"""You are a compliance expert reviewing pension guidance for FCA compliance.

Customer Context:
- Age: {customer.demographics.age if customer.demographics else 'Unknown'}
- Financial Literacy: {literacy}
- Goals: {customer.goals}
{db_context}

Guidance to Review:
"{guidance}"

Advisor's Reasoning:
{reasoning if reasoning else "Not provided"}

FCA Compliance Checklist:

1. **Guidance vs Advice Boundary**
   - Does the guidance avoid making specific recommendations?
   - Does it use language like "you could consider" rather than "you should"?
   - Does it maintain impartiality and present options without preference?
   - FAIL if it crosses into regulated advice territory

2. **Risk Disclosure**
   - Are relevant risks clearly explained?
   - Are tax implications mentioned where relevant?
   - Is the guidance balanced (pros and cons)?
   - FAIL if risks are missing or inadequately explained

3. **Clear and Not Misleading**
   - Is the language appropriate for the customer's literacy level?
   - Is the guidance clear and unambiguous?
   - Does it avoid technical jargon without explanation?
   - FAIL if unclear or potentially misleading

4. **Understanding Verification**
   - Does the guidance check or encourage customer understanding?
   - Are follow-up questions asked?
   - Is comprehension verified before proceeding?
   - FAIL if no attempt to verify understanding

5. **Signposting**
   - For DB transfers or complex decisions, is customer signposted to FCA-regulated advisor?
   - Is appropriate escalation suggested when needed?
   - FAIL if signposting required but missing

Provide your analysis in this exact format:

ANALYSIS:
1. Guidance vs Advice boundary: [PASS/FAIL/UNCERTAIN] - [brief explanation]
2. Risk disclosure: [PASS/FAIL/UNCERTAIN] - [brief explanation]
3. Clear and not misleading: [PASS/FAIL/UNCERTAIN] - [brief explanation]
4. Understanding verification: [PASS/FAIL/UNCERTAIN] - [brief explanation]
5. Signposting: [PASS/FAIL/UNCERTAIN/N/A] - [brief explanation]

OVERALL: [PASS/FAIL/UNCERTAIN]
CONFIDENCE: [0.00-1.00]
ISSUES: [comma-separated list of issues, or "None"]
"""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/agent.py
# Lines: 78-101
# ============================================================================

def original_simulate_comprehension_prompt(
    profile: CustomerProfile,
    guidance: str,
) -> str:
    """Build prompt for simulating customer comprehension.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/agent.py:78-101

    Args:
        profile: Customer profile
        guidance: Guidance provided by advisor

    Returns:
        Comprehension simulation prompt
    """
    prompt = f"""Simulate customer comprehension of pension guidance.

Customer Profile:
- Age: {profile.demographics.age if profile.demographics else 'unknown'}
- Financial literacy: {profile.demographics.financial_literacy if profile.demographics else 'medium'}
- Goals: {profile.goals}

Guidance Provided:
"{guidance}"

Assess comprehension based on:
1. Customer's literacy level ({profile.demographics.financial_literacy if profile.demographics else 'medium'})
2. Complexity of guidance
3. Use of technical language vs plain English
4. Presence of analogies or examples
5. Whether advisor checked understanding

Determine:
- understanding_level: "not_understood" | "partially_understood" | "fully_understood"
- confusion_points: list of specific concepts that confused customer (empty if understood)
- customer_feeling: "confident" | "uncertain" | "overwhelmed" | "satisfied" | "confused"

Return JSON only, no explanation."""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/agent.py
# Lines: 146-179
# ============================================================================

def original_customer_respond_prompt(
    profile: CustomerProfile,
    advisor_message: str,
    comprehension: dict,
) -> str:
    """Build prompt for generating customer response.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/agent.py:146-179

    Args:
        profile: Customer profile
        advisor_message: Message from advisor
        comprehension: Comprehension assessment

    Returns:
        Customer response generation prompt
    """
    prompt = f"""Generate realistic customer response in pension guidance conversation.

Customer Profile:
- Age: {profile.demographics.age if profile.demographics else 'unknown'}
- Financial literacy: {profile.demographics.financial_literacy if profile.demographics else 'medium'}
- Goals: {profile.goals}

Advisor just said:
"{advisor_message}"

Comprehension Assessment:
- Understanding: {comprehension['understanding_level']}
- Confusion points: {comprehension['confusion_points']}
- Customer feeling: {comprehension['customer_feeling']}

Generate customer's response that:
1. Reflects their understanding level
   - If confused: Ask for clarification on specific points
   - If understood: Acknowledge and move forward or ask about next steps
   - If partially understood: Express understanding but ask about unclear parts

2. Matches their literacy level ({profile.demographics.financial_literacy if profile.demographics else 'medium'})
   - Low: Simple language, may need concepts explained again
   - Medium: Clear but not overly sophisticated
   - High: Can engage with more complex explanations

3. Is natural and conversational (1-3 sentences typically)

4. Shows realistic customer behavior:
   - If overwhelmed: Express anxiety or uncertainty
   - If confident: Express satisfaction and readiness to proceed
   - If uncertain: Ask for reassurance or examples

Customer response:"""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/simulator.py
# Lines: 43-86
# ============================================================================

def original_simulate_outcome_prompt(
    customer,
    conversation_history: List[dict],
    has_db_pension: bool,
) -> str:
    """Build prompt for simulating consultation outcome.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/simulator.py:43-86

    Args:
        customer: CustomerAgent with profile and conversation memory
        conversation_history: List of conversation messages
        has_db_pension: Whether customer has DB pension

    Returns:
        Outcome simulation prompt
    """
    # Build conversation summary
    conversation_text = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in conversation_history]
    )

    prompt = f"""Simulate the outcome of a pension guidance consultation.

Customer Profile:
- Age: {customer.profile.demographics.age if customer.profile.demographics else 'unknown'}
- Financial literacy: {customer.profile.demographics.financial_literacy if customer.profile.demographics else 'medium'}
- Goals: {customer.profile.goals}
- Presenting question: {customer.profile.presenting_question}
- Has DB pension: {has_db_pension}

Conversation:
{conversation_text}

Customer comprehension level throughout: {customer.comprehension_level:.2f}

Evaluate the consultation and provide scores:

1. customer_satisfaction (0-10): How satisfied was the customer with the guidance?
   - Consider: Were questions answered? Was advisor helpful and clear?

2. comprehension (0-10): How well did customer understand the guidance?
   - Consider: Was language appropriate? Were concepts explained? Understanding checked?

3. goal_alignment (0-10): How well did guidance align with customer's goals?
   - Consider: Were stated goals addressed? Were underlying concerns resolved?

4. risks_identified (true/false): Were relevant risks identified and explained?

5. guidance_appropriate (true/false): Was guidance appropriate for customer's situation?

6. fca_compliant (true/false): Did advisor stay within guidance boundary (not advice)?
   - Guidance: General information, options, pros/cons
   - Advice: Specific recommendations ("you should do X")

7. understanding_checked (true/false): Did advisor check customer understanding?

8. signposted_when_needed (true/false): Did advisor signpost to regulated advice when needed?

9. has_db_pension (true/false): {has_db_pension}

10. db_warning_given (true/false): If DB pension present, was transfer warning given?

11. reasoning: Brief explanation of outcome assessment (1-2 sentences)

Return JSON only, no explanation."""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/generator.py
# Lines: 49-70
# ============================================================================

def original_generate_demographics_prompt(
    age: int,
    literacy: str = None,
) -> str:
    """Build prompt for generating customer demographics.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/generator.py:49-70

    Args:
        age: Customer age
        literacy: Optional literacy level

    Returns:
        Demographics generation prompt
    """
    prompt = f"""Generate realistic UK customer demographics for pension guidance simulation.

Age: {age}
Financial literacy: {literacy if literacy else 'varied'}

Generate JSON with:
- gender: "M" | "F" | "Other"
- location: UK city/region
- employment_status: "employed" | "self-employed" | "unemployed" | "retired"
- occupation: realistic for age (teacher, nurse, engineer, retail worker, etc.)
- financial_literacy: "low" | "medium" | "high"

Ensure:
- Occupation realistic for age and location
- Employment status realistic for age (retired if 65+)
- Diverse occupations and backgrounds
- Financial literacy appropriate to occupation

Return only valid JSON, no explanation."""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/generator.py
# Lines: 113-138
# ============================================================================

def original_generate_financial_situation_prompt(
    demographics,
) -> str:
    """Build prompt for generating financial situation.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/generator.py:113-138

    Args:
        demographics: Customer demographics

    Returns:
        Financial situation generation prompt
    """
    prompt = f"""Generate realistic financial situation for UK pension guidance simulation.

Customer: Age {demographics.age}, {demographics.employment_status}
Location: {demographics.location}

Based on UK statistics:
- Age {demographics.age}
- Employment: {demographics.employment_status}

Generate JSON with:
- annual_income: realistic for age/status (£20k-£80k typically)
- total_assets: pension + savings (age-appropriate)
- total_debt: realistic (mortgage, loans, credit cards)
- dependents: number of dependents (age-appropriate)
- risk_tolerance: "low" | "medium" | "high"

Guidelines:
- Younger: Lower income/assets, possibly higher debt
- Mid-career: Moderate income/assets, family debt
- Near retirement: Higher assets, lower debt
- Retired: Lower income (pension), higher assets
- Unemployed: Minimal income, rely on savings

Return only valid JSON, no explanation."""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/generator.py
# Lines: 203-231
# ============================================================================

def original_generate_pension_pot_prompt(
    demographics,
    pot_number: int,
    total_pots: int,
    pot_type: str,
) -> str:
    """Build prompt for generating pension pot details.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/generator.py:203-231

    Args:
        demographics: Customer demographics
        pot_number: Current pot number
        total_pots: Total number of pots
        pot_type: Type of pension pot

    Returns:
        Pension pot generation prompt
    """
    prompt = f"""Generate realistic pension pot details for UK pension guidance simulation.

Customer: Age {demographics.age}, {demographics.employment_status}
Pension pot {pot_number} of {total_pots}
Type: {pot_type}

Generate JSON with:
- pot_id: unique identifier (e.g., "pot{pot_number}")
- provider: realistic UK provider (NEST, Aviva, Royal London, Standard Life, etc.)
- pot_type: "{pot_type}"
- current_value: realistic for age and career stage (£0-£200k typically)
- projected_value: future value (typically 1.2-1.5x current for DC)
- age_accessible: typically 55 or 58
- is_db_scheme: {str(pot_type == "defined_benefit").lower()}
- db_guaranteed_amount: annual amount if DB, else null

Ensure:
- Values consistent with age {demographics.age}
- DC pensions have current_value > 0
- DB pensions have db_guaranteed_amount > 0
- Realistic providers for pot age
- Older pots may have legacy providers

Return only valid JSON, no explanation."""

    return prompt


# ============================================================================
# From: src/guidance_agent/customer/generator.py
# Lines: 287-314
# ============================================================================

def original_generate_goals_and_inquiry_prompt(
    demographics,
    financial,
    pots: List,
) -> str:
    """Build prompt for generating customer goals and inquiry.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/customer/generator.py:287-314

    Args:
        demographics: Customer demographics
        financial: Financial situation
        pots: List of pension pots

    Returns:
        Goals and inquiry generation prompt
    """
    prompt = f"""Generate realistic customer goals and inquiry for pension guidance simulation.

Customer: Age {demographics.age}, {demographics.employment_status}
Financial literacy: {demographics.financial_literacy}
Number of pensions: {len(pots)}
Total pension value: £{sum(p.current_value for p in pots):,.0f}

Generate JSON with:
- goals: customer's main objectives (1-2 sentences)
- presenting_question: what they ask first (natural, conversational, 1-3 sentences)

Ensure:
- Question appropriate for literacy level ("{demographics.financial_literacy}")
- Goals realistic for age {demographics.age}
- Natural conversational tone
- Not overly sophisticated (most aren't pension experts)
- Reflects genuine confusion or need for guidance

Common goals by age:
- 20s-30s: "Understand basics", "Check I'm saving enough"
- 40s: "Consolidate pensions", "Reduce fees", "Plan for retirement"
- 50s-60s: "Maximize retirement income", "Access options", "Tax planning"
- 65+: "Make pension last", "Understand drawdown"

Return only valid JSON, no explanation."""

    return prompt


# ============================================================================
# From: src/guidance_agent/learning/reflection.py
# Lines: 45-67
# ============================================================================

def original_reflect_on_failure_prompt(
    customer_profile: CustomerProfile,
    guidance_provided: str,
    outcome,
) -> str:
    """Build prompt for reflecting on consultation failure.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/learning/reflection.py:45-67

    Args:
        customer_profile: Customer profile from the failed consultation
        guidance_provided: Guidance that was provided
        outcome: Failed outcome with reasoning and issues

    Returns:
        Reflection prompt
    """
    prompt = f"""Analyze this failed pension guidance consultation and extract a learning principle.

Customer Profile:
- Age: {customer_profile.demographics.age if customer_profile.demographics else 'Unknown'}
- Financial Literacy: {customer_profile.demographics.financial_literacy if customer_profile.demographics else 'Unknown'}
- Question: {customer_profile.presenting_question}

Guidance Provided:
{guidance_provided}

What Went Wrong:
- Customer Satisfaction: {outcome.customer_satisfaction}/10
- Comprehension: {outcome.comprehension}/10
- Issues: {', '.join(outcome.issues)}
- Reasoning: {outcome.reasoning}

Task: Extract ONE specific, actionable principle that would prevent this type of failure.

Format your response as:
Principle: [specific principle]

Domain: [domain this applies to, e.g., communication, risk_disclosure, compliance, etc.]"""

    return prompt


# ============================================================================
# From: src/guidance_agent/learning/reflection.py
# Lines: 108-126
# ============================================================================

def original_validate_principle_prompt(
    principle: str,
) -> str:
    """Build prompt for validating a principle.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/learning/reflection.py:108-126

    Args:
        principle: The principle to validate

    Returns:
        Validation prompt
    """
    prompt = f"""Validate this pension guidance principle against FCA guidelines.

Principle: "{principle}"

Check:
1. Does it stay within the guidance boundary (not crossing into regulated advice)?
2. Does it align with FCA consumer protection principles?
3. Is it specific and actionable?
4. Would following it improve customer outcomes?

If the principle suggests:
- Recommending specific products → INVALID (advice, not guidance)
- Making suitability assessments → INVALID (requires regulation)
- Generic good practices → LOW CONFIDENCE (too vague)

Format your response as:
Valid: [True/False]
Confidence: [0.0-1.0]
Reason: [brief explanation]"""

    return prompt


# ============================================================================
# From: src/guidance_agent/learning/reflection.py
# Lines: 166-176
# ============================================================================

def original_refine_principle_prompt(
    principle: str,
    domain: str,
) -> str:
    """Build prompt for refining a principle.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/learning/reflection.py:166-176

    Args:
        principle: The principle to refine
        domain: The domain this principle applies to

    Returns:
        Refinement prompt
    """
    prompt = f"""Refine this pension guidance principle to make it more specific and actionable.

Original Principle: "{principle}"
Domain: {domain}

Make it:
1. Specific (what exactly should be done?)
2. Actionable (clear steps or criteria)
3. Measurable (how do you know if you followed it?)

Provide the refined principle (2-3 sentences maximum):"""

    return prompt


# ============================================================================
# From: src/guidance_agent/learning/reflection.py
# Lines: 210-228
# ============================================================================

def original_judge_rule_value_prompt(
    rule_principle: str,
    domain: str,
) -> str:
    """Build prompt for judging rule value.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/learning/reflection.py:210-228

    Args:
        rule_principle: The rule principle to judge
        domain: The domain this rule applies to

    Returns:
        Value judgment prompt
    """
    prompt = f"""Judge whether this pension guidance rule is valuable enough to store.

Rule: "{rule_principle}"
Domain: {domain}

A rule is valuable if it:
1. Addresses a specific, non-obvious situation
2. Provides concrete, actionable guidance
3. Goes beyond common sense
4. Could prevent real customer harm or confusion

A rule is NOT valuable if it:
1. States obvious common sense ("be polite", "be clear")
2. Is too vague or generic
3. Doesn't add to existing FCA guidance

Format your response as:
Valuable: [True/False]
Score: [0.0-1.0]"""

    return prompt


# ============================================================================
# From: src/guidance_agent/core/memory.py
# Lines: 389-397
# ============================================================================

def original_rate_importance_prompt(
    observation: str,
) -> str:
    """Build prompt for rating observation importance.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/core/memory.py:389-397

    Args:
        observation: The observation text to rate

    Returns:
        Importance rating prompt
    """
    prompt = f"""On the scale of 1 to 10, where 1 is purely mundane
(e.g., routine question about pension balance) and 10 is
extremely important (e.g., customer about to make life-changing
pension decision), rate the likely importance of the
following observation.

Observation: {observation}
Rating: <fill in>"""

    return prompt


# ============================================================================
# From: src/guidance_agent/evaluation/judge_validation.py
# Lines: 75-86
# ============================================================================

def original_llm_judge_evaluate_prompt(
    transcript: str,
) -> str:
    """Build prompt for LLM judge evaluation.

    ORIGINAL IMPLEMENTATION - DO NOT MODIFY
    Source: src/guidance_agent/evaluation/judge_validation.py:75-86

    Args:
        transcript: Full consultation transcript

    Returns:
        Evaluation prompt
    """
    prompt = f"""Evaluate if this pension guidance consultation was FCA-compliant.

Transcript:
{transcript}

Respond with:
- PASS or FAIL
- Confidence (0-1)
- Brief reasoning

Format: PASS|0.9|Reasoning here
"""

    return prompt


# ============================================================================
# SUMMARY
# ============================================================================

# Total original prompt functions backed up: 20
#
# Distribution by module:
# - src/guidance_agent/advisor/prompts.py: 4 functions
# - src/guidance_agent/advisor/agent.py: 2 inline prompts
# - src/guidance_agent/compliance/validator.py: 1 function
# - src/guidance_agent/customer/agent.py: 2 functions
# - src/guidance_agent/customer/simulator.py: 1 function
# - src/guidance_agent/customer/generator.py: 4 functions
# - src/guidance_agent/learning/reflection.py: 4 functions
# - src/guidance_agent/core/memory.py: 1 function
# - src/guidance_agent/evaluation/judge_validation.py: 1 inline prompt
#
# All functions are marked with:
# - Original file path
# - Line number range
# - "ORIGINAL IMPLEMENTATION - DO NOT MODIFY" warning
