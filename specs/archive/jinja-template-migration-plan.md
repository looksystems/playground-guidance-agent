# Jinja Template Migration Plan

**Status:** ✅ **COMPLETED** - November 3, 2025

**See:** [JINJA_MIGRATION_COMPLETE.md](JINJA_MIGRATION_COMPLETE.md) for implementation summary.

**Results:**
- ✅ All 20 templates created and tested (19 planned + 1 bonus)
- ✅ All 9 Python files migrated to use templates
- ✅ 60/60 tests passing (40 unit + 20 regression)
- ✅ 100% backward compatible - identical output verified
- ✅ ~200 lines of code removed, replaced with clean template calls

---

## Executive Summary

This document outlines the complete migration of all prompt strings from Python f-strings to Jinja2 templates across the guidance-agent codebase. The migration covers 19 prompts across 9 Python files, totaling approximately 3,361 lines of prompt-related code.

**Migration Strategy:** Complete migration in one comprehensive refactor
**Helper Functions:** Kept as Python code, registered as Jinja filters
**Backward Compatibility:** None - immediate replacement of f-strings
**Testing Strategy:** Unit tests, snapshot/regression tests, and integration tests

---

## Current State Analysis

### Prompt Inventory

| Module | File | Prompts | Complexity |
|--------|------|---------|------------|
| Advisor | `advisor/prompts.py` | 4 | High (nested formatters, caching) |
| Advisor | `advisor/agent.py` | 2 | Medium (compliance refinement) |
| Compliance | `compliance/validator.py` | 1 | Medium (structured output) |
| Customer | `customer/agent.py` | 2 | Medium (simulation) |
| Customer | `customer/simulator.py` | 1 | Medium (outcome evaluation) |
| Customer | `customer/generator.py` | 4 | Medium (JSON generation) |
| Learning | `learning/reflection.py` | 4 | Low-Medium (principle extraction) |
| Memory | `core/memory.py` | 1 | Low (importance rating) |
| Evaluation | `evaluation/judge_validation.py` | 1 | Low (judge evaluation) |

**Total:** 19 prompts across 9 files

### Current Prompt Patterns

#### Pattern 1: Multi-Section Structured Prompts
Most common pattern used in advisor prompts:
```python
prompt = f"""You are {role}.

SECTION 1:
{formatted_data}

SECTION 2:
{more_data}

TASK:
Instructions here"""
```

#### Pattern 2: JSON Output Prompts
Used for customer generation, simulation, reflection:
```python
prompt = f"""Generate X.

Input: {context}

Generate JSON with:
- field1: description
- field2: description

Return only valid JSON, no explanation."""
```

#### Pattern 3: Structured Output Prompts
Used for validation and assessment:
```python
prompt = f"""Analyze X.

Data: {data}

Format:
CRITERION1: [VALUE]
CRITERION2: [VALUE]
OVERALL: [RESULT]"""
```

#### Pattern 4: Cache-Optimized Message Arrays
Special case in `build_guidance_prompt_cached()`:
```python
messages = [
    {"role": "system", "content": [...], "cache_control": {"type": "ephemeral"}},
    # Multiple message dicts
]
```

### Helper Functions (to be converted to filters)

Located in `advisor/prompts.py`:
- `format_customer_profile()` - Formats customer data
- `format_conversation()` - Formats conversation history
- `format_cases()` - Formats similar cases
- `format_rules()` - Formats guidance rules
- `format_memories()` - Formats memory nodes

### Common Variables Used in Prompts

**Customer-Related:**
- `customer.demographics.age`
- `customer.demographics.financial_literacy`
- `customer.demographics.location`
- `customer.demographics.employment_status`
- `customer.financial.annual_income`
- `customer.financial.total_assets`
- `customer.financial.risk_tolerance`
- `customer.pensions` (list)
- `customer.goals`
- `customer.presenting_question`

**Context-Related:**
- `conversation_history` (list of dicts)
- `context.cases` (list)
- `context.rules` (list)
- `context.memories` (list)
- `context.fca_requirements` (string)

