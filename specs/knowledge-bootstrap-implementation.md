# Knowledge Bootstrap Implementation Plan

**Version:** 2.0
**Date:** November 2025
**Status:** Ready for Implementation
**Estimated Effort:** 11-13 hours (1.5-2 days)

---

## Executive Summary

This plan implements comprehensive knowledge bootstrapping for the pension guidance platform, transforming from 0 entries to 330-480 high-quality knowledge base entries. The implementation focuses on three key areas:

1. **Dynamic Schema Architecture**: Make embedding dimensions configurable via environment variables
2. **FCA Compliance**: Extract comprehensive principles from the 2,127-line FCA Compliance Manual
3. **Pension Knowledge**: Massively expand from 190 lines to ~1,200 lines covering 15 major UK pension topics

---

## Goals

1. Make database schema dynamically read `EMBEDDING_DIMENSION` from env var (future-proof for different deployments)
2. Fix existing schema from 1536 → 768 dimensions to match current local embedding model (nomic-embed-text)
3. Extract comprehensive FCA principles from `specs/fca-compliance-manual.md` (all major sections)
4. Massively expand pension knowledge from 190 → ~1,200 lines covering all 15 major topic areas
5. Bootstrap all data to populate knowledge base with 330-480 entries

---

## Current State

### Database Schema
- ✅ Tables exist: `fca_knowledge`, `pension_knowledge`, `cases`, `rules`
- ❌ Hardcoded to `vector(1536)` (mismatch with local 768d embeddings)
- ✅ 0 entries (safe to alter schema)
- ✅ HNSW indexes configured

### Configuration
- ✅ `.env` correctly set: `EMBEDDING_DIMENSION=768`
- ✅ Local embedding model: `openai/nomic-embed-text` (768 dimensions)
- ✅ Bootstrap scripts ready

### Source Materials
- ✅ Comprehensive FCA Compliance Manual (2,127 lines, 10 sections + appendices)
- ✅ Basic pension knowledge module (190 lines, 4 sections)
- ✅ Bootstrap scripts tested and working

---

## Implementation Plan

### **Step 1: Make Database Schema Dynamic** (20 min)

#### 1A. Update Database Models

**File**: `src/guidance_agent/core/database.py`

Add at module level (before model definitions):
```python
import os

# Read embedding dimension from environment variable
# This allows different deployments to use different embedding models
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIMENSION", "1536"))
```

Update all model definitions with embeddings:
```python
class FCAKnowledge(Base):
    # ... existing fields ...
    embedding: Mapped[Optional[list]] = mapped_column(VECTOR(EMBEDDING_DIM))

class PensionKnowledge(Base):
    # ... existing fields ...
    embedding: Mapped[Optional[list]] = mapped_column(VECTOR(EMBEDDING_DIM))

class Memory(Base):
    # ... existing fields ...
    embedding: Mapped[Optional[list]] = mapped_column(VECTOR(EMBEDDING_DIM))

class Case(Base):
    # ... existing fields ...
    embedding: Mapped[Optional[list]] = mapped_column(VECTOR(EMBEDDING_DIM))

class Rule(Base):
    # ... existing fields ...
    embedding: Mapped[Optional[list]] = mapped_column(VECTOR(EMBEDDING_DIM))
```

#### 1B. Create Migration to Update Schema

**Create migration:**
```bash
alembic revision -m "update_embedding_dimension_to_768"
```

**Edit generated file**: `alembic/versions/[timestamp]_update_embedding_dimension_to_768.py`

