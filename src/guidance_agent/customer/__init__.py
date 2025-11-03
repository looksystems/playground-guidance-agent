"""Customer simulation module for virtual training."""

from guidance_agent.customer.generator import (
    generate_demographics,
    generate_financial_situation,
    generate_pension_pots,
    generate_goals_and_inquiry,
    generate_customer_profile,
    validate_profile,
)
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.customer.simulator import simulate_outcome

__all__ = [
    "generate_demographics",
    "generate_financial_situation",
    "generate_pension_pots",
    "generate_goals_and_inquiry",
    "generate_customer_profile",
    "validate_profile",
    "CustomerAgent",
    "simulate_outcome",
]
