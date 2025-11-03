"""Event orchestration for multi-turn consultations.

This module manages the flow of advisor-customer consultations, handling
multi-turn conversations, completion detection, and outcome simulation.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

from guidance_agent.advisor.agent import AdvisorAgent
from guidance_agent.customer.agent import CustomerAgent
from guidance_agent.customer.simulator import simulate_outcome
from guidance_agent.core.types import OutcomeResult


@dataclass
class ConsultationResult:
    """Result of a complete consultation.

    Attributes:
        conversation_history: Full conversation between advisor and customer
        turn_count: Number of advisor turns (not including initial inquiry)
        completed_naturally: Whether conversation ended naturally vs max turns
        outcome: Simulated outcome of the consultation
    """

    conversation_history: List[Dict[str, str]]
    turn_count: int
    completed_naturally: bool
    outcome: OutcomeResult


class EventOrchestrator:
    """Orchestrates multi-turn consultations between advisor and customer.

    The orchestrator manages the conversation flow:
    1. Customer presents initial inquiry
    2. Advisor provides guidance
    3. Customer responds (comprehension-based)
    4. Repeat until completion or max turns
    5. Simulate outcome

    Completion is detected via:
    - Customer satisfaction signals ("thank you", "that's all")
    - Advisor summary and closure
    - Max turn limit reached

    Example:
        >>> orchestrator = EventOrchestrator(max_turns=20)
        >>> result = orchestrator.run_consultation(advisor, customer)
        >>> print(f"Conversation had {result.turn_count} turns")
        >>> print(f"Outcome: {result.outcome.successful}")
    """

    def __init__(self, max_turns: int = 20):
        """Initialize event orchestrator.

        Args:
            max_turns: Maximum number of advisor turns before forced completion.
                Default 20 turns is typically sufficient for most consultations.
        """
        self.max_turns = max_turns

    def run_consultation(
        self,
        advisor: AdvisorAgent,
        customer: CustomerAgent,
    ) -> ConsultationResult:
        """Run a complete consultation between advisor and customer.

        Args:
            advisor: AdvisorAgent instance
            customer: CustomerAgent instance

        Returns:
            ConsultationResult with conversation history and outcome

        Example:
            >>> result = orchestrator.run_consultation(advisor, customer)
            >>> if result.outcome.successful:
            ...     print("Consultation was successful!")
        """
        conversation_history: List[Dict[str, str]] = []

        # 1. Customer presents inquiry
        inquiry = customer.present_inquiry()
        conversation_history.append({"role": "customer", "content": inquiry})

        turn_count = 0
        completed_naturally = False

        # 2. Multi-turn conversation
        while turn_count < self.max_turns:
            # Advisor provides guidance
            guidance = advisor.provide_guidance(
                customer.profile, conversation_history
            )
            conversation_history.append({"role": "advisor", "content": guidance})
            turn_count += 1

            # Customer responds
            response = customer.respond(guidance, conversation_history)
            conversation_history.append({"role": "customer", "content": response})

            # Check for completion signals
            if self._is_completion_signal(response):
                completed_naturally = True
                break

        # 3. Simulate outcome
        outcome = simulate_outcome(customer, conversation_history)

        return ConsultationResult(
            conversation_history=conversation_history,
            turn_count=turn_count,
            completed_naturally=completed_naturally,
            outcome=outcome,
        )

    def _is_completion_signal(self, message: str) -> bool:
        """Detect if customer message signals consultation completion.

        Args:
            message: Customer's message

        Returns:
            True if message indicates completion

        Completion signals include:
        - Thank you phrases ("thank you", "thanks", "appreciate")
        - Satisfaction expressions ("understand now", "makes sense")
        - Closure phrases ("that's all", "no more questions")
        """
        message_lower = message.lower()

        # Thank you signals
        thank_you_phrases = [
            "thank you",
            "thanks",
            "appreciate",
            "grateful",
        ]

        # Satisfaction signals
        satisfaction_phrases = [
            "understand now",
            "makes sense",
            "that helps",
            "that's helpful",
            "got it",
        ]

        # Closure signals
        closure_phrases = [
            "that's all",
            "that's everything",
            "no more questions",
            "nothing else",
            "i'm good",
            "all i needed",
        ]

        # Check for any completion signal
        for phrase in thank_you_phrases + satisfaction_phrases + closure_phrases:
            if phrase in message_lower:
                return True

        return False
