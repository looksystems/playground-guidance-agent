# Knowledge Base Bootstrap Specification

## Status: ✅ COMPLETED (November 1, 2025)

**Implementation Completed**: November 1, 2025
**Duration**: 1 day (using TDD and AI agents)
**Tests**: 29 passing (pension knowledge module)
**Migration**: `d54d8651560e_add_fca_and_pension_knowledge_tables.py` applied

### Completed Deliverables

1. ✅ **Database Schema**
   - Migration created and applied
   - `fca_knowledge` table with HNSW vector index
   - `pension_knowledge` table with HNSW vector index
   - SQLAlchemy models: `FCAKnowledge`, `PensionKnowledge`

2. ✅ **Pension Knowledge Module**
   - `src/guidance_agent/knowledge/pension_knowledge.py` (comprehensive UK pension data)
   - 29 unit tests, all passing
   - TDD approach: tests written first, then implementation

3. ✅ **FCA Compliance Data**
   - `data/knowledge/fca_compliance_principles.yaml` (6 categories)
   - Guidance boundaries, prohibited/permitted language
   - DB transfer warnings, risk disclosure, verification techniques

4. ✅ **Bootstrap Scripts** (all 6 implemented)
   - `scripts/load_pension_knowledge.py` - Load pension knowledge to DB
   - `scripts/bootstrap_fca_knowledge.py` - Load FCA compliance from YAML
   - `scripts/generate_seed_cases.py` - LLM-generate 20 consultation cases
   - `scripts/generate_seed_rules.py` - LLM-generate 8 guidance rules
   - `scripts/verify_knowledge_bases.py` - Verify all KBs populated
   - `scripts/bootstrap_all_knowledge.py` - Master orchestration script

5. ✅ **Documentation**
   - `docs/KNOWLEDGE_BASE_BOOTSTRAP.md` - Complete implementation guide
   - Setup instructions, usage, troubleshooting, cost estimates

### Ready to Use

The knowledge base bootstrap system is fully implemented and ready to run. To bootstrap:

```bash
# 1. Set up environment (add API keys to .env)
cp .env.example .env

# 2. Run complete bootstrap
uv run python scripts/bootstrap_all_knowledge.py

# 3. Verify success
uv run python scripts/verify_knowledge_bases.py
```

**Estimated cost**: ~$0.50 per bootstrap run (embeddings + LLM generation)

See `docs/KNOWLEDGE_BASE_BOOTSTRAP.md` for detailed instructions.

---

## Overview

This document specifies how to bootstrap the four knowledge bases required for the Financial Guidance Agent system. The knowledge bases provide the foundation for the advisor agent's retrieval-augmented generation (RAG) system and learning mechanisms.

**Purpose**: Populate the system with initial domain knowledge, compliance rules, and exemplar cases before virtual training begins.

**Scope**: All knowledge bases needed for Phase 3 (Advisor Agent) and beyond.

**Approach**: Comprehensive bootstrap using LLM-assisted generation and structured data (estimated 5-8 days, **completed in 1 day using TDD and AI agents**).

## Knowledge Bases Required

### 1. FCA Compliance Knowledge Base

**Purpose**: Store FCA regulatory guidance, boundary definitions, and compliance requirements for retrieval during advisor decision-making.

**What Needs to Be Stored**:
- Guidance vs advice boundary definitions with examples
- Risk disclosure requirements with sample language
- Customer understanding verification protocols
- Prohibited language patterns (e.g., "should", "recommend", "best for you")
- Permitted language patterns (e.g., "could consider", "some people choose")
- DB pension transfer regulations and warnings
- Signposting requirements and thresholds
- Case law and FCA precedents for boundary decisions

**Storage Format**:
- Text chunks with vector embeddings in `fca_knowledge` table
- Each principle/guideline as a retrievable document
- JSONB metadata for categorization and filtering

**Database Schema**:
```sql
CREATE TABLE fca_knowledge (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    source VARCHAR(255),
    category VARCHAR(100) NOT NULL,  -- 'guidance_boundary', 'db_warnings', 'risk_disclosure', etc.
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX fca_knowledge_embedding_idx
ON fca_knowledge USING hnsw (embedding vector_cosine_ops);

CREATE INDEX fca_knowledge_category_idx
ON fca_knowledge(category);
```

**Example Entry**:
```json
{
  "id": "uuid",
  "content": "When discussing pension options, avoid directive language such as 'you should' or 'I recommend'. Instead, use guidance-appropriate phrases like 'you could consider', 'some people choose to', or 'options available include'. This maintains the guidance/advice boundary per FCA COBS 19.5.",
  "source": "FCA_COBS_19.5_Guidance",
  "category": "guidance_boundary",
  "metadata": {
    "principle_type": "language_boundaries",
    "compliance_level": "mandatory",
    "examples": ["you could consider", "some people choose", "options include"]
  }
}
```

### 2. Pension Domain Knowledge Base

**Purpose**: Provide factual knowledge about the UK pension system for grounding customer generation, advisor guidance, and outcome simulation.

**What Needs to Be Stored**:
- Pension types (DC, DB, personal, stakeholder) with definitions and features
- Typical providers by era and pension type
- Auto-enrollment regulations (started 2012, minimum contributions, earnings trigger)
- Small pots regulations (definition, consolidation rules)
- DB transfer regulations (£30k threshold requiring regulated advice)
- Special features (guaranteed annuity rates, protected tax-free cash)
- Age-appropriate pension scenarios (young worker, mid-career, pre-retirement)
- Typical fee structures by pot size and provider type
- Tax regulations and implications (lifetime allowance, annual allowance, MPAA)

**Storage Format**:
- **Primary**: Structured Python module (`src/guidance_agent/knowledge/pension_knowledge.py`)
- **Secondary**: Database entries with embeddings for RAG retrieval