```python
"""update_embedding_dimension_to_768

Revision ID: [auto-generated]
Revises: d54d8651560e
Create Date: [auto-generated]
"""
import os
from alembic import op

revision = '[auto-generated]'
down_revision = 'd54d8651560e'

def upgrade() -> None:
    """Update embedding columns to use dimension from EMBEDDING_DIMENSION env var."""
    # Read target dimension from environment (will be 768 for local model)
    target_dim = int(os.getenv("EMBEDDING_DIMENSION", "768"))

    print(f"Updating embedding dimensions to {target_dim}...")

    # Drop HNSW indexes (required before column type change)
    op.execute('DROP INDEX IF EXISTS fca_knowledge_embedding_idx')
    op.execute('DROP INDEX IF EXISTS pension_knowledge_embedding_idx')
    op.execute('DROP INDEX IF EXISTS memory_embedding_idx')
    op.execute('DROP INDEX IF EXISTS case_embedding_idx')
    op.execute('DROP INDEX IF EXISTS rule_embedding_idx')

    # Alter column types to new dimension
    op.execute(f'ALTER TABLE fca_knowledge ALTER COLUMN embedding TYPE vector({target_dim})')
    op.execute(f'ALTER TABLE pension_knowledge ALTER COLUMN embedding TYPE vector({target_dim})')
    op.execute(f'ALTER TABLE memories ALTER COLUMN embedding TYPE vector({target_dim})')
    op.execute(f'ALTER TABLE cases ALTER COLUMN embedding TYPE vector({target_dim})')
    op.execute(f'ALTER TABLE rules ALTER COLUMN embedding TYPE vector({target_dim})')

    # Recreate HNSW indexes with new dimension
    op.execute('CREATE INDEX fca_knowledge_embedding_idx ON fca_knowledge USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX pension_knowledge_embedding_idx ON pension_knowledge USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX memory_embedding_idx ON memories USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX case_embedding_idx ON cases USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX rule_embedding_idx ON rules USING hnsw (embedding vector_cosine_ops)')

    print(f"✅ Successfully updated to {target_dim}-dimensional vectors")

def downgrade() -> None:
    """Revert to 1536 dimensions."""
    print("Reverting to 1536 dimensions...")

    # Drop indexes
    op.execute('DROP INDEX IF EXISTS fca_knowledge_embedding_idx')
    op.execute('DROP INDEX IF EXISTS pension_knowledge_embedding_idx')
    op.execute('DROP INDEX IF EXISTS memory_embedding_idx')
    op.execute('DROP INDEX IF EXISTS case_embedding_idx')
    op.execute('DROP INDEX IF EXISTS rule_embedding_idx')

    # Revert to 1536
    op.execute('ALTER TABLE fca_knowledge ALTER COLUMN embedding TYPE vector(1536)')
    op.execute('ALTER TABLE pension_knowledge ALTER COLUMN embedding TYPE vector(1536)')
    op.execute('ALTER TABLE memories ALTER COLUMN embedding TYPE vector(1536)')
    op.execute('ALTER TABLE cases ALTER COLUMN embedding TYPE vector(1536)')
    op.execute('ALTER TABLE rules ALTER COLUMN embedding TYPE vector(1536)')

    # Recreate indexes
    op.execute('CREATE INDEX fca_knowledge_embedding_idx ON fca_knowledge USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX pension_knowledge_embedding_idx ON pension_knowledge USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX memory_embedding_idx ON memories USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX case_embedding_idx ON cases USING hnsw (embedding vector_cosine_ops)')
    op.execute('CREATE INDEX rule_embedding_idx ON rules USING hnsw (embedding vector_cosine_ops)')

    print("✅ Reverted to 1536 dimensions")
```

**Run migration:**
```bash
alembic upgrade head
```

**Verify:**
```bash
psql $DATABASE_URL -c "\d fca_knowledge" | grep embedding
# Should show: embedding | vector(768)
```

---

### **Step 2: Extract Comprehensive FCA Principles** (4-5 hours)

**File**: `data/knowledge/fca_compliance_principles.yaml`

**Strategy**: Extract ALL major content from the 2,127-line FCA Compliance Manual, ensuring comprehensive coverage of all sections.

#### Coverage Map

Extract content from all manual sections:

**Section 1: Foundational Principles**
- What staff CANNOT do (all 7 prohibited activities)
- What staff CAN do (all 7 permitted activities)
- Critical distinction: Information vs Advice
- Core legal framework (FSMA, RAO, COBS, PERG)
- FCA Principles 2, 6, 7, 9

**Section 2: Three-Tier Framework**
- Tier 1: Pure Information (definition, characteristics, all examples)
- Tier 2: Generic Advice (when acceptable, when regulated, examples)
- Tier 3: Personal Recommendations (four-part test, all examples)

**Section 3: Absolute Red Lines**
- Category A: Direct Recommendations (all phrases + examples)
- Category B: Suitability Language (all phrases + examples)
- Category C: Comparative Value Judgments (all phrases + examples)
- Category D: Personal Circumstance References (all phrases + examples)
- Category E: Implicit Steering (all approaches + examples)
- Category F: Persuasive Language (all phrases + examples)
- Prohibited Actions (all 4 types)

**Section 4: Evaluation Process**
- Five-step evaluation method (complete)
- Four-part personal recommendation test (detailed criteria)
- Decision tree flowchart logic
- Tone and context evaluation

**Section 5: Language Analysis Framework**
- High risk words (complete table)
- Medium risk words (context-dependent analysis)
- Tone indicators (subtle warning signs)
- Phrase patterns (all 4 patterns with examples)
- Implicit recommendation indicators

**Section 6: Scenario-Based Decision Making**
- All 8 scenario types with complete examples:
  - Type 1: Product information requests
  - Type 2: "What should I choose?" requests
  - Type 3: Existing product concerns
  - Type 4: Comparison requests
  - Type 5: Risk tolerance questions
  - Type 6: Time horizon queries
  - Type 7: Product feature explanation
  - Type 8: Fee/charge queries

**Section 7: Practical Examples Library**
- Example Sets A-F (all with compliant/non-compliant versions)
- Example Set G: Common violations with corrections

**Section 8: Edge Cases and Grey Areas**
- Edge Case 1: Following up on customer's decision
- Edge Case 2: Customer misunderstanding corrections
- Edge Case 3: Responding to external advice
- Edge Case 4: Urgent time-sensitive situations
- Edge Case 5: Vulnerable customer protocols
- Disclaimers and limitations
- Group vs individual communications
- Digital interface considerations

