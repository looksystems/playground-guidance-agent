"""Core types and enums for the guidance agent system."""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional
from uuid import UUID, uuid4


class MemoryType(str, Enum):
    """Types of memories in the memory stream."""

    OBSERVATION = "observation"  # Direct observations from interactions
    REFLECTION = "reflection"  # Higher-level inferences
    PLAN = "plan"  # Future-oriented plans


class TaskType(str, Enum):
    """Types of pension guidance tasks."""

    GENERAL_INQUIRY = "general_inquiry"
    WITHDRAWAL_OPTIONS = "withdrawal_options"
    PENSION_TRANSFER = "pension_transfer"
    RETIREMENT_PLANNING = "retirement_planning"
    TAX_IMPLICATIONS = "tax_implications"
    DEFINED_BENEFIT_TRANSFER = "defined_benefit_transfer"
    ANNUITY_OPTIONS = "annuity_options"
    DRAWDOWN_STRATEGY = "drawdown_strategy"
    CONSOLIDATION = "consolidation"
    FEE_REDUCTION = "fee_reduction"
    RISK_ASSESSMENT = "risk_assessment"


class OutcomeStatus(str, Enum):
    """Status of consultation outcome."""

    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    NEEDS_ESCALATION = "needs_escalation"


@dataclass
class AdvisorProfile:
    """Profile configuration for an advisor agent."""

    name: str
    description: str
    specialization: Optional[str] = None
    experience_level: str = "intermediate"


@dataclass
class CustomerDemographics:
    """Customer demographic information."""

    age: int
    gender: str
    location: str
    employment_status: str
    financial_literacy: Literal["low", "medium", "high"]


@dataclass
class FinancialSituation:
    """Customer financial situation."""

    annual_income: float
    total_assets: float
    total_debt: float
    dependents: int
    risk_tolerance: Literal["low", "medium", "high"]


@dataclass
class PensionPot:
    """Information about a pension pot."""

    pot_id: str
    provider: str
    pot_type: Literal["defined_contribution", "defined_benefit", "private"]
    current_value: float
    projected_value: float
    age_accessible: int
    is_db_scheme: bool = False
    db_guaranteed_amount: Optional[float] = None


@dataclass
class CustomerProfile:
    """Complete customer profile."""

    customer_id: UUID = field(default_factory=uuid4)
    demographics: CustomerDemographics = field(default_factory=lambda: None)
    financial: FinancialSituation = field(default_factory=lambda: None)
    pensions: list[PensionPot] = field(default_factory=list)
    goals: str = ""
    presenting_question: str = ""
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OutcomeResult:
    """Result of a guidance consultation."""

    outcome_id: UUID = field(default_factory=uuid4)
    status: OutcomeStatus = OutcomeStatus.SUCCESS
    successful: bool = True

    # Customer satisfaction metrics
    customer_satisfaction: float = 0.0  # 0-10
    comprehension: float = 0.0  # 0-10
    goal_alignment: float = 0.0  # 0-10

    # Quality metrics
    risks_identified: bool = True
    guidance_appropriate: bool = True
    fca_compliant: bool = True
    understanding_checked: bool = True
    signposted_when_needed: bool = True

    # Specific checks
    has_db_pension: bool = False
    db_warning_given: bool = False

    # Reasoning
    reasoning: str = ""
    issues: list[str] = field(default_factory=list)

    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "outcome_id": str(self.outcome_id),
            "status": self.status.value,
            "successful": self.successful,
            "customer_satisfaction": self.customer_satisfaction,
            "comprehension": self.comprehension,
            "goal_alignment": self.goal_alignment,
            "risks_identified": self.risks_identified,
            "guidance_appropriate": self.guidance_appropriate,
            "fca_compliant": self.fca_compliant,
            "understanding_checked": self.understanding_checked,
            "signposted_when_needed": self.signposted_when_needed,
            "has_db_pension": self.has_db_pension,
            "db_warning_given": self.db_warning_given,
            "reasoning": self.reasoning,
            "issues": self.issues,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Case:
    """A successful consultation case for case-based retrieval."""

    case_id: str
    task_type: str
    customer_situation: str
    guidance_provided: str
    outcome_summary: str
    similarity_score: float = 0.0


@dataclass
class GuidanceRule:
    """A learned guidance rule from reflection."""

    rule_id: str
    principle: str
    domain: str
    confidence: float
    evidence_count: int = 0


@dataclass
class RetrievedContext:
    """Context retrieved for guidance generation."""

    memories: list = field(default_factory=list)
    cases: list = field(default_factory=list)
    rules: list = field(default_factory=list)
    fca_requirements: Optional[str] = None
    reasoning: str = ""
