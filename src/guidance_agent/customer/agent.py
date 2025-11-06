"""Customer agent for simulating customer behaviour in virtual training.

This module implements the CustomerAgent class that simulates realistic
customer responses and comprehension during pension guidance consultations.
"""

import os
import json
from typing import List, Dict
from litellm import completion

from guidance_agent.core.types import CustomerProfile
from guidance_agent.core.template_engine import render_template


class CustomerAgent:
    """Customer agent that simulates customer behaviour during guidance sessions.

    The customer agent:
    - Presents their initial inquiry
    - Simulates comprehension based on literacy level
    - Responds naturally to advisor guidance
    - Tracks understanding throughout conversation
    - Maintains conversation memory
    """

    def __init__(self, profile: CustomerProfile, model: str = None):
        """Initialize customer agent.

        Args:
            profile: Customer profile with demographics, financial situation, etc.
            model: LLM model to use (defaults to LITELLM_MODEL_CUSTOMER env var)
        """
        self.profile = profile
        self.model = model or os.getenv("LITELLM_MODEL_CUSTOMER", "gpt-4o-mini")

        # Initialize state
        self.conversation_memory: List[Dict[str, str]] = []
        self.comprehension_level = self._initialize_comprehension_level()

    def _initialize_comprehension_level(self) -> float:
        """Initialize comprehension level based on financial literacy.

        Returns:
            Initial comprehension level (0-1)
        """
        if not self.profile.demographics:
            return 0.5

        literacy_mapping = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
        }

        return literacy_mapping.get(
            self.profile.demographics.financial_literacy, 0.5
        )

    def present_inquiry(self) -> str:
        """Present initial inquiry to advisor.

        Returns:
            Customer's presenting question
        """
        return self.profile.presenting_question

    def simulate_comprehension(
        self, guidance: str, conversation_history: List[dict]
    ) -> Dict[str, any]:
        """Simulate customer comprehension of advisor guidance.

        Args:
            guidance: Guidance provided by advisor
            conversation_history: Prior conversation messages

        Returns:
            Dict with understanding_level, confusion_points, customer_feeling
        """
        prompt = render_template(
            "customer/comprehension.jinja",
            customer=self.profile,
            guidance=guidance
        )

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            result = json.loads(response.choices[0].message.content)

            # Update comprehension level based on understanding
            if result["understanding_level"] == "fully_understood":
                self.comprehension_level = min(1.0, self.comprehension_level + 0.1)
            elif result["understanding_level"] == "not_understood":
                self.comprehension_level = max(0.0, self.comprehension_level - 0.1)

            return result

        except Exception as e:
            # Fallback comprehension
            return {
                "understanding_level": "partially_understood",
                "confusion_points": [],
                "customer_feeling": "uncertain",
            }

    def respond(
        self, advisor_message: str, conversation_history: List[dict]
    ) -> str:
        """Generate customer response to advisor guidance.

        Args:
            advisor_message: Message from advisor
            conversation_history: Prior conversation messages

        Returns:
            Customer's response
        """
        # First, simulate comprehension
        comprehension = self.simulate_comprehension(
            advisor_message, conversation_history
        )

        # Build response based on comprehension
        prompt = render_template(
            "customer/response.jinja",
            customer=self.profile,
            advisor_message=advisor_message,
            comprehension=comprehension
        )

        try:
            response = completion(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
            )

            customer_response = response.choices[0].message.content.strip()

            # Update conversation memory
            self.conversation_memory.append(
                {
                    "role": "advisor",
                    "content": advisor_message,
                    "comprehension": comprehension,
                }
            )
            self.conversation_memory.append(
                {"role": "customer", "content": customer_response}
            )

            return customer_response

        except Exception as e:
            # Fallback response based on comprehension
            if comprehension["understanding_level"] == "not_understood":
                return "I'm not sure I understand. Could you explain that differently?"
            elif comprehension["understanding_level"] == "partially_understood":
                return "I think I understand most of that, but could you clarify a bit more?"
            else:
                return "Thank you, that's helpful."
