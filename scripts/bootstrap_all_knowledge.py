"""
Master script to bootstrap all knowledge bases in sequence.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def run_script(script_name: str, description: str):
    """Run a bootstrap script and report status."""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}")

    script_path = Path(__file__).parent / script_name

    try:
        # Execute script in same Python process
        with open(script_path) as f:
            code = compile(f.read(), script_path, 'exec')
            exec(code, {'__name__': '__main__', '__file__': str(script_path)})
        print(f"✅ {description} - COMPLETED\n")
        return True
    except FileNotFoundError:
        print(f"⚠️  {script_name} not found - SKIPPED\n")
        return False
    except Exception as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}\n")
        return False


def main():
    """Bootstrap all knowledge bases."""

    print("\n" + "="*70)
    print("  KNOWLEDGE BASE BOOTSTRAP")
    print("  Comprehensive initialization of all knowledge bases")
    print("="*70)

    results = {}

    # Phase 1: Pension Knowledge
    results['pension'] = run_script(
        'load_pension_knowledge.py',
        'Phase 1: Loading Pension Domain Knowledge'
    )

    # Phase 2: FCA Compliance Knowledge
    results['fca'] = run_script(
        'bootstrap_fca_knowledge.py',
        'Phase 2: Loading FCA Compliance Knowledge'
    )

    # Phase 3: Seed Cases
    results['cases'] = run_script(
        'generate_seed_cases.py',
        'Phase 3: Generating Seed Cases (LLM-assisted)'
    )

    # Phase 4: Seed Rules
    results['rules'] = run_script(
        'generate_seed_rules.py',
        'Phase 4: Generating Seed Rules (LLM-assisted)'
    )

    # Summary
    print("\n" + "="*70)
    print("  BOOTSTRAP SUMMARY")
    print("="*70)

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for name, success in results.items():
        status = "✅ COMPLETED" if success else "❌ FAILED"
        print(f"  {name.title()}: {status}")

    print(f"\n  Overall: {success_count}/{total_count} completed successfully")

    if success_count == total_count:
        print("\n  🎉 All knowledge bases bootstrapped successfully!")
        print("  Ready to proceed with Phase 3 (Advisor Agent)")
    else:
        print("\n  ⚠️  Some knowledge bases failed to bootstrap")
        print("  Review errors above and re-run individual scripts")

    print("="*70 + "\n")


if __name__ == "__main__":
    main()
