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

    print("Loading pension knowledge to database...\n")

    # Process pension types
    print("Processing pension types...")
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
            meta=info
        )
        session.add(entry)
        count += 1
        print(f"  Added pension type: {pension_type}")

    # Process regulations
    print("\nProcessing regulations...")
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
                meta=info
            )
            session.add(entry)
            count += 1
            print(f"  Added regulation: {regulation_name}")

    # Process typical scenarios
    print("\nProcessing typical scenarios...")
    for scenario_name, info in PENSION_KNOWLEDGE["typical_scenarios"].items():
        content = f"Typical scenario for {scenario_name}: "

        # Handle different age field names
        if 'age_range' in info:
            age_min, age_max = info['age_range']
            content += f"Age {age_min}-{age_max}, "
        elif 'typical_age_range' in info:
            age_min, age_max = info['typical_age_range']
            content += f"Typical age {age_min}-{age_max}, "
        elif 'typical_age' in info:
            age_min, age_max = info['typical_age']
            content += f"Typical age {age_min}-{age_max}, "

        # Add pension count if available
        if 'pension_count_range' in info:
            content += f"typically {info['pension_count_range'][0]}-{info['pension_count_range'][1]} pensions, "

        # Add total value if available
        if 'total_value_range' in info:
            content += f"total value £{info['total_value_range'][0]:,}-£{info['total_value_range'][1]:,}. "

        # Add common goals if available
        if 'common_goals' in info:
            content += f"Common goals: {', '.join(info['common_goals'])}"

        entry = PensionKnowledge(
            id=uuid4(),
            content=content,
            category="typical_scenario",
            subcategory=scenario_name,
            embedding=embed(content),
            meta=info
        )
        session.add(entry)
        count += 1
        print(f"  Added scenario: {scenario_name}")

    # Process fee structures
    print("\nProcessing fee structures...")
    for fee_category, info in PENSION_KNOWLEDGE["fee_structures"].items():
        content = f"Fee structure for {fee_category}: "
        if isinstance(info, dict):
            content += " ".join([f"{k}={v}" for k, v in info.items()])
        
        entry = PensionKnowledge(
            id=uuid4(),
            content=content,
            category="fee_structure",
            subcategory=fee_category,
            embedding=embed(content),
            meta=info
        )
        session.add(entry)
        count += 1
        print(f"  Added fee structure: {fee_category}")

    session.commit()
    print(f"\n✅ Successfully loaded {count} pension knowledge entries")


if __name__ == "__main__":
    load_pension_knowledge_to_db()