**Agent-Related:**
- `advisor.name`
- `advisor.description`

**Outcome/Validation:**
- `guidance` (string)
- `reasoning` (string)
- `validation.confidence` (float)
- `outcome.customer_satisfaction` (float)
- `issues` (list)

---

## Migration Plan

### Phase 1: Infrastructure Setup

#### 1.1 Add Dependencies
Add Jinja2 to project dependencies:

**pyproject.toml:**
```toml
[project]
dependencies = [
    # ... existing dependencies ...
    "jinja2>=3.1.0",
]
```

#### 1.2 Create Template Directory Structure
```
src/guidance_agent/templates/
├── advisor/
│   ├── guidance_main.jinja
│   ├── guidance_cached.jinja
│   ├── reasoning.jinja
│   ├── guidance_with_reasoning.jinja
│   ├── compliance_refinement.jinja
│   └── borderline_strengthening.jinja
├── customer/
│   ├── comprehension.jinja
│   ├── response.jinja
│   ├── outcome.jinja
│   └── generation/
│       ├── demographics.jinja
│       ├── financial.jinja
│       ├── pension_pots.jinja
│       └── goals.jinja
├── compliance/
│   └── validation.jinja
├── learning/
│   ├── reflection.jinja
│   ├── principle_validation.jinja
│   ├── principle_refinement.jinja
│   └── rule_judgment.jinja
├── memory/
│   └── importance_rating.jinja
└── evaluation/
    └── judge.jinja
```

#### 1.3 Create Template Engine Module

**File:** `src/guidance_agent/core/template_engine.py`

```python
"""Jinja2 template engine for prompt management."""

from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape


class TemplateEngine:
    """Manages Jinja2 templates for prompts."""

    def __init__(self, template_dir: Path | None = None):
        """Initialize the template engine.

        Args:
            template_dir: Directory containing templates.
                         Defaults to src/guidance_agent/templates/
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Register custom filters
        self._register_filters()

    def _register_filters(self):
        """Register custom Jinja filters from helper functions."""
        from guidance_agent.advisor.prompts import (
            format_customer_profile,
            format_conversation,
            format_cases,
            format_rules,
            format_memories,
        )

        self.env.filters['customer_profile'] = format_customer_profile
        self.env.filters['conversation'] = format_conversation
        self.env.filters['cases'] = format_cases
        self.env.filters['rules'] = format_rules
        self.env.filters['memories'] = format_memories

    def render(self, template_name: str, **context: Any) -> str:
        """Render a template with the given context.

        Args:
            template_name: Name of template file (e.g., 'advisor/guidance_main.jinja')
            **context: Template variables

        Returns:
            Rendered template string
        """
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_messages(self, template_name: str, **context: Any) -> list[dict]:
        """Render a template that returns a message array.

        Used for cache-optimized prompts that return message structures.

        Args:
            template_name: Name of template file
            **context: Template variables

        Returns:
            List of message dicts
        """
        import json
        template = self.env.get_template(template_name)
        rendered = template.render(**context)
        return json.loads(rendered)


# Global template engine instance
_engine = None

def get_template_engine() -> TemplateEngine:
    """Get the global template engine instance."""
    global _engine
    if _engine is None:
        _engine = TemplateEngine()
    return _engine


def render_template(template_name: str, **context: Any) -> str:
    """Convenience function to render a template.

    Args:
        template_name: Name of template file
        **context: Template variables

    Returns:
        Rendered template string
    """
    return get_template_engine().render(template_name, **context)
```

---

### Phase 2: Convert All Prompts to Templates

#### 2.1 Advisor Templates (6 prompts)

##### advisor/guidance_main.jinja
Converts: `build_guidance_prompt()` in `advisor/prompts.py:155-216`

