"""
Generate seed rules using LLM assistance based on FCA requirements.
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
                meta={
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