**Section 9: QA Checklist and Scoring**
- Rapid compliance assessment (Sections A-D)
- Overall compliance scoring matrix
- Detailed QA evaluation form

**Section 10: Escalation Procedures**
- When to escalate (immediate vs standard)
- Escalation process flow
- Documentation requirements
- Customer remediation protocol
- Staff management protocols

**Appendices: Quick Reference Materials**
- Card 1: Five-second check
- Card 2: Safe response templates
- Card 3: Prohibited vs permitted
- Card 4: Red flag checklist

#### YAML Structure Example

```yaml
# ============================================================================
# FOUNDATIONAL PRINCIPLES (Section 1)
# ============================================================================
foundational_principles:
  - principle: "Prohibited Activity: Provide personal recommendations on investments"
    content: "Customer support staff cannot provide personal recommendations on investments. This is a regulated activity requiring FCA authorization."
    fca_reference: "FSMA 2000, RAO Article 53(1)"
    manual_section: "1.2"
    mandatory: true
    severity: "critical"

  - principle: "Critical Distinction: Information vs Advice"
    content: "Information = factual statements without judgment. Advice = opinion, judgment, or recommendation."
    fca_reference: "PERG 8.28-8.29"
    manual_section: "1.4"
    mandatory: true
    examples_information:
      - "This product has a 5-year term"
      - "The fee structure is X% per annum"
      - "There are three options available: A, B, and C"
    examples_advice:
      - "This product would be good for you"
      - "You should choose option B"
      - "Most people in your situation pick this one"

# ============================================================================
# THREE-TIER FRAMEWORK (Section 2)
# ============================================================================
three_tier_framework:
  - principle: "Four-Part Test for Personal Recommendation"
    content: "All four must be met: (1) to someone as investor, (2) about particular investment, (3) suitable OR based on circumstances, (4) NOT exclusively to public"
    fca_reference: "RAO Article 53(1), PERG 8.28"
    manual_section: "2.3, 4.1"
    mandatory: true
    severity: "critical"
    test_criteria:
      test_1: "Is this to someone in their capacity as an investor?"
      test_2: "Is this about a particular investment product?"
      test_3: "Is it presented as suitable OR based on customer's circumstances?"
      test_4: "Is it NOT exclusively to the public?"
    interpretation: "If ALL four = YES → Personal Recommendation = BREACH"

# ============================================================================
# PROHIBITED LANGUAGE CATEGORIES (Section 3)
# ============================================================================
prohibited_language_category_a:
  - principle: "Category A: Direct Recommendation Verbs - Never Use"
    content: "Never use recommend, suggest, advise, should, need to, must, think you should"
    fca_reference: "PERG 8.29"
    manual_section: "3.1 Category A"
    mandatory: true
    severity: "critical"
    prohibited_phrases:
      - "I recommend..."
      - "I suggest..."
      - "I advise..."
      - "You should..."
      - "You need to..."
      - "You must..."
      - "I think you should..."
      - "My recommendation would be..."
      - "I'd advise you to..."
    examples_non_compliant:
      - "I recommend the Growth ISA for your needs"
      - "You should move your pension to our platform"
      - "I suggest you invest in Fund X"
    compliant_alternatives:
      - "Fund X is available"
      - "Options include..."
      - "I can explain the features"
      - "An adviser can recommend..."

# ============================================================================
# SCENARIO-BASED RESPONSES (Sections 6 & 7)
# ============================================================================
scenario_what_should_i_choose:
  - principle: "Scenario: What Should I Choose?"
    content: "Never answer with product suggestion. Clear disclaimer, explain adviser value, appropriate signposting."
    fca_reference: "PERG 8.28-8.31"
    manual_section: "6.1 Scenario Type 2, 7.1 Example B1"
    customer_query: "I'm 45 and want to save for retirement. What should I invest in?"
    non_compliant_response: "At your age, I'd suggest a balanced fund. It gives you growth potential while managing risk as you're 20 years from retirement. Fund X is our best balanced option."
    non_compliant_problems:
      - "Directive advice (I'd suggest)"
      - "Personalized to age"
      - "Recommended specific fund"
      - "Value judgment (best)"
    compliant_response: |
      I can't provide investment recommendations, but I can explain what products we offer.
      We have pension products with various investment strategies. To get a recommendation
      on what would suit your specific circumstances, I'd recommend speaking with one of
      our authorized financial advisers. They can consider your retirement goals, current
      situation, and create a suitable plan. Would you like me to arrange a call with an adviser?
    why_compliant: "Clear disclaimer, factual information, appropriate signposting, no recommendation"

# ============================================================================
# EDGE CASES (Section 8)
# ============================================================================
edge_case_vulnerable_customer:
  - principle: "Edge Case: Vulnerable Customer Protocol"
    content: "Identify vulnerability, no rush, extra support, specialist referral, document"
    fca_reference: "FCA Guidance on Vulnerable Customers"
    manual_section: "8.1 Edge Case 5"
    vulnerability_indicators:
      - "Recent bereavement"
      - "Confusion about finances"
      - "Health issues mentioned"
      - "Pressure or anxiety"
      - "Rushed decision-making"
      - "Dependency on others for financial decisions"
    required_actions:
      - "Acknowledge vulnerability sensitively"
      - "Emphasize no rush needed"
      - "Offer to include trusted person"
      - "Refer to specialist adviser"
      - "Document vulnerability on account"
      - "Extra care in all communications"
    compliant_protocol: |
      [Acknowledge situation sensitively]. Making important financial decisions
      during [challenging time] can be overwhelming, and there's often no need to rush.

      Important decisions are best made when you're ready. Taking time to consider
      options is completely fine. The money is safe [where it is] while you think.

      I'd strongly recommend speaking with a financial adviser who can take time
      to understand your full situation and provide appropriate support.

      Would you like someone else to join the call (family member, friend)?
      There's no pressure to make any decisions today.

# ============================================================================
# QA CHECKLIST (Section 9)
# ============================================================================
qa_rapid_assessment:
  - principle: "QA Section A: Prohibited Language Check"
    content: "Check response for all prohibited language categories. 0 flags = pass, 1-2 = review, 3+ = likely breach"
    manual_section: "9.1 Section A"
    checklist_items:
      - "Recommend/recommendation"
      - "Should in directive context"
      - "Suggest/suggestion re products"
      - "Advise/advice re investments"
      - "Best/better/superior"
      - "Perfect/ideal"
      - "Suitable/right for you"
      - "Given your [age/situation/goals]"
      - "People like you phrasing"
      - "Would work well for you"
      - "Enthusiastic emphasis on specific product"
      - "Comparison using value judgments"
      - "Validation of customer's choice as good"
      - "Risk assessment of customer"
      - "Suitability assessment"
    scoring:
      0_points: "Pass Section A"
      1_2_points: "Review required"
      3_plus_points: "Likely breach"

# ============================================================================
# QUICK REFERENCE TEMPLATES (Appendix A)
# ============================================================================
quick_reference_templates:
  - principle: "Five-Second Check Before Responding"
    manual_section: "Appendix A - Card 1"
    checklist:
      - "Are they asking about investments? (If NO, proceed normally)"
      - "Am I about to recommend something? (If YES, STOP)"
      - "Am I about to say what's 'suitable'? (If YES, STOP)"
      - "Am I using their circumstances? (If YES, STOP)"
      - "Can this be neutral + signpost? (If YES, do that)"

  - principle: "Safe Response: What should I invest in?"
    manual_section: "Appendix A - Card 2"
    template: |
      I can't provide investment recommendations as I'm not an authorized adviser.
      I can explain our product range, or arrange for you to speak with an adviser
      who can assess your circumstances and recommend suitable options.
```