**Structure Example**:
```python
PENSION_KNOWLEDGE = {
    "pension_types": {
        "defined_contribution": {
            "description": "Pension pot built from contributions, value depends on investment growth",
            "typical_providers": ["NEST", "Aviva", "Royal London", "Standard Life"],
            "common_features": ["flexible_access", "investment_choice", "death_benefits"],
            "typical_fees": {"min": 0.003, "max": 0.015},
            "fca_considerations": "No guaranteed income, investment risk borne by member",
            "min_value_range": (100, 500000),
            "typical_by_age": {
                "25-35": (1000, 15000),
                "35-50": (10000, 100000),
                "50-retirement": (50000, 300000)
            }
        },
        "defined_benefit": {
            "description": "Guaranteed income based on salary and years of service",
            "calculation": "accrual_rate × years_service × final_salary",
            "typical_accrual_rates": [1/60, 1/80],
            "typical_sectors": ["public_sector", "large_employers_pre_2000", "local_government"],
            "fca_warning": "Valuable guarantees lost if transferred out - requires regulated advice if >£30k",
            "special_features": ["guaranteed_income", "inflation_protection", "survivor_benefits", "early_retirement_factors"],
            "transfer_value_multiple": {"min": 20, "max": 40}  # Typical CETV as multiple of annual income
        }
    },
    "regulations": {
        "auto_enrollment": {
            "started": 2012,
            "minimum_total_contribution": 0.08,
            "employer_minimum": 0.03,
            "employee_minimum": 0.05,
            "earnings_trigger": 10000,
            "age_range": (22, "state_pension_age")
        },
        "db_transfers": {
            "advice_threshold": 30000,
            "fca_requirement": "Regulated financial advice mandatory for transfers >£30k",
            "typical_outcome": "Most people worse off transferring from DB to DC",
            "tvas_requirement": "Transfer Value Analysis required",
            "appropriate_pension_transfer_analysis": "APTA required from FCA authorized adviser"
        },
        "small_pots": {
            "definition": "Pension pot worth less than £10,000",
            "limit_per_year": 3,
            "no_advice_needed": True,
            "common_scenario": "Consolidation of old workplace pensions"
        }
    },
    "typical_scenarios": {
        "young_worker_22_30": {
            "age_range": (22, 30),
            "pension_count_range": (1, 2),
            "total_value_range": (1000, 15000),
            "common_types": ["defined_contribution"],
            "common_goals": ["understand_basics", "check_on_track", "consolidate_old_pots"],
            "typical_providers": ["NEST", "NOW Pensions", "The People's Pension"]
        },
        "mid_career_35_50": {
            "age_range": (35, 50),
            "pension_count_range": (2, 5),
            "total_value_range": (20000, 150000),
            "common_types": ["defined_contribution", "small_db_from_early_career"],
            "common_goals": ["consolidation", "reduce_fees", "check_on_track", "boost_savings"],
            "typical_providers": ["Aviva", "Standard Life", "Royal London", "Prudential"]
        },
        "pre_retirement_55_67": {
            "age_range": (55, 67),
            "pension_count_range": (3, 8),
            "total_value_range": (50000, 400000),
            "common_types": ["defined_contribution", "defined_benefit", "personal_pensions"],
            "common_goals": ["consolidation", "access_planning", "understand_options", "maximize_income"],
            "special_considerations": ["protected_tax_free_cash", "guaranteed_annuity_rates", "db_safeguarded_benefits"]
        }
    },
    "fee_structures": {
        "workplace_dc": {
            "nest": 0.003,  # 0.3%
            "now_pensions": 0.003,
            "peoples_pension": 0.005,
            "provider_default": 0.01  # Typical 1%
        },
        "personal_pensions": {
            "platform_fee": (0.002, 0.0045),  # 0.2% - 0.45%
            "fund_fees": (0.001, 0.015),  # 0.1% - 1.5%
            "total_typical": 0.01  # 1% combined
        }
    }
}
```

**Database Schema** (for RAG retrieval):
```sql
CREATE TABLE pension_knowledge (
    id UUID PRIMARY KEY,
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,  -- 'pension_type', 'regulation', 'scenario', etc.
    subcategory VARCHAR(100),
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX pension_knowledge_embedding_idx
ON pension_knowledge USING hnsw (embedding vector_cosine_ops);
```

### 3. Case Base (Episodic Memory)

**Purpose**: Store successful guidance interactions for retrieval during advisor decision-making (case-based reasoning).

**Current State**:
- ✅ Database schema EXISTS (`cases` table with pgvector support)
- ✅ Storage mechanisms IMPLEMENTED (`CaseBase` class in `retrieval/retriever.py`)
- ❌ NOT YET POPULATED with seed data

**Database Schema** (already exists):
```sql
-- From alembic/versions/a7b3073fdead_initial_migration.py
CREATE TABLE cases (
    id UUID PRIMARY KEY,
    task_type VARCHAR(100),
    customer_situation TEXT,
    guidance_provided TEXT,
    outcome JSONB,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE
);

CREATE INDEX cases_embedding_idx
ON cases USING hnsw (embedding vector_cosine_ops);

CREATE INDEX cases_task_type_idx
ON cases(task_type);
```

**What Needs to Be Populated**:

1. **FCA Exemplar Cases** (20-30 cases from FCA guidance documents)
   - Extract scenarios from FCA publications
   - Convert to Case format with customer situation + guidance
   - Tag as "FCA validated" exemplar cases

2. **LLM-Generated Seed Cases** (20-50 diverse cases)
   - DB pension warning scenarios (5 cases)
   - Small pot consolidation scenarios (5 cases)
   - Fee reduction inquiries (5 cases)
   - Risk assessment scenarios (5 cases)
   - Understanding verification examples (5 cases)
   - Complex multi-pension scenarios (5 cases)
   - Literacy-adapted communication examples (5 cases)

3. **Virtual Training Cases** (thousands, accumulated during Phase 5)
   - Generated automatically through advisor-customer simulations
   - Successful consultations automatically stored
   - Grows as training progresses

**Example Case Entry**:
```json
{
  "id": "uuid",
  "task_type": "defined_benefit_transfer",
  "customer_situation": "Customer aged 58 with DB pension from local government (£35,000 transfer value, £850/month guaranteed income at 65) considering consolidation with 2 DC pensions (total £45,000). Wants to understand options.",
  "guidance_provided": "I can see you have a defined benefit pension from your time in local government. This type of pension provides valuable guarantees - a fixed monthly income of £850 for life starting at 65, protected against inflation. Most people would be worse off transferring out of a DB pension because you're giving up those guarantees. If you're considering transferring this pension (worth more than £30,000), FCA rules require you to get regulated financial advice from an authorized adviser. I can help you understand your other DC pensions and consolidation options for those, but for decisions about the DB pension, you'd need to speak with a regulated adviser.",
  "outcome": {
    "successful": true,
    "fca_compliant": true,
    "customer_satisfaction": 9,
    "comprehension": 8,
    "db_warning_given": true,
    "signposted_correctly": true
  },
  "metadata": {
    "source": "seed_generation",
    "validated": true,
    "literacy_level": "medium",
    "complexity": "high"
  }
}
```

### 4. Rules Base (Semantic Memory)

**Purpose**: Store learned principles from reflection on failures and seed with critical compliance rules.

**Current State**:
- ✅ Database schema EXISTS (`rules` table with pgvector support)
- ✅ Storage mechanisms IMPLEMENTED (`RulesBase` class in `retrieval/retriever.py`)
- ❌ NOT YET POPULATED with initial rules

**Database Schema** (already exists):
```sql
-- From alembic/versions/a7b3073fdead_initial_migration.py
CREATE TABLE rules (
    id UUID PRIMARY KEY,
    principle TEXT NOT NULL,
    domain VARCHAR(100),
    confidence REAL DEFAULT 0.5,
    supporting_evidence JSONB,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_accessed TIMESTAMP WITH TIME ZONE
);

CREATE INDEX rules_embedding_idx
ON rules USING hnsw (embedding vector_cosine_ops);

CREATE INDEX rules_domain_idx
ON rules(domain);
```

**What Needs to Be Populated**:

1. **Critical Compliance Rules** (5-10 mandatory rules, confidence=1.0)
   - DB transfer warning requirement
   - Prohibited advice language
   - Risk disclosure requirement
   - Understanding verification requirement
   - Signposting threshold rules

