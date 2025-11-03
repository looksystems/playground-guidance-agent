# Advisor Template Mapping Reference

Quick reference showing how each original f-string prompt maps to the new Jinja template.

## 1. guidance_main.jinja

**Original Function:** `advisor/prompts.py:155-216` - `build_guidance_prompt()`

**Original Code:**
```python
def build_guidance_prompt(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> str:
    prompt = f"""You are {advisor.name}, a pension guidance specialist.

{advisor.description}

Your role is to provide FCA-compliant pension GUIDANCE (not advice). This means:
- Present options without recommending specific choices
- Use language like "you could consider" rather than "you should"
...
"""
    return prompt
```

**New Usage:**
```python
from guidance_agent.core.template_engine import render_template

def build_guidance_prompt(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> str:
    return render_template(
        "advisor/guidance_main.jinja",
        advisor=advisor,
        customer=customer,
        context=context,
        conversation_history=conversation_history,
    )
```

---

## 2. guidance_cached.jinja

**Original Function:** `advisor/prompts.py:219-316` - `build_guidance_prompt_cached()`

**Original Code:**
```python
def build_guidance_prompt_cached(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> List[dict]:
    system_prompt = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": f"""You are {advisor.name}, a pension guidance specialist.
...
```

**New Usage:**
```python
from guidance_agent.core.template_engine import get_template_engine

def build_guidance_prompt_cached(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> List[dict]:
    engine = get_template_engine()
    return engine.render_messages(
        "advisor/guidance_cached.jinja",
        advisor=advisor,
        customer=customer,
        context=context,
        conversation_history=conversation_history,
    )
```

---

## 3. reasoning.jinja

**Original Function:** `advisor/prompts.py:319-361` - `build_reasoning_prompt()`

**Original Code:**
```python
def build_reasoning_prompt(
    customer: CustomerProfile,
    context: RetrievedContext,
) -> str:
    prompt = f"""Before providing guidance, think through the situation step-by-step.

CUSTOMER PROFILE:
{format_customer_profile(customer)}
...
```

**New Usage:**
```python
from guidance_agent.core.template_engine import render_template

def build_reasoning_prompt(
    customer: CustomerProfile,
    context: RetrievedContext,
) -> str:
    return render_template(
        "advisor/reasoning.jinja",
        customer=customer,
        context=context,
    )
```

---

## 4. guidance_with_reasoning.jinja

**Original Function:** `advisor/prompts.py:364-403` - `build_guidance_prompt_with_reasoning()`

**Original Code:**
```python
def build_guidance_prompt_with_reasoning(
    customer: CustomerProfile,
    context: RetrievedContext,
    reasoning: str,
) -> str:
    prompt = f"""You have analyzed a customer's pension question. Now provide guidance based on your reasoning.

CUSTOMER PROFILE:
{format_customer_profile(customer)}
...
```

**New Usage:**
```python
from guidance_agent.core.template_engine import render_template

def build_guidance_prompt_with_reasoning(
    customer: CustomerProfile,
    context: RetrievedContext,
    reasoning: str,
) -> str:
    return render_template(
        "advisor/guidance_with_reasoning.jinja",
        customer=customer,
        context=context,
        reasoning=reasoning,
    )
```

---

## 5. compliance_refinement.jinja

**Original Location:** `advisor/agent.py:461-490` - Inline in `_refine_for_compliance()`

**Original Code:**
```python
def _refine_for_compliance(self, guidance: str, issues: List, customer: CustomerProfile) -> str:
    issues_text = "\n".join([
        f"- {issue.description} (Suggestion: {issue.suggestion})"
        for issue in issues
    ])

    prompt = f"""The following pension guidance failed FCA compliance validation.
Please revise it to address the issues while maintaining the helpful intent.

ORIGINAL GUIDANCE:
{guidance}

COMPLIANCE ISSUES:
{issues_text}
...
```

**New Usage:**
```python
from guidance_agent.core.template_engine import render_template

def _refine_for_compliance(self, guidance: str, issues: List, customer: CustomerProfile) -> str:
    prompt = render_template(
        "advisor/compliance_refinement.jinja",
        guidance=guidance,
        issues=issues,  # Template loops over this
        customer=customer,
    )

    # Then call LLM with prompt
    response = self.llm.generate(prompt)
    return response
```

**Note:** The template handles the loop over issues internally, so no need to build `issues_text` in Python.

---

## 6. borderline_strengthening.jinja

**Original Location:** `advisor/agent.py:504-540` - Inline in `_handle_borderline_case()`

**Original Code:**
```python
def _handle_borderline_case(self, guidance: str, validation, context: RetrievedContext) -> str:
    prompt = f"""The following pension guidance passed compliance checks but with borderline confidence ({validation.confidence:.2f}).
Please strengthen and clarify it while maintaining compliance.

ORIGINAL GUIDANCE:
{guidance}

VALIDATION CONCERNS:
{validation.reasoning}
...
```