#### Extraction Approach

1. **Systematic Coverage**: Go through manual sections 1-10 + appendices sequentially
2. **Complete Examples**: Include both compliant AND non-compliant with full explanations
3. **Preserve Structure**: Maintain manual section references for traceability
4. **Full Templates**: Include complete response templates from manual
5. **All Checklists**: QA criteria, red flags, quick checks
6. **Natural Count**: Let comprehensive coverage determine entry count (likely 150-250)

**Expected Output: ~150-250 comprehensive YAML entries**

---

### **Step 3: Massively Expand Pension Knowledge** (5-6 hours)

**File**: `src/guidance_agent/knowledge/pension_knowledge.py`

**Expand from 190 lines → ~1,200 lines covering 15 major topic areas**

#### Structure Overview

```python
PENSION_KNOWLEDGE = {
    # ENHANCED EXISTING SECTIONS (4 sections)
    "pension_types": {...},      # ADD: SIPP, Stakeholder, GPP, SSAS, Master Trust, EPP
    "regulations": {...},         # ADD: Complete auto-enrollment, DB transfer detail, small pots
    "typical_scenarios": {...},   # ADD: Divorce, redundancy, ill-health, career break, overseas
    "fee_structures": {...},      # ADD: Platform fees, SIPP costs, exit penalties

    # NEW MAJOR SECTIONS (11 sections)
    "pension_access_options": {
        "minimum_pension_age": {...},
        "flexi_access_drawdown": {...},
        "ufpls": {...},
        "annuities": {...},
        "phased_retirement": {...},
        "tax_free_cash": {...},
        "capped_drawdown": {...}
    },

    "tax_rules": {
        "annual_allowance": {...},
        "tapered_annual_allowance": {...},
        "mpaa": {...},
        "lifetime_allowance": {...},
        "lump_sum_allowances": {...},
        "emergency_tax": {...},
        "income_tax_on_pensions": {...},
        "inheritance_tax": {...}
    },

    "state_pension": {
        "new_state_pension": {...},
        "old_state_pension": {...},
        "ni_qualifying_years": {...},
        "state_pension_age": {...},
        "deferral": {...},
        "contracting_out": {...},
        "protected_payments": {...},
        "voluntary_contributions": {...}
    },

    "transfer_mechanics": {
        "cetv": {...},
        "tvas": {...},
        "apta": {...},
        "transfer_timeline": {...},
        "exit_penalties": {...},
        "loss_of_guarantees": {...},
        "pension_scams": {...}
    },

    "death_benefits": {
        "dc_before_75": {...},
        "dc_after_75": {...},
        "db_death_benefits": {...},
        "expression_of_wish": {...},
        "beneficiary_options": {...},
        "iht_treatment": {...},
        "small_pots_beneficiary": {...}
    },

    "contribution_rules": {
        "tax_relief_mechanisms": {...},
        "salary_sacrifice": {...},
        "employer_contributions": {...},
        "contribution_limits": {...},
        "opt_out_rules": {...}
    },

    "investment_concepts": {
        "default_funds": {...},
        "risk_grading": {...},
        "asset_classes": {...},
        "lifestyling": {...},
        "fund_types": {...},
        "passive_vs_active": {...}
    },

    "consolidation": {
        "benefits": {...},
        "risks": {...},
        "when_not_to": {...},
        "process": {...},
        "partial_consolidation": {...}
    },

    "provider_landscape": {
        "platforms": {...},
        "insurance_companies": {...},
        "master_trusts": {...},
        "workplace_schemes": {...},
        "fee_comparison": {...}
    },

    "regulatory_timeline": {
        "a_day_2006": {...},
        "auto_enrollment_2012": {...},
        "pension_freedoms_2015": {...},
        "pension_dashboard_2025": {...},
        "lta_abolition_2024": {...}
    },

    "special_circumstances": {
        "divorce": {...},
        "redundancy": {...},
        "ill_health": {...},
        "overseas": {...},
        "career_breaks": {...},
        "multiple_employment": {...}
    },

    "protections": {
        "ppf": {...},
        "fscs": {...},
        "fos": {...},
        "pension_regulator": {...}
    },

    "pension_wise": {
        "eligibility": {...},
        "what_covered": {...},
        "vs_regulated_advice": {...},
        "moneyhelper_integration": {...}
    },

    "glossary": {
        "crystallization": "Converting uncrystallised pension funds to provide benefits",
        "gmp": "Guaranteed Minimum Pension from contracting out",
        "pcls": "Pension Commencement Lump Sum - tax-free cash",
        "ufpls": "Uncrystallised Funds Pension Lump Sum",
        "mpaa": "Money Purchase Annual Allowance - £10k limit after flexible access",
        "cetv": "Cash Equivalent Transfer Value from DB schemes",
        "tvas": "Transfer Value Analysis System",
        "care": "Career Average Revalued Earnings DB scheme type",
        # ... 30+ more terms
    },

    "common_questions": {
        # Factual answers to frequent questions
        "when_can_access": {...},
        "how_much_tax_free": {...},
        "state_pension_amount": {...},
        # ... 20+ common FAQs
    }
}
```

