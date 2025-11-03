"""Customer agent for simulating customer behavior in virtual training.

This module implements the CustomerAgent class that simulates realistic
customer responses and comprehension during pension guidance consultations.
"""

import os
import json
from typing import List, Dict
from litellm import completion

from guidance_agent.core.types import CustomerProfile


class CustomerAgent:
    """Customer agent that simulates customer behavior during guidance sessions.

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
        prompt = f"""Simulate customer comprehension of pension guidance.

Customer Profile:
- Age: {self.profile.demographics.age if self.profile.demographics else 'unknown'}
- Financial literacy: {self.profile.demographics.financial_literacy if self.profile.demographics else 'medium'}
- Goals: {self.profile.goals}

Guidance Provided:
"{guidance}"

Assess comprehension based on:
1. Customer's literacy level ({self.profile.demographics.financial_literacy if self.profile.demographics else 'medium'})
2. Complexity of guidance
3. Use of technical language vs plain English
4. Presence of analogies or examples
5. Whether advisor checked understanding

Determine:
- understanding_level: "not_understood" | "partially_understood" | "fully_understood"
- confusion_points: list of specific concepts that confused customer (empty if understood)
- customer_feeling: "confident" | "uncertain" | "overwhelmed" | "satisfied" | "confused"

Return JSON only, no explanation."""

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
        prompt = f"""Generate realistic customer response in pension guidance conversation.

Customer Profile:
- Age: {self.profile.demographics.age if self.profile.demographics else 'unknown'}
- Financial literacy: {self.profile.demographics.financial_literacy if self.profile.demographics else 'medium'}
- Goals: {self.profile.goals}

Advisor just said:
"{advisor_message}"

Comprehension Assessment:
- Understanding: {comprehension['understanding_level']}
- Confusion points: {comprehension['confusion_points']}
- Customer feeling: {comprehension['customer_feeling']}

Generate customer's response that:
1. Reflects their understanding level
   - If confused: Ask for clarification on specific points
   - If understood: Acknowledge and move forward or ask about next steps
   - If partially understood: Express understanding but ask about unclear parts

2. Matches their literacy level ({self.profile.demographics.financial_literacy if self.profile.demographics else 'medium'})
   - Low: Simple language, may need concepts explained again
   - Medium: Clear but not overly sophisticated
   - High: Can engage with more complex explanations

3. Is natural and conversational (1-3 sentences typically)

4. Shows realistic customer behavior:
   - If overwhelmed: Express anxiety or uncertainty
   - If confident: Express satisfaction and readiness to proceed
   - If uncertain: Ask for reassurance or examples

Customer response:"""

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