```jinja
You are {{ advisor.name }}, {{ advisor.description }}

Your role is to provide GUIDANCE, not advice. You must:
1. Help the customer understand their options
2. Explain relevant concepts clearly
3. Ask questions to better understand their situation
4. NEVER recommend specific actions or products

=== FCA COMPLIANCE REQUIREMENTS ===
{{ fca_requirements }}

=== CUSTOMER PROFILE ===
{{ customer | customer_profile }}

{% if conversation_history %}
=== CONVERSATION HISTORY ===
{{ conversation_history | conversation }}
{% endif %}

{% if context.cases %}
=== SIMILAR CASES ===
{{ context.cases | cases }}
{% endif %}

{% if context.rules %}
=== GUIDANCE RULES ===
{{ context.rules | rules }}
{% endif %}

{% if context.memories %}
=== RELEVANT MEMORIES ===
{{ context.memories | memories }}
{% endif %}

=== PRESENTING QUESTION ===
{{ presenting_question }}

=== YOUR TASK ===
Provide guidance that:
- Addresses the customer's question
- Is appropriate for their financial literacy level ({{ financial_literacy }})
- Complies with FCA regulations
- Helps them understand their options without recommending specific actions
```

##### advisor/guidance_cached.jinja
Converts: `build_guidance_prompt_cached()` in `advisor/prompts.py:219-316`

Returns JSON array of message objects with cache control:

```jinja
[
  {
    "role": "system",
    "content": [
      {
        "type": "text",
        "text": "You are {{ advisor.name }}, {{ advisor.description }}\n\nYour role is to provide GUIDANCE, not advice...",
        "cache_control": {"type": "ephemeral"}
      }
    ]
  },
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "=== CUSTOMER PROFILE ===\n{{ customer | customer_profile }}",
        "cache_control": {"type": "ephemeral"}
      }
    ]
  },
  {% if conversation_history %}
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "=== CONVERSATION HISTORY ===\n{{ conversation_history | conversation }}"
      }
    ]
  },
  {% endif %}
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "=== PRESENTING QUESTION ===\n{{ presenting_question }}\n\nProvide guidance..."
      }
    ]
  }
]
```

##### advisor/reasoning.jinja
Converts: `build_reasoning_prompt()` in `advisor/prompts.py:319-361`

##### advisor/guidance_with_reasoning.jinja
Converts: `build_guidance_prompt_with_reasoning()` in `advisor/prompts.py:364-403`

##### advisor/compliance_refinement.jinja
Converts: compliance refinement prompt in `advisor/agent.py:469-490`

```jinja
The following guidance failed FCA compliance validation:

{{ guidance }}

Compliance issues:
{{ issues_text }}

Customer context:
- Age: {{ customer.demographics.age }}
- Financial literacy: {{ customer.demographics.financial_literacy }}
- Question: {{ customer.presenting_question }}

Please revise the guidance to address these compliance issues while maintaining clarity and relevance to the customer's question.
```

##### advisor/borderline_strengthening.jinja
Converts: borderline case prompt in `advisor/agent.py:520-540`

#### 2.2 Customer Templates (7 prompts)

##### customer/comprehension.jinja
Converts: `simulate_comprehension()` in `customer/agent.py:79-101`

##### customer/response.jinja
Converts: `respond()` in `customer/agent.py:146-179`

##### customer/outcome.jinja
Converts: `simulate_outcome()` in `customer/simulator.py:43-86`

##### customer/generation/demographics.jinja
Converts: `generate_demographics()` in `customer/generator.py:52-70`

##### customer/generation/financial.jinja
Converts: `generate_financial_situation()` in `customer/generator.py:115-138`

##### customer/generation/pension_pots.jinja
Converts: pension generation in `customer/generator.py:208-231`

##### customer/generation/goals.jinja
Converts: `generate_goals_and_inquiry()` in `customer/generator.py:289-313`

#### 2.3 Compliance Templates (1 prompt)

##### compliance/validation.jinja
Converts: `_build_validation_prompt()` in `compliance/validator.py:215-273`

#### 2.4 Learning Templates (4 prompts)

##### learning/reflection.jinja
Converts: `reflect_on_failure()` in `learning/reflection.py:46-67`

##### learning/principle_validation.jinja
Converts: `validate_principle()` in `learning/reflection.py:108-126`

