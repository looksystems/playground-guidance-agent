#!/usr/bin/env python3
"""Training script for advisor agents.

This script runs a virtual training session where an advisor agent practices
pension guidance consultations with simulated customers in an accelerated
time environment.

Usage:
    python scripts/train_advisor.py --consultations 1000
    python scripts/train_advisor.py --consultations 500 --acceleration 100
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import guidance_agent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from guidance_agent.environment import VirtualEnvironment
from guidance_agent.core.types import AdvisorProfile


def main():
    """Run advisor training session."""
    parser = argparse.ArgumentParser(
        description="Train an advisor agent using virtual consultations"
    )
    parser.add_argument(
        "--consultations",
        "-n",
        type=int,
        default=100,
        help="Number of consultations to run (default: 100)",
    )
    parser.add_argument(
        "--acceleration",
        "-a",
        type=int,
        default=60,
        help="Time acceleration factor (default: 60x)",
    )
    parser.add_argument(
        "--max-turns",
        "-t",
        type=int,
        default=20,
        help="Maximum turns per consultation (default: 20)",
    )
    parser.add_argument(
        "--progress-interval",
        "-p",
        type=int,
        default=100,
        help="Progress display interval (default: every 100)",
    )
    parser.add_argument(
        "--advisor-name",
        default="Sarah",
        help="Advisor name (default: Sarah)",
    )

    args = parser.parse_args()

    # Create advisor profile
    advisor_profile = AdvisorProfile(
        name=args.advisor_name,
        description="AI pension guidance specialist in training",
    )

    print("=" * 70)
    print("FINANCIAL GUIDANCE AGENT - VIRTUAL TRAINING ENVIRONMENT")
    print("=" * 70)
    print(f"\nAdvisor: {advisor_profile.name}")
    print(f"Consultations: {args.consultations}")
    print(f"Time Acceleration: {args.acceleration}x")
    print(f"Max Turns per Consultation: {args.max_turns}")
    print()

    # Create virtual environment
    env = VirtualEnvironment(
        advisor_profile=advisor_profile,
        acceleration_factor=args.acceleration,
        max_turns_per_consultation=args.max_turns,
        progress_interval=args.progress_interval,
    )

    # Run training
    try:
        metrics = env.run_training_session(
            num_consultations=args.consultations,
            display_progress=True,
        )

        # Display final results
        print("\n" + "=" * 70)
        print("TRAINING COMPLETE - FINAL RESULTS")
        print("=" * 70)
        print(f"\nPerformance Metrics:")
        print(f"  Total Consultations:      {metrics.total_consultations}")
        print(f"  Successful:               {metrics.successful_consultations} ({metrics.success_rate:.1%})")
        print(f"  Average Satisfaction:     {metrics.avg_satisfaction:.2f}/10")
        print(f"  Average Comprehension:    {metrics.avg_comprehension:.2f}/10")
        print(f"  Compliance Rate:          {metrics.compliance_rate:.1%}")
        print(f"\nLearning Progress:")
        print(f"  Cases Learned:            {metrics.cases_learned}")
        print(f"  Rules Learned:            {metrics.rules_learned}")
        print(f"\nTime:")
        print(f"  Virtual Time Elapsed:     {env.time_manager.get_elapsed_virtual_time()}")
        print(f"  Real Time Elapsed:        {env.time_manager.get_elapsed_real_time()}")
        print("=" * 70)

        return 0

    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        print(f"Completed {env.metrics.total_consultations} consultations.")
        return 1
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