#### Key Section Details

**pension_access_options** - Full details:
- Minimum pension age (55 now, 57 from 2028, protected ages, ill-health)
- Flexi-access drawdown (how it works, MPAA trigger, sustainability, death benefits)
- UFPLS (25%/75% split, MPAA trigger, emergency tax risk)
- Annuities (all types: single/joint, level/escalating, enhanced, value-protected, rates)
- Phased retirement (crystallizing in stages, tax spreading)
- Tax-free cash (PCLS, 25% standard, £268,275 max, protected amounts)
- Capped drawdown (legacy pre-2015 rules)

**tax_rules** - Comprehensive UK pension tax:
- Annual allowance (£60k, carry forward, excess charge)
- Tapered AA (£260k threshold, £360k adjusted, minimum £10k, calculation)
- MPAA (£10k, triggers, irreversible, DB exclusion)
- LTA abolition (April 2024, historical context)
- Lump sum allowances (LSA £268,275, LSDBA £1,073,100)
- Emergency tax (Month 1 basis, BR code, reclaim process)
- Income tax on pensions (rates 2024/25, Scotland differences)
- IHT treatment (usually outside estate, death benefits)

**state_pension** - Complete state pension system:
- New state pension (from 2016, £203.85/week, 35 years, triple lock)
- Old state pension (pre-2016, basic + SERPS/S2P)
- NI qualifying years (how to qualify, credits, gaps, voluntary)
- State pension age (66 now, 67 by 2028, 68 planned)
- Deferral (5.8% per year, no lump sum since 2016)
- Contracting out (ended 2016, GMP, impact on entitlement)
- Protected payments (>35 years under old system)
- Voluntary contributions (Class 2, Class 3, time limits, worth check)

**transfer_mechanics** - Complete transfer process:
- CETV (calculation, validity 3 months, typical multiples 20-40x)
- TVAS (critical yield, discount rates, comparison report)
- APTA (FCA requirement, specialist needed, presumption against)
- Transfer timeline (quote to completion 8-12 weeks)
- Exit penalties (MVR, surrender charges, when waived)
- Loss of guarantees (GAR, protected TFC, final salary links)
- Pension scams (warning signs, red flags, protection, ScamSmart)