##### learning/principle_refinement.jinja
Converts: `refine_principle()` in `learning/reflection.py:166-176`

##### learning/rule_judgment.jinja
Converts: `judge_rule_value()` in `learning/reflection.py:210-228`

#### 2.5 Memory Templates (1 prompt)

##### memory/importance_rating.jinja
Converts: `rate_importance()` in `core/memory.py:390-397`

```jinja
On a scale of 1-10, rate the importance of the following observation for an FCA-compliant pension guidance system:

{{ observation }}

Return only a number between 1 and 10.
```

#### 2.6 Evaluation Templates (1 prompt)

##### evaluation/judge.jinja
Converts: judge prompt in `evaluation/judge_validation.py:75-86`

---

### Phase 3: Update Python Code

#### 3.1 Update advisor/prompts.py

**Before:**
```python
def build_guidance_prompt(
    advisor,
    customer,
    conversation_history,
    context,
    fca_requirements,
    presenting_question,
    financial_literacy,
):
    prompt = f"""You are {advisor.name}, {advisor.description}

    Your role is to provide GUIDANCE...
    """
    return prompt
```

**After:**
```python
from guidance_agent.core.template_engine import render_template

def build_guidance_prompt(
    advisor,
    customer,
    conversation_history,
    context,
    fca_requirements,
    presenting_question,
    financial_literacy,
):
    return render_template(
        "advisor/guidance_main.jinja",
        advisor=advisor,
        customer=customer,
        conversation_history=conversation_history,
        context=context,
        fca_requirements=fca_requirements,
        presenting_question=presenting_question,
        financial_literacy=financial_literacy,
    )
```

#### 3.2 Update advisor/agent.py (2 prompts)
Replace inline f-string prompts with `render_template()` calls in:
- `_refine_for_compliance()` method (line 469)
- `_handle_borderline_case()` method (line 520)

#### 3.3 Update compliance/validator.py (1 prompt)
Replace `_build_validation_prompt()` method

#### 3.4 Update customer/agent.py (2 prompts)
Replace prompts in:
- `simulate_comprehension()` method
- `respond()` method

#### 3.5 Update customer/simulator.py (1 prompt)
Replace `simulate_outcome()` function prompt

#### 3.6 Update customer/generator.py (4 prompts)
Replace prompts in:
- `generate_demographics()`
- `generate_financial_situation()`
- `generate_pension_pots()` (loop)
- `generate_goals_and_inquiry()`

#### 3.7 Update learning/reflection.py (4 prompts)
Replace prompts in:
- `reflect_on_failure()`
- `validate_principle()`
- `refine_principle()`
- `judge_rule_value()`

#### 3.8 Update core/memory.py (1 prompt)
Replace `rate_importance()` function prompt

#### 3.9 Update evaluation/judge_validation.py (1 prompt)
Replace prompt in `LLMJudge.evaluate()` method

---

### Phase 4: Testing Strategy

#### 4.1 Unit Tests for Template Rendering

**File:** `tests/templates/test_template_rendering.py`

```python
"""Unit tests for Jinja template rendering."""

import pytest
from guidance_agent.core.template_engine import get_template_engine


class TestAdvisorTemplates:
    """Test advisor templates render correctly."""

    def test_guidance_main_template(self):
        """Test main guidance template renders with all variables."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor={"name": "Test Advisor", "description": "Test description"},
            customer={"demographics": {"age": 55}},
            conversation_history=[],
            context={"cases": [], "rules": [], "memories": []},
            fca_requirements="Test requirements",
            presenting_question="Test question",
            financial_literacy="medium",
        )

        assert "Test Advisor" in result
        assert "Test question" in result
        assert "FCA COMPLIANCE" in result

    def test_guidance_main_with_conversation(self):
        """Test template handles conversation history."""
        engine = get_template_engine()

        result = engine.render(
            "advisor/guidance_main.jinja",
            advisor={"name": "Test", "description": "Test"},
            customer={},
            conversation_history=[
                {"role": "customer", "message": "Hello"}
            ],
            context={"cases": [], "rules": [], "memories": []},
            fca_requirements="Test",
            presenting_question="Test",
            financial_literacy="medium",
        )

        assert "CONVERSATION HISTORY" in result
        assert "Hello" in result


class TestCustomerTemplates:
    """Test customer templates."""

    def test_demographics_template(self):
        """Test demographics generation template."""
        # Similar structure
        pass


class TestComplianceTemplates:
    """Test compliance templates."""

    def test_validation_template(self):
        """Test validation prompt template."""
        pass


# Add tests for all 19 templates
```

