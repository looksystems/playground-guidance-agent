"""
Verify all knowledge bases are properly populated.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.core.database import get_session, FCAKnowledge, PensionKnowledge, Case, Rule
from sqlalchemy import func


def verify_knowledge_bases():
    """Verify all knowledge bases have data."""

    session = get_session()

    print("\n" + "="*60)
    print("  KNOWLEDGE BASE VERIFICATION")
    print("="*60 + "\n")

    # Check FCA Knowledge
    fca_count = session.query(func.count(FCAKnowledge.id)).scalar()
    print(f"FCA Compliance Knowledge: {fca_count} entries")
    if fca_count == 0:
        print("  ⚠️  Warning: No FCA knowledge entries found")

    # Check Pension Knowledge
    pension_count = session.query(func.count(PensionKnowledge.id)).scalar()
    print(f"Pension Domain Knowledge: {pension_count} entries")
    if pension_count == 0:
        print("  ⚠️  Warning: No pension knowledge entries found")

    # Check Cases
    case_count = session.query(func.count(Case.id)).scalar()
    print(f"Case Base: {case_count} cases")
    if case_count == 0:
        print("  ⚠️  Warning: No seed cases found")
    elif case_count < 20:
        print(f"  ⚠️  Warning: Only {case_count} cases (recommended: 20-50)")

    # Check Rules
    rule_count = session.query(func.count(Rule.id)).scalar()
    print(f"Rules Base: {rule_count} rules")
    if rule_count == 0:
        print("  ⚠️  Warning: No seed rules found")
    elif rule_count < 5:
        print(f"  ⚠️  Warning: Only {rule_count} rules (recommended: 5-10)")

    # Overall status
    print("\n" + "="*60)
    all_populated = all([fca_count > 0, pension_count > 0, case_count >= 20, rule_count >= 5])

    if all_populated:
        print("  ✅ All knowledge bases properly populated")
        print("  Ready for Phase 3 (Advisor Agent) implementation")
    else:
        print("  ⚠️  Some knowledge bases need attention")
        print("  Review warnings above and re-run bootstrap scripts")

    print("="*60 + "\n")


if __name__ == "__main__":
    verify_knowledge_bases()
