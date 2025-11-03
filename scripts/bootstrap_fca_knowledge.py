"""
Bootstrap FCA compliance knowledge from curated YAML file.
"""

import sys
import yaml
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.core.database import get_session, FCAKnowledge
from guidance_agent.retrieval.embeddings import embed


def load_fca_compliance_knowledge():
    """Load FCA compliance principles from YAML file into database."""

    # Load YAML file
    yaml_path = Path(__file__).parent.parent / "data" / "knowledge" / "fca_compliance_principles.yaml"
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        print("Please create the FCA compliance principles YAML file first")
        return

    with open(yaml_path) as f:
        principles = yaml.safe_load(f)

    session = get_session()
    count = 0

    print("Loading FCA compliance knowledge to database...\n")

    # Process each category
    for category, items in principles.items():
        print(f"\nProcessing category: {category}")

        for item in items:
            principle_text = item.get('principle', '')
            content_text = item.get('content', principle_text)

            # Main principle entry
            entry = FCAKnowledge(
                id=uuid4(),
                content=f"{principle_text}. {content_text}",
                source="FCA_Curated_Principles",
                category=category,
                embedding=embed(f"{principle_text}. {content_text}"),
                meta={
                    "principle": principle_text,
                    "fca_reference": item.get('fca_reference'),
                    "mandatory": item.get('mandatory', False)
                }
            )
            session.add(entry)
            count += 1

            # Add compliant examples as separate entries for better retrieval
            if 'examples_compliant' in item:
                for example in item['examples_compliant']:
                    example_entry = FCAKnowledge(
                        id=uuid4(),
                        content=f"Compliant example: {example}. Context: {principle_text}",
                        source="FCA_Curated_Principles",
                        category=f"{category}_examples",
                        embedding=embed(example),
                        meta={
                            "example_type": "compliant",
                            "parent_principle": principle_text
                        }
                    )
                    session.add(example_entry)
                    count += 1

            # Add non-compliant examples
            if 'examples_non_compliant' in item:
                for example in item['examples_non_compliant']:
                    example_entry = FCAKnowledge(
                        id=uuid4(),
                        content=f"Non-compliant example: {example}. Reason: {principle_text}",
                        source="FCA_Curated_Principles",
                        category=f"{category}_examples",
                        embedding=embed(example),
                        meta={
                            "example_type": "non_compliant",
                            "parent_principle": principle_text
                        }
                    )
                    session.add(example_entry)
                    count += 1

            # Add template if present
            if 'template' in item:
                template_entry = FCAKnowledge(
                    id=uuid4(),
                    content=f"Template for {category}: {item['template']}",
                    source="FCA_Curated_Principles",
                    category=f"{category}_templates",
                    embedding=embed(item['template']),
                    meta={
                        "template_type": category,
                        "key_elements": item.get('key_elements', [])
                    }
                )
                session.add(template_entry)
                count += 1

        print(f"  ✓ Added entries for {category}")

    session.commit()
    print(f"\n✅ Successfully loaded {count} FCA knowledge entries")


if __name__ == "__main__":
    load_fca_compliance_knowledge()