#### 4.2 Snapshot/Regression Tests

**File:** `tests/regression/test_template_migration.py`

```python
"""Regression tests to ensure template output matches f-string output."""

import pytest
from guidance_agent.core.template_engine import render_template

# Import original f-string functions (saved for comparison)
# from tests.regression.original_prompts import build_guidance_prompt_original


class TestGuidancePromptRegression:
    """Ensure new templates produce identical output to original f-strings."""

    def test_guidance_prompt_matches_original(self):
        """Test guidance_main.jinja matches original f-string."""
        # Sample data
        advisor = type('obj', (object,), {
            'name': 'Sarah Thompson',
            'description': 'FCA-compliant pension guidance specialist'
        })()

        customer = {
            "demographics": {
                "age": 55,
                "financial_literacy": "medium",
            }
        }

        # Original f-string output
        # original = build_guidance_prompt_original(...)

        # New template output
        new = render_template(
            "advisor/guidance_main.jinja",
            advisor=advisor,
            customer=customer,
            conversation_history=[],
            context={"cases": [], "rules": [], "memories": []},
            fca_requirements="Test requirements",
            presenting_question="Should I take my pension at 55?",
            financial_literacy="medium",
        )

        # Compare (whitespace-normalized)
        # assert normalize_whitespace(original) == normalize_whitespace(new)

    # Add regression tests for all 19 prompts


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace for comparison."""
    import re
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    # Remove empty lines
    lines = [line for line in lines if line]
    # Join with single newline
    return '\n'.join(lines)
```

**Setup:** Before migration, save original f-string outputs to `tests/regression/original_prompts.py` for comparison.

#### 4.3 Integration Tests

**Update existing tests in:**
- `tests/api/test_admin_cases.py`
- `tests/api/test_admin_customers.py`
- `tests/api/test_admin_fca_knowledge.py`
- `tests/api/test_admin_memories.py`
- `tests/api/test_admin_pension_knowledge.py`
- `tests/api/test_admin_rules.py`

**Changes needed:**
- Ensure template engine is initialized in test setup
- Verify full API flows work with new templates
- Check that LLM outputs are still valid with new prompts

#### 4.4 Test Data Fixtures

**File:** `tests/fixtures/template_data.py`

```python
"""Test data fixtures for template testing."""

import pytest


@pytest.fixture
def sample_advisor():
    """Sample advisor for testing."""
    return type('Advisor', (object,), {
        'name': 'Sarah Thompson',
        'description': 'FCA-compliant pension guidance specialist'
    })()


@pytest.fixture
def sample_customer():
    """Sample customer for testing."""
    return {
        "demographics": {
            "age": 55,
            "financial_literacy": "medium",
            "location": "London",
            "employment_status": "employed",
        },
        "financial": {
            "annual_income": 45000,
            "total_assets": 250000,
            "risk_tolerance": "medium",
        },
        "pensions": [
            {
                "pot_id": "pot_001",
                "provider": "Aviva",
                "current_value": 150000,
            }
        ],
        "presenting_question": "Should I take my pension at 55?",
    }


@pytest.fixture
def sample_context():
    """Sample context for testing."""
    return {
        "cases": [],
        "rules": [],
        "memories": [],
    }


# Add more fixtures for all common test data
```

---

### Phase 5: Migration Checklist

#### Pre-Migration
- [ ] Add Jinja2 to dependencies
- [ ] Create template directory structure
- [ ] Implement `template_engine.py`
- [ ] Save original f-string outputs for regression testing
- [ ] Create test fixtures