2. **Best Practice Principles** (5-10 recommended rules, confidence=0.8-0.9)
   - Language simplification for low literacy
   - Analogy usage for complex concepts
   - Breaking complex topics into chunks
   - Checking understanding with open questions

3. **Learned Rules** (accumulated during Phase 5 virtual training)
   - Generated through reflection on failures
   - Validated against exemplar cases
   - Confidence-weighted based on evidence

**Example Rule Entry**:
```json
{
  "id": "uuid",
  "principle": "When customer has DB pension with transfer value >£30,000, ALWAYS include warning about valuable guarantees and requirement for regulated financial advice BEFORE any discussion of transfer options, because FCA mandates this protection and most people lose out by transferring from DB to DC pensions.",
  "domain": "regulatory_compliance",
  "confidence": 1.0,
  "supporting_evidence": ["FCA-DB-001", "FCA-DB-002", "CASE-DB-TRANSFER-012"],
  "metadata": {
    "source": "fca_requirement",
    "mandatory": true,
    "fca_reference": "COBS 19.1.6",
    "penalty_for_violation": "high"
  }
}
```

## Data Sources

### FCA Compliance Knowledge

**Approach**: Synthetic/curated examples based on FCA principles (faster than PDF processing).

**Source Strategy**:
1. Create curated YAML file with FCA principles organized by category
2. Use LLM to expand principles into multiple phrasings and examples
3. Chunk and embed for semantic retrieval

**Categories to Cover**:
- `guidance_boundary` - Guidance vs advice distinctions
- `prohibited_language` - Words/phrases that cross into advice
- `permitted_language` - Guidance-appropriate phrasing
- `db_warnings` - DB pension transfer warnings
- `risk_disclosure` - Risk communication requirements
- `understanding_verification` - Checking customer comprehension
- `signposting` - When to refer to regulated advisers

**Example Source File** (`data/knowledge/fca_compliance_principles.yaml`):
```yaml
guidance_boundary:
  - principle: "Guidance helps customers understand their options; advice recommends specific actions"
    examples:
      compliant:
        - "You could consider consolidating your pensions to reduce fees"
        - "Some people in your situation choose to access their pension at 55"
        - "Options available include taking a lump sum or buying an annuity"
      non_compliant:
        - "You should consolidate your pensions"
        - "I recommend taking your pension at 55"
        - "The best option for you is to take a lump sum"

db_warnings:
  - principle: "DB transfers >£30k require regulated advice warning before discussion"
    template: "I can see you have a defined benefit pension [from X]. This type provides valuable guarantees - [specify guaranteed income]. Most people would be worse off transferring out. If you're considering transferring (worth more than £30,000), FCA rules require regulated financial advice. I can help with [other pensions], but for the DB pension, you'd need a regulated adviser."
    mandatory: true
    fca_reference: "COBS 19.1.6"
```

### Pension Domain Knowledge

**Approach**: Structured Python module + database entries with embeddings.

**Source Strategy**:
1. Research UK government pension resources (GOV.UK, TPR, HMRC)
2. Create structured Python dictionary with all domain knowledge
3. Generate embeddings for each knowledge item for RAG retrieval
4. Maintain Python file as source of truth, sync to database

**Key Resources**:
- GOV.UK Pension Guidance: https://www.gov.uk/pension-types
- The Pensions Regulator: https://www.thepensionsregulator.gov.uk/
- MoneyHelper: https://www.moneyhelper.org.uk/en/pensions-and-retirement
- FCA Handbook: https://www.handbook.fca.org.uk/handbook/COBS/

### Case Base Seeds

**Approach**: LLM-assisted generation with manual validation.

**Source Strategy**:
1. Define case templates for each scenario type
2. Use LiteLLM to generate diverse customer situations and guidance
3. Run compliance validation on each generated case
4. Manually review and adjust for quality
5. Store approved cases in database

**Case Generation Prompt Template**:
```
Generate a realistic UK pension guidance consultation case.

Scenario Type: {scenario_type}
Customer Age: {age_range}
Pension Types: {pension_types}
Complexity: {complexity_level}
Literacy Level: {literacy_level}

Generate:
1. Customer situation (detailed pension portfolio and inquiry)
2. FCA-compliant guidance response from advisor
3. Reasoning for approach taken
4. Expected outcome metrics

Requirements:
- Guidance must stay within FCA boundary (no advice)
- Use appropriate language for literacy level
- Include required warnings for DB pensions >£30k
- Demonstrate understanding verification
- Show balanced pros/cons discussion
```

### Rules Base Seeds

**Approach**: LLM-assisted generation based on FCA requirements.

**Source Strategy**:
1. Define critical compliance requirements from FCA
2. Use LiteLLM to generate principle statements with reasoning
3. Set confidence levels (1.0 for mandatory, 0.8-0.9 for best practices)
4. Store with supporting evidence references

**Rule Generation Prompt Template**:
```
Generate a guidance principle for UK pension advisors.

Domain: {domain}
Based on: {fca_requirement}
Confidence Level: {confidence}

Generate a clear, actionable principle statement that explains:
1. WHEN the principle applies (triggering conditions)
2. WHAT action should be taken
3. WHY this is important (reasoning/consequences)

Format: "[WHEN condition], [ALWAYS/SHOULD] [action], because [reasoning]"

Example: "When customer has DB pension with transfer value >£30,000, ALWAYS include warning about valuable guarantees and requirement for regulated financial advice BEFORE any discussion of transfer options, because FCA mandates this protection and most people lose out by transferring."
```

## Technical Implementation

### Database Migrations

**Migration 1: Add FCA Knowledge Table** (if not exists)

```python
# alembic/versions/xxx_add_fca_knowledge_table.py

def upgrade():
    op.create_table('fca_knowledge',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('source', sa.String(255), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    # HNSW index for fast similarity search
    op.execute(
        'CREATE INDEX fca_knowledge_embedding_idx '
        'ON fca_knowledge USING hnsw (embedding vector_cosine_ops)'
    )

    # Index for filtering by category
    op.create_index('fca_knowledge_category_idx', 'fca_knowledge', ['category'])

def downgrade():
    op.drop_index('fca_knowledge_category_idx')
    op.execute('DROP INDEX fca_knowledge_embedding_idx')
    op.drop_table('fca_knowledge')
```

**Migration 2: Add Pension Knowledge Table**

```python
# alembic/versions/xxx_add_pension_knowledge_table.py

def upgrade():
    op.create_table('pension_knowledge',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('subcategory', sa.String(100), nullable=True),
        sa.Column('embedding', pgvector.sqlalchemy.Vector(dim=1536), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

    op.execute(
        'CREATE INDEX pension_knowledge_embedding_idx '
        'ON pension_knowledge USING hnsw (embedding vector_cosine_ops)'
    )

    op.create_index('pension_knowledge_category_idx', 'pension_knowledge', ['category'])

def downgrade():
    op.drop_index('pension_knowledge_category_idx')
    op.execute('DROP INDEX pension_knowledge_embedding_idx')
    op.drop_table('pension_knowledge')
```

### SQLAlchemy Models

**File**: `src/guidance_agent/core/database.py` (extend existing file)

