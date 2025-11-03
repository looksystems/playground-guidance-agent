"""
Generate seed cases using LLM assistance.
"""

import sys
import json
from pathlib import Path
from uuid import uuid4
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv(override=True)

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
                    meta={
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