#### Migration (Do in order)
- [ ] Create all 19 .jinja template files
- [ ] Update `advisor/prompts.py` (4 prompts)
- [ ] Update `advisor/agent.py` (2 prompts)
- [ ] Update `compliance/validator.py` (1 prompt)
- [ ] Update `customer/agent.py` (2 prompts)
- [ ] Update `customer/simulator.py` (1 prompt)
- [ ] Update `customer/generator.py` (4 prompts)
- [ ] Update `learning/reflection.py` (4 prompts)
- [ ] Update `core/memory.py` (1 prompt)
- [ ] Update `evaluation/judge_validation.py` (1 prompt)

#### Testing
- [ ] Write unit tests for all 19 templates
- [ ] Write regression tests comparing old vs new output
- [ ] Update integration tests
- [ ] Run full test suite
- [ ] Manual testing of key flows

#### Post-Migration
- [ ] Update documentation
- [ ] Update README with template usage instructions
- [ ] Remove commented-out f-string code
- [ ] Code review
- [ ] Deploy to staging
- [ ] Monitor for issues

---

## Benefits of Migration

### 1. Separation of Concerns
- Prompts live in dedicated template files
- Code focuses on logic, not string formatting
- Easier to review and version control prompts separately

### 2. Maintainability
- Centralized prompt management in `/templates` directory
- No more searching through Python files for prompt text
- Consistent formatting and structure

### 3. Testing
- Templates can be tested independently of business logic
- Regression tests ensure no unintended changes
- Easier to A/B test different prompt variations

### 4. Collaboration
- Domain experts can edit prompts without touching Python code
- Version control shows clear prompt changes
- Easier to track prompt evolution over time

### 5. Reusability
- Common patterns can be extracted to macros
- Filters (helper functions) can be used across templates
- DRY principle applied to prompt engineering

### 6. Flexibility
- Easy to swap templates for different use cases
- Support multiple template versions (A/B testing)
- Template inheritance for shared structures

---

## Risks and Mitigation

### Risk 1: Output Regressions
**Impact:** Templates produce different output than f-strings, breaking LLM behavior

**Mitigation:**
- Comprehensive regression tests comparing old vs new output
- Whitespace normalization in tests
- Manual review of critical prompts before deployment

### Risk 2: Cache Invalidation
**Impact:** Changing prompts invalidates existing cache entries, increasing costs

**Mitigation:**
- Plan migration during low-traffic period
- Monitor cache hit rates post-migration
- Consider phased rollout if cache warming is needed

### Risk 3: Template Rendering Errors
**Impact:** Runtime errors if templates fail to render with actual data

**Mitigation:**
- Unit tests with various data shapes
- Defensive template code (default values, safe navigation)
- Good error messages in template engine

### Risk 4: Performance Overhead
**Impact:** Template rendering adds latency vs f-strings

**Mitigation:**
- Benchmark template rendering performance
- Cache compiled templates (Jinja does this automatically)
- Profile critical paths before/after migration

### Risk 5: Debugging Complexity
**Impact:** Stack traces less clear when errors occur in templates

**Mitigation:**
- Enable Jinja line numbers in errors
- Good logging in template engine
- Template lint/validation in CI

### Risk 6: Team Learning Curve
**Impact:** Team needs to learn Jinja2 syntax

**Mitigation:**
- Documentation with examples
- Template style guide
- Code review for initial template changes

---

## Timeline Estimate

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| **Phase 1: Infrastructure** | Dependencies, directory structure, template_engine.py | 2-3 hours |
| **Phase 2: Template Creation** | Create all 19 .jinja files | 6-8 hours |
| **Phase 3: Python Updates** | Update 9 Python files | 4-5 hours |
| **Phase 4: Testing** | Unit, regression, integration tests | 6-8 hours |
| **Phase 5: Review & QA** | Code review, manual testing, fixes | 4-6 hours |
| **Total** | | **22-30 hours** |

**Recommended approach:** Allocate 3-4 full working days for complete migration with thorough testing.

---

## Success Criteria

Migration is considered successful when:

