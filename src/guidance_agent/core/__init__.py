"""Core abstractions for the guidance agent system."""

from guidance_agent.core.agent import BaseAgent, AgentConfig
from guidance_agent.core.memory import MemoryNode, MemoryStream
from guidance_agent.core.types import (
    AdvisorProfile,
    Case,
    CustomerDemographics,
    CustomerProfile,
    FinancialSituation,
    GuidanceRule,
    MemoryType,
    OutcomeResult,
    OutcomeStatus,
    PensionPot,
    RetrievedContext,
    TaskType,
)

__all__ = [
    # Agent
    "BaseAgent",
    "AgentConfig",
    # Memory
    "MemoryNode",
    "MemoryStream",
    # Types
    "AdvisorProfile",
    "Case",
    "CustomerDemographics",
    "CustomerProfile",
    "FinancialSituation",
    "GuidanceRule",
    "MemoryType",
    "OutcomeResult",
    "OutcomeStatus",
    "PensionPot",
    "RetrievedContext",
    "TaskType",
]