**New Usage:**
```python
from guidance_agent.core.template_engine import render_template

def _handle_borderline_case(self, guidance: str, validation, context: RetrievedContext) -> str:
    # Format confidence to 2 decimal places before passing to template
    # (or add a custom filter for formatting)
    validation_data = {
        "confidence": f"{validation.confidence:.2f}",
        "reasoning": validation.reasoning,
    }

    prompt = render_template(
        "advisor/borderline_strengthening.jinja",
        guidance=guidance,
        validation=validation_data,  # Or pass validation directly if object
        context=context,
    )

    # Then call LLM with prompt
    response = self.llm.generate(prompt)
    return response
```

**Note:** If you want to preserve the `.2f` formatting, either pre-format the value or create a custom filter.

---

## Custom Filters Used

All templates use these custom filters registered in `template_engine.py`:

```python
# From advisor/prompts.py - registered as Jinja filters
self.env.filters['customer_profile'] = format_customer_profile
self.env.filters['conversation'] = format_conversation
self.env.filters['cases'] = format_cases
self.env.filters['rules'] = format_rules
self.env.filters['memories'] = format_memories
```

**Usage in templates:**
```jinja
{{ customer | customer_profile }}          # Instead of format_customer_profile(customer)
{{ conversation_history | conversation }}   # Instead of format_conversation(conversation_history)
{{ context.cases | cases }}                 # Instead of format_cases(context.cases)
{{ context.rules | rules }}                 # Instead of format_rules(context.rules)
{{ context.memories | memories }}           # Instead of format_memories(context.memories)
```

---

## Variable Access Examples

### Nested Attributes
```python
# Original f-string
f"{customer.demographics.financial_literacy if customer.demographics else 'medium'}"

# Jinja template
{{ customer.demographics.financial_literacy if customer.demographics else 'medium' }}
```

### List Iteration
```python
# Original f-string (Python)
issues_text = "\n".join([
    f"- {issue.description} (Suggestion: {issue.suggestion})"
    for issue in issues
])

# Jinja template
{% for issue in issues -%}
- {{ issue.description }} (Suggestion: {{ issue.suggestion }})
{% endfor %}
```

### Conditionals
```python
# Original f-string
f"{context.fca_requirements if context.fca_requirements else 'Stay within guidance boundary'}"

# Jinja template
{{ context.fca_requirements if context.fca_requirements else "Stay within guidance boundary" }}
```

---

## Migration Checklist for Each Function

When migrating a prompt function to use templates:

1. ✅ Import the template rendering function:
   ```python
   from guidance_agent.core.template_engine import render_template
   # or for JSON messages:
   from guidance_agent.core.template_engine import get_template_engine
   ```

2. ✅ Replace f-string prompt building with `render_template()` call

3. ✅ Pass all required variables as keyword arguments

4. ✅ Remove any helper function calls (like `format_customer_profile()`) - templates handle this via filters

5. ✅ For cached prompts, use `engine.render_messages()` instead of `render_template()`

6. ✅ Test that the function still returns the same output type (str or List[dict])

---

## Example Migration (Step-by-Step)

### Before (Original):
```python
def build_guidance_prompt(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> str:
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
```

### After (Using Template):
```python
from guidance_agent.core.template_engine import render_template

def build_guidance_prompt(
    advisor: AdvisorProfile,
    customer: CustomerProfile,
    context: RetrievedContext,
    conversation_history: List[dict],
) -> str:
    return render_template(
        "advisor/guidance_main.jinja",
        advisor=advisor,
        customer=customer,
        context=context,
        conversation_history=conversation_history,
    )
```

**Changes:**
- ✅ Removed multi-line f-string
- ✅ Removed calls to format functions (template handles via filters)
- ✅ Return `render_template()` call directly
- ✅ Pass all variables as keyword arguments
- ✅ Function signature unchanged (same params, same return type)

---

## Testing the Migration

After updating Python code to use templates, test that output is identical:

```python
def test_guidance_prompt_migration():
    """Test that template produces same output as original f-string."""
    # Setup test data
    advisor = AdvisorProfile(name="Test Advisor", description="Test description")
    customer = CustomerProfile(...)
    context = RetrievedContext(...)
    conversation_history = [...]

    # Call original function (if preserved for testing)
    original_output = build_guidance_prompt_original(advisor, customer, context, conversation_history)

    # Call new template-based function
    new_output = build_guidance_prompt(advisor, customer, context, conversation_history)

    # Compare (whitespace-normalized)
    assert normalize_whitespace(original_output) == normalize_whitespace(new_output)
```