1. ✅ All 19 templates created and rendering correctly
2. ✅ All Python files updated to use templates
3. ✅ Unit tests pass (100% template coverage)
4. ✅ Regression tests pass (output matches original)
5. ✅ Integration tests pass (full API flows work)
6. ✅ No console errors or warnings in logs
7. ✅ Manual smoke testing confirms LLM outputs are valid
8. ✅ Code review approved
9. ✅ Documentation updated

---

## Post-Migration Best Practices

### Template Naming Convention
- Use descriptive names: `advisor/guidance_main.jinja` not `advisor/prompt1.jinja`
- Group by module: `customer/generation/demographics.jinja`
- Use `.jinja` extension consistently

### Template Documentation
Add comments to complex templates:
```jinja
{#
  Guidance generation prompt for advisor agent

  Required variables:
  - advisor: Advisor object with name, description
  - customer: Customer dict with demographics, financial, pensions
  - fca_requirements: String of FCA compliance requirements

  Optional variables:
  - conversation_history: List of conversation turns (default: [])
  - context.cases: List of similar cases (default: [])
#}
```

### Version Control
- Commit template changes separately from code changes when possible
- Include rationale in commit messages for prompt changes
- Tag major prompt revisions for rollback capability

### A/B Testing
Structure for testing multiple template versions:
```
templates/
  advisor/
    guidance_main.jinja          # Current version
    guidance_main_v2.jinja        # A/B test variant
```

### Template Validation
Consider adding pre-commit hooks to:
- Validate Jinja syntax
- Check for required variables
- Lint whitespace/formatting

---

## Appendix A: Complete File Mapping

| Original Location | New Template | Python Function |
|-------------------|--------------|-----------------|
| `advisor/prompts.py:155-216` | `advisor/guidance_main.jinja` | `build_guidance_prompt()` |
| `advisor/prompts.py:219-316` | `advisor/guidance_cached.jinja` | `build_guidance_prompt_cached()` |
| `advisor/prompts.py:319-361` | `advisor/reasoning.jinja` | `build_reasoning_prompt()` |
| `advisor/prompts.py:364-403` | `advisor/guidance_with_reasoning.jinja` | `build_guidance_prompt_with_reasoning()` |
| `advisor/agent.py:469-490` | `advisor/compliance_refinement.jinja` | `_refine_for_compliance()` |
| `advisor/agent.py:520-540` | `advisor/borderline_strengthening.jinja` | `_handle_borderline_case()` |
| `compliance/validator.py:215-273` | `compliance/validation.jinja` | `_build_validation_prompt()` |
| `customer/agent.py:79-101` | `customer/comprehension.jinja` | `simulate_comprehension()` |
| `customer/agent.py:146-179` | `customer/response.jinja` | `respond()` |
| `customer/simulator.py:43-86` | `customer/outcome.jinja` | `simulate_outcome()` |
| `customer/generator.py:52-70` | `customer/generation/demographics.jinja` | `generate_demographics()` |
| `customer/generator.py:115-138` | `customer/generation/financial.jinja` | `generate_financial_situation()` |
| `customer/generator.py:208-231` | `customer/generation/pension_pots.jinja` | Loop in `generate_pension_pots()` |
| `customer/generator.py:289-313` | `customer/generation/goals.jinja` | `generate_goals_and_inquiry()` |
| `learning/reflection.py:46-67` | `learning/reflection.jinja` | `reflect_on_failure()` |
| `learning/reflection.py:108-126` | `learning/principle_validation.jinja` | `validate_principle()` |
| `learning/reflection.py:166-176` | `learning/principle_refinement.jinja` | `refine_principle()` |
| `learning/reflection.py:210-228` | `learning/rule_judgment.jinja` | `judge_rule_value()` |
| `core/memory.py:390-397` | `memory/importance_rating.jinja` | `rate_importance()` |
| `evaluation/judge_validation.py:75-86` | `evaluation/judge.jinja` | `LLMJudge.evaluate()` |

---

## Appendix B: Example Template Conversions

### Example 1: Simple Prompt