```python
class FCAKnowledge(Base):
    """FCA compliance knowledge for retrieval."""
    __tablename__ = 'fca_knowledge'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String, nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )

class PensionKnowledge(Base):
    """Pension domain knowledge for retrieval."""
    __tablename__ = 'pension_knowledge'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536))
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text("now()")
    )
```

### Bootstrap Scripts

#### 1. Pension Knowledge Structure

**File**: `src/guidance_agent/knowledge/pension_knowledge.py`

```python
"""
UK Pension System Domain Knowledge

This module contains structured knowledge about the UK pension system,
used for customer generation validation, advisor context, and outcome simulation.
"""

from typing import Dict, List, Tuple, Optional

PENSION_KNOWLEDGE = {
    # ... (full structure from earlier in this document)
}

def get_pension_type_info(pension_type: str) -> Optional[Dict]:
    """Get information about a specific pension type."""
    return PENSION_KNOWLEDGE["pension_types"].get(pension_type)

def get_regulation_info(regulation_name: str) -> Optional[Dict]:
    """Get regulatory information."""
    return PENSION_KNOWLEDGE["regulations"].get(regulation_name)

def get_typical_scenario(scenario_name: str) -> Optional[Dict]:
    """Get typical customer scenario information."""
    return PENSION_KNOWLEDGE["typical_scenarios"].get(scenario_name)

def get_fee_structure(pension_category: str) -> Optional[Dict]:
    """Get typical fee structure for pension category."""
    return PENSION_KNOWLEDGE["fee_structures"].get(pension_category)

def validate_pension_value_for_age(age: int, total_value: float, pension_type: str) -> bool:
    """Validate if pension value is realistic for customer age."""
    pension_info = get_pension_type_info(pension_type)
    if not pension_info or "typical_by_age" not in pension_info:
        return True  # Unknown type, skip validation

    # Find appropriate age range
    for age_range_key, (min_val, max_val) in pension_info["typical_by_age"].items():
        age_range = parse_age_range(age_range_key)
        if age_range[0] <= age <= age_range[1]:
            return min_val <= total_value <= max_val * 2  # Allow 2x for edge cases

    return True

def parse_age_range(age_range_str: str) -> Tuple[int, int]:
    """Parse age range string like '25-35' into tuple (25, 35)."""
    parts = age_range_str.split('-')
    return (int(parts[0]), int(parts[1]) if parts[1] != 'retirement' else 67)
```

#### 2. Load Pension Knowledge to Database

**File**: `scripts/load_pension_knowledge.py`

```python
"""
Load pension knowledge from structured Python module to database with embeddings.
"""

import sys
from pathlib import Path
from uuid import uuid4

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.knowledge.pension_knowledge import PENSION_KNOWLEDGE
from guidance_agent.core.database import get_session, PensionKnowledge
from guidance_agent.retrieval.embeddings import embed

def load_pension_knowledge_to_db():
    """Load structured pension knowledge into database with embeddings."""
    session = get_session()
    count = 0

    # Process pension types
    for pension_type, info in PENSION_KNOWLEDGE["pension_types"].items():
        content = f"{pension_type}: {info['description']}"
        if 'fca_considerations' in info:
            content += f" FCA considerations: {info['fca_considerations']}"

        entry = PensionKnowledge(
            id=uuid4(),
            content=content,
            category="pension_type",
            subcategory=pension_type,
            embedding=embed(content),
            metadata=info
        )
        session.add(entry)
        count += 1
        print(f"Added pension type: {pension_type}")

    # Process regulations
    for regulation_name, info in PENSION_KNOWLEDGE["regulations"].items():
        if isinstance(info, dict):
            content = f"{regulation_name}: "
            content += " ".join([f"{k}={v}" for k, v in info.items() if isinstance(v, (str, int, float))])

            entry = PensionKnowledge(
                id=uuid4(),
                content=content,
                category="regulation",
                subcategory=regulation_name,
                embedding=embed(content),
                metadata=info
            )
            session.add(entry)
            count += 1
            print(f"Added regulation: {regulation_name}")

    # Process typical scenarios
    for scenario_name, info in PENSION_KNOWLEDGE["typical_scenarios"].items():
        content = f"Typical scenario for {scenario_name}: "
        content += f"Age {info['age_range']}, "
        content += f"typically {info['pension_count_range'][0]}-{info['pension_count_range'][1]} pensions, "
        content += f"total value £{info['total_value_range'][0]:,}-£{info['total_value_range'][1]:,}. "
        content += f"Common goals: {', '.join(info['common_goals'])}"

        entry = PensionKnowledge(
            id=uuid4(),
            content=content,
            category="typical_scenario",
            subcategory=scenario_name,
            embedding=embed(content),
            metadata=info
        )
        session.add(entry)
        count += 1
        print(f"Added scenario: {scenario_name}")

    session.commit()
    print(f"\n✅ Successfully loaded {count} pension knowledge entries")

if __name__ == "__main__":
    load_pension_knowledge_to_db()
```

**Usage**:
```bash
uv run python scripts/load_pension_knowledge.py
```

#### 3. Bootstrap FCA Compliance Knowledge

**File**: `data/knowledge/fca_compliance_principles.yaml` (create this first)