**death_benefits** - All death benefit scenarios:
- DC before 75 (tax-free lump sum/drawdown/annuity, 2-year designation)
- DC after 75 (taxed at beneficiary's marginal rate)
- DB death benefits (before/after retirement, lump sums, survivor pensions)
- Expression of wish (purpose, not binding, updating, IHT benefit)
- Beneficiary options (lump sum, drawdown, annuity, leave invested)
- IHT treatment (outside estate usually, discretionary trusts)
- Small pots beneficiary (£30k limit, 2 allowed)

**Expected: ~1,000-1,200 lines generating ~150-200 knowledge entries**

---

### **Step 4: Run Bootstrap** (30-45 min)

Execute all bootstrap scripts to populate the database:

```bash
# Run master bootstrap script
python scripts/bootstrap_all_knowledge.py
```

This will execute in order:
1. `load_pension_knowledge.py` - Loads expanded pension knowledge (~150-200 entries)
2. `bootstrap_fca_knowledge.py` - Loads FCA compliance from YAML (~150-250 entries)
3. `generate_seed_cases.py` - LLM-generates consultation cases (~20 entries)
4. `generate_seed_rules.py` - LLM-generates guidance rules (~8 entries)
5. `verify_knowledge_bases.py` - Verifies all loaded correctly

**Expected Counts:**
- **fca_knowledge**: ~150-250 entries
- **pension_knowledge**: ~150-200 entries
- **cases**: ~20 entries
- **rules**: ~8 entries
- **TOTAL**: ~330-480 entries

**Monitor for:**
- Embedding generation progress
- Any dimension mismatches (should be none)
- LLM API calls (for case/rule generation)
- Final verification output

---

### **Step 5: Verify & Validate** (30-45 min)

#### 5A. Schema Verification

```bash
# Check embedding dimensions
psql $DATABASE_URL -c "\d fca_knowledge" | grep embedding
# Expected: embedding | vector(768)

psql $DATABASE_URL -c "\d pension_knowledge" | grep embedding
# Expected: embedding | vector(768)

# Verify HNSW indexes exist
psql $DATABASE_URL -c "\d fca_knowledge" | grep idx
psql $DATABASE_URL -c "\d pension_knowledge" | grep idx
```

#### 5B. Count Verification

```bash
# Check entry counts
psql $DATABASE_URL -c "SELECT COUNT(*) FROM fca_knowledge"
# Expected: ~150-250

psql $DATABASE_URL -c "SELECT COUNT(*) FROM pension_knowledge"
# Expected: ~150-200

psql $DATABASE_URL -c "SELECT COUNT(*) FROM cases"
# Expected: ~20

psql $DATABASE_URL -c "SELECT COUNT(*) FROM rules"
# Expected: ~8

psql $DATABASE_URL -c "SELECT
    (SELECT COUNT(*) FROM fca_knowledge) as fca,
    (SELECT COUNT(*) FROM pension_knowledge) as pension,
    (SELECT COUNT(*) FROM cases) as cases,
    (SELECT COUNT(*) FROM rules) as rules,
    (SELECT COUNT(*) FROM fca_knowledge) +
    (SELECT COUNT(*) FROM pension_knowledge) +
    (SELECT COUNT(*) FROM cases) +
    (SELECT COUNT(*) FROM rules) as total"
# Expected total: ~330-480
```

#### 5C. Embedding Dimension Check

```bash
# Verify all embeddings are 768-dimensional
psql $DATABASE_URL -c "SELECT DISTINCT vector_dims(embedding) FROM fca_knowledge"
# Expected: 768

psql $DATABASE_URL -c "SELECT DISTINCT vector_dims(embedding) FROM pension_knowledge"
# Expected: 768

# Check for NULL embeddings (should be 0)
psql $DATABASE_URL -c "SELECT COUNT(*) FROM fca_knowledge WHERE embedding IS NULL"
# Expected: 0

psql $DATABASE_URL -c "SELECT COUNT(*) FROM pension_knowledge WHERE embedding IS NULL"
# Expected: 0
```

#### 5D. Quality Spot-Checks

**Sample FCA entries:**
```bash
psql $DATABASE_URL -c "SELECT content, category FROM fca_knowledge ORDER BY RANDOM() LIMIT 5"
```

Verify:
- Content matches FCA manual source
- Categories are sensible
- No duplicate content

**Sample pension entries:**
```bash
psql $DATABASE_URL -c "SELECT content, category, subcategory FROM pension_knowledge ORDER BY RANDOM() LIMIT 5"
```

Verify:
- UK pension accuracy (amounts, rates, dates)
- Categories align with module structure
- Factual correctness

**Sample LLM-generated cases:**
```bash
psql $DATABASE_URL -c "SELECT title, summary FROM cases ORDER BY RANDOM() LIMIT 3"
```

Verify:
- FCA compliant (no directive language)
- Realistic scenarios
- Appropriate complexity

#### 5E. Retrieval Testing

Create test script: `scripts/test_retrieval.py`

```python
#!/usr/bin/env python3
"""Test knowledge base retrieval quality."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.retrieval.retriever import retrieve_context

# Test cases
test_queries = [
    {
        "query": "Should I transfer my DB pension?",
        "expected_content": ["£30,000", "regulated advice", "valuable benefits", "guaranteed income"],
        "should_not_contain": ["you should", "I recommend", "best option"]
    },
    {
        "query": "How much can I contribute to my pension?",
        "expected_content": ["£60,000", "annual allowance", "carry forward"],
        "should_not_contain": ["you should contribute", "best to"]
    },
    {
        "query": "When can I claim state pension?",
        "expected_content": ["age 66", "rising to 67", "birthdate"],
        "should_not_contain": []
    },
    {
        "query": "What happens to my pension if I die?",
        "expected_content": ["before 75", "after 75", "beneficiary", "expression of wish"],
        "should_not_contain": []
    },
    {
        "query": "Can I access my pension at 55?",
        "expected_content": ["minimum pension age", "rising to 57", "2028"],
        "should_not_contain": []
    },
    {
        "query": "Tell me about pension tax relief",
        "expected_content": ["tax relief", "salary sacrifice", "employer contributions"],
        "should_not_contain": ["you should", "best way"]
    },
]

print("Testing knowledge base retrieval...\n")

passed = 0
failed = 0

for i, test in enumerate(test_queries, 1):
    print(f"Test {i}/{len(test_queries)}: {test['query']}")

    result = retrieve_context(test['query'])
    result_text = result.lower() if isinstance(result, str) else str(result).lower()

    # Check expected content
    missing_expected = []
    for expected in test['expected_content']:
        if expected.lower() not in result_text:
            missing_expected.append(expected)

    # Check prohibited content
    found_prohibited = []
    for prohibited in test['should_not_contain']:
        if prohibited.lower() in result_text:
            found_prohibited.append(prohibited)

    # Evaluate
    if not missing_expected and not found_prohibited:
        print("  ✅ PASS\n")
        passed += 1
    else:
        print("  ❌ FAIL")
        if missing_expected:
            print(f"     Missing expected: {missing_expected}")
        if found_prohibited:
            print(f"     Found prohibited: {found_prohibited}")
        print()
        failed += 1

print(f"\n{'='*50}")
print(f"Results: {passed}/{len(test_queries)} passed, {failed} failed")
print(f"{'='*50}\n")

sys.exit(0 if failed == 0 else 1)
```

Run tests:
```bash
python scripts/test_retrieval.py
```

Expected: All tests pass (6/6)

#### 5F. Coverage Analysis

```bash
# Check FCA category distribution
psql $DATABASE_URL -c "SELECT category, COUNT(*) FROM fca_knowledge GROUP BY category ORDER BY COUNT(*) DESC"

# Check pension category distribution
psql $DATABASE_URL -c "SELECT category, COUNT(*) FROM pension_knowledge GROUP BY category ORDER BY COUNT(*) DESC"

# Check for comprehensive coverage
psql $DATABASE_URL -c "SELECT category, COUNT(*) as count FROM pension_knowledge GROUP BY category HAVING COUNT(*) < 3"
# Ideally: no categories with <3 entries (indicates thin coverage)
```

---

## Success Criteria

### Technical Success
✅ Database schema reads `EMBEDDING_DIMENSION` from env var (verified in models)
✅ Migration successfully updates schema to `vector(768)`
✅ All 5 tables updated (fca_knowledge, pension_knowledge, memories, cases, rules)
✅ HNSW indexes recreated successfully
✅ Zero dimension mismatch errors
✅ All embeddings are 768-dimensional
✅ No NULL embeddings in any table

### Content Success - FCA Compliance
✅ All 10 manual sections represented (Sections 1-10)
✅ All appendices included (Quick reference cards)
✅ All 6 prohibited language categories (A-F) fully extracted
✅ All 8 scenario types with complete examples
✅ All 5 edge cases with protocols
✅ Complete QA framework embedded
✅ Vulnerable customer protocols included
✅ 150-250 comprehensive FCA entries

### Content Success - Pension Knowledge
✅ All 15 major topic areas comprehensively covered:
  - ✅ Enhanced pension types (DC, DB, SIPP, Stakeholder, GPP, SSAS, Master Trust, EPP)
  - ✅ Access options (minimum age, drawdown, UFPLS, annuities, phased, TFC, capped)
  - ✅ Tax rules (AA, tapered AA, MPAA, LTA abolition, LSA, emergency tax, IHT)
  - ✅ State pension (new/old, NI years, SPA, deferral, contracting out, voluntary)
  - ✅ Transfer mechanics (CETV, TVAS, APTA, timelines, penalties, scams)
  - ✅ Death benefits (before/after 75, DB/DC, expression of wish, IHT)
  - ✅ Contribution rules (tax relief, salary sacrifice, limits, opt-out)
  - ✅ Investment concepts (defaults, risk grading, asset classes, lifestyling)
  - ✅ Consolidation (benefits, risks, when not to, process)
  - ✅ Provider landscape (platforms, insurers, master trusts, fees)
  - ✅ Regulatory timeline (2006-2024 key changes)
  - ✅ Special circumstances (divorce, redundancy, ill-health, overseas, career breaks)
  - ✅ Protections (PPF, FSCS, FOS, Pension Regulator)
  - ✅ Pension Wise (free guidance service)
  - ✅ Glossary and common questions
✅ 150-200 pension knowledge entries
✅ Accurate UK-specific information (amounts, rates, dates)
✅ Current 2024/25 tax year figures

### Overall Success
✅ 330-480 total knowledge entries in database
✅ Retrieval returns accurate, compliant, comprehensive guidance
✅ No FCA boundary violations in retrieved content
✅ Coverage across all major pension topics
✅ Production-ready for UK pension guidance
✅ Knowledge base scales appropriately with comprehensive content
✅ Future-proof: different deployments can use different embedding dimensions

---

## Post-Bootstrap Next Steps

### Immediate (Within 1 week)
1. Monitor retrieval quality with real queries
2. Gather feedback from test users
3. Identify any coverage gaps
4. Fine-tune retrieval parameters if needed

### Short-term (1-2 months)
1. Add document ingestion (from Phase 1 of knowledge-ingestion-roadmap.md)
2. Implement deduplication system
3. Add full CRUD API for knowledge management
4. Begin automated MoneyHelper scraping

### Medium-term (3-6 months)
1. Scale to 1,000+ entries via automated ingestion
2. Implement quality scoring and monitoring
3. Add version control and audit trails
4. Build admin UI for knowledge curation

---

## Cost Estimates

### One-Time Bootstrap Costs
- **LLM API calls** (case/rule generation): ~£0.50
- **Embedding generation** (local model): £0 (using LM Studio)
- **Total**: ~£0.50

### Ongoing Costs
- **Local embeddings**: £0/month (nomic-embed-text via LM Studio)
- **Storage**: Minimal (768d vectors vs 1536d = 50% storage savings)
- **Maintenance**: Periodic content updates as regulations change

---

## Risk Mitigation

### Technical Risks

**Risk**: Migration fails partway through
**Mitigation**:
- Test on development database first
- Migration includes downgrade path
- Zero data loss risk (tables are empty)

**Risk**: Embedding dimension mismatch after migration
**Mitigation**:
- Comprehensive verification in Step 5
- Environment variable validation
- Explicit dimension checks in bootstrap scripts

**Risk**: Bootstrap scripts fail
**Mitigation**:
- Scripts already tested in TDD approach
- Each script can run independently
- Verification script catches issues

### Content Quality Risks

**Risk**: Extracted FCA content misrepresents manual
**Mitigation**:
- Manual section references preserved
- Spot-check verification in Step 5
- Direct quotes from manual where critical

**Risk**: UK pension information becomes outdated
**Mitigation**:
- Document source dates (2024/25 figures)
- Plan for annual updates
- Track regulatory changes

**Risk**: Retrieval returns non-compliant guidance
**Mitigation**:
- Comprehensive FCA principle embedding
- Retrieval testing in Step 5
- Ongoing monitoring and refinement

---

## Documentation

### Files Created/Modified

**Created:**
- `alembic/versions/[timestamp]_update_embedding_dimension_to_768.py`
- `data/knowledge/fca_compliance_principles.yaml`
- `scripts/test_retrieval.py` (verification script)

**Modified:**
- `src/guidance_agent/core/database.py` (dynamic EMBEDDING_DIM)
- `src/guidance_agent/knowledge/pension_knowledge.py` (190 → 1200 lines)

### References

- FCA Compliance Manual: `specs/fca-compliance-manual.md`
- Original Bootstrap Spec: `specs/knowledge-base-bootstrap.md`
- Ingestion Roadmap: `specs/knowledge-ingestion-roadmap.md`
- Implementation Guide: `docs/KNOWLEDGE_BASE_BOOTSTRAP.md`

---

## Timeline Summary

| Step | Description | Time | Status |
|------|-------------|------|--------|
| 1 | Dynamic schema implementation | 20 min | Pending |
| 2 | FCA principles extraction | 4-5 hours | Pending |
| 3 | Pension knowledge expansion | 5-6 hours | Pending |
| 4 | Bootstrap execution | 30-45 min | Pending |
| 5 | Verification & validation | 30-45 min | Pending |
| **Total** | **Complete implementation** | **11-13 hours** | **Ready** |

---

## Conclusion

This implementation plan provides a comprehensive, production-ready knowledge bootstrap that:

1. **Future-proofs architecture** with dynamic embedding dimensions
2. **Achieves comprehensive FCA coverage** from authoritative manual source
3. **Covers UK pension system exhaustively** across 15 major topic areas
4. **Enables accurate, compliant guidance** through structured knowledge
5. **Scales appropriately** with 330-480 high-quality entries

Upon completion, the system will have a solid foundation for UK pension guidance, ready for production use and future expansion via automated ingestion pipelines.

---

**Document Version**: 2.0
**Last Updated**: November 2025
**Next Review**: After bootstrap completion