**Before (Python f-string):**
```python
def rate_importance(observation: str) -> float:
    prompt = f"""On a scale of 1-10, rate the importance of the following observation:

{observation}

Return only a number between 1 and 10."""

    response = llm.generate(prompt)
    return float(response) / 10
```

**After (Jinja template):**

**Template file:** `memory/importance_rating.jinja`
```jinja
On a scale of 1-10, rate the importance of the following observation for an FCA-compliant pension guidance system:

{{ observation }}

Return only a number between 1 and 10.
```

**Python code:**
```python
from guidance_agent.core.template_engine import render_template

def rate_importance(observation: str) -> float:
    prompt = render_template(
        "memory/importance_rating.jinja",
        observation=observation,
    )

    response = llm.generate(prompt)
    return float(response) / 10
```

### Example 2: Conditional Sections

**Before (Python f-string):**
```python
def build_prompt(customer, context):
    prompt = f"""Customer: {customer.name}

Question: {customer.question}
"""

    if context.cases:
        prompt += f"""
Similar cases:
{format_cases(context.cases)}
"""

    if context.rules:
        prompt += f"""
Guidance rules:
{format_rules(context.rules)}
"""

    return prompt
```

**After (Jinja template):**
```jinja
Customer: {{ customer.name }}

Question: {{ customer.question }}

{% if context.cases %}
Similar cases:
{{ context.cases | cases }}
{% endif %}

{% if context.rules %}
Guidance rules:
{{ context.rules | rules }}
{% endif %}
```

### Example 3: Loops

**Before (Python f-string):**
```python
def format_pensions(pensions):
    text = "Pension pots:\n"
    for i, pension in enumerate(pensions, 1):
        text += f"{i}. {pension.provider}: £{pension.value:,.2f}\n"
    return text
```

**After (Jinja template):**
```jinja
Pension pots:
{% for pension in pensions %}
{{ loop.index }}. {{ pension.provider }}: £{{ pension.value | format_currency }}
{% endfor %}
```

With custom filter:
```python
# In template_engine.py
def format_currency(value):
    return f"{value:,.2f}"

self.env.filters['format_currency'] = format_currency
```

---

## Appendix C: Jinja2 Quick Reference

### Variables
```jinja
{{ variable }}
{{ object.attribute }}
{{ dict['key'] }}
{{ list[0] }}
```

### Conditionals
```jinja
{% if condition %}
  content
{% elif other_condition %}
  other content
{% else %}
  default content
{% endif %}
```

### Loops
```jinja
{% for item in items %}
  {{ loop.index }}: {{ item }}
{% endfor %}

{# loop.index, loop.index0, loop.first, loop.last #}
```

### Filters
```jinja
{{ variable | filter }}
{{ variable | filter(arg1, arg2) }}
{{ text | upper }}
{{ list | join(', ') }}
{{ value | default('default value') }}
```

### Comments
```jinja
{# This is a comment #}
```

### Whitespace Control
```jinja
{% if True -%}    {# Remove whitespace after #}
  content
{%- endif %}      {# Remove whitespace before #}
```

---

## Questions for Stakeholders

Before beginning migration, confirm:

1. ✅ **Approach confirmed:** Complete migration in one refactor
2. ✅ **Helper functions:** Keep as Python, register as Jinja filters
3. ✅ **Backward compatibility:** None - immediate replacement
4. ✅ **Testing:** Unit + regression + integration tests
5. ❓ **Timeline:** Is 3-4 days acceptable for this migration?
6. ❓ **Deployment:** Can we deploy during low-traffic period?
7. ❓ **Review:** Who should review template changes?
8. ❓ **Rollback:** What's the rollback plan if issues arise?

---

## Document Status

- **Version:** 1.0
- **Date:** 2025-11-03
- **Status:** Draft - Awaiting approval
- **Author:** Claude Code
- **Reviewers:** TBD

---

## Next Steps

1. Review and approve this specification
2. Set migration timeline and assign resources
3. Create feature branch for migration work
4. Execute Phase 1 (Infrastructure Setup)
5. Begin template creation and testing