```yaml
guidance_boundary:
  - principle: "Guidance helps customers understand their options; advice recommends specific actions"
    content: "The FCA defines guidance as helping customers understand their options without recommending a specific course of action. Guidance is informational and educational. Advice, by contrast, involves recommending specific actions based on the customer's circumstances."
    examples_compliant:
      - "You could consider consolidating your pensions to reduce fees"
      - "Some people in your situation choose to access their pension at 55"
      - "Options available include taking a lump sum, buying an annuity, or flexi-access drawdown"
      - "One thing to think about is whether the fees you're paying are value for money"
    examples_non_compliant:
      - "You should consolidate your pensions"
      - "I recommend taking your pension at 55"
      - "The best option for you is to take a lump sum"
      - "You need to transfer out of that expensive pension"

prohibited_language:
  - principle: "Avoid directive language that crosses into advice territory"
    prohibited_phrases:
      - "you should"
      - "you shouldn't"
      - "you must"
      - "you need to"
      - "I recommend"
      - "I suggest you"
      - "the best option for you"
      - "you ought to"
    permitted_phrases:
      - "you could consider"
      - "some people choose to"
      - "options available include"
      - "one thing to think about"
      - "you might want to consider"
      - "it's worth thinking about"
      - "many people find that"

db_warnings:
  - principle: "DB transfers >£30k require regulated advice warning BEFORE discussion"
    fca_reference: "COBS 19.1.6"
    mandatory: true
    template: |
      I can see you have a defined benefit pension [from {employer}]. This type of pension
      provides valuable guarantees - a fixed income of [£{amount}/month] for life [starting
      at {age}], [inflation protection]. Most people would be worse off transferring out of
      a DB pension because they lose these guarantees.

      If you're considering transferring this pension (worth more than £30,000), FCA rules
      require you to get regulated financial advice from an authorized adviser before making
      any decision. I can help you understand your other pensions, but for decisions about
      the DB pension, you'd need to speak with a regulated adviser.

    key_elements:
      - Identify DB pension type
      - Specify guaranteed income amount
      - State "most people worse off"
      - Mention £30k threshold
      - State FCA requirement for regulated advice
      - Offer to help with other pensions
      - Signpost to regulated adviser for DB decisions

risk_disclosure:
  - principle: "Clearly explain risks associated with pension decisions"
    content: "Customers must understand the risks of their options. This includes investment risk, longevity risk, inflation risk, and the risk of running out of money."
    required_elements:
      - "Identify specific risks relevant to customer's situation"
      - "Explain risks in plain language appropriate to literacy level"
      - "Provide concrete examples of what could go wrong"
      - "Ensure customer demonstrates understanding before proceeding"
    examples:
      - "One risk with taking your pension as cash is that you might spend it quickly and have less for later in retirement"
      - "If you invest your pension pot, its value can go down as well as up, meaning you might have less than you started with"
      - "Consolidating means putting all your eggs in one basket - if that provider has problems, all your pension could be affected"

understanding_verification:
  - principle: "Check customer understanding throughout the conversation"
    content: "Don't assume customer understands. Ask open-ended questions to verify comprehension of key concepts and risks."
    techniques:
      - "Ask customer to explain concept back in their own words"
      - "Use open questions: 'What are your thoughts on...?'"
      - "Check understanding of risks: 'What concerns do you have about...?'"
      - "Verify next steps: 'What would you like to do next?'"
      - "Avoid yes/no questions that don't test understanding"
    examples:
      - "Just to make sure I've explained this clearly, could you tell me in your own words what the main difference is between your DB and DC pensions?"
      - "What concerns do you have about consolidating your pensions?"
      - "Based on what we've discussed, what are you thinking about next steps?"

signposting:
  - principle: "Signpost to regulated advice when approaching the boundary"
    triggers:
      - "Customer asking for recommendation on specific action"
      - "Complex situation requiring personal recommendation"
      - "DB pension transfer consideration (>£30k)"
      - "Safeguarded benefits at risk"
      - "Customer explicitly requests advice"
    template: |
      Based on what you've told me, this is a decision that needs regulated financial
      advice rather than guidance. A regulated adviser can make a personal recommendation
      based on your full circumstances. I can point you to [MoneyHelper's adviser directory /
      FCA register] to find an authorized adviser.
```

**File**: `scripts/bootstrap_fca_knowledge.py`

```python
"""
Bootstrap FCA compliance knowledge from curated YAML file.
"""

import sys
import yaml
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.core.database import get_session, FCAKnowledge
from guidance_agent.retrieval.embeddings import embed

def load_fca_compliance_knowledge():
    """Load FCA compliance principles from YAML file into database."""

    # Load YAML file
    yaml_path = Path(__file__).parent.parent / "data" / "knowledge" / "fca_compliance_principles.yaml"
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        print("Please create the FCA compliance principles YAML file first")
        return

    with open(yaml_path) as f:
        principles = yaml.safe_load(f)

    session = get_session()
    count = 0

    # Process each category
    for category, items in principles.items():
        print(f"\nProcessing category: {category}")

        for item in items:
            principle_text = item.get('principle', '')
            content_text = item.get('content', principle_text)

            # Main principle entry
            entry = FCAKnowledge(
                id=uuid4(),
                content=f"{principle_text}. {content_text}",
                source="FCA_Curated_Principles",
                category=category,
                embedding=embed(f"{principle_text}. {content_text}"),
                metadata={
                    "principle": principle_text,
                    "fca_reference": item.get('fca_reference'),
                    "mandatory": item.get('mandatory', False)
                }
            )
            session.add(entry)
            count += 1

            # Add examples as separate entries for better retrieval
            if 'examples_compliant' in item:
                for example in item['examples_compliant']:
                    example_entry = FCAKnowledge(
                        id=uuid4(),
                        content=f"Compliant example: {example}. Context: {principle_text}",
                        source="FCA_Curated_Principles",
                        category=f"{category}_examples",
                        embedding=embed(example),
                        metadata={
                            "example_type": "compliant",
                            "parent_principle": principle_text
                        }
                    )
                    session.add(example_entry)
                    count += 1

            if 'examples_non_compliant' in item:
                for example in item['examples_non_compliant']:
                    example_entry = FCAKnowledge(
                        id=uuid4(),
                        content=f"Non-compliant example: {example}. Reason: {principle_text}",
                        source="FCA_Curated_Principles",
                        category=f"{category}_examples",
                        embedding=embed(example),
                        metadata={
                            "example_type": "non_compliant",
                            "parent_principle": principle_text
                        }
                    )
                    session.add(example_entry)
                    count += 1

            # Add template if present
            if 'template' in item:
                template_entry = FCAKnowledge(
                    id=uuid4(),
                    content=f"Template for {category}: {item['template']}",
                    source="FCA_Curated_Principles",
                    category=f"{category}_templates",
                    embedding=embed(item['template']),
                    metadata={
                        "template_type": category,
                        "key_elements": item.get('key_elements', [])
                    }
                )
                session.add(template_entry)
                count += 1

        print(f"  ✓ Added {len(items)} principles for {category}")

    session.commit()
    print(f"\n✅ Successfully loaded {count} FCA knowledge entries")

if __name__ == "__main__":
    load_fca_compliance_knowledge()
```

**Usage**:
```bash
# First create the YAML file, then run:
uv run python scripts/bootstrap_fca_knowledge.py
```

#### 4. Generate Seed Cases (LLM-Assisted)

**File**: `scripts/generate_seed_cases.py`

