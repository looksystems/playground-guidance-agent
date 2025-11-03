"""Virtual training environment for advisor agents.

This module provides the infrastructure for running simulated consultations
between advisor and customer agents in an accelerated time frame.
"""

from guidance_agent.environment.time_manager import VirtualTimeManager
from guidance_agent.environment.orchestrator import EventOrchestrator, ConsultationResult
from guidance_agent.environment.virtual_env import VirtualEnvironment, TrainingMetrics

__all__ = [
    "VirtualTimeManager",
    "EventOrchestrator",
    "ConsultationResult",
    "VirtualEnvironment",
    "TrainingMetrics",
]