```python
"""
Generate seed cases using LLM assistance.
"""

import sys
import json
from pathlib import Path
from uuid import uuid4
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from litellm import completion
import os
from guidance_agent.core.database import get_session, Case
from guidance_agent.core.types import TaskType
from guidance_agent.retrieval.embeddings import embed

# Scenario templates
SCENARIO_TEMPLATES = [
    {
        "type": TaskType.DEFINED_BENEFIT_TRANSFER.value,
        "description": "DB pension transfer consideration",
        "count": 5,
        "variations": [
            {"age": 58, "sector": "local_government", "transfer_value": 35000},
            {"age": 52, "sector": "nhs", "transfer_value": 120000},
            {"age": 48, "sector": "teaching", "transfer_value": 45000},
            {"age": 60, "sector": "civil_service", "transfer_value": 280000},
            {"age": 55, "sector": "police", "transfer_value": 95000},
        ]
    },
    {
        "type": TaskType.CONSOLIDATION.value,
        "description": "Small pot consolidation",
        "count": 5,
        "variations": [
            {"age": 35, "pots": 3, "total_value": 18000, "literacy": "low"},
            {"age": 42, "pots": 5, "total_value": 45000, "literacy": "medium"},
            {"age": 28, "pots": 2, "total_value": 8000, "literacy": "high"},
            {"age": 50, "pots": 7, "total_value": 120000, "literacy": "medium"},
            {"age": 39, "pots": 4, "total_value": 32000, "literacy": "low"},
        ]
    },
    {
        "type": TaskType.FEE_REDUCTION.value,
        "description": "Fee reduction inquiry",
        "count": 5,
        "variations": [
            {"age": 45, "current_fee": 0.015, "pot_value": 80000},
            {"age": 52, "current_fee": 0.02, "pot_value": 150000},
            {"age": 38, "current_fee": 0.012, "pot_value": 35000},
            {"age": 60, "current_fee": 0.018, "pot_value": 220000},
            {"age": 33, "current_fee": 0.01, "pot_value": 12000},
        ]
    },
    {
        "type": TaskType.RISK_ASSESSMENT.value,
        "description": "Investment risk assessment",
        "count": 5,
        "variations": [
            {"age": 30, "risk_appetite": "low", "pot_value": 15000},
            {"age": 55, "risk_appetite": "medium", "pot_value": 180000},
            {"age": 42, "risk_appetite": "high", "pot_value": 95000},
            {"age": 62, "risk_appetite": "low", "pot_value": 250000},
            {"age": 48, "risk_appetite": "medium", "pot_value": 120000},
        ]
    },
]

def generate_case_with_llm(scenario_type: str, variation: Dict) -> Dict:
    """Use LLM to generate a realistic case."""

    prompt = f"""Generate a realistic UK pension guidance consultation case.

Scenario Type: {scenario_type}
Customer Details: {json.dumps(variation, indent=2)}

Generate a JSON response with:
1. "customer_situation": Detailed description of customer's pension portfolio and specific inquiry (2-3 sentences)
2. "guidance_provided": FCA-compliant guidance response from advisor (3-4 sentences, use guidance-appropriate language)
3. "reasoning": Why this guidance approach was chosen (1-2 sentences)

Requirements:
- Guidance must stay within FCA boundary (no advice, no "should" or "recommend")
- Use appropriate language for literacy level if specified
- Include required warnings for DB pensions >£30k
- Demonstrate understanding verification
- Show balanced discussion of options

Return ONLY valid JSON in this format:
{{
  "customer_situation": "...",
  "guidance_provided": "...",
  "reasoning": "..."
}}
"""

    response = completion(
        model=os.getenv("LITELLM_MODEL_ADVISOR", "gpt-4o"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    # Extract JSON from response (handle markdown code blocks)
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    return json.loads(content)

def validate_case_compliance(case_data: Dict, scenario_type: str) -> bool:
    """Validate that generated case is FCA compliant."""

    guidance = case_data.get("guidance_provided", "")

    # Check for prohibited language
    prohibited = ["you should", "i recommend", "you must", "you need to", "best for you"]
    for phrase in prohibited:
        if phrase in guidance.lower():
            print(f"  ❌ Found prohibited phrase: '{phrase}'")
            return False

    # Check DB warning for DB transfer scenarios
    if scenario_type == TaskType.DEFINED_BENEFIT_TRANSFER.value:
        required_elements = ["defined benefit", "guaranteed", "£30", "regulated", "advice"]
        missing = [elem for elem in required_elements if elem not in guidance.lower()]
        if missing:
            print(f"  ❌ Missing DB warning elements: {missing}")
            return False

    print("  ✅ Compliance check passed")
    return True

def generate_seed_cases():
    """Generate all seed cases using LLM."""

    session = get_session()
    total_generated = 0

    for scenario in SCENARIO_TEMPLATES:
        scenario_type = scenario["type"]
        print(f"\n{'='*60}")
        print(f"Generating {scenario['count']} cases for: {scenario['description']}")
        print(f"{'='*60}")

        for i, variation in enumerate(scenario["variations"][:scenario["count"]], 1):
            print(f"\nCase {i}/{scenario['count']} - Variation: {variation}")

            # Generate case with LLM
            try:
                case_data = generate_case_with_llm(scenario_type, variation)
                print(f"  Generated case")

                # Validate compliance
                if not validate_case_compliance(case_data, scenario_type):
                    print(f"  ⚠️  Skipping non-compliant case")
                    continue

                # Create Case database entry
                case = Case(
                    id=uuid4(),
                    task_type=scenario_type,
                    customer_situation=case_data["customer_situation"],
                    guidance_provided=case_data["guidance_provided"],
                    outcome={
                        "successful": True,
                        "fca_compliant": True,
                        "reasoning": case_data["reasoning"],
                        "source": "llm_generated_seed"
                    },
                    embedding=embed(case_data["customer_situation"]),
                    metadata={
                        "source": "seed_generation",
                        "scenario_type": scenario_type,
                        "variation": variation,
                        "validated": True
                    }
                )

                session.add(case)
                total_generated += 1
                print(f"  ✅ Added to database (total: {total_generated})")

            except Exception as e:
                print(f"  ❌ Error generating case: {e}")
                continue

    session.commit()
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {total_generated} seed cases")
    print(f"{'='*60}")

if __name__ == "__main__":
    print("Starting seed case generation with LLM assistance...\n")
    generate_seed_cases()
```

**Usage**:
```bash
uv run python scripts/generate_seed_cases.py
```

#### 5. Generate Seed Rules (LLM-Assisted)

**File**: `scripts/generate_seed_rules.py`

```python
"""
Generate seed rules using LLM assistance based on FCA requirements.
"""

import sys
import json
from pathlib import Path
from uuid import uuid4
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from litellm import completion
import os
from guidance_agent.core.database import get_session, Rule
from guidance_agent.retrieval.embeddings import embed

# Rule templates
RULE_TEMPLATES = [
    {
        "domain": "regulatory_compliance",
        "fca_requirement": "DB pension transfers >£30k require regulated advice warning",
        "confidence": 1.0,
        "mandatory": True
    },
    {
        "domain": "regulatory_compliance",
        "fca_requirement": "Prohibited advice language must be avoided to maintain guidance boundary",
        "confidence": 1.0,
        "mandatory": True
    },
    {
        "domain": "regulatory_compliance",
        "fca_requirement": "Risk disclosure must be clear and appropriate to customer's literacy level",
        "confidence": 1.0,
        "mandatory": True
    },
    {
        "domain": "regulatory_compliance",
        "fca_requirement": "Customer understanding must be verified throughout consultation",
        "confidence": 0.9,
        "mandatory": False
    },
    {
        "domain": "regulatory_compliance",
        "fca_requirement": "Signpost to regulated adviser when customer requests personal recommendation",
        "confidence": 1.0,
        "mandatory": True
    },
    {
        "domain": "communication_best_practices",
        "fca_requirement": "Use simple language and analogies for customers with low financial literacy",
        "confidence": 0.85,
        "mandatory": False
    },
    {
        "domain": "communication_best_practices",
        "fca_requirement": "Break complex topics into smaller chunks for better comprehension",
        "confidence": 0.8,
        "mandatory": False
    },
    {
        "domain": "communication_best_practices",
        "fca_requirement": "Use open-ended questions to check understanding rather than yes/no questions",
        "confidence": 0.85,
        "mandatory": False
    },
]

def generate_rule_with_llm(domain: str, fca_requirement: str, confidence: float) -> str:
    """Use LLM to generate a principle statement."""

    prompt = f"""Generate a clear, actionable guidance principle for UK pension advisors.

Domain: {domain}
Based on FCA Requirement: {fca_requirement}
Confidence Level: {confidence}

Generate a principle statement in this format:
"[WHEN condition], [ALWAYS/SHOULD] [action], because [reasoning]"

The principle must:
1. Specify WHEN it applies (triggering conditions)
2. State WHAT action to take (use ALWAYS for mandatory rules, SHOULD for best practices)
3. Explain WHY it's important (consequences or reasoning)

Example format:
"When customer has DB pension with transfer value >£30,000, ALWAYS include warning about valuable guarantees and requirement for regulated financial advice BEFORE any discussion of transfer options, because FCA mandates this protection and most people lose out by transferring from DB to DC pensions."

Generate ONLY the principle statement, no extra text:
"""

    response = completion(
        model=os.getenv("LITELLM_MODEL_ADVISOR", "claude-sonnet-4.5"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # Lower temperature for more consistent format
    )

    principle = response.choices[0].message.content.strip()

    # Remove quotes if LLM added them
    if principle.startswith('"') and principle.endswith('"'):
        principle = principle[1:-1]

    return principle

def generate_seed_rules():
    """Generate all seed rules using LLM."""

    session = get_session()
    total_generated = 0

    print("Generating seed rules with LLM assistance...\n")

    for i, template in enumerate(RULE_TEMPLATES, 1):
        print(f"\nRule {i}/{len(RULE_TEMPLATES)}")
        print(f"Domain: {template['domain']}")
        print(f"Requirement: {template['fca_requirement']}")
        print(f"Confidence: {template['confidence']}")

        try:
            # Generate principle with LLM
            principle = generate_rule_with_llm(
                template["domain"],
                template["fca_requirement"],
                template["confidence"]
            )

            print(f"Generated: {principle[:100]}...")

            # Create Rule database entry
            rule = Rule(
                id=uuid4(),
                principle=principle,
                domain=template["domain"],
                confidence=template["confidence"],
                supporting_evidence=[],  # Will be populated during training
                embedding=embed(principle),
                metadata={
                    "source": "seed_generation",
                    "fca_requirement": template["fca_requirement"],
                    "mandatory": template["mandatory"]
                }
            )

            session.add(rule)
            total_generated += 1
            print(f"✅ Added to database (total: {total_generated})")

        except Exception as e:
            print(f"❌ Error generating rule: {e}")
            continue

    session.commit()
    print(f"\n{'='*60}")
    print(f"✅ Successfully generated {total_generated} seed rules")
    print(f"{'='*60}")

if __name__ == "__main__":
    generate_seed_rules()
```

**Usage**:
```bash
uv run python scripts/generate_seed_rules.py
```

#### 6. Master Bootstrap Script

**File**: `scripts/bootstrap_all_knowledge.py`

```python
"""
Master script to bootstrap all knowledge bases in sequence.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_script(script_name: str, description: str):
    """Run a bootstrap script and report status."""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}")

    script_path = Path(__file__).parent / script_name

    try:
        # Execute script in same Python process
        with open(script_path) as f:
            code = compile(f.read(), script_path, 'exec')
            exec(code, {'__name__': '__main__', '__file__': str(script_path)})
        print(f"✅ {description} - COMPLETED\n")
        return True
    except FileNotFoundError:
        print(f"⚠️  {script_name} not found - SKIPPED\n")
        return False
    except Exception as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}\n")
        return False

def main():
    """Bootstrap all knowledge bases."""

    print("\n" + "="*70)
    print("  KNOWLEDGE BASE BOOTSTRAP")
    print("  Comprehensive initialization of all knowledge bases")
    print("="*70)

    results = {}

    # Phase 1: Pension Knowledge
    results['pension'] = run_script(
        'load_pension_knowledge.py',
        'Phase 1: Loading Pension Domain Knowledge'
    )

    # Phase 2: FCA Compliance Knowledge
    results['fca'] = run_script(
        'bootstrap_fca_knowledge.py',
        'Phase 2: Loading FCA Compliance Knowledge'
    )

    # Phase 3: Seed Cases
    results['cases'] = run_script(
        'generate_seed_cases.py',
        'Phase 3: Generating Seed Cases (LLM-assisted)'
    )

    # Phase 4: Seed Rules
    results['rules'] = run_script(
        'generate_seed_rules.py',
        'Phase 4: Generating Seed Rules (LLM-assisted)'
    )

    # Summary
    print("\n" + "="*70)
    print("  BOOTSTRAP SUMMARY")
    print("="*70)

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for name, success in results.items():
        status = "✅ COMPLETED" if success else "❌ FAILED"
        print(f"  {name.title()}: {status}")

    print(f"\n  Overall: {success_count}/{total_count} completed successfully")

    if success_count == total_count:
        print("\n  🎉 All knowledge bases bootstrapped successfully!")
        print("  Ready to proceed with Phase 3 (Advisor Agent)")
    else:
        print("\n  ⚠️  Some knowledge bases failed to bootstrap")
        print("  Review errors above and re-run individual scripts")

    print("="*70 + "\n")

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
# Run complete bootstrap
uv run python scripts/bootstrap_all_knowledge.py

# Or run individual scripts
uv run python scripts/load_pension_knowledge.py
uv run python scripts/bootstrap_fca_knowledge.py
uv run python scripts/generate_seed_cases.py
uv run python scripts/generate_seed_rules.py
```

## Bootstrap Sequence

### Recommended Implementation Order

```bash
# Step 1: Database Migrations (if needed)
alembic revision --autogenerate -m "Add FCA and pension knowledge tables"
alembic upgrade head

# Step 2: Create Source Data Files
# - Create src/guidance_agent/knowledge/pension_knowledge.py (structured Python)
# - Create data/knowledge/fca_compliance_principles.yaml (curated FCA principles)

# Step 3: Run Bootstrap Scripts
uv run python scripts/load_pension_knowledge.py
uv run python scripts/bootstrap_fca_knowledge.py
uv run python scripts/generate_seed_cases.py
uv run python scripts/generate_seed_rules.py

# Or run all at once:
uv run python scripts/bootstrap_all_knowledge.py

# Step 4: Verify Knowledge Bases
uv run python scripts/verify_knowledge_bases.py
```

### Verification Script

**File**: `scripts/verify_knowledge_bases.py`

```python
"""
Verify all knowledge bases are properly populated.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.core.database import get_session, FCAKnowledge, PensionKnowledge, Case, Rule
from sqlalchemy import func

def verify_knowledge_bases():
    """Verify all knowledge bases have data."""

    session = get_session()

    print("\n" + "="*60)
    print("  KNOWLEDGE BASE VERIFICATION")
    print("="*60 + "\n")

    # Check FCA Knowledge
    fca_count = session.query(func.count(FCAKnowledge.id)).scalar()
    print(f"FCA Compliance Knowledge: {fca_count} entries")
    if fca_count == 0:
        print("  ⚠️  Warning: No FCA knowledge entries found")

    # Check Pension Knowledge
    pension_count = session.query(func.count(PensionKnowledge.id)).scalar()
    print(f"Pension Domain Knowledge: {pension_count} entries")
    if pension_count == 0:
        print("  ⚠️  Warning: No pension knowledge entries found")

    # Check Cases
    case_count = session.query(func.count(Case.id)).scalar()
    print(f"Case Base: {case_count} cases")
    if case_count == 0:
        print("  ⚠️  Warning: No seed cases found")
    elif case_count < 20:
        print(f"  ⚠️  Warning: Only {case_count} cases (recommended: 20-50)")

    # Check Rules
    rule_count = session.query(func.count(Rule.id)).scalar()
    print(f"Rules Base: {rule_count} rules")
    if rule_count == 0:
        print("  ⚠️  Warning: No seed rules found")
    elif rule_count < 5:
        print(f"  ⚠️  Warning: Only {rule_count} rules (recommended: 5-10)")

    # Overall status
    print("\n" + "="*60)
    all_populated = all([fca_count > 0, pension_count > 0, case_count >= 20, rule_count >= 5])

    if all_populated:
        print("  ✅ All knowledge bases properly populated")
        print("  Ready for Phase 3 (Advisor Agent) implementation")
    else:
        print("  ⚠️  Some knowledge bases need attention")
        print("  Review warnings above and re-run bootstrap scripts")

    print("="*60 + "\n")

if __name__ == "__main__":
    verify_knowledge_bases()
```

## Validation and Quality Control

### Automated Validation

Each bootstrap script should include validation:

1. **FCA Knowledge**: Check for required categories (guidance_boundary, db_warnings, etc.)
2. **Pension Knowledge**: Validate age ranges, fee ranges, regulatory thresholds
3. **Cases**: Compliance validation (no prohibited language, required warnings present)
4. **Rules**: Format validation (WHEN-ALWAYS/SHOULD-BECAUSE structure)

### Manual Review

After LLM-assisted generation:

1. Review 10-20% of generated cases for quality and realism
2. Review all generated rules for clarity and accuracy
3. Test retrieval queries to ensure relevant results returned
4. Verify embeddings are being created correctly

### Iteration

If quality issues found:

1. Adjust LLM prompts for better generation
2. Add more specific requirements to templates
3. Increase validation strictness
4. Re-generate failed items

## Timeline and Effort Estimates

**Total Estimated Time**: 5-8 days

### Day 1-2: Infrastructure and Static Knowledge
- Create database migrations (2-3 hours)
- Create `pension_knowledge.py` module (4-6 hours)
- Create `fca_compliance_principles.yaml` (4-6 hours)
- Test database schema and models (2 hours)

### Day 3-4: Bootstrap Scripts
- Write `load_pension_knowledge.py` (2-3 hours)
- Write `bootstrap_fca_knowledge.py` (2-3 hours)
- Write `generate_seed_cases.py` (4-6 hours)
- Write `generate_seed_rules.py` (3-4 hours)

### Day 5: LLM Generation and Validation
- Run seed case generation (2-3 hours including LLM time)
- Run seed rule generation (1-2 hours)
- Manual review and quality control (4-6 hours)
- Iterate on failed items (2-4 hours)

### Day 6-7: Integration and Testing
- Create master bootstrap script (1-2 hours)
- Create verification script (1-2 hours)
- Full end-to-end bootstrap test (2-3 hours)
- Documentation and cleanup (2-3 hours)

### Day 8: Buffer
- Address any issues discovered
- Final quality review
- Prepare for Phase 3 handoff

## Cost Estimates

### LLM API Costs (LiteLLM with 2025 Models)

**Seed Case Generation** (25 cases using GPT-4o):
- Generation: 25 cases × $0.015 = $0.38
- Validation retries (20% failure rate): 5 cases × $0.015 = $0.08
- **Total**: ~$0.46

**Seed Rule Generation** (8 rules using Claude 4.5 Sonnet):
- Generation: 8 rules × $0.012 = $0.10
- **Total**: ~$0.10

**Embeddings** (all knowledge entries):
- FCA knowledge: ~100 entries × $0.00002 = $0.002
- Pension knowledge: ~50 entries × $0.00002 = $0.001
- Cases: 25 × $0.00002 = $0.0005
- Rules: 8 × $0.00002 = $0.00016
- **Total**: ~$0.004

**Overall LLM Cost**: ~$0.56 (negligible - 55% cheaper than 2024 pricing)

### Human Effort Cost

At $100/hour (developer rate):
- 5 days × 8 hours = 40 hours
- 40 hours × $100 = **$4,000**

**Total Estimated Cost**: ~$4,000 (dominated by human effort)

## Success Criteria

### Phase Completion Criteria

Bootstrap phase is complete when:

1. ✅ All 4 knowledge bases have data populated
2. ✅ FCA knowledge covers all critical categories (guidance_boundary, db_warnings, risk_disclosure, etc.)
3. ✅ Pension knowledge includes all pension types, regulations, and scenarios
4. ✅ Case base has 20-50 diverse, FCA-compliant seed cases
5. ✅ Rules base has 5-10 critical compliance rules with confidence scores
6. ✅ All entries have vector embeddings generated
7. ✅ Verification script passes all checks
8. ✅ Test retrieval queries return relevant results

### Quality Criteria

- **FCA Knowledge**: 90%+ coverage of critical compliance topics
- **Pension Knowledge**: Accurate regulatory thresholds and realistic scenarios
- **Cases**: 100% FCA compliance (no prohibited language, required warnings present)
- **Rules**: Clear WHEN-ALWAYS/SHOULD-BECAUSE structure, actionable principles
- **Embeddings**: Semantic search returns relevant items (manual spot check)

## Next Steps After Bootstrap

Once knowledge bases are populated:

1. ✅ Verify retrieval system works correctly
2. ✅ Proceed to **Phase 3: Advisor Agent** implementation
3. ✅ Test advisor agent can retrieve and use knowledge effectively
4. ✅ Begin virtual training (Phase 5) to grow Case and Rules bases

The bootstrapped knowledge bases provide the foundation for the advisor agent's RAG system and enable the learning mechanisms to function from day 1.

---

## Appendix: File Structure

```
guidance-agent/
├── src/guidance_agent/
│   ├── knowledge/
│   │   └── pension_knowledge.py          # Structured pension domain knowledge
│   └── core/
│       └── database.py                     # + FCAKnowledge, PensionKnowledge models
│
├── data/knowledge/
│   └── fca_compliance_principles.yaml      # Curated FCA principles
│
├── scripts/
│   ├── load_pension_knowledge.py           # Load pension knowledge to DB
│   ├── bootstrap_fca_knowledge.py          # Load FCA knowledge to DB
│   ├── generate_seed_cases.py              # LLM-generate seed cases
│   ├── generate_seed_rules.py              # LLM-generate seed rules
│   ├── bootstrap_all_knowledge.py          # Master orchestration script
│   └── verify_knowledge_bases.py           # Verification script
│
└── alembic/versions/
    ├── xxx_add_fca_knowledge_table.py      # Migration for FCA knowledge
    └── xxx_add_pension_knowledge_table.py  # Migration for pension knowledge
```

## References

- Implementation Plan: `specs/implementation-plan.md`
- Advisor Agent Spec: `specs/advisor-agent.md`
- Learning System Spec: `specs/learning-system.md`
- FCA Handbook: https://www.handbook.fca.org.uk/
- GOV.UK Pension Guidance: https://www.gov.uk/pension-types
- MoneyHelper: https://www.moneyhelper.org.uk/en/pensions-and-retirement
